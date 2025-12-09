#!/bin/bash
# ============================================
# Railway ga Avtomatik Deploy Script
# ============================================

echo "🚀 Railway ga Deploy qilish..."
echo ""

# 1. Git repository tekshirish
if [ ! -d ".git" ]; then
    echo "❌ Git repository topilmadi!"
    echo "Git repository yaratish kerak:"
    echo "  git init"
    echo "  git add ."
    echo "  git commit -m 'Initial commit'"
    exit 1
fi

# 2. Railway CLI tekshirish
if ! command -v railway &> /dev/null; then
    echo "⚠️ Railway CLI topilmadi!"
    echo "O'rnatish: npm i -g @railway/cli"
    echo "Yoki Railway web interface orqali deploy qiling"
    exit 1
fi

# 3. Railway ga login
echo "1️⃣ Railway ga login qilinmoqda..."
railway login

# 4. Project yaratish yoki tanlash
echo "2️⃣ Project yaratilmoqda..."
railway init

# 5. Environment variables sozlash
echo "3️⃣ Environment variables sozlanmoqda..."

# Bot token
read -p "Bot Token (Enter bosib o'tkazib yuborish uchun config.py dan olinadi): " BOT_TOKEN
if [ -z "$BOT_TOKEN" ]; then
    BOT_TOKEN="8161852003:AAFwAP8fLiAsaMJyQQJj62dKPwDCm_QgfVQ"
fi

# Firebase credentials
if [ -f "firebase_credentials.json" ]; then
    FIREBASE_CREDENTIALS=$(cat firebase_credentials.json | jq -c .)
    echo "✅ Firebase credentials topildi"
else
    echo "❌ firebase_credentials.json topilmadi!"
    exit 1
fi

# Environment variables ni o'rnatish
railway variables set BOT_TOKEN="$BOT_TOKEN"
railway variables set FIREBASE_CREDENTIALS="$FIREBASE_CREDENTIALS"
railway variables set USE_FIRESTORE="True"

echo "✅ Environment variables o'rnatildi"

# 6. Deploy
echo "4️⃣ Deploy qilinmoqda..."
railway up

echo ""
echo "✅ Deploy yakunlandi!"
echo "Railway dashboard da bot holatini ko'rishingiz mumkin"

