import os

# ══════════════════════════════════════════════════════════════
#  КОНФИГ — все настройки через переменные окружения / .env
# ══════════════════════════════════════════════════════════════

# Токен управляющего бота (от @BotFather)
BOT_TOKEN = os.environ["BOT_TOKEN"]

# Твой Telegram user_id — бот слушает только тебя
# Узнать: напиши @userinfobot в Telegram
ADMIN_ID = int(os.environ["ADMIN_ID"])

# Anthropic API
ANTHROPIC_KEY = os.environ["ANTHROPIC_API_KEY"]

# ── Канал 1: Новости ──────────────────────────────────────────
NEWS_CHANNEL_ID    = os.environ["NEWS_CHANNEL_ID"]     # @channel1 или -100xxx
NEWS_CHANNEL_NAME  = os.environ.get("NEWS_CHANNEL_NAME", "📰 Новости")
NEWS_NICHE         = os.environ.get("NEWS_NICHE", "tech")  # tech|ai|crypto|science|business
NEWS_LANGUAGE      = os.environ.get("NEWS_LANGUAGE", "russian")

# ── Канал 2: AI-Постер ────────────────────────────────────────
POST_CHANNEL_ID    = os.environ["POST_CHANNEL_ID"]
POST_CHANNEL_NAME  = os.environ.get("POST_CHANNEL_NAME", "🤖 AI-Постер")
POST_TOPIC         = os.environ.get("POST_TOPIC", "интересные факты о технологиях")
POST_LANGUAGE      = os.environ.get("POST_LANGUAGE", "russian")
# Время автопостинга (UTC): 06:00, 11:00, 16:00 = 09, 14, 19 МСК
POST_SCHEDULE      = [6, 11, 16]

# ── Канал 3: Саморазвитие ─────────────────────────────────────
SELFDEV_CHANNEL_ID   = os.environ["SELFDEV_CHANNEL_ID"]
SELFDEV_CHANNEL_NAME = os.environ.get("SELFDEV_CHANNEL_NAME", "🧠 Саморазвитие")
SELFDEV_LANGUAGE     = os.environ.get("SELFDEV_LANGUAGE", "russian")
# Время автопостинга (UTC): 05:00, 10:00, 17:00 = 08, 13, 20 МСК
SELFDEV_SCHEDULE     = [5, 10, 17]

# ── RSS-ленты по нишам ────────────────────────────────────────
RSS_FEEDS = {
    "tech": [
        "https://feeds.feedburner.com/TechCrunch",
        "https://www.wired.com/feed/rss",
        "https://hnrss.org/frontpage",
    ],
    "ai": [
        "https://hnrss.org/frontpage?q=AI+LLM+GPT",
        "https://venturebeat.com/category/ai/feed/",
        "https://www.technologyreview.com/feed/",
    ],
    "crypto": [
        "https://cointelegraph.com/rss",
        "https://decrypt.co/feed",
    ],
    "science": [
        "https://www.sciencedaily.com/rss/top.xml",
        "https://www.newscientist.com/feed/home/",
    ],
    "business": [
        "https://feeds.reuters.com/reuters/businessNews",
        "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
    ],
}

# Темы для канала саморазвития
SELFDEV_TOPICS = [
    "управление временем и продуктивность",
    "психология мышления и когнитивные искажения",
    "привычки: как формировать и ломать",
    "эмоциональный интеллект и осознанность",
    "принятие решений под давлением",
    "нейронаука обучения и памяти",
    "техники борьбы с прокрастинацией",
    "финансовое мышление",
    "коммуникация и влияние",
    "стресс: физиология и управление",
    "целеполагание и долгосрочное мышление",
    "самодисциплина и сила воли",
    "сон и восстановление",
    "как расти через провалы и неудачи",
]

POST_FORMATS_RU = [
    "интересный факт с неожиданным поворотом",
    "мини-история с моралью",
    "топ-3 малоизвестных факта",
    "развенчание популярного мифа",
    "провокационный тезис для обсуждения",
    "разбор явления простым языком",
]

POST_FORMATS_EN = [
    "surprising fact with an unexpected twist",
    "mini-story with a moral",
    "top-3 little-known facts",
    "debunking a popular myth",
    "provocative thesis to spark discussion",
    "explaining a phenomenon in plain language",
]

SELFDEV_FORMATS_RU = [
    "практический совет с конкретными шагами",
    "разбор научного исследования простым языком",
    "история + вывод + как применить",
    "развенчание мифа о саморазвитии",
    "упражнение которое можно сделать прямо сейчас",
    "сравнение двух подходов — какой работает лучше",
]

SELFDEV_FORMATS_EN = [
    "practical tip with concrete action steps",
    "breaking down a study in plain language",
    "story + lesson + how to apply it",
    "debunking a self-improvement myth",
    "an exercise you can do right now",
    "comparing two approaches — which actually works",
]
