# Avtomatik Deploy Qo'llanmasi

## ✅ Tayyorlangan:
- ✅ Git repository yaratildi
- ✅ Barcha fayllar commit qilindi
- ✅ Environment variables fayllari tayyor

## 🚀 Keyingi Qadamlar:

### 1. GitHub Repository Yaratish

**Sizdan so'raladigan ma'lumotlar:**
- GitHub username: ________________
- Repository nomi: `fath-unified-bot` (yoki istalgan nom)

**GitHub ga push qilish:**

```bash
# GitHub repository URL ni o'zgartiring
git remote add origin https://github.com/YOUR_USERNAME/fath-unified-bot.git

# Push qilish
git branch -M main
git push -u origin main
```

**Yoki GitHub CLI orqali:**
```bash
gh repo create fath-unified-bot --public --source=. --remote=origin --push
```

### 2. Railway ga Deploy

1. **Railway.app ga kiring**
   - https://railway.app/
   - GitHub bilan login qiling

2. **New Project → Deploy from GitHub**
   - Repository ni tanlang

3. **Environment Variables qo'shish**
   
   Railway dashboard da "Variables" tabiga o'ting va quyidagilarni qo'ying:
   
   ```
   BOT_TOKEN=8161852003:AAFwAP8fLiAsaMJyQQJj62dKPwDCm_QgfVQ
   USE_FIRESTORE=True
   ```
   
   **FIREBASE_CREDENTIALS ni qo'shish:**
   
   `railway.env` faylini oching va `FIREBASE_CREDENTIALS` qiymatini Railway ga qo'ying.
   
   Yoki PowerShell da:
   ```powershell
   (Get-Content firebase_credentials.json -Raw) -replace "`n", "" -replace "`r", ""
   ```
   
   Bu qiymatni Railway da `FIREBASE_CREDENTIALS` variable ga qo'ying.

4. **Deploy**
   - Railway avtomatik deploy qiladi
   - Loglarni ko'rishingiz mumkin

### 3. Botni Tekshirish

- Railway dashboard da loglarni ko'ring
- Telegram botni test qiling: `/start`

---

## 📋 Kerakli Ma'lumotlar:

**Sizdan so'raladigan:**
1. ✅ GitHub username: ________________
2. ✅ GitHub repository yaratildimi? (Ha/Yo'q)
3. ✅ Railway account mavjudmi? (Ha/Yo'q)

**Agar GitHub repository yaratilgan bo'lsa:**
- Repository URL ni bering, men push qilaman

**Agar Railway account yo'q bo'lsa:**
- Railway.app ga kiring va GitHub bilan login qiling

---

## 🔧 Muammolarni Hal Qilish

### GitHub authentication:
```bash
# Personal Access Token yaratish
# GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
# "repo" scope ni tanlang

# Token ni ishlatish
git remote set-url origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/fath-unified-bot.git
```

### Railway deploy xatosi:
- Loglarni tekshiring
- Environment variables to'g'ri ekanligini tekshiring
- `railway.env` faylini qayta yuklang

---

**Deploy qilishga tayyor! 🚀**

