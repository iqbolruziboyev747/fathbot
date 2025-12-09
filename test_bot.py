# ============================================
# BOT TEST SCRIPT
# Botni ishga tushirishdan oldin tekshirish
# ============================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config

print("🤖 Bot test boshlandi...\n")

# 1. Config tekshirish
print("1️⃣ Config tekshirilmoqda...")
print(f"   ✅ BOT_TOKEN: {config.BOT_TOKEN[:20]}...")
print(f"   ✅ ADMINS: {config.ADMINS}")
print(f"   ✅ USE_FIRESTORE: {config.USE_FIRESTORE}")

# 2. Firebase tekshirish
if config.USE_FIRESTORE:
    print("\n2️⃣ Firebase tekshirilmoqda...")
    if os.path.exists(config.FIREBASE_CREDENTIALS_PATH):
        print(f"   ✅ Firebase credentials: {config.FIREBASE_CREDENTIALS_PATH}")
        try:
            from database.firestore_service import get_firestore_client
            db = get_firestore_client()
            print("   ✅ Firestore client tayyor")
        except Exception as e:
            print(f"   ❌ Firestore xatosi: {e}")
            sys.exit(1)
    else:
        print(f"   ❌ Firebase credentials topilmadi: {config.FIREBASE_CREDENTIALS_PATH}")
        sys.exit(1)

# 3. Database service tekshirish
print("\n3️⃣ Database service tekshirilmoqda...")
try:
    from services.database_service import trading_db, license_db
    print("   ✅ TradingDB tayyor")
    print("   ✅ LicenseDB tayyor")
except Exception as e:
    print(f"   ❌ Database service xatosi: {e}")
    sys.exit(1)

# 4. Handlers tekshirish
print("\n4️⃣ Handlers tekshirilmoqda...")
try:
    from handlers.start_handler import register_start_handlers
    from handlers.trading_handler import register_trading_handlers
    from handlers.license_handler import register_license_handlers
    from handlers.admin_handler import register_admin_handlers
    from handlers.premium_handler import register_premium_handlers
    print("   ✅ Barcha handlers tayyor")
except Exception as e:
    print(f"   ❌ Handler xatosi: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 5. Papkalar tekshirish
print("\n5️⃣ Papkalar tekshirilmoqda...")
os.makedirs(config.ANALYSES_DIR, exist_ok=True)
os.makedirs(config.PRO_ANALYSES_DIR, exist_ok=True)
print(f"   ✅ {config.ANALYSES_DIR} papkasi tayyor")
print(f"   ✅ {config.PRO_ANALYSES_DIR} papkasi tayyor")

print("\n" + "="*50)
print("✅ Barcha testlar muvaffaqiyatli o'tdi!")
print("="*50)
print("\n🚀 Botni ishga tushirish uchun:")
print("   python main.py")
print()

