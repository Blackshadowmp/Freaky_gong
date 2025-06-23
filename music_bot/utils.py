import asyncio
import yt_dlp
import discord
import aiohttp

session: aiohttp.ClientSession | None = None

def get_session() -> aiohttp.ClientSession:
    print('Getting aiohttp session')
    global session
    if session is None or session.closed:
        session = aiohttp.ClientSession()
    print(f'Aiohttp session is ready: {session}')
    return session

async def close_session():
    global session
    print(f'Closing aiohttp session: {session}')
    if session and not session.closed:
        await session.close()
        print('[Shutdown] aiohttp session closed')

# Extract video info using yt-dlp asynchronously
async def extract_video_info(url, ydl_opts):
    def run_ydl():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                _ = info.get('url', None)  # Force URL eval
            except :
                return None
        return info

    return await asyncio.to_thread(run_ydl)

def currently_playing(ctx: discord.ApplicationContext) -> bool:
    return (ctx.guild.voice_client and ctx.guild.voice_client.is_playing())
def is_valid(info):
    print(f'info: {info}')
    if info is None:
        return False
    
    return True
async def tien_edit_check(ctx: discord.ApplicationContext, chanel_name: str, video_name: str):
    keywords = [
    '3daysgrace', 'three days grace', 'three daysgrace', '3 days grace',
    'three days of grace', '3dg', 'three dg', 'tdg', 'grace 3 days',
    'three-days-grace', 'three.days.grace', 'threedaysgrace', 'three_days_grace',
    '3days-grace', '3-days-grace', '3.days.grace', 'three days g',
    'three dg', '3 dg', 'three d grace'
    ]
    gif_path = './data/tien_edit.gif'
    if any(keyword in chanel_name.lower() or keyword in video_name.lower() for keyword in keywords):
        await ctx.send(file=discord.File(gif_path))