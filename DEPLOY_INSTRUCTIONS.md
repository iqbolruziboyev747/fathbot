# Deploy Qo'llanmasi - Qadam-baqadam

## ✅ Tayyorlangan:
- ✅ Barcha kodlar tayyor
- ✅ Firebase credentials tayyor
- ✅ Environment variables fayllari yaratildi (.env.example, railway.env)
- ✅ Deploy fayllari tayyor (Dockerfile, Procfile, railway.json)

## 📋 Deploy uchun kerakli ma'lumotlar:

### 1. GitHub Repository
- [ ] GitHub account mavjudmi?
- [ ] Yangi repository yaratish kerakmi yoki mavjud repository URL?

### 2. Platform Tanlash
Quyidagilardan birini tanlang:
- [ ] **Railway** (eng oson, tavsiya etiladi) ⭐
- [ ] **Render** (bepul tier)
- [ ] **Google Cloud Run**

---

## 🚀 Deploy Jarayoni:

### QADAM 1: Git Repository Yaratish

```bash
# Git repository yaratish
git init
git add .
git commit -m "Initial commit - FATH Bot with Firestore"
```

### QADAM 2: GitHub Repository Yaratish

**Variant A: GitHub Web Interface orqali**
1. GitHub.com ga kiring
2. "New repository" tugmasini bosing
3. Repository nomi: `fath-unified-bot` (yoki istalgan nom)
4. "Create repository" tugmasini bosing
5. Repository URL ni oling (masalan: `https://github.com/username/fath-unified-bot.git`)

**Variant B: GitHub CLI orqali**
```bash
gh repo create fath-unified-bot --public
```

### QADAM 3: GitHub ga Push Qilish

```bash
# Remote qo'shish
git remote add origin https://github.com/YOUR_USERNAME/fath-unified-bot.git

# Push qilish
git branch -M main
git push -u origin main
```

### QADAM 4: Railway ga Deploy (Eng Oson)

1. **Railway.app ga kiring**
   - https://railway.app/
   - GitHub bilan login qiling

2. **New Project yaratish**
   - "New Project" tugmasini bosing
   - "Deploy from GitHub repo" ni tanlang
   - Repository ni tanlang (`fath-unified-bot`)

3. **Environment Variables qo'shish**
   Railway dashboard da "Variables" tabiga o'ting va quyidagilarni qo'ying:
   
   ```
   BOT_TOKEN=8161852003:AAFwAP8fLiAsaMJyQQJj62dKPwDCm_QgfVQ
   USE_FIRESTORE=True
   FIREBASE_CREDENTIALS={"type":"service_account","project_id":"fathbot-552a7",...}
   ```
   
   **FIREBASE_CREDENTIALS ni olish:**
   ```powershell
   # Windows PowerShell
   (Get-Content firebase_credentials.json -Raw) -replace "`n", "" -replace "`r", ""
   ```
   
   Yoki `railway.env` faylidan ko'chirib oling.

4. **Deploy**
   - Railway avtomatik deploy qiladi
   - Loglarni ko'rishingiz mumkin

### QADAM 5: Botni Tekshirish

1. Railway dashboard da "Deployments" bo'limiga o'ting
2. Loglarni ko'ring
3. Telegram botni test qiling

---

## 🔧 Muammolarni Hal Qilish

### Git push xatosi:
```bash
# GitHub authentication
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# SSH key yaratish (agar kerak bo'lsa)
ssh-keygen -t ed25519 -C "your.email@example.com"
```

### Railway deploy xatosi:
- Loglarni tekshiring
- Environment variables to'g'ri ekanligini tekshiring
- `railway.env` faylini qayta yuklang

---

## 📞 Yordam

Agar muammo bo'lsa:
1. Loglarni ko'ring
2. Environment variables ni tekshiring
3. `setup_deploy.py` ni qayta ishga tushiring

---

**Deploy qilishga tayyor! 🚀**

