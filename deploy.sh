#!/bin/bash
# ============================================
# FATH BOT - VPS Deployment Script
# ============================================

set -e

echo "🚀 FATH Bot VPS Deployment Script"
echo "=================================="
echo ""

# Ranglar
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# O'zgaruvchilar
BOT_DIR="/opt/fath-bot"
SERVICE_NAME="fath-bot"
USER="root"

# 1. Paketlarni o'rnatish
echo -e "${GREEN}1️⃣ Paketlar o'rnatilmoqda...${NC}"
if command -v apt-get &> /dev/null; then
    sudo apt-get update -y
    sudo apt-get install -y python3 python3-pip git screen tmux
elif command -v yum &> /dev/null; then
    sudo yum update -y
    sudo yum install -y python3 python3-pip git screen tmux
else
    echo -e "${RED}❌ Paket manager topilmadi!${NC}"
    exit 1
fi

# 2. Bot papkasini yaratish
echo -e "${GREEN}2️⃣ Bot papkasi yaratilmoqda...${NC}"
sudo mkdir -p $BOT_DIR
sudo chown $USER:$USER $BOT_DIR

# 3. Bot kodlarini ko'chirish
echo -e "${GREEN}3️⃣ Bot kodlarini ko'chirish...${NC}"
echo -e "${YELLOW}⚠️ Iltimos, bot kodlarini $BOT_DIR ga ko'chiring!${NC}"
echo "   Masalan: scp -r /path/to/bot/* $USER@server:$BOT_DIR/"

# 4. Python paketlarini o'rnatish
echo -e "${GREEN}4️⃣ Python paketlari o'rnatilmoqda...${NC}"
cd $BOT_DIR
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
else
    echo -e "${RED}❌ requirements.txt topilmadi!${NC}"
    exit 1
fi

# 5. Firebase credentials tekshirish
echo -e "${GREEN}5️⃣ Firebase credentials tekshirilmoqda...${NC}"
if [ -f "$BOT_DIR/firebase_credentials.json" ]; then
    chmod 600 $BOT_DIR/firebase_credentials.json
    echo -e "${GREEN}✅ Firebase credentials topildi${NC}"
else
    echo -e "${YELLOW}⚠️ firebase_credentials.json topilmadi!${NC}"
    echo "   Iltimos, firebase_credentials.json ni $BOT_DIR ga ko'chiring"
fi

# 6. Firestore ni initialize qilish
echo -e "${GREEN}6️⃣ Firestore initialize qilinmoqda...${NC}"
cd $BOT_DIR
if [ -f "init_firestore.py" ]; then
    python3 init_firestore.py
else
    echo -e "${YELLOW}⚠️ init_firestore.py topilmadi, o'tkazib yuborildi${NC}"
fi

# 7. Systemd service yaratish
echo -e "${GREEN}7️⃣ Systemd service yaratilmoqda...${NC}"
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=FATH Unified Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$BOT_DIR
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 $BOT_DIR/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# 8. Service ni ishga tushirish
echo -e "${GREEN}8️⃣ Service ishga tushirilmoqda...${NC}"
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}.service

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Deployment yakunlandi!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Foydali buyruqlar:"
echo "  Botni ishga tushirish:  sudo systemctl start ${SERVICE_NAME}"
echo "  Botni to'xtatish:       sudo systemctl stop ${SERVICE_NAME}"
echo "  Botni qayta ishga tushirish: sudo systemctl restart ${SERVICE_NAME}"
echo "  Bot holatini ko'rish:   sudo systemctl status ${SERVICE_NAME}"
echo "  Loglarni ko'rish:       sudo journalctl -u ${SERVICE_NAME} -f"
echo ""
echo -e "${YELLOW}⚠️ Eslatma: Botni ishga tushirishdan oldin firebase_credentials.json ni ko'chirib qo'ying!${NC}"

