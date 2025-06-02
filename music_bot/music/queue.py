import discord
from discord.ext import commands
from ..core import bot
import html
from .playback import song_queue_metadata, song_queue

@bot.slash_command(name='queue', description='List songs in the queue')
async def queue(ctx: discord.ApplicationContext):
    await ctx.response.defer()
    if song_queue_metadata:
        embed = discord.Embed(
            title='Current Song Queue',
            description=f'Top {min(len(song_queue_metadata), 25)} songs currently in the queue:',
            color=discord.Color.blurple()
        )

        for idx, metadata in enumerate(song_queue_metadata[:25], start=1):
            title = html.unescape(metadata.get('title', 'Unknown Title'))
            channel_title = html.unescape(metadata.get('channel_title', 'Unknown Channel'))
            username = html.unescape(metadata.get('user', 'Unknown User'))

            embed.add_field(
                name=f'{idx}.) {title}',
                value=f'Uploaded by **{channel_title}** | Added by **{username}**',
                inline=False
            )

        embed.set_thumbnail(url=ctx.user.display_avatar.url)
    else:
        embed = discord.Embed(
            title='Current Song Queue',
            description='The queue is empty.',
            color=discord.Color.red()
        )

    await ctx.followup.send(embed=embed)

@bot.slash_command(name='clear_queue', description='Clears the queue without skipping the current song')
async def clear_queue(ctx: discord.ApplicationContext):
    song_queue.clear()
    song_queue_metadata.clear()
    embed = discord.Embed(
        title=f'{ctx.user.display_name} has cleared the queue',
        color=discord.Color.dark_red()
    )
    embed.set_thumbnail(url=ctx.user.display_avatar.url)
    await ctx.respond(embed=embed)
