# ============================================
# FATH UNIFIED BOT - CLOUD RUN VERSION
# Google Cloud Run uchun moslashtirilgan versiya
# ============================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
import logging
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import config

# Firebase credentials ni environment variable dan olish
if os.getenv('FIREBASE_CREDENTIALS'):
    import json
    creds_json = os.getenv('FIREBASE_CREDENTIALS')
    creds_path = 'firebase_credentials.json'
    with open(creds_path, 'w') as f:
        f.write(creds_json)
    config.FIREBASE_CREDENTIALS_PATH = creds_path

# Handlers
from handlers.start_handler import register_start_handlers
from handlers.trading_handler import register_trading_handlers
from handlers.license_handler import register_license_handlers
from handlers.admin_handler import register_admin_handlers
from handlers.premium_handler import register_premium_handlers

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Bot va Dispatcher
bot = Bot(token=config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Barcha handlerlarni ro'yxatdan o'tkazish
register_start_handlers(dp)
register_admin_handlers(dp)
register_trading_handlers(dp)
register_license_handlers(dp)
register_premium_handlers(dp)


async def on_startup(dp):
    """Bot ishga tushganda"""
    print("\n" + "="*50)
    print("🤖 FATH UNIFIED BOT ISHGA TUSHDI!")
    print("="*50)
    print(f"📊 Bot Token: {config.BOT_TOKEN[:20]}...")
    print(f"👑 Adminlar: {config.ADMINS}")
    
    if config.USE_FIRESTORE:
        print(f"🔥 Database: Firebase Firestore")
        # Default pricing plans ni yaratish
        try:
            from database.firestore_service import firestore_license_db
            firestore_license_db.init_default_plans()
            print("✅ Default pricing plans yaratildi")
        except Exception as e:
            print(f"⚠️ Pricing plans yaratishda xatolik: {e}")
    else:
        print(f"🗄️ Trading DB: {config.TRADING_DB_PATH}")
        print(f"🗄️ License DB: {config.LICENSE_DB_PATH}")
    
    print("="*50 + "\n")


async def on_shutdown(dp):
    """Bot to'xtaganda"""
    print("\n" + "="*50)
    print("⚠️ FATH BOT TO'XTATILDI")
    print("="*50 + "\n")
    
    await dp.storage.close()
    await dp.storage.wait_closed()


if __name__ == "__main__":
    try:
        # Papkalarni tekshirish
        os.makedirs(config.ANALYSES_DIR, exist_ok=True)
        os.makedirs(config.PRO_ANALYSES_DIR, exist_ok=True)
        
        # Botni ishga tushirish
        executor.start_polling(
            dp,
            skip_updates=True,
            on_startup=on_startup,
            on_shutdown=on_shutdown
        )
    except KeyboardInterrupt:
        print("\n⚠️ Bot to'xtatildi (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ XATOLIK: {e}")
        import traceback
        traceback.print_exc()

