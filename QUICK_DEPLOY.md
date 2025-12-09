# Tezkor Deploy Qo'llanmasi (VPS Yo'q)

## Variant 1: Railway (Eng Oson) ⭐

### 1. Railway ga Kirish
1. [Railway.app](https://railway.app/) ga kiring
2. GitHub bilan login qiling

### 2. Project Yaratish
1. "New Project" tugmasini bosing
2. "Deploy from GitHub repo" ni tanlang
3. Repository ni tanlang

### 3. Environment Variables Qo'shish
Railway dashboard da:
- `BOT_TOKEN` = your-bot-token
- `FIREBASE_CREDENTIALS` = firebase_credentials.json ning to'liq kontenti (JSON string)

### 4. Deploy
Railway avtomatik deploy qiladi!

---

## Variant 2: Render (Bepul)

### 1. Render ga Kirish
1. [Render.com](https://render.com/) ga kiring
2. GitHub bilan login qiling

### 2. New Web Service
1. "New +" → "Web Service"
2. Repository ni tanlang
3. Sozlamalar:
   - **Name:** fath-bot
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`

### 3. Environment Variables
- `BOT_TOKEN` = your-bot-token
- `FIREBASE_CREDENTIALS` = firebase_credentials.json kontenti

### 4. Deploy
"Create Web Service" tugmasini bosing

---

## Variant 3: Google Cloud Run

### 1. Google Cloud CLI O'rnatish
```bash
# Windows
choco install gcloudsdk
```

### 2. Deploy
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Docker build va push
docker build -t gcr.io/YOUR_PROJECT_ID/fath-bot .
docker push gcr.io/YOUR_PROJECT_ID/fath-bot

# Deploy
gcloud run deploy fath-bot \
  --image gcr.io/YOUR_PROJECT_ID/fath-bot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "BOT_TOKEN=your-token" \
  --set-secrets "FIREBASE_CREDENTIALS=firebase-credentials:latest"
```

---

## Variant 4: Heroku

### 1. Heroku CLI O'rnatish
```bash
# Windows
choco install heroku-cli
```

### 2. Deploy
```bash
heroku login
heroku create fath-bot
heroku config:set BOT_TOKEN=your-token
heroku config:set FIREBASE_CREDENTIALS="$(cat firebase_credentials.json)"
git push heroku main
```

---

## Firebase Credentials ni Environment Variable ga O'zgartirish

### Windows PowerShell:
```powershell
# JSON faylni o'qish va environment variable ga o'rnatish
$creds = Get-Content firebase_credentials.json -Raw
[Environment]::SetEnvironmentVariable("FIREBASE_CREDENTIALS", $creds, "User")
```

### Linux/Mac:
```bash
export FIREBASE_CREDENTIALS="$(cat firebase_credentials.json)"
```

---

## Eng Oson Variant: Railway ⭐

1. GitHub ga kodlarni push qiling
2. Railway.app ga kiring
3. New Project → GitHub repo tanlang
4. Environment variables qo'shing:
   - `BOT_TOKEN`
   - `FIREBASE_CREDENTIALS` (JSON string)
5. Deploy!

**Tayyor! Bot endi Railway da ishlaydi! 🚀**

---

**Batafsil qo'llanma:** `CLOUD_DEPLOYMENT.md`

