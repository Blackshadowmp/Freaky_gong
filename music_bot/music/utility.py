import discord
from discord.ext import commands
from ..core import bot
import sys
import os
from .playback import get_current_song_meta

@bot.slash_command(name='current_song', description='Gives title of current song playing on the bot')
async def current_song(ctx: discord.ApplicationContext):
    current_song_meta = get_current_song_meta()
    if current_song_meta is not None:
        embed = discord.Embed(
            title=current_song_meta['title'],
            description=(
                f'Uploaded by {current_song_meta['channel_title']}\n'
                f'Queued by {current_song_meta['user']}'
            ),
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url=ctx.user.display_avatar.url)
        await ctx.respond(embed=embed)
    else:
        await ctx.respond('There is no song currently playing.', ephemeral=True)

@bot.slash_command(name='restart', description='Restart the bot.')
async def restart(ctx: discord.ApplicationContext):
    try:
        if not ctx.response.is_done():
            await ctx.response.defer()

        embed = discord.Embed(
            title=f'{ctx.user.display_name} has restarted the bot',
            color=discord.Color.brand_red()
        )
        embed.set_thumbnail(url=ctx.user.display_avatar.url)
        await ctx.followup.send(embed=embed)

    except discord.NotFound:
        print('[restart] Interaction expired. Skipping response.')

    # Shutdown bot first
    from music_bot.events import graceful_shutdown
    await graceful_shutdown()

    # Restart the script
    python = sys.executable
    script = sys.argv[0]
    os.execv(python, [python, script])
