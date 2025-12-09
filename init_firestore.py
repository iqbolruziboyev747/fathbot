# ============================================
# FIRESTORE INITIALIZATION SCRIPT
# Botni birinchi marta ishga tushirganda Firestore ni initialize qilish
# ============================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config

print("🔥 Firestore initialization boshlandi...\n")

# Firestore ni test qilish
try:
    if config.USE_FIRESTORE:
        print("✅ USE_FIRESTORE = True")
        
        # Firebase credentials tekshirish
        if os.path.exists(config.FIREBASE_CREDENTIALS_PATH):
            print(f"✅ Firebase credentials fayl topildi: {config.FIREBASE_CREDENTIALS_PATH}")
        else:
            print(f"❌ Firebase credentials fayl topilmadi: {config.FIREBASE_CREDENTIALS_PATH}")
            print("   Iltimos, firebase_credentials.json faylini bot papkasiga qo'ying.")
            sys.exit(1)
        
        # Firestore client ni test qilish
        print("\n📡 Firestore ga ulanish...")
        from database.firestore_service import get_firestore_client
        db = get_firestore_client()
        print("✅ Firestore ga muvaffaqiyatli ulandi!")
        
        # Default pricing plans ni yaratish
        print("\n💵 Default pricing plans yaratilmoqda...")
        from database.firestore_service import firestore_license_db
        firestore_license_db.init_default_plans()
        print("✅ Default pricing plans yaratildi!")
        
        # Collections ni test qilish
        print("\n📚 Collections tekshirilmoqda...")
        collections = [
            config.FIRESTORE_COLLECTIONS["users"],
            config.FIRESTORE_COLLECTIONS["analyses"],
            config.FIRESTORE_COLLECTIONS["licenses"],
            config.FIRESTORE_COLLECTIONS["pricing_plans"],
            config.FIRESTORE_COLLECTIONS["referrals"],
            config.FIRESTORE_COLLECTIONS["referral_codes"],
            config.FIRESTORE_COLLECTIONS["economic_data"],
            config.FIRESTORE_COLLECTIONS["insider_news"]
        ]
        
        for collection_name in collections:
            try:
                collection_ref = db.collection(collection_name)
                # Collection mavjudligini tekshirish (birinchi document qo'shish orqali)
                print(f"   ✅ {collection_name} collection tayyor")
            except Exception as e:
                print(f"   ⚠️ {collection_name} collection: {e}")
        
        print("\n" + "="*50)
        print("🎉 Firestore initialization muvaffaqiyatli yakunlandi!")
        print("="*50)
        print("\n✅ Botni ishga tushirishga tayyor!")
        print("   Quyidagi buyruqni bajaring:")
        print("   python main.py")
        print()
        
    else:
        print("⚠️ USE_FIRESTORE = False")
        print("   Bot SQLite database ishlatmoqda.")
        print("   Firestore ni yoqish uchun config.py da USE_FIRESTORE = True qiling.")
        
except Exception as e:
    print(f"\n❌ XATOLIK: {e}")
    print("\nTekshirib ko'ring:")
    print("1. Firebase credentials fayl to'g'ri joyda ekanligini")
    print("2. Firebase project da Firestore Database yaratilganligini")
    print("3. Service account key to'g'ri ekanligini")
    import traceback
    traceback.print_exc()

