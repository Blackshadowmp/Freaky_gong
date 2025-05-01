from music_bot.core import bot
import signal
from music_bot.events import handle_sigint
from config.settings import DISCORD_API_KEY

import music_bot.music
# Handle Ctrl+C gracefully
signal.signal(signal.SIGINT, lambda *_: handle_sigint())

if __name__ == '__main__':
    try:
        bot.run(DISCORD_API_KEY)
    except KeyboardInterrupt:
        print('KeyboardInterrupt received. Shutting down...')
