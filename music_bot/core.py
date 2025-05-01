import discord
from discord.ext import commands

# Create intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True  # (Needed for music)

# Create the bot
bot = commands.Bot(command_prefix='!', intents=intents)
