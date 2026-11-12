import logging
from platforms.base import BasePlatformAdapter
from config import Config

logger = logging.getLogger(__name__)

class VKAdapter(BasePlatformAdapter):
    """
    Адаптер для VK Video Live.

    ВНИМАНИЕ: На данный момент (2026) не существует официальной и стабильной
    Python-библиотеки для управления метаданными трансляции на VK Video Live.
    У VK есть открытый DevAPI, но он ориентирован на интерактивные элементы
    (мини-игры, викторины), а не на смену названия/категории.

    Для реальной работы необходимо:
    1. Изучить запросы, которые делает расширение для Streamer.bot
       (https://github.com/ivnjey-dev/vkvideolive-streamerbot-extension).
    2. Воспроизвести эти запросы через aiohttp, используя VK_ACCESS_TOKEN.
    3. Либо использовать автоматизацию браузера (Playwright/Selenium),
       что менее надёжно.

    Пока этот адаптер можно оставить выключенным или использовать как заготовку.
    """

    def __init__(self):
        self.access_token = Config.VK_ACCESS_TOKEN
        self.channel_id = Config.VK_CHANNEL_ID
        if not self.access_token or not self.channel_id:
            logger.warning("VK Video Live: не заданы VK_ACCESS_TOKEN или VK_CHANNEL_ID.")
        else:
            logger.warning("VK Video Live: адаптер находится в режиме заглушки. "
                           "Реальная интеграция не реализована.")

    @property
    def name(self) -> str:
        return "VK Video Live"

    async def update_title(self, title: str) -> bool:
        logger.info("[VK] Запрос на смену названия: %s (заглушка)", title)
        return False

    async def update_category(self, category_name: str) -> bool:
        logger.info("[VK] Запрос на смену категории: %s (заглушка)", category_name)
        return False