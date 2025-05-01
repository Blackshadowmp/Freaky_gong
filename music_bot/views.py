import discord
import html

class VideoSelect(discord.ui.Select):
    def __init__(self, ctx, videos, song_queue, song_queue_metadata):
        options = [
            discord.SelectOption(
                label=html.unescape(video['snippet']['title'])[:100],  # Discord limit
                description=f'Uploaded by {html.unescape(video['snippet']['channelTitle'])}'[:100],
                value=video['id']['videoId'] if 'id' in video and 'videoId' in video['id'] and video['id']['videoId'] else str(i)
            )
            for i, video in enumerate(videos)
        ]

        super().__init__(placeholder='Select a video to play', options=options)

        self.ctx = ctx
        self.videos = videos
        self.song_queue = song_queue
        self.song_queue_metadata = song_queue_metadata

    async def callback(self, interaction: discord.Interaction):
        video_id = self.values[0]

        # Try to find by videoId match
        selected_video = next(
            (v for v in self.videos if v.get('id', {}).get('videoId') == video_id),
            None
        )

        # If not found, maybe it was a fallback index value
        if not selected_video and video_id.isdigit():
            try:
                selected_video = self.videos[int(video_id)]
                video_id = selected_video.get('id', {}).get('videoId')
            except (IndexError, ValueError):
                selected_video = None

        if not selected_video or not video_id:
            await interaction.response.send_message('Could not find the selected video.', ephemeral=True)
            return

        video_url = f'https://www.youtube.com/watch?v={video_id}'
        self.song_queue.append(video_url)
        self.song_queue_metadata.append({
            'title': html.unescape(selected_video['snippet']['title']),
            'channel_title': html.unescape(selected_video['snippet']['channelTitle']),
            'user': html.unescape(self.ctx.user.display_name),
            'thumbnail': self.ctx.user.display_avatar.url
        })

        embed = discord.Embed(
            title=f'Added to Queue: {html.unescape(selected_video['snippet']['title'])}',
            description=f'Queued by {self.ctx.user.display_name}\n[Watch Video]({video_url})',
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=selected_video['snippet']['thumbnails']['default']['url'])
        embed.set_footer(text=f'Uploaded by {html.unescape(selected_video['snippet']['channelTitle'])}')

        await interaction.message.edit(embed=embed, view=None)

        from music_bot.utils import currently_playing
        from music_bot.music.playback import play_next
        if not currently_playing(ctx=self.ctx):
            await play_next(self.ctx)
