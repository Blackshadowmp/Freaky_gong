import asyncio
import discord
from .core import bot
from .utils import get_session, close_session

def handle_sigint():
    loop = asyncio.get_event_loop()
    loop.create_task(graceful_shutdown())

async def graceful_shutdown():
    print('Shutting down gracefully...')

    await close_session()

    for vc in bot.voice_clients:
        if vc.is_playing():
            vc.stop()
        await vc.disconnect(force=True)
        print('[Shutdown] Disconnected from voice')

    await bot.close()

@bot.event
async def on_shutdown():
    await close_session()
    for vc in bot.voice_clients:
        if vc.is_playing():
            vc.stop()
        await vc.disconnect(force=True)

@bot.event
async def on_ready():
    session = get_session()
    if session is None or session.closed:
        print('[on_ready] aiohttp session is not available, start up failed?')
        return
    await bot.change_presence(
        status=discord.Status.idle,
        activity=discord.Activity(type=discord.ActivityType.listening, name='Nothing')
    )
    print(f'[Startup] Logged in as {bot.user} and synced commands.')
