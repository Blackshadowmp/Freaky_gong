import discord
from discord.ext import commands
from ..core import bot
from ..utils import extract_video_info, currently_playing, tien_edit_check
from ..views import VideoSelect #, PlaylistButtons
from config.settings import YOUTUBE_API_KEY

import asyncio
import html
import aiohttp

song_queue_metadata = []
song_queue = []
current_song_meta = None
session: aiohttp.ClientSession | None = None

@bot.slash_command(name='play', description='Add a song to the queue and play it.')
async def play(ctx: discord.ApplicationContext, query: str):
    await ctx.response.defer()

    if not ctx.guild.voice_client:
        if ctx.user.voice:
            try:
                await asyncio.sleep(1)
                await ctx.user.voice.channel.connect()
            except Exception as e:
                if not ctx.response.is_done():
                    await ctx.respond(f'Failed to join the voice channel: {str(e)}', ephemeral=True)
                else:
                    await ctx.followup.send(f'Failed to join the voice channel: {str(e)}', ephemeral=True)
                return
        else:
            await ctx.followup.send('You are not in a voice channel!', ephemeral=True)
            return

    await handle_play(ctx, query)

@bot.slash_command(name='freak', description='Alias to play command.')
async def freak(ctx: discord.ApplicationContext, query: str):
    await play(ctx, query)

@bot.slash_command(name='skip', description='Skip the currently playing song.')
async def skip(ctx: discord.ApplicationContext):
    if currently_playing(ctx=ctx):
        await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.listening, name='Nothing'))
        embed = discord.Embed(
            title=f'{current_song_meta['title']} has been skipped',
            description=f'{ctx.user.display_name} skipped it',
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=ctx.user.display_avatar.url)
        await ctx.respond(embed=embed)

        if ctx.guild.voice_client:
            ctx.guild.voice_client.stop()
    else:
        await ctx.respond('No song is currently playing!', ephemeral=True)

async def handle_play(ctx: discord.ApplicationContext, query: str):
    global session

    if 'list=' in query:
        ydl_opts = {'quiet': True, 'extract_flat': 'in_playlist',"format": "bestaudio/best",'cookiefile': 'data/cookies.txt',}
        playlist_info = await extract_video_info(query, ydl_opts)
        videos = playlist_info.get('entries', [])
        if not videos:
            await ctx.followup.send('The playlist is empty or failed to load.', ephemeral=True)
            return
        number_to_add=min(30,len(videos))
        for _ in range(number_to_add):
            video=videos.pop(0)
            song_queue.append(video['url'])
            await add_info(ctx, video,video['url'])
        await ctx.followup.send(f'Added {number_to_add} songs to the queue', ephemeral=True)

    elif query.startswith('http://') or query.startswith('https://'):
        song_queue.append(query)
        ydl_opts = {'quiet': True, 'extract_flat': True,"format": "bestaudio/best",'cookiefile': 'data/cookies.txt',}
        info = await extract_video_info(query, ydl_opts)
        await add_info(ctx, info=info,query=query)

    else:
        if session is None or session.closed:
            session = aiohttp.ClientSession()

        search_url = (
            f'https://www.googleapis.com/youtube/v3/search'
            f'?part=snippet&type=video&maxResults=5&q={query}&key={YOUTUBE_API_KEY}'
        )
        async with session.get(search_url) as response:
            if response.status != 200:
                await ctx.followup.send('Failed to fetch results from YouTube.', ephemeral=True)
                return

            data = await response.json()
            videos = data.get('items', [])
            if not videos:
                await ctx.followup.send('No results found.', ephemeral=True)
                return

            embed = discord.Embed(
                title=f'Search Results for: {query}',
                description='Select a video from the dropdown below.',
                color=discord.Color.dark_orange()
            )
            embed.set_thumbnail(url=ctx.user.display_avatar.url)

            view = discord.ui.View()
            view.add_item(VideoSelect(ctx, videos, song_queue, song_queue_metadata))

            await ctx.followup.send(embed=embed, view=view)

async def add_info(ctx: discord.ApplicationContext, info, query):

    song_queue_metadata.append({
            'title': html.unescape(info.get('title', query)),
            'channel_title': html.unescape(info.get('uploader', 'Unknown Channel')),
            'user': html.unescape(ctx.user.display_name),
            'thumbnail': ctx.user.display_avatar.url
        })

    embed = discord.Embed(
            title=f'Added to queue: {html.unescape(info.get('title', query))}',
            description=f'Queued by {ctx.user.display_name}',
            color=discord.Color.yellow()
        )
    embed.set_thumbnail(url=ctx.user.display_avatar.url)
    await ctx.followup.send(embed=embed)

    if not currently_playing(ctx=ctx):
        await play_next(ctx)

async def play_next(ctx: discord.ApplicationContext):
    global current_song_meta
    if not song_queue:
        current_song_meta = None
        await bot.change_presence(
            status=discord.Status.idle,
            activity=discord.Activity(type=discord.ActivityType.listening, name='Nothing')
        )
        return

    url = song_queue.pop(0)
    metadata = song_queue_metadata.pop(0) if song_queue_metadata else {'user': 'Unknown User'}
    current_song_meta = metadata

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'cookiefile': 'data/cookies.txt',
    }

    info = await extract_video_info(url, ydl_opts)
    stream_url = info['url']

    vc = ctx.guild.voice_client
    if not vc or not vc.is_connected():
        print('[VoiceClient] Not connected to voice. Aborting playback.')
        return

    def after_playing(error):
        if error:
            print(f'[play_next] Error: {error}')
        fut = asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)
        try:
            fut.result()
        except Exception as e:
            print(f'[play_next Exception]: {e}')

    audio_source = discord.FFmpegOpusAudio(
        source=stream_url,
        before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 2',
        options='-vn -bufsize 64k'
    )
    vc.play(audio_source, after=after_playing)

    embed = discord.Embed(
        title=f'Now playing: {info['title']}',
        description=f'Uploaded by {metadata['channel_title']}\nQueued by {metadata['user']}\nSongs in queue: {len(song_queue)}',
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=metadata['thumbnail'])
    await ctx.followup.send(embed=embed)

    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name=metadata['title']))
    await tien_edit_check(ctx=ctx,chanel_name=metadata['channel_title'], video_name=info['title'])
    
def get_current_song_meta():
    global current_song_meta
    return current_song_meta if current_song_meta else None