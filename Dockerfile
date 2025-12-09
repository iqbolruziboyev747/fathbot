# ============================================
# Dockerfile - Google Cloud Run uchun
# ============================================

FROM python:3.9-slim

# Working directory
WORKDIR /app

# System paketlarini o'rnatish
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Requirements ni ko'chirish va o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bot kodlarini ko'chirish
COPY . .

# Firebase credentials ni environment variable dan olish
# (Cloud Run da environment variable sifatida beriladi)

# Botni ishga tushirish
CMD ["python", "main.py"]

