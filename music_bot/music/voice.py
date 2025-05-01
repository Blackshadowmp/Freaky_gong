import discord
from discord.ext import commands
from ..core import bot

song_queue_metadata = []
song_queue = []

@bot.slash_command(name='join', description='Join the user s current voice channel.')
async def join(ctx: discord.ApplicationContext):
    if ctx.user.voice:
        channel = ctx.user.voice.channel
        await channel.connect()
        await ctx.respond('Joining...', ephemeral=True)
    else:
        await ctx.respond('You are not in a voice channel!', ephemeral=True)

@bot.slash_command(name='leave', description='Leave the voice channel and clear the queue.')
async def leave(ctx: discord.ApplicationContext):
    if ctx.guild.voice_client:
        await ctx.guild.voice_client.disconnect(force=True)
        song_queue.clear()
        song_queue_metadata.clear()
        await ctx.respond('Disconnected and cleared the queue!', ephemeral=True)
    else:
        await ctx.respond('I m not in a voice channel!', ephemeral=True)
