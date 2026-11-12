from kickpy import KickClient
from platforms.base import BasePlatformAdapter
from config import Config

class KickAdapter(BasePlatformAdapter):
    def __init__(self):
        self.client = KickClient(
            Config.KICK_CLIENT_ID,
            Config.KICK_CLIENT_SECRET,
        )
        # Добавлены обязательные expires_in и scope
        self.client.set_user_token(
            access_token=Config.KICK_ACCESS_TOKEN,
            refresh_token=Config.KICK_REFRESH_TOKEN,
            expires_in=Config.KICK_TOKEN_EXPIRES_IN,  # <- новое
            scope=Config.KICK_TOKEN_SCOPE,            # <- новое
        )
        self.broadcaster_id = Config.KICK_BROADCASTER_ID

    @property
    def name(self) -> str:
        return "Kick"

    async def update_title(self, title: str) -> bool:
        await self.client.update_channel(stream_title=title)
        return True

    async def update_category(self, category_name: str) -> bool:
        categories = await self.client.fetch_categories(query=category_name)
        if not categories:
            raise ValueError(f'Категория "{category_name}" не найдена на Kick.')
        category_id = categories[0].id
        await self.client.update_channel(category_id=category_id)
        return True

    async def close(self):
        await self.client.close()