import discord
import os 
import asyncio
from nowon import Now
from urllib.parse import urlparse, parse_qs
from view import MusicView,  QueueView
from dotenv import load_dotenv
from collections import deque
from youtubesearchpython import VideosSearch
from data import adata
from typing import Deque, Dict
from source import _get
from yt_dlp import DownloadError


load_dotenv() 
bot = discord.Bot()
now=Now()
voice_client:Dict= {}
queue:Deque= deque()


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
        now.source_url=item[1][0]['url']
        esource=discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(item[1][1], **_FFMPEG_OPTIONS))
        esource.volume=0.5
        now.asource=esource
        vc.play(esource, after=lambda e: print(e) if e else asyncio.run_coroutine_threadsafe(next(ctx), bot.loop))
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
        now.Embed=embed
        await ctx.send(
            f"⚙️ now playing **{item[1][0]['title']}** ...", 
            embed=embed,
            view=MusicView(vc.is_paused(), now.source_url)
            )
    else:
        if vc.is_connected():
            await ctx.interaction.followup.send(
                embed=discord.Embed(
                description="**Queue is empty.**",
                color=discord.Color.red()
                )
            )
        elif vc.is_connected()==False:
            await ctx.send(
                embed=discord.Embed(
                description="**bot disconnected**",
                color=discord.Color.red()
                )
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
            now.source_url=item[1][0]['url']
            esource=discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(item[1][1], **_FFMPEG_OPTIONS))
            esource.volume=0.5
            now.asource=esource
            vc.play(esource, after=lambda e: print(e) if e else asyncio.run_coroutine_threadsafe(next(ctx), bot.loop))
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
            now.Embed=embed
            await ctx.send(
                    f"⚙️ now playing **{item[1][0]['title']}** ...", 
                    embed=embed,
                    view=MusicView(False, now.source_url)
                    )
    else:
        pass

@bot.slash_command(
    name="play",
    description="Plays a song in the voice channel."
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
        await ctx.interaction.followup.send(
            embed=discord.Embed(
                description=f"<:warn:1313125520032006164> **Please join the voice channel first.**",
                color=discord.Color.red()
            ),
            ephemeral=True
        )
    
    if voice_client:
        if ctx.author.voice.channel.id not in voice_client.keys(): 
            await ctx.interaction.followup.send(
                embed=discord.Embed(
                description="<:x_:1313130964146196490> **The bot has joined the voice channel, execute this command on the correct voice channel.**", 
                color=discord.Color.red(),
                ),
                ephemeral=True
            )
        else:
            result= await search(ctx,query)
            now.current=[query, result]
            queue.append(now.current)
            
            await asyncio.gather(
                ctx.interaction.followup.send(
                embed=discord.Embed(
                    description=f"<:tick:1313128320812056646> **The song has been added to the queue.**",
                    color=discord.Color.blue()
                    )
                ),
                play_music(ctx)
            )
    else:     
        vc = await ctx.author.voice.channel.connect()
        voice_client[ctx.author.voice.channel.id]=vc
        result= await search(ctx,query)
        if result:
            now.current=[query, result]
            queue.append(now.current)
        else:
            await ctx.interaction.followup.send(f"**<:multiply_2716fe0f:1311300000822857789> The video could not be found ...**")
        await asyncio.gather(
            ctx.interaction.followup.send(
                embed=discord.Embed(
                    description=f"<:tick:1313128320812056646> **The song has been added to the queue.**",
                    color=discord.Color.blue()
                    )
                ),
            play_music(ctx)
        )
    
@bot.slash_command(
    name="queue",   
    description="Displays the current queue."
    )
async def current_queue(ctx: discord.ApplicationContext) -> None:
    """
    :param ctx: discord.ApplicationContext
    :return: None
    """
    await ctx.response.defer(invisible=False)
    if (group:=len(queue)//10)>=1:
        now.data_page={f"{i+1}": list(queue)[i*10:(i+1)*10] for i in range(group)}
        if group%10!=0:
            now.data_page.update({f"{group+1}": list(queue)[group*10:]})
        embed=discord.Embed(
            footer=discord.EmbedFooter(text=f"[1/{len(now.data_page)}]"),
            )
        for i,s in enumerate(now.data_page[f"{now.current_queue_index}"]):
            embed.add_field(
                    name='',
                    value=f"**{i+1}.** [{s[1][0]['title']}]({s[1][0]['url']}) **`[{s[1][0]['length']}]`**",
                    inline=False
                )
        c= now.current_queue_index   
        indices = [
            c -2, 
            c -1, 
            c + 1, 
            c +2
            ]
        
        for i, index in enumerate(indices):
            now.cool[i] = not bool(now.data_page.get(str(index), False))

        await ctx.interaction.followup.send(embed=embed, view=QueueView(now.cool))

    elif not bool(queue):
        embed=discord.Embed(
            description=f"<:multiply_2716fe0f:1311300000822857789> **The queue is empty.**",
            color=discord.Color.red()
            )
        await ctx.interaction.followup.send(embed=embed)
    else:
        embed=discord.Embed(
                footer=discord.EmbedFooter(text=f"[1/1]"),
        )
        for i,s in enumerate(list(queue)[:len(queue)]):
            embed.add_field(
                    name='',
                    value=f"**{i+1}.** [{s[1][0]['title']}]({s[1][0]['url']}) **`[{s[1][0]['length']}]`**",
                    inline=False
                )
        now.cool=[True]*4
        await ctx.interaction.followup.send(embed=embed, view=QueueView(now.cool))
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
        if voice_client:
            if interaction.data["custom_id"] == "resume":
                vc=voice_client[interaction.user.voice.channel.id]
                vc.pause()
                try:
                    await interaction.response.edit_message(embed=now.Embed, view=MusicView(True, now.source_url))
                except discord.errors.NotFound as e:
                    print(e)

            elif interaction.data["custom_id"] == "pause":
                vc=voice_client[interaction.user.voice.channel.id]
                vc.resume()
                await interaction.response.edit_message(embed=now.Embed, view=MusicView(False, now.source_url))
                
            elif interaction.data["custom_id"] == "next":
                
                vc=voice_client[interaction.user.voice.channel.id]
                if queue:
                    vc.stop()
                    await interaction.response.edit_message(embed=now.Embed, view=MusicView(False, now.source_url))
                else:
                    await asyncio.gather(
                        interaction.response.edit_message(embed=now.Embed, view=MusicView(False, now.source_url)),
                        interaction.followup.send(
                            embed=discord.Embed(
                                description="**<:warn:1313125520032006164> There's no next song in the queue**", 
                                color=discord.Color.red()
                            ),
                        ephemeral=True
                        )
                    )
                
            elif interaction.data["custom_id"] == "repeat":
                
                vc=voice_client[interaction.user.voice.channel.id]
                queue.appendleft(now.current)
                vc.stop()
                try:
                    await interaction.response.edit_message(embed=now.Embed, view=MusicView(False, now.source_url))
                except discord.errors.InteractionResponded as e:
                    print(e)
            
            elif interaction.data["custom_id"] == "soundplus":
                if now.asource.volume<1.0:
                    now.asource.volume+=0.1
                    await interaction.response.edit_message(embed=now.Embed, view=MusicView(False, now.source_url))
                elif now.asource.volume>1.0:
                    await interaction.response.edit_message(embed=now.Embed, view=MusicView(False, now.source_url))
                    await interaction.followup.send(
                        embed=discord.Embed(
                            description="**<:warn:1313125520032006164> The maximum volume is reached.**",
                            color=discord.Color.red()
                        ),
                        ephemeral=True
                    )
            
            elif interaction.data["custom_id"] == "soundminus":
                if now.asource.volume>0:
                    now.asource.volume-=0.1
                    await interaction.response.edit_message(embed=now.Embed, view=MusicView(False, now.source_url))
                elif now.asource.volume<0:
                    await interaction.response.edit_message(embed=now.Embed, view=MusicView(False, now.source_url))
                    await interaction.followup.send(
                        embed=discord.Embed(
                            description="**<:warn:1313125520032006164> The minimum volume is reached.**",
                            color=discord.Color.red()
                        ),
                        ephemeral=True
                    )
                    
            elif interaction.data["custom_id"] == "stop":
                vc=voice_client[interaction.user.voice.channel.id]
                await asyncio.gather(
                    vc.disconnect(),
                    interaction.response.edit_message(embed=now.Embed, view=MusicView(False, now.source_url)),
                    interaction.followup.send(
                    embed=discord.Embed(
                    description="**bot disconnected**",
                    color=discord.Color.red()
                        ),
                    )
                )
                voice_client.clear()

            elif interaction.data["custom_id"] == "chevronsleft":
                now.current_queue_index-=2
                embed=discord.Embed(
                    footer=discord.EmbedFooter(text=f"[{now.current_queue_index}/{len(now.data_page)}]"),
                )
                if now.data_page.get(f"{now.current_queue_index}"):
                    for i,s  in enumerate(now.data_page[f"{now.current_queue_index}"]):
                        embed.add_field(
                            name='',
                            value=f"**{i+1}.** [{s[1][0]['title']}]({s[1][0]['url']}) **`[{s[1][0]['length']}]`**",
                            inline=False
                        )
                        c= now.current_queue_index
                    indices = [
                        c -2, 
                        c -1, 
                        c + 1,     
                        c +2
                        ]
                    for i, index in enumerate(indices):
                        now.cool[i] = not bool(now.data_page.get(str(index), False))
                    await interaction.response.edit_message(embed=embed, view=QueueView(now.cool))
            
            elif interaction.data["custom_id"] == "chevronleft":
                now.current_queue_index-=1
                embed=discord.Embed(
                    footer=discord.EmbedFooter(text=f"[{now.current_queue_index}/{len(now.data_page)}]"),
                )
                if now.data_page.get(f"{now.current_queue_index}"):
                    for i,s  in enumerate(now.data_page[f"{now.current_queue_index}"]):
                        embed.add_field(
                            name='',
                            value=f"**{i+1}.** [{s[1][0]['title']}]({s[1][0]['url']}) **`[{s[1][0]['length']}]`**",
                            inline=False
                        )

                    c= now.current_queue_index
                    indices = [
                        c -2, 
                        c -1, 
                        c + 1,     
                        c +2
                        ]
                    for i, index in enumerate(indices):
                        now.cool[i] = not bool(now.data_page.get(str(index), False))
                    await interaction.response.edit_message(embed=embed, view=QueueView(now.cool))
                
            elif interaction.data["custom_id"] == "chevronright":

                now.current_queue_index+=1
                embed=discord.Embed(
                    footer=discord.EmbedFooter(text=f"[{now.current_queue_index}/{len(now.data_page)}]"),
                )
                if now.data_page.get(f"{now.current_queue_index}"):
                    for i,s  in enumerate(now.data_page[f"{now.current_queue_index}"]):
                        embed.add_field(
                            name='',
                            value=f"**{i+1}.** [{s[1][0]['title']}]({s[1][0]['url']}) **`[{s[1][0]['length']}]`**",
                            inline=False
                        )
                    c= now.current_queue_index
                    indices = [
                        c -2, 
                        c -1, 
                        c + 1, 
                        c +2
                        ]
                    for i, index in enumerate(indices):
                        now.cool[i] = not bool(now.data_page.get(str(index), False))
                    await interaction.response.edit_message(embed=embed, view=QueueView(now.cool))
            
            elif interaction.data["custom_id"] == "chevronsright":
                now.current_queue_index+=2
                embed=discord.Embed(
                    footer=discord.EmbedFooter(text=f"[{now.current_queue_index}/{len(now.data_page)}]"),
                )
                if now.data_page.get(f"{now.current_queue_index}"):    
                    for i,s  in enumerate(now.data_page[f"{now.current_queue_index}"]):
                        embed.add_field(
                            name='',
                            value=f"**{i+1}.** [{s[1][0]['title']}]({s[1][0]['url']}) **`[{s[1][0]['length']}]`**",
                            inline=False
                        )
                    c= now.current_queue_index
                    indices = [
                        c -2, 
                        c -1, 
                        c + 1,     
                        c +2
                        ]
                    for i, index in enumerate(indices):
                        now.cool[i] = not bool(now.data_page.get(str(index), False))
                    await interaction.response.edit_message(embed=embed, view=QueueView(now.cool))
               
        else:
            await interaction.followup.send(
                    embed=discord.Embed(
                        description="**<:warn:1313125520032006164> You can't do it because of bot disconnect.**", 
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )
            
    
    await bot.process_application_commands(interaction)


if __name__ == "__main__":
    bot.run(os.getenv('TOKEN')) 