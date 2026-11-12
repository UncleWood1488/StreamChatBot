import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Twitch
    TWITCH_TOKEN = os.getenv("TWITCH_TOKEN")
    TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
    TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
    TWITCH_BOT_NICK = os.getenv("TWITCH_BOT_NICK")
    TWITCH_CHANNEL = os.getenv("TWITCH_CHANNEL")
    TWITCH_BROADCASTER_ID = os.getenv("TWITCH_BROADCASTER_ID")

    # Kick
    KICK_CLIENT_ID = os.getenv("KICK_CLIENT_ID")
    KICK_CLIENT_SECRET = os.getenv("KICK_CLIENT_SECRET")
    KICK_ACCESS_TOKEN = os.getenv("KICK_ACCESS_TOKEN")
    KICK_REFRESH_TOKEN = os.getenv("KICK_REFRESH_TOKEN")
    KICK_TOKEN_EXPIRES_IN = int(os.getenv("KICK_TOKEN_EXPIRES_IN", "3600"))
    KICK_TOKEN_SCOPE = os.getenv("KICK_TOKEN_SCOPE", "channel:write")
    KICK_BROADCASTER_ID = os.getenv("KICK_BROADCASTER_ID")

    # VK Video Live
    VK_ACCESS_TOKEN = os.getenv("VK_ACCESS_TOKEN")
    VK_CHANNEL_ID = os.getenv("VK_CHANNEL_ID")

    # YouTube
    YOUTUBE_CREDENTIALS_FILE = os.getenv("YOUTUBE_CREDENTIALS_FILE", "credentials.json")
    YOUTUBE_VIDEO_ID = os.getenv("YOUTUBE_VIDEO_ID")

    # Общие настройки
    COMMAND_PREFIX = "!"