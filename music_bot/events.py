import asyncio
import aiohttp
import discord
from .core import bot

session: aiohttp.ClientSession | None = None

def handle_sigint():
    loop = asyncio.get_event_loop()
    loop.create_task(graceful_shutdown())

async def graceful_shutdown():
    print('Shutting down gracefully...')

    global session
    if session and not session.closed:
        await session.close()
        print('[Shutdown] aiohttp session closed')

    for vc in bot.voice_clients:
        if vc.is_playing():
            vc.stop()
        await vc.disconnect(force=True)
        print('[Shutdown] Disconnected from voice')

    await bot.close()

@bot.event
async def on_shutdown():
    if session and not session.closed:
        await session.close()
    for vc in bot.voice_clients:
        if vc.is_playing():
            vc.stop()
        await vc.disconnect(force=True)

@bot.event
async def on_ready():
    global session
    if session is None or session.closed:
        session = aiohttp.ClientSession()

    await bot.change_presence(
        status=discord.Status.idle,
        activity=discord.Activity(type=discord.ActivityType.listening, name='Nothing')
    )
    print(f'[Startup] Logged in as {bot.user} and synced commands.')
