# Google Cloud Run ga Botni Deploy Qilish Qo'llanmasi

## 1. Google Cloud Project Yaratish

1. [Google Cloud Console](https://console.cloud.google.com/) ga kiring
2. Yangi project yarating yoki mavjud projectni tanlang
3. Billing ni yoqing (Cloud Run uchun kerak)

## 2. Google Cloud CLI O'rnatish

### Windows:
```powershell
# Chocolatey orqali
choco install gcloudsdk

# Yoki manual yuklab olish
# https://cloud.google.com/sdk/docs/install
```

### Linux/Mac:
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

## 3. Google Cloud ga Kirish

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

## 4. Firebase Credentials ni Environment Variable ga O'zgartirish

### Variant A: Base64 encode qilish (Tavsiya etiladi)

**Windows PowerShell:**
```powershell
# Firebase credentials ni base64 ga o'zgartirish
$content = Get-Content firebase_credentials.json -Raw
$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
$base64 = [System.Convert]::ToBase64String($bytes)
$base64 | Out-File firebase_creds_base64.txt
```

**Linux/Mac:**
```bash
base64 firebase_credentials.json > firebase_creds_base64.txt
```

### Variant B: Secret Manager ishlatish (Tavsiya etiladi)

```bash
# Secret yaratish
gcloud secrets create firebase-credentials --data-file=firebase_credentials.json

# Secret ni Cloud Run ga ulash
# (Bu quyidagi deploy buyrug'ida qo'shiladi)
```

## 5. Docker Image Yaratish va Push Qilish

### Local test qilish:
```bash
# Docker image yaratish
docker build -t fath-bot .

# Local test
docker run -e BOT_TOKEN="your-token" -e FIREBASE_CREDENTIALS="$(cat firebase_creds_base64.txt | base64 -d)" fath-bot
```

### Google Container Registry ga push qilish:
```bash
# Docker ga authenticate qilish
gcloud auth configure-docker

# Image yaratish va push qilish
docker build -t gcr.io/YOUR_PROJECT_ID/fath-bot .
docker push gcr.io/YOUR_PROJECT_ID/fath-bot
```

## 6. Cloud Run ga Deploy Qilish

### Variant A: gcloud CLI orqali

```bash
gcloud run deploy fath-bot \
  --image gcr.io/YOUR_PROJECT_ID/fath-bot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars "BOT_TOKEN=your-bot-token" \
  --set-secrets "FIREBASE_CREDENTIALS=firebase-credentials:latest"
```

### Variant B: Cloud Build orqali (Avtomatik)

```bash
# Cloud Build ni ishga tushirish
gcloud builds submit --config cloudbuild.yaml
```

## 7. Environment Variables Sozlash

Cloud Run Console orqali yoki CLI orqali:

```bash
gcloud run services update fath-bot \
  --set-env-vars "BOT_TOKEN=your-bot-token,USE_FIRESTORE=True" \
  --region us-central1
```

## 8. Secret Manager orqali Firebase Credentials

```bash
# Secret yaratish
gcloud secrets create firebase-credentials \
  --data-file=firebase_credentials.json \
  --replication-policy="automatic"

# Cloud Run ga ulash
gcloud run services update fath-bot \
  --update-secrets FIREBASE_CREDENTIALS=firebase-credentials:latest \
  --region us-central1
```

## 9. Botni Tekshirish

```bash
# Service holatini ko'rish
gcloud run services describe fath-bot --region us-central1

# Loglarni ko'rish
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=fath-bot" --limit 50
```

## 10. Avtomatik Deploy (CI/CD)

### GitHub Actions yaratish (`.github/workflows/deploy.yml`):

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - id: 'auth'
        uses: 'google-github-actions/auth@v1'
        with:
          credentials_json: '${{ secrets.GCP_SA_KEY }}'
      
      - name: 'Set up Cloud SDK'
        uses: 'google-github-actions/setup-gcloud@v1'
      
      - name: 'Build and Deploy'
        run: |
          gcloud builds submit --config cloudbuild.yaml
```

## 11. Xarajatlar

Cloud Run pricing:
- **CPU:** $0.00002400 per vCPU-second
- **Memory:** $0.00000250 per GiB-second
- **Requests:** $0.40 per million requests
- **Free tier:** 2 million requests/month

**Tahminiy xarajat:** ~$5-10/oy (kichik bot uchun)

## 12. Scaling Sozlamalari

```bash
# Min/Max instances
gcloud run services update fath-bot \
  --min-instances 1 \
  --max-instances 10 \
  --region us-central1

# Concurrency (bir instance nechta requestni bir vaqtda qayta ishlaydi)
gcloud run services update fath-bot \
  --concurrency 80 \
  --region us-central1
```

## 13. Monitoring va Logging

```bash
# Loglarni real-time ko'rish
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=fath-bot"

# Metrics ko'rish
gcloud monitoring dashboards list
```

## 14. Muammolarni Hal Qilish

### Bot ishlamayapti:
```bash
# Loglarni ko'rish
gcloud logging read "resource.type=cloud_run_revision" --limit 100

# Service ni qayta deploy qilish
gcloud run services update fath-bot --region us-central1
```

### Firebase ulanishi yo'q:
```bash
# Environment variables ni tekshirish
gcloud run services describe fath-bot --region us-central1

# Secret ni tekshirish
gcloud secrets versions access latest --secret="firebase-credentials"
```

## 15. Foydali Buyruqlar

```bash
# Service holatini ko'rish
gcloud run services list

# Service ni o'chirish
gcloud run services delete fath-bot --region us-central1

# Service ni yangilash
gcloud run services update fath-bot --region us-central1

# Loglarni ko'rish
gcloud logging read "resource.type=cloud_run_revision" --limit 50
```

## 16. Alternativ: Railway/Render/Heroku

Agar Cloud Run murakkab bo'lsa, quyidagi platformalar ham ishlaydi:

### Railway:
```bash
railway login
railway init
railway up
```

### Render:
1. GitHub repository ga ulash
2. Render.com ga kiring
3. New Web Service
4. Repository ni tanlang
5. Build: `pip install -r requirements.txt && python main.py`

---

**Muvaffaqiyatli deployment! 🚀**

