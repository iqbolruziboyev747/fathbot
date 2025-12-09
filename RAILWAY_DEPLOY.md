# Railway ga Deploy Qo'llanmasi

## ✅ GitHub Repository Tayyor!
Repository: https://github.com/iqbolruziboyev747/fathbot

## 🚀 Railway ga Deploy Qilish

### QADAM 1: Railway ga Kirish
1. https://railway.app ga kiring
2. "Start a New Project" tugmasini bosing
3. GitHub bilan login qiling (agar login qilmagan bo'lsangiz)

### QADAM 2: Repository ni Tanlash
1. "Deploy from GitHub repo" ni tanlang
2. Repository ro'yxatidan `fathbot` ni tanlang
3. Railway avtomatik deploy qilishni boshlaydi

### QADAM 3: Environment Variables Qo'shish

Railway dashboard da:
1. Project ni oching
2. "Variables" tabiga o'ting
3. Quyidagi environment variables ni qo'shing:

#### 1. BOT_TOKEN
```
BOT_TOKEN=8161852003:AAFwAP8fLiAsaMJyQQJj62dKPwDCm_QgfVQ
```

#### 2. USE_FIRESTORE
```
USE_FIRESTORE=True
```

#### 3. FIREBASE_CREDENTIALS (Muhim!)

Firebase credentials ni qo'shish uchun:

**Variant A: PowerShell orqali**
```powershell
# PowerShell da quyidagi buyruqni bajaring:
(Get-Content firebase_credentials.json -Raw) -replace "`n", "" -replace "`r", ""
```

Bu chiqadigan qiymatni Railway da `FIREBASE_CREDENTIALS` variable ga qo'ying.

**Variant B: Manual**
1. `firebase_credentials.json` faylini oching
2. Barcha kontentni nusxalang (Ctrl+A, Ctrl+C)
3. Railway da `FIREBASE_CREDENTIALS` variable yarating
4. Qiymat sifatida nusxalangan JSON ni qo'ying

**Muhim:** JSON ni bir qator qilib qo'yish kerak (yoki Railway avtomatik format qiladi).

### QADAM 4: Deploy

Environment variables qo'shgandan so'ng:
1. Railway avtomatik qayta deploy qiladi
2. Yoki "Deployments" tabida "Redeploy" tugmasini bosing

### QADAM 5: Botni Tekshirish

1. **Loglarni ko'rish:**
   - Railway dashboard da "Deployments" → "View Logs"
   - Quyidagi xabarlarni ko'rishingiz kerak:
     ```
     ✅ Firestore database ishlatilmoqda
     🤖 FATH UNIFIED BOT ISHGA TUSHDI!
     ```

2. **Telegram botni test qiling:**
   - Telegram da botni toping
   - `/start` buyrug'ini yuboring
   - Bot javob berishi kerak

## 🔧 Muammolarni Hal Qilish

### Bot ishlamayapti?
1. Loglarni tekshiring - Railway dashboard da "View Logs"
2. Environment variables to'g'ri ekanligini tekshiring
3. `FIREBASE_CREDENTIALS` to'g'ri formatda ekanligini tekshiring

### Firebase ulanishi yo'q?
1. `FIREBASE_CREDENTIALS` ni qayta tekshiring
2. Firebase Console da Firestore Database yaratilganligini tekshiring
3. Loglarda Firebase xatolarini qidiring

### Deploy xatosi?
1. Railway dashboard da "Settings" → "Build & Deploy"
2. "Start Command" ni tekshiring: `python main.py`
3. "Root Directory" bo'sh bo'lishi kerak

## 📊 Monitoring

Railway dashboard da:
- **Metrics** - CPU, Memory ishlatilishi
- **Logs** - Real-time loglar
- **Deployments** - Deploy tarixi

## 💰 Xarajatlar

Railway:
- **Free tier:** $5 credit/oy (bot uchun yetarli)
- **Pro:** $20/oy (agar kerak bo'lsa)

## ✅ Tayyor!

Bot endi Railway da ishlaydi va Firestore da ma'lumotlarni saqlaydi!

---

**Qo'shimcha yordam:** Railway dashboard da "Support" tugmasini bosing

