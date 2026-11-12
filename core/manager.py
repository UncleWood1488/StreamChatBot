import logging
from typing import List
from platforms.base import BasePlatformAdapter

logger = logging.getLogger(__name__)

class PlatformManager:
    """Управляет всеми подключенными адаптерами."""

    def __init__(self):
        self._adapters: List[BasePlatformAdapter] = []

    def register(self, adapter: BasePlatformAdapter):
        self._adapters.append(adapter)
        logger.info("Подключена платформа: %s", adapter.name)

    async def update_title(self, title: str) -> dict[str, bool]:
        results = {}
        for adapter in self._adapters:
            try:
                success = await adapter.update_title(title)
                results[adapter.name] = success
                if success:
                    logger.info("[%s] Название обновлено на: %s", adapter.name, title)
                else:
                    logger.warning("[%s] Не удалось обновить название.", adapter.name)
            except Exception as e:
                logger.exception("[%s] Ошибка при обновлении названия: %s", adapter.name, e)
                results[adapter.name] = False
        return results

    async def update_category(self, category_name: str) -> dict[str, bool]:
        results = {}
        for adapter in self._adapters:
            try:
                success = await adapter.update_category(category_name)
                results[adapter.name] = success
                if success:
                    logger.info("[%s] Категория обновлена на: %s", adapter.name, category_name)
                else:
                    logger.warning("[%s] Не удалось обновить категорию.", adapter.name)
            except Exception as e:
                logger.exception("[%s] Ошибка при обновлении категории: %s", adapter.name, e)
                results[adapter.name] = False
        return results

    async def close(self):
        """Закрывает ресурсы адаптеров, если нужно."""
        for adapter in self._adapters:
            if hasattr(adapter, "close"):
                try:
                    await adapter.close()
                except Exception:
                    logger.exception("[%s] Ошибка при закрытии.", adapter.name)