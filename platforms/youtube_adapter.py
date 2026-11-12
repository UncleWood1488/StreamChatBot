import asyncio
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from platforms.base import BasePlatformAdapter
from config import Config

class YouTubeAdapter(BasePlatformAdapter):
    def __init__(self):
        self.video_id = Config.YOUTUBE_VIDEO_ID
        self.youtube = None
        self._init_service()

    def _init_service(self):
        creds = None
        # Загрузка сохранённых учётных данных
        try:
            creds = Credentials.from_authorized_user_file(
                Config.YOUTUBE_CREDENTIALS_FILE,
                scopes=["https://www.googleapis.com/auth/youtube"],
            )
        except FileNotFoundError:
            raise RuntimeError(
                f"Файл учётных данных YouTube не найден: {Config.YOUTUBE_CREDENTIALS_FILE}. "
                "Сначала выполните OAuth-авторизацию."
            )

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                raise RuntimeError("Учётные данные YouTube недействительны. Требуется повторная авторизация.")

        self.youtube = build("youtube", "v3", credentials=creds)

    @property
    def name(self) -> str:
        return "YouTube"

    async def update_title(self, title: str) -> bool:
        return await asyncio.to_thread(self._sync_update_title, title)

    async def update_category(self, category_name: str) -> bool:
        return await asyncio.to_thread(self._sync_update_category, category_name)

    def _sync_update_title(self, title: str) -> bool:
        # Сначала получаем текущие данные видео, чтобы сохранить categoryId
        current = self._get_video_snippet()
        body = {
            "id": self.video_id,
            "snippet": {
                "title": title[:100],  # Лимит YouTube
                "categoryId": current["categoryId"],  # Обязательное поле
                "description": current.get("description", ""),  # Сохраняем описание
            },
        }
        self.youtube.videos().update(part="snippet", body=body).execute()
        return True

    def _sync_update_category(self, category_name: str) -> bool:
        category_id = self._find_category_id(category_name)
        if not category_id:
            raise ValueError(f'Категория "{category_name}" не найдена на YouTube.')

        current = self._get_video_snippet()
        body = {
            "id": self.video_id,
            "snippet": {
                "title": current["title"],  # Сохраняем текущее название
                "categoryId": category_id,
                "description": current.get("description", ""),
            },
        }
        self.youtube.videos().update(part="snippet", body=body).execute()
        return True

    def _get_video_snippet(self) -> dict:
        response = self.youtube.videos().list(
            part="snippet",
            id=self.video_id,
        ).execute()
        if not response["items"]:
            raise RuntimeError(f"Видео с ID {self.video_id} не найдено.")
        return response["items"][0]["snippet"]

    def _find_category_id(self, name: str) -> str | None:
        # Поиск по названию категории (регион можно настроить)
        response = self.youtube.videoCategories().list(
            part="snippet",
            regionCode="RU",
        ).execute()
        for item in response.get("items", []):
            if item["snippet"]["title"].lower() == name.lower():
                return item["id"]
        return None