import threading
import time
from datetime import datetime, timezone
import config
import generators
import publisher

# ══════════════════════════════════════════════════════════════
#  ПЛАНИРОВЩИК АВТОПОСТИНГА
#  Работает в отдельном потоке, проверяет время каждую минуту
# ══════════════════════════════════════════════════════════════

_posted_hours: set = set()  # "channel_hour" — чтобы не дублировать


def _should_post(channel_key: str, schedule: list) -> bool:
    now = datetime.now(timezone.utc)
    hour = now.hour
    minute = now.minute
    key = f"{channel_key}_{now.date()}_{hour}"

    if minute > 5:  # публикуем только в первые 5 минут часа
        return False
    if hour not in schedule:
        return False
    if key in _posted_hours:
        return False
    return True


def _mark_posted(channel_key: str, hour: int):
    from datetime import date
    key = f"{channel_key}_{date.today()}_{hour}"
    _posted_hours.add(key)


def scheduler_loop():
    """Бесконечный цикл планировщика."""
    print("[Scheduler] Started")
    while True:
        now_hour = datetime.now(timezone.utc).hour

        # ── AI-Постер ──────────────────────────────────────────
        if _should_post("post", config.POST_SCHEDULE):
            print(f"[Scheduler] Auto-posting to {config.POST_CHANNEL_NAME}")
            try:
                post = generators.generate_ai_post()
                publisher.send_message(config.POST_CHANNEL_ID, post)
                _mark_posted("post", now_hour)
                print("[Scheduler] AI-post published OK")
            except Exception as e:
                print(f"[Scheduler] AI-post error: {e}")

        # ── Саморазвитие ───────────────────────────────────────
        if _should_post("selfdev", config.SELFDEV_SCHEDULE):
            print(f"[Scheduler] Auto-posting to {config.SELFDEV_CHANNEL_NAME}")
            try:
                post = generators.generate_selfdev_post()
                publisher.send_message(config.SELFDEV_CHANNEL_ID, post)
                _mark_posted("selfdev", now_hour)
                print("[Scheduler] Selfdev post published OK")
            except Exception as e:
                print(f"[Scheduler] Selfdev error: {e}")

        time.sleep(60)  # проверяем каждую минуту


def start():
    t = threading.Thread(target=scheduler_loop, daemon=True)
    t.start()
