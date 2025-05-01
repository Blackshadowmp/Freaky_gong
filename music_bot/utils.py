import asyncio
import yt_dlp
import discord

# Extract video info using yt-dlp asynchronously
async def extract_video_info(url, ydl_opts):
    def run_ydl():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            _ = info.get('url', None)  # Force URL eval
        return info

    return await asyncio.to_thread(run_ydl)

def currently_playing(ctx: discord.ApplicationContext) -> bool:
    return (ctx.guild.voice_client and ctx.guild.voice_client.is_playing())

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