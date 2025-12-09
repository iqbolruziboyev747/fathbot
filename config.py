# ============================================
# FATH UNIFIED BOT - CONFIGURATION
# ============================================

# 🤖 BOT TOKEN (Bot 1 dan olingan)
BOT_TOKEN = "8161852003:AAFwAP8fLiAsaMJyQQJj62dKPwDCm_QgfVQ"

# 🧠 GEMINI API KEY
GEMINI_API_KEY = "AIzaSyD_SUcW-rpfT2wycP4sKcu7TQ-xqbN3PIY"

# 👑 ADMIN IDs (sizning Telegram ID)
ADMINS = [6418310545]
ADMIN_USERNAME = "@TraderMql"

# 💳 PAYME SOZLAMALARI
PAYME_TOKEN = "387026696:LIVE:67dfe987a30a894dfc5b06e6"
PAYME_CASSETTE_ID = "67dfe987a30a894dfc5b06e6"
PAYME_CASH_KEY = "7277b092acc00e445efbca012f67f0e9d755e7f936291681bfd90d36e35ec00f84f740bf0aa278d79c9adbc552437987b450b40450939bd7e9ba8b9bae25e238"

# 📢 KANAL ID (agar kerak bo'lsa)
CHANNEL_ID = -1002934293554

# 🗄️ DATABASE PATHS (Legacy SQLite - Firestore ga o'tkazilganda ishlatilmaydi)
TRADING_DB_PATH = "database/trading_bot.db"
LICENSE_DB_PATH = "database/licenses.db"
REFERRAL_DB_PATH = "database/referrals.db"

# 🔥 FIREBASE FIRESTORE SOZLAMALARI
# Firebase credentials JSON fayl yo'li (serviceAccountKey.json)
FIREBASE_CREDENTIALS_PATH = "firebase_credentials.json"

# Firestore Collections nomlari
FIRESTORE_COLLECTIONS = {
    "users": "users",
    "analyses": "analyses",
    "economic_data": "economic_data",
    "insider_news": "insider_news",
    "licenses": "licenses",
    "pricing_plans": "pricing_plans",
    "referrals": "referrals",
    "referral_codes": "referral_codes"
}

# Firestore ishlatish (True bo'lsa Firestore, False bo'lsa SQLite)
USE_FIRESTORE = True

# 📁 FILE PATHS
STRATEGIES_FILE = "strategies.json"
INDICATORS_FILE = "indicators.json"
ANALYSES_DIR = "analyses"
PRO_ANALYSES_DIR = "pro_analyses"

# 🔒 BEPUL SO'ROVLAR LIMITI (VIP bo'lmagan userlar uchun)
FREE_REQUEST_LIMIT = 3

# 📊 DEFAULT PRICING PLANS
DEFAULT_PLANS = [
    {
        "plan_code": "trial",
        "name": "7 kunlik (TRIAL)",
        "days": 7,
        "price": 0,
        "description": "Admin beradi - BEPUL"
    },
    {
        "plan_code": "1m",
        "name": "1 oylik",
        "days": 30,
        "price": 2_500_000,
        "description": "30 kun VIP"
    },
    {
        "plan_code": "3m",
        "name": "3 oylik",
        "days": 90,
        "price": 6_500_000,
        "description": "90 kun VIP"
    },
    {
        "plan_code": "6m",
        "name": "6 oylik",
        "days": 180,
        "price": 12_000_000,
        "description": "180 kun VIP"
    },
    {
        "plan_code": "1y",
        "name": "1 yillik",
        "days": 365,
        "price": 20_000_000,
        "description": "365 kun VIP"
    },
    {
        "plan_code": "3y",
        "name": "3 yillik",
        "days": 1095,
        "price": 50_000_000,
        "description": "1095 kun VIP"
    }
]

# 🌐 API URLs
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# 📝 LOGGING
import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)