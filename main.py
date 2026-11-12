import asyncio
import logging
from kickpython import KickAPI
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

PREFIX = "!"

async def main():
    api = KickAPI(
        client_id=Config.KICK_CLIENT_ID,
        client_secret=Config.KICK_CLIENT_SECRET,
        redirect_uri="http://127.0.0.1:3000/callback",
        db_path="kick_tokens.db",
    )

    # --- ШАГ 1: Авторизация ---
    auth_data = api.get_auth_url([
        "user:read",
        "channel:read",
        "channel:write",
        "chat:write",
    ])
    print("Откройте ссылку для авторизации:")
    print(auth_data["auth_url"])
    print("\nПосле редиректа скопируйте ТОЛЬКО значение параметра code из URL.")
    print("Пример: если URL .../callback?code=ABC123&state=xyz, вставьте ABC123")
    code = input("Вставьте code: ").strip()
    
    # Проверяем, что пользователь не вставил весь URL
    if "http" in code or "&" in code:
        print("Похоже, вы вставили не код, а часть URL. Попробуйте снова, скопировав только значение после 'code='.")
        return

    try:
        await api.exchange_code(code, auth_data["code_verifier"])
        await api.start_token_refresh()
        print("✅ Авторизация успешна, токены сохранены.")
    except Exception as e:
        print(f"❌ Ошибка авторизации: {e}")
        return

    # --- ШАГ 2: Получаем информацию о канале, чтобы узнать правильный ID/username ---
    # Это поможет избежать ошибки "Could not find chatroom ID"
    try:
        channels = await api.get_channels()
        # Предполагаем, что первый канал — ваш. Если каналов несколько, нужно выбрать нужный.
        # Выведем информацию для проверки.
        print("\nВаши каналы:")
        for ch in channels:
            print(f"  - username: {ch.get('slug')}, id: {ch.get('id')}, chatroom_id: {ch.get('chatroom', {}).get('id')}")
        
        # Если в .env всё ещё заглушка, попробуем взять первый канал.
        # В идеале нужно вручную указать правильный username или ID в .env.
        if Config.KICK_BROADCASTER_ID == "id_вашего_канала" and channels:
            # Временно используем slug первого канала для демонстрации
            # В реальности лучше явно указать свой ник в .env
            chat_identifier = channels[0].get("slug")
            channel_id_for_api = channels[0].get("id")  # числовой ID для update_channel/post_chat
            print(f"\n⚠️ В .env указан placeholder. Временно использую канал: {chat_identifier}")
        else:
            chat_identifier = Config.KICK_BROADCASTER_ID
            # Для update_channel и post_chat всё равно нужен числовой ID,
            # поэтому попробуем найти его среди полученных каналов.
            channel_id_for_api = None
            for ch in channels:
                if ch.get("slug") == chat_identifier or str(ch.get("id")) == str(chat_identifier):
                    channel_id_for_api = ch.get("id")
                    break
            if not channel_id_for_api:
                print(f"❌ Не удалось найти числовой ID для '{chat_identifier}' среди ваших каналов.")
                print("Укажите в .env правильный username (slug) или числовой ID.")
                return

        print(f"\nИспользую для чата: {chat_identifier}, для API: {channel_id_for_api}")

    except Exception as e:
        print(f"❌ Не удалось получить информацию о каналах: {e}")
        return

    # --- ШАГ 3: Обработчик сообщений ---
    async def on_chat_message(message: dict):
        text = message.get("content", "").strip()
        if not text.startswith(PREFIX):
            return

        username = message.get("sender_username", "")
        badges = message.get("badges", [])

        # Проверка прав: замените "ВАШ_НИК" на ваш реальный ник
        is_broadcaster = username.lower() == "ВАШ_НИК".lower()
        is_moderator = any(
            b.get("type") == "moderator" for b in badges if isinstance(b, dict)
        )
        if not (is_broadcaster or is_moderator):
            return

        command_line = text[len(PREFIX):].strip()
        parts = command_line.split(maxsplit=1)
        cmd = parts[0].lower() if parts else ""
        arg = parts[1] if len(parts) > 1 else ""

        if cmd == "title" and arg:
            await api.update_channel(
                channel_id=channel_id_for_api,
                stream_title=arg,
            )
            await api.post_chat(
                channel_id=channel_id_for_api,
                content=f"✅ Название обновлено: {arg}",
            )
            logger.info("Название изменено на: %s", arg)

        elif cmd == "game" and arg:
            categories = await api.get_categories(query=arg)
            if not categories:
                await api.post_chat(
                    channel_id=channel_id_for_api,
                    content=f'⚠️ Категория "{arg}" не найдена.',
                )
                return
            category_id = categories[0]["id"]
            await api.update_channel(
                channel_id=channel_id_for_api,
                category_id=category_id,
            )
            await api.post_chat(
                channel_id=channel_id_for_api,
                content=f"✅ Категория обновлена: {categories[0]['name']}",
            )
            logger.info("Категория изменена на: %s", arg)

        else:
            await api.post_chat(
                channel_id=channel_id_for_api,
                content=f"Неизвестная команда. Используйте: {PREFIX}title <...> или {PREFIX}game <...>",
            )

    # --- ШАГ 4: Подключение к чату и запуск ---
    api.add_message_handler(on_chat_message)
    await api.connect_to_chatroom(chat_identifier)
    logger.info("Бот слушает чат Kick. Команды: %stitle, %sgame", PREFIX, PREFIX)
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())