import asyncio
import logging
from kickpython import KickAPI
from core.manager import PlatformManager
from platforms.kick_adapter import KickAdapter
from platforms.vk_adapter import VKAdapter
from config import Config

logger = logging.getLogger(__name__)

# Настройки
PREFIX = "!"

async def main():
    # 1. Инициализация API Kick с вашими client_id/secret
    api = KickAPI(
        client_id=Config.KICK_CLIENT_ID,
        client_secret=Config.KICK_CLIENT_SECRET,
        redirect_uri="http://127.0.0.1:3000/callback",  # Должен совпадать с настройками приложения
        db_path="kick_tokens.db"  # Файл для хранения токенов
    )

    # 2. OAuth-авторизация (при первом запуске откроется браузер)
    # Если токены уже сохранены в kick_tokens.db, повторно авторизация не потребуется
    scopes = ["user:read", "channel:read", "channel:write", "chat:write"]
    auth_data = api.get_auth_url(scopes)
    print(f"Откройте эту ссылку для авторизации:\n{auth_data['auth_url']}")
    code = input("Вставьте код авторизации (code) из URL: ").strip()
    await api.exchange_code(code, auth_data["code_verifier"])
    await api.start_token_refresh()  # Автоматическое обновление токена

    # 3. Настройка менеджера платформ (ваши существующие адаптеры)
    manager = PlatformManager()
    manager.register(KickAdapter())  # Обновление канала на Kick
    manager.register(VKAdapter())
    # manager.register(YouTubeAdapter())

    # 4. Обработчик входящих сообщений из чата
    async def on_chat_message(message: dict):
        """Вызывается на каждое сообщение в чате."""
        text = message.get("content", "").strip()
        username = message.get("sender_username", "")

        # Игнорируем сообщения, не начинающиеся с префикса
        if not text.startswith(PREFIX):
            return

        # Убираем префикс и разбиваем на команду и аргументы
        command_line = text[len(PREFIX):].strip()
        if not command_line:
            return

        parts = command_line.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        # Проверка прав: разрешаем только вам или модераторам
        # (нужно знать ваш user_id; можно получить через api.get_channels())
        # Для простоты проверим по имени канала — замените на ваш ник
        if username != Config.KICK_BROADCASTER_ID:  # ← ЗАМЕНИТЕ на ваш ник или ID
            # В реальном боте лучше проверять badge модератора
            return

        # Обработка команд
        if cmd == "title" and arg:
            results = await manager.update_title(arg)
            response = f"Результат смены названия: {results}"
            await api.post_chat(channel_id=Config.KICK_BROADCASTER_ID, content=response)
            logger.info("Обновление названия: %s", results)

        elif cmd == "game" and arg:
            results = await manager.update_category(arg)
            response = f"Результат смены категории: {results}"
            await api.post_chat(channel_id=Config.KICK_BROADCASTER_ID, content=response)
            logger.info("Обновление категории: %s", results)

        else:
            await api.post_chat(
                channel_id=Config.KICK_BROADCASTER_ID,
                content=f"Неизвестная команда. Используйте: {PREFIX}title <...> или {PREFIX}game <...>"
            )

    # 5. Подключаемся к чату и регистрируем обработчик
    api.add_message_handler(on_chat_message)
    await api.connect_to_chatroom(Config.KICK_BROADCASTER_ID)  # Укажите ник или ID канала

    logger.info("Бот слушает чат. Команды: %stitle, %sgame", PREFIX, PREFIX)
    # Держим бота запущенным
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())