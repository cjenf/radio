import discord
import os 
import asyncio
from urllib.parse import urlparse, parse_qs
from view import MusicView
from dotenv import load_dotenv
from collections import deque
from youtubesearchpython import VideosSearch
from dataclasses import dataclass
from source import _source
from data import adata
from check import check_youtube_video


load_dotenv() 
bot = discord.Bot()

voice_client={}
queue=deque()
source_url=''

_FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
    'options': '-vn'
    }


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

def search(item:str) -> adata:
    """
    search youtube for item.
    :param item: The item to search for
    :type item: str
    :return: result
    :rtype: result
    """
    if item.startswith("https://www.youtube.com"):
        if check_youtube_video(item):
            parsed_url = urlparse(item)
            query_params = parse_qs(parsed_url.query)
            video_id = query_params.get("v", [None])[0]
            _data= adata(f"https://www.youtube.com/watch?v={video_id}")
            return _data
        else:
            return check_youtube_video(item)
        
    else:
        search= VideosSearch(item, limit=1)
        url= search.result()["result"][0]["link"]
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        video_id = query_params.get("v", [None])[0]
        _data= adata(f"https://www.youtube.com/watch?v={video_id}")
        return _data
    
async def next(ctx: discord.ApplicationContext) -> None:
    """
    play the next item in the queue.

    :param ctx: discord.ApplicationContext
    :return: None
    """
    if queue:
        item=queue.popleft()
        vc=voice_client[ctx.author.voice.channel.id]
        global source_url
        source_url=item[1]['url']
        vc.play(discord.FFmpegPCMAudio(item[1]['source'], **_FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(next(ctx), bot.loop))
        embed=discord.Embed(
            title=f"**{item[1]['title']}**",
            color=discord.Color.blue()
            )
        embed.add_field(
            name="💿duration",
            value=f"> **{item[1]['length']}**"
            )
        embed.add_field(
            name="👀views",
            value=f"> **{item[1]['views']}**"
            )
        embed.add_field(
            name="🖊️author",
            value=f"> **{item[1]['author']}**"
            )
        embed.set_thumbnail(url=item[1]['thumbnail'])
        
        await ctx.channel.send(
            f"正在播放 **{item[1]['title']}**", 
            embed=embed,
            view=MusicView(vc.is_paused(), item[1]['url'])
            )

async def play_music(ctx : discord.ApplicationContext) -> None:
    """
    play the next item in the queue.

    :param ctx: discord.ApplicationContext
    :return: None
    """
    vc= voice_client[ctx.author.voice.channel.id]
    if not vc.is_playing():
        if queue:
            item=queue.popleft()
            global source_url
            source_url=item[1]['url']
            vc.play(discord.FFmpegPCMAudio(item[1]['source'], **_FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(next(ctx), bot.loop))
            embed=discord.Embed(
                title=f"**{item[1]['title']}**",
                color=discord.Color.blue()
                )
            embed.add_field(
                name="💿duraction",
                value=f"> **{item[1]['length']}**"
                )
            embed.add_field(
                name="👀views",
                value=f"> **{item[1]['views']}**"
                )
            embed.add_field(
                name="🖊️author",
                value=f"> **{item[1]['author']}**"
                )
            embed.set_thumbnail(url=item[1]['thumbnail'])
            
            await ctx.channel.send(
                f"正在播放 **{item[1]['title']}**", 
                embed=embed,
                view=MusicView(vc.is_paused(), item[1]['url'])
                )


@bot.slash_command(
    name="撥放",
    description="撥放音樂"
)
async def play(
        ctx: discord.ApplicationContext, 
        query: str
    ) -> None:
    """
    :param ctx:discord.ApplicationContext
    :param query:str
    :return: None
    """
    await ctx.response.defer(invisible=False)
    if not ctx.author.voice:
        return await ctx.respond("請先加入語音頻道")
    
    if voice_client:
        if ctx.author.voice.channel.id not in voice_client.keys(): 
            return await ctx.respond("✖️ 機器人已加入語音頻道，請在正確的語音頻道上執行此指令")
        else:
            result= search(query)
            queue.append([query, result])
            await ctx.respond("✔️已將歌曲加入播放清單")
            await play_music(ctx)
    else:     
        vc = await ctx.author.voice.channel.connect()
        voice_client[ctx.author.voice.channel.id]=vc
        result= search(query)
        queue.append([query, result])
        await ctx.respond("✔️已將歌曲加入播放清單")
        await play_music(ctx)

@bot.slash_command(
    name="重複循環",
    description="重複循環播放音樂"
)
async def repeat(
        ctx: discord.ApplicationContext
    ) -> None:
    """
    :param ctx:discord.ApplicationContext
    :return: None
    """
    if voice_client:
        if ctx.author.voice.channel.id in voice_client.keys(): 
            vc=voice_client[ctx.author.voice.channel.id]
            vc.stop()
            await ctx.respond("✔️已停止播放")

@bot.event
async def on_interaction(interaction: discord.Interaction) -> None:
    """
    Handles interaction events for the Discord bot.

    This function is triggered when an interaction is received. It checks the
    custom_id in the interaction data and performs actions such as pausing, 
    resuming, or stopping the music playback based on the interaction type.

    :param interaction: The interaction object from Discord, containing information
                        about the event and the user who triggered it.

    :type interaction: discord.Interaction
    """
    if interaction.data and interaction.data.get("custom_id",False):
        if interaction.data["custom_id"] == "resume":
            vc=voice_client[interaction.user.voice.channel.id]
            vc.pause()
            await interaction.response.edit_message(view=MusicView(True, source_url))

        elif interaction.data["custom_id"] == "pause":
            vc=voice_client[interaction.user.voice.channel.id]
            vc.resume()
            await interaction.response.edit_message(view=MusicView(False, source_url))

        elif interaction.data["custom_id"] == "next":
            vc=voice_client[interaction.user.voice.channel.id]
            vc.stop()
            await interaction.response.edit_message(view=MusicView(False, source_url))
            
            
    await bot.process_application_commands(interaction)

if __name__ == "__main__":
    bot.run(os.getenv('TOKEN')) 