import requests
import time
import json
from datetime import datetime, timezone
import config
import generators
import publisher
import scheduler

# ══════════════════════════════════════════════════════════════
#  МАСТЕР-БОТ — управление тремя каналами из одного места
#  Поддерживает команды и inline-кнопки с preview перед постом
# ══════════════════════════════════════════════════════════════

# Хранилище preview в памяти: {message_id: {"text": ..., "channel_id": ..., "type": ...}}
_previews: dict = {}

# ── Клавиатуры ────────────────────────────────────────────────

def main_menu() -> dict:
    return {
        "inline_keyboard": [
            [
                {"text": "📰 Новость", "callback_data": "gen_news"},
                {"text": "🤖 AI-Пост",  "callback_data": "gen_post"},
                {"text": "🧠 Саморазвитие", "callback_data": "gen_selfdev"},
            ],
            [
                {"text": "📊 Статус каналов", "callback_data": "status"},
            ],
        ]
    }

def preview_keyboard(preview_id: int) -> dict:
    return {
        "inline_keyboard": [
            [
                {"text": "✅ Опубликовать", "callback_data": f"publish_{preview_id}"},
                {"text": "🔄 Перегенерировать", "callback_data": f"regen_{preview_id}"},
            ],
            [
                {"text": "❌ Отмена", "callback_data": "cancel"},
            ],
        ]
    }

# ── Обработчики ───────────────────────────────────────────────

def handle_start(chat_id: int):
    text = (
        "👋 <b>Мастер-бот управления каналами</b>\n\n"
        f"📰 Новости → <code>{config.NEWS_CHANNEL_NAME}</code>\n"
        f"🤖 AI-Постер → <code>{config.POST_CHANNEL_NAME}</code>\n"
        f"🧠 Саморазвитие → <code>{config.SELFDEV_CHANNEL_NAME}</code>\n\n"
        "AI-Постер и Саморазвитие публикуются <b>автоматически</b> 3 раза в день.\n"
        "Новости — <b>вручную</b> по кнопке когда нужно.\n\n"
        "Выбери действие:"
    )
    publisher.send_message(str(chat_id), text, main_menu())


def handle_status(chat_id: int, message_id: int = None):
    from datetime import date
    now = datetime.now(timezone.utc)

    def next_post_time(schedule):
        for h in sorted(schedule):
            if h > now.hour or (h == now.hour and now.minute < 5):
                delta = (h - now.hour) * 60 - now.minute
                return f"через ~{delta} мин"
        h = sorted(schedule)[0]
        delta = (24 - now.hour + h) * 60 - now.minute
        return f"через ~{delta} мин (завтра)"

    text = (
        "📊 <b>Статус каналов</b>\n\n"
        f"📰 <b>{config.NEWS_CHANNEL_NAME}</b>\n"
        f"   Ниша: {config.NEWS_NICHE} | Язык: {config.NEWS_LANGUAGE}\n"
        f"   Режим: ручной\n\n"
        f"🤖 <b>{config.POST_CHANNEL_NAME}</b>\n"
        f"   Тема: {config.POST_TOPIC[:40]}...\n"
        f"   Следующий пост: {next_post_time(config.POST_SCHEDULE)}\n\n"
        f"🧠 <b>{config.SELFDEV_CHANNEL_NAME}</b>\n"
        f"   Язык: {config.SELFDEV_LANGUAGE}\n"
        f"   Следующий пост: {next_post_time(config.SELFDEV_SCHEDULE)}\n\n"
        f"🕐 Сейчас: {now.strftime('%H:%M')} UTC"
    )

    if message_id:
        publisher.edit_message(str(chat_id), message_id, text, main_menu())
    else:
        publisher.send_message(str(chat_id), text, main_menu())


def handle_generate(chat_id: int, post_type: str, message_id: int = None):
    """Генерирует пост и показывает preview с кнопками."""
    loading_text = {
        "news":    "⏳ Ищу свежую новость и адаптирую...",
        "post":    "⏳ Генерирую AI-пост...",
        "selfdev": "⏳ Генерирую пост о саморазвитии...",
    }[post_type]

    channel_id = {
        "news":    config.NEWS_CHANNEL_ID,
        "post":    config.POST_CHANNEL_ID,
        "selfdev": config.SELFDEV_CHANNEL_ID,
    }[post_type]

    channel_name = {
        "news":    config.NEWS_CHANNEL_NAME,
        "post":    config.POST_CHANNEL_NAME,
        "selfdev": config.SELFDEV_CHANNEL_NAME,
    }[post_type]

    # Показываем "загружается..."
    if message_id:
        publisher.edit_message(str(chat_id), message_id, loading_text)
    else:
        msg = publisher.send_message(str(chat_id), loading_text)
        message_id = msg.get("result", {}).get("message_id")

    # Генерируем
    try:
        if post_type == "news":
            post = generators.fetch_and_generate_news()
            if post is None:
                publisher.edit_message(
                    str(chat_id), message_id,
                    "😔 Нет новых новостей. Все уже были опубликованы.\n\nПопробуй позже или смени нишу.",
                    main_menu()
                )
                return
        elif post_type == "post":
            post = generators.generate_ai_post()
        else:
            post = generators.generate_selfdev_post()
    except Exception as e:
        publisher.edit_message(
            str(chat_id), message_id,
            f"❌ Ошибка генерации: {e}\n\nПопробуй ещё раз.",
            main_menu()
        )
        return

    # Сохраняем preview
    _previews[message_id] = {
        "text": post,
        "channel_id": channel_id,
        "channel_name": channel_name,
        "type": post_type,
    }

    preview_text = (
        f"👁 <b>Preview → {channel_name}</b>\n"
        f"{'─' * 30}\n\n"
        f"{post}\n\n"
        f"{'─' * 30}\n"
        f"Опубликовать или перегенерировать?"
    )
    publisher.edit_message(str(chat_id), message_id, preview_text, preview_keyboard(message_id))


def handle_publish(chat_id: int, message_id: int, preview_id: int):
    """Публикует сохранённый preview в канал."""
    preview = _previews.get(preview_id)
    if not preview:
        publisher.edit_message(str(chat_id), message_id, "❌ Preview устарел. Начни заново.", main_menu())
        return

    result = publisher.send_message(preview["channel_id"], preview["text"])
    del _previews[preview_id]

    if result.get("ok"):
        publisher.edit_message(
            str(chat_id), message_id,
            f"✅ <b>Опубликовано в {preview['channel_name']}!</b>\n\nЧто дальше?",
            main_menu()
        )
    else:
        publisher.edit_message(
            str(chat_id), message_id,
            f"❌ Ошибка публикации: {result}\n\nПроверь что бот — администратор канала.",
            main_menu()
        )


# ── Polling ───────────────────────────────────────────────────

def process_update(update: dict):
    # Сообщения
    if "message" in update:
        msg     = update["message"]
        chat_id = msg["chat"]["id"]
        user_id = msg["from"]["id"]
        text    = msg.get("text", "")

        if user_id != config.ADMIN_ID:
            publisher.send_message(str(chat_id), "⛔ Доступ запрещён.")
            return

        if text in ("/start", "/menu"):
            handle_start(chat_id)
        elif text == "/status":
            handle_status(chat_id)
        elif text == "/news":
            handle_generate(chat_id, "news")
        elif text == "/post":
            handle_generate(chat_id, "post")
        elif text == "/selfdev":
            handle_generate(chat_id, "selfdev")
        else:
            publisher.send_message(str(chat_id), "Используй кнопки или команды:\n/news /post /selfdev /status", main_menu())

    # Нажатия кнопок
    elif "callback_query" in update:
        cq      = update["callback_query"]
        chat_id = cq["message"]["chat"]["id"]
        msg_id  = cq["message"]["message_id"]
        user_id = cq["from"]["id"]
        data    = cq["data"]

        publisher.answer_callback(cq["id"])

        if user_id != config.ADMIN_ID:
            return

        if data == "gen_news":
            handle_generate(chat_id, "news", msg_id)
        elif data == "gen_post":
            handle_generate(chat_id, "post", msg_id)
        elif data == "gen_selfdev":
            handle_generate(chat_id, "selfdev", msg_id)
        elif data == "status":
            handle_status(chat_id, msg_id)
        elif data == "cancel":
            publisher.edit_message(str(chat_id), msg_id, "Отменено. Выбери действие:", main_menu())
        elif data.startswith("publish_"):
            preview_id = int(data.split("_")[1])
            handle_publish(chat_id, msg_id, preview_id)
        elif data.startswith("regen_"):
            preview_id = int(data.split("_")[1])
            preview = _previews.get(preview_id)
            if preview:
                del _previews[preview_id]
                handle_generate(chat_id, preview["type"], msg_id)
            else:
                publisher.edit_message(str(chat_id), msg_id, "Preview устарел. Начни заново.", main_menu())


def run():
    print(f"[Bot] Starting master bot...")
    print(f"[Bot] Admin ID: {config.ADMIN_ID}")
    print(f"[Bot] Channels: {config.NEWS_CHANNEL_NAME} | {config.POST_CHANNEL_NAME} | {config.SELFDEV_CHANNEL_NAME}")

    scheduler.start()
    print("[Bot] Scheduler started")

    offset = 0
    base_url = f"https://api.telegram.org/bot{config.BOT_TOKEN}"

    while True:
        try:
            r = requests.get(
                f"{base_url}/getUpdates",
                params={"offset": offset, "timeout": 30},
                timeout=35,
            )
            data = r.json()

            for update in data.get("result", []):
                offset = update["update_id"] + 1
                try:
                    process_update(update)
                except Exception as e:
                    print(f"[Bot] Update error: {e}")

        except requests.exceptions.Timeout:
            pass
        except Exception as e:
            print(f"[Bot] Polling error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    run()
