import requests
import config

# ══════════════════════════════════════════════════════════════
#  ОТПРАВКА СООБЩЕНИЙ В TELEGRAM
# ══════════════════════════════════════════════════════════════

def send_message(chat_id: str, text: str, reply_markup: dict = None) -> dict:
    """Отправляет сообщение в канал или чат."""
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    r = requests.post(
        f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage",
        json=payload,
        timeout=15,
    )
    return r.json()


def edit_message(chat_id: str, message_id: int, text: str, reply_markup: dict = None) -> dict:
    """Редактирует существующее сообщение (для preview)."""
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "HTML",
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    r = requests.post(
        f"https://api.telegram.org/bot{config.BOT_TOKEN}/editMessageText",
        json=payload,
        timeout=15,
    )
    return r.json()


def answer_callback(callback_query_id: str, text: str = ""):
    """Отвечает на нажатие кнопки (убирает часики)."""
    requests.post(
        f"https://api.telegram.org/bot{config.BOT_TOKEN}/answerCallbackQuery",
        json={"callback_query_id": callback_query_id, "text": text},
        timeout=10,
    )


def delete_message(chat_id: str, message_id: int):
    requests.post(
        f"https://api.telegram.org/bot{config.BOT_TOKEN}/deleteMessage",
        json={"chat_id": chat_id, "message_id": message_id},
        timeout=10,
    )
