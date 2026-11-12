from abc import ABC, abstractmethod

class BasePlatformAdapter(ABC):
    """Базовый интерфейс для всех платформ."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Название платформы (для логов)."""
        ...

    @abstractmethod
    async def update_title(self, title: str) -> bool:
        """Обновляет название стрима. Возвращает True при успехе."""
        ...

    @abstractmethod
    async def update_category(self, category_name: str) -> bool:
        """Обновляет категорию (игру). Возвращает True при успехе."""
        ...