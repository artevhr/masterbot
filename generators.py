import requests
import random
import re
import hashlib
import time
import xml.etree.ElementTree as ET
from datetime import datetime
import config

# ══════════════════════════════════════════════════════════════
#  ГЕНЕРАТОРЫ КОНТЕНТА
# ══════════════════════════════════════════════════════════════

def _claude(prompt: str, max_tokens: int = 1200, retries: int = 3) -> str:
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.0-flash-lite:generateContent?key={config.GEMINI_KEY}"
    )
    for attempt in range(retries):
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"maxOutputTokens": max_tokens},
            },
            timeout=40,
        )
        if response.status_code == 429:
            wait = 60 * (attempt + 1)
            print(f"Gemini rate limit, жду {wait}с...")
            time.sleep(wait)
            continue
        response.raise_for_status()
        return response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    raise Exception("Gemini недоступен после нескольких попыток")

def _pick_lang(lang: str) -> str:
    if lang == "both":
        return random.choice(["russian", "english"])
    return lang if lang in ("russian", "english") else "russian"


# ── Генератор: AI-Постер ──────────────────────────────────────

def generate_ai_post(lang: str = None) -> str:
    lang = _pick_lang(lang or config.POST_LANGUAGE)
    today = datetime.now().strftime("%d.%m.%Y")

    if lang == "russian":
        fmt = random.choice(config.POST_FORMATS_RU)
        prompt = f"""Ты — автор популярного Telegram-канала. Тема: {config.POST_TOPIC}.
Напиши пост в формате: {fmt}.
- Язык: русский, живой и разговорный
- Длина: 150–350 слов
- Начни с крючка (первые 2 строки — цепляющие)
- 2–4 эмодзи органично в тексте
- В конце: вопрос или призыв к реакции
- 3–5 хэштегов в конце
- Дата: {today}
- Без заголовка — сразу текст
Только текст поста."""
    else:
        fmt = random.choice(config.POST_FORMATS_EN)
        prompt = f"""You are a popular Telegram channel author. Topic: {config.POST_TOPIC}.
Write a post in this format: {fmt}.
- Language: English, lively and conversational
- Length: 150–350 words
- Start with a hook (first 2 lines must grab attention)
- 2–4 emojis naturally in the text
- End with a question or call to react
- 3–5 hashtags at the end
- Date: {today}
- No headline — start right away
Output only the post text."""

    return _claude(prompt)


# ── Генератор: Саморазвитие ───────────────────────────────────

def generate_selfdev_post(lang: str = None) -> str:
    lang = _pick_lang(lang or config.SELFDEV_LANGUAGE)
    topic = random.choice(config.SELFDEV_TOPICS)
    hour = datetime.utcnow().hour

    if hour < 10:
        time_ctx_ru = "утреннее — заряди энергией и мотивацией"
        time_ctx_en = "morning — energize and motivate"
    elif hour < 15:
        time_ctx_ru = "дневное — дай практический инсайт прямо сейчас"
        time_ctx_en = "midday — give a practical insight for right now"
    else:
        time_ctx_ru = "вечернее — подтолкни к рефлексии и планированию"
        time_ctx_en = "evening — inspire reflection and planning"

    if lang == "russian":
        fmt = random.choice(config.SELFDEV_FORMATS_RU)
        prompt = f"""Ты — автор Telegram-канала о саморазвитии (50 000+ подписчиков).
Напиши {time_ctx_ru} пост. Тема: {topic}. Формат: {fmt}.
- Язык: живой русский
- Длина: 200–400 слов
- Сильный крючок в начале (не банальность)
- Конкретика: цифры, исследования, примеры
- 2–4 эмодзи органично
- В конце: вопрос или мини-задание на сегодня
- 4–5 хэштегов
- Без заголовка
Только текст поста."""
    else:
        fmt = random.choice(config.SELFDEV_FORMATS_EN)
        prompt = f"""You are the author of a self-development Telegram channel (50,000+ subscribers).
Write a {time_ctx_en} post. Topic: {topic}. Format: {fmt}.
- Language: lively English
- Length: 200–400 words
- Strong hook (no clichés)
- Be specific: numbers, studies, examples
- 2–4 emojis naturally placed
- End with a question or mini-task for today
- 4–5 hashtags
- No headline
Output only the post text."""

    return _claude(prompt, max_tokens=1400)


# ── Генератор: Новости ────────────────────────────────────────

POSTED_HASHES_FILE = "posted_hashes.txt"

def _get_posted_hashes() -> set:
    try:
        with open(POSTED_HASHES_FILE, "r") as f:
            return set(f.read().splitlines())
    except FileNotFoundError:
        return set()

def _save_hash(h: str):
    with open(POSTED_HASHES_FILE, "a") as f:
        f.write(h + "\n")

def _fetch_rss(url: str, limit: int = 15) -> list:
    try:
        r = requests.get(url, timeout=15,
                         headers={"User-Agent": "Mozilla/5.0 (compatible; NewsBot/1.0)"})
        r.raise_for_status()
        root = ET.fromstring(r.content)
        items = []
        for item in root.findall(".//item")[:limit]:
            title = item.findtext("title", "").strip()
            desc  = re.sub(r"<[^>]+>", "", item.findtext("description", ""))[:500].strip()
            if title:
                items.append({"title": title, "desc": desc})
        return items
    except Exception as e:
        print(f"RSS error {url}: {e}")
        return []

def fetch_and_generate_news(lang: str = None) -> str | None:
    """Берёт свежую новость из RSS и адаптирует через Claude. Возвращает None если нет новинок."""
    lang = _pick_lang(lang or config.NEWS_LANGUAGE)
    feeds = config.RSS_FEEDS.get(config.NEWS_NICHE, config.RSS_FEEDS["tech"])
    posted = _get_posted_hashes()

    all_items = []
    for url in feeds:
        all_items.extend(_fetch_rss(url))
    random.shuffle(all_items)

    for item in all_items:
        h = hashlib.md5(item["title"].encode()).hexdigest()
        if h in posted:
            continue

        if lang == "russian":
            prompt = f"""Ты — редактор Telegram-канала. Перепиши новость в живой пост на русском.
ЗАГОЛОВОК: {item['title']}
СОДЕРЖАНИЕ: {item['desc']}
- Язык: живой русский, без канцелярита
- Длина: 120–250 слов
- Начни с цепляющей фразы (не с заголовка)
- Объясни почему это важно
- 2–3 эмодзи органично
- В конце: вывод или вопрос
- 3–4 хэштега
- Без "по данным...", "как сообщает..." — пиши от себя
Только текст поста."""
        else:
            prompt = f"""You are a Telegram channel editor. Rewrite this news into an engaging English post.
HEADLINE: {item['title']}
CONTENT: {item['desc']}
- Language: lively English, conversational
- Length: 120–250 words
- Start with a hook (not the headline)
- Explain why it matters
- 2–3 emojis naturally placed
- End with takeaway or question
- 3–4 hashtags
- No "according to..." — write in your own voice
Output only the post text."""

        try:
            post = _claude(prompt, max_tokens=1024)
            _save_hash(h)
            return post
        except Exception as e:
            print(f"Claude error: {e}")
            return None

    return None  # нет новых новостей
