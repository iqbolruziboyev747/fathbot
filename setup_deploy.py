# ============================================
# Deploy Setup Script
# Deploy uchun kerakli ma'lumotlarni yig'ish va tayyorlash
# ============================================

import os
import json
import sys

print("="*50)
print("🚀 FATH BOT - Deploy Setup")
print("="*50)
print()

# 1. Config tekshirish
print("1️⃣ Config tekshirilmoqda...")
try:
    import config
    print(f"   ✅ BOT_TOKEN: {config.BOT_TOKEN[:20]}...")
    print(f"   ✅ ADMINS: {config.ADMINS}")
    print(f"   ✅ USE_FIRESTORE: {config.USE_FIRESTORE}")
except Exception as e:
    print(f"   ❌ Config xatosi: {e}")
    sys.exit(1)

# 2. Firebase credentials tekshirish
print("\n2️⃣ Firebase credentials tekshirilmoqda...")
if os.path.exists("firebase_credentials.json"):
    print("   ✅ firebase_credentials.json topildi")
    
    # Firebase credentials ni o'qish
    try:
        with open("firebase_credentials.json", "r") as f:
            firebase_creds = json.load(f)
        print(f"   ✅ Project ID: {firebase_creds.get('project_id', 'N/A')}")
        
        # Environment variable uchun tayyorlash
        creds_json_string = json.dumps(firebase_creds)
        print(f"   ✅ Credentials uzunligi: {len(creds_json_string)} belgi")
    except Exception as e:
        print(f"   ❌ Credentials o'qishda xatolik: {e}")
        sys.exit(1)
else:
    print("   ❌ firebase_credentials.json topilmadi!")
    sys.exit(1)

# 3. Deploy fayllarini tekshirish
print("\n3️⃣ Deploy fayllari tekshirilmoqda...")
deploy_files = [
    "Dockerfile",
    "Procfile",
    "railway.json",
    "requirements.txt",
    "main.py"
]

for file in deploy_files:
    if os.path.exists(file):
        print(f"   ✅ {file}")
    else:
        print(f"   ⚠️ {file} topilmadi")

# 4. Environment variables faylini yaratish (.env.example)
print("\n4️⃣ Environment variables fayli yaratilmoqda...")
env_example = f"""# Bot Token
BOT_TOKEN={config.BOT_TOKEN}

# Firebase Credentials (JSON string)
FIREBASE_CREDENTIALS={json.dumps(firebase_creds)}

# Firestore
USE_FIRESTORE=True
"""

with open(".env.example", "w") as f:
    f.write(env_example)
print("   ✅ .env.example yaratildi")

# 5. Railway environment variables fayli
print("\n5️⃣ Railway environment variables fayli yaratilmoqda...")
railway_env = f"""BOT_TOKEN={config.BOT_TOKEN}
USE_FIRESTORE=True
FIREBASE_CREDENTIALS={json.dumps(firebase_creds)}
"""

with open("railway.env", "w") as f:
    f.write(railway_env)
print("   ✅ railway.env yaratildi")

# 6. Deploy qo'llanmasi
print("\n" + "="*50)
print("✅ Deploy tayyor!")
print("="*50)
print()
print("Keyingi qadamlar:")
print()
print("VARIANT 1: Railway (Tavsiya etiladi)")
print("  1. GitHub ga kodlarni push qiling")
print("  2. railway.app ga kiring")
print("  3. New Project → Deploy from GitHub")
print("  4. railway.env faylidagi environment variables ni qo'ying")
print()
print("VARIANT 2: Render")
print("  1. GitHub ga kodlarni push qiling")
print("  2. render.com ga kiring")
print("  3. New Web Service → GitHub repo")
print("  4. Environment variables ni .env.example dan qo'ying")
print()
print("VARIANT 3: Google Cloud Run")
print("  Batafsil: CLOUD_DEPLOYMENT.md faylida")
print()

