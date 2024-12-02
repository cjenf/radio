import discord
import os 
import asyncio
from urllib.parse import urlparse, parse_qs
from view import MusicView
from dotenv import load_dotenv
from collections import deque
from youtubesearchpython import VideosSearch
from data import adata
from typing import List, Deque, Dict
from source import _get
from yt_dlp import DownloadError


load_dotenv() 
bot = discord.Bot()

voice_client:Dict= {}
queue:Deque= deque()
source_url:str= ""
current:List= []
Embed:discord.Embed= discord.Embed()

_FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
    'options': '-vn'
    }

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

async def search(
    ctx: discord.ApplicationContext,
    item:str
    ) -> adata:
    """
    search youtube for item.
    :param item: The item to search for
    :type item: str
    :return: result
    :rtype: result
    """
    if item.startswith("https://www.youtube.com"):
        if (audio :=await _get(item)):
            if isinstance(audio, DownloadError): 
                await ctx.respond(audio)
            elif isinstance(audio, bool) and audio  is False:
                await ctx.respond("Video not found")
            else:
                vid_id= id(item)
                _data= adata(f"https://www.youtube.com/watch?v={vid_id}")
                return [_data, audio]
        
    else:
        search= VideosSearch(item, limit=1)
        url= search.result()["result"][0]["link"]
        vid_id= id(url)
        audio= await _get(f"https://www.youtube.com/watch?v={vid_id}")
        if isinstance(audio, DownloadError): 
            await ctx.respond(audio)
        elif isinstance(audio, bool) and audio  is False:
            await ctx.respond("Video not found")
        else:
            _data= adata(f"https://www.youtube.com/watch?v={vid_id}")
            return [_data, audio]
        
def id(url:str):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return query_params.get("v", [None])[0]
    
async def next(ctx: discord.ApplicationContext) -> None:
    """
    play the next item in the queue.

    :param ctx: discord.ApplicationContext
    :return: None
    """
    if queue:
        item=queue.popleft()
        vc=voice_client[ctx.author.voice.channel.id]
        global source_url, Embed
        source_url=item[1][0]['url']
        vc.play(discord.FFmpegPCMAudio(item[1][1], **_FFMPEG_OPTIONS), after=lambda e: print(e) if e else asyncio.run_coroutine_threadsafe(next(ctx), bot.loop))
        embed=discord.Embed(
            title=f"**{item[1][0]['title']}**",
            color=discord.Color.blue()
            )
        embed.add_field(
            name="duration",
            value=f"> **{item[1][0]['length']}**"
            )
        embed.add_field(
            name="views",
            value=f"> **{item[1][0]['views']}**"
            )
        embed.add_field(
            name="author",
            value=f"> **{item[1][0]['author']}**"
            )
        embed.set_thumbnail(url=item[1][0]['thumbnail'])
        Embed=embed
        await ctx.respond(
            f"⚙️ now playing **{item[1][0]['title']}** ...", 
            embed=embed,
            view=MusicView(vc.is_paused(), source_url)
            )
    else:
        await ctx.interaction.followup.send("**queue is empty<:whiteexclamationmark_2755:1311298893866340362>**")

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
            global source_url, Embed
            source_url=item[1][0]['url']
            vc.play(discord.FFmpegPCMAudio(item[1][1], **_FFMPEG_OPTIONS), after=lambda e: print(e) if e else asyncio.run_coroutine_threadsafe(next(ctx), bot.loop))
            embed=discord.Embed(
                title=f"**{item[1][0]['title']}**",
                color=discord.Color.blue()
                )
            embed.add_field(
                name="duraction",
                value=f"> **{item[1][0]['length']}**"
                )
            embed.add_field(
                name="views",
                value=f"> **{item[1][0]['views']}**"
                )
            embed.add_field(
                name="author",
                value=f"> **{item[1][0]['author']}**"
                )
            embed.set_thumbnail(url=item[1][0]['thumbnail'])
            Embed=embed
            await ctx.interaction.followup.send(
                    f"⚙️ now playing **{item[1][0]['title']}** ...", 
                    embed=embed,
                    view=MusicView(False, source_url)
                    )
    else:
        pass

@bot.slash_command(
    name="play",
    description="play music"
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
    global current
    if not ctx.author.voice:
        return await ctx.respond("**Please join the voice channel first.**")
    
    if voice_client:
        if ctx.author.voice.channel.id not in voice_client.keys(): 
            return await ctx.respond("<:multiply_2716fe0f:1311300000822857789> **The bot has joined the voice channel, execute this command on the correct voice channel.**")
        else:
            result= await search(ctx,query)
            current=[query, result]
            queue.append([query, result])
            
            await asyncio.gather(
                ctx.respond("<:checkmark_2714fe0f:1311300012227166268> ****The song has been added to the queue.****"), 
                play_music(ctx)
            )
    else:     
        vc = await ctx.author.voice.channel.connect()
        voice_client[ctx.author.voice.channel.id]=vc
        result= await search(ctx,query)
        if result:
            current=[query, result]
            queue.append([query, result])
        else:
            return await ctx.interaction.followup.send(f"**<:multiply_2716fe0f:1311300000822857789> The video could not be found ...**")
        
        await asyncio.gather(
            ctx.interaction.followup.send(f"<:checkmark_2714fe0f:1311300012227166268> **The song has been added to the queue.**"),
            play_music(ctx)
        )
        
       
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
            try:
                await interaction.response.edit_message(embed=Embed, view=MusicView(True, source_url))
            except discord.errors.NotFound as e:
                print(e)

        elif interaction.data["custom_id"] == "pause":
            vc=voice_client[interaction.user.voice.channel.id]
            vc.resume()
            await interaction.response.edit_message(embed=Embed, view=MusicView(False, source_url))

        elif interaction.data["custom_id"] == "next":
            vc=voice_client[interaction.user.voice.channel.id]
            if queue:
                vc.stop()
                await interaction.response.edit_message(embed=Embed, view=MusicView(False, source_url))
            else:
                await asyncio.gather(
                    interaction.response.edit_message(embed=Embed, view=MusicView(False, source_url)),
                    interaction.channel.send("**queue is empty<:whiteexclamationmark_2755:1311298893866340362>**")
                )

        elif interaction.data["custom_id"] == "repeat":
            vc=voice_client[interaction.user.voice.channel.id]
            queue.appendleft(current)
            vc.stop()
            try:
                await interaction.response.edit_message(embed=Embed, view=MusicView(False, source_url))
            except discord.errors.InteractionResponded as e:
                print(e)
            
    await bot.process_application_commands(interaction)


if __name__ == "__main__":
    bot.run(os.getenv('TOKEN')) 