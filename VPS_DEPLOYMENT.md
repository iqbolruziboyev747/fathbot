# VPS Serverda Botni O'rnatish Qo'llanmasi

## 1. VPS Serverga Ulanish

```bash
ssh root@your-vps-ip
# yoki
ssh user@your-vps-ip
```

## 2. Kerakli Paketlarni O'rnatish

### Ubuntu/Debian:
```bash
# Python va pip o'rnatish
sudo apt update
sudo apt install python3 python3-pip git -y

# Bot papkasini yaratish
mkdir -p /opt/fath-bot
cd /opt/fath-bot
```

### CentOS/RHEL:
```bash
sudo yum update -y
sudo yum install python3 python3-pip git -y
mkdir -p /opt/fath-bot
cd /opt/fath-bot
```

## 3. Bot Kodlarini Yuklab Olish

### Variant A: Git orqali (agar Git repository bo'lsa)
```bash
git clone your-repository-url /opt/fath-bot
cd /opt/fath-bot
```

### Variant B: Manual ko'chirish
```bash
# Sizning kompyuteringizdan VPS ga ko'chirish
scp -r /path/to/fath_unified_bot/* root@your-vps-ip:/opt/fath-bot/
```

## 4. Firebase Credentials Faylini Ko'chirish

```bash
# Sizning kompyuteringizdan:
scp firebase_credentials.json root@your-vps-ip:/opt/fath-bot/

# VPS da tekshirish:
cd /opt/fath-bot
ls -la firebase_credentials.json
```

## 5. Python Paketlarini O'rnatish

```bash
cd /opt/fath-bot
pip3 install -r requirements.txt
```

## 6. Botni Test Qilish

```bash
cd /opt/fath-bot
python3 init_firestore.py
python3 test_bot.py
```

## 7. Systemd Service Yaratish (Avtomatik Ishga Tushirish)

### Service faylini yaratish:
```bash
sudo nano /etc/systemd/system/fath-bot.service
```

### Quyidagi kontentni qo'ying:
```ini
[Unit]
Description=FATH Unified Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/fath-bot
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 /opt/fath-bot/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### Service ni ishga tushirish:
```bash
# Service ni reload qilish
sudo systemctl daemon-reload

# Service ni yoqish
sudo systemctl enable fath-bot.service

# Service ni ishga tushirish
sudo systemctl start fath-bot.service

# Status ni tekshirish
sudo systemctl status fath-bot.service

# Loglarni ko'rish
sudo journalctl -u fath-bot.service -f
```

## 8. Screen/Tmux orqali Ishga Tushirish (Alternativ)

### Screen:
```bash
# Screen o'rnatish
sudo apt install screen -y

# Screen session yaratish
screen -S fath-bot

# Botni ishga tushirish
cd /opt/fath-bot
python3 main.py

# Screen dan chiqish: Ctrl+A, keyin D

# Screen ga qaytish
screen -r fath-bot
```

### Tmux:
```bash
# Tmux o'rnatish
sudo apt install tmux -y

# Tmux session yaratish
tmux new -s fath-bot

# Botni ishga tushirish
cd /opt/fath-bot
python3 main.py

# Tmux dan chiqish: Ctrl+B, keyin D

# Tmux ga qaytish
tmux attach -t fath-bot
```

## 9. Firewall Sozlamalari

```bash
# Agar firewall ishlatilsa, portlarni ochish (agar kerak bo'lsa)
sudo ufw allow 22/tcp  # SSH
# Bot uchun port kerak emas, chunki u polling ishlatadi
```

## 10. Loglarni Ko'rish va Boshqarish

### Systemd loglari:
```bash
# Oxirgi 100 qator log
sudo journalctl -u fath-bot.service -n 100

# Real-time loglar
sudo journalctl -u fath-bot.service -f

# Bugungi loglar
sudo journalctl -u fath-bot.service --since today

# Loglarni faylga saqlash (ixtiyoriy)
sudo journalctl -u fath-bot.service > /opt/fath-bot/logs/bot.log
```

### Log rotation sozlash:
```bash
sudo nano /etc/logrotate.d/fath-bot
```

Kontent:
```
/opt/fath-bot/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

## 11. Botni Yangilash

```bash
# Botni to'xtatish
sudo systemctl stop fath-bot.service

# Kodlarni yangilash
cd /opt/fath-bot
# Git bo'lsa:
git pull
# Yoki manual ko'chirish

# Paketlarni yangilash (agar kerak bo'lsa)
pip3 install -r requirements.txt --upgrade

# Botni qayta ishga tushirish
sudo systemctl start fath-bot.service
```

## 12. Monitoring va Boshqarish

### Bot holatini tekshirish:
```bash
# Service status
sudo systemctl status fath-bot.service

# Bot ishlayaptimi?
ps aux | grep main.py

# Firestore ulanishini tekshirish
cd /opt/fath-bot
python3 init_firestore.py
```

## 13. Xavfsizlik

### 1. Firebase credentials faylini himoya qilish:
```bash
chmod 600 /opt/fath-bot/firebase_credentials.json
chown root:root /opt/fath-bot/firebase_credentials.json
```

### 2. Bot papkasini himoya qilish:
```bash
chmod 700 /opt/fath-bot
```

### 3. Firestore Security Rules ni tekshirish:
Firebase Console da Firestore Security Rules ni production uchun qattiqroq qiling.

## 14. Muammolarni Hal Qilish

### Bot ishlamayapti:
```bash
# Loglarni ko'rish
sudo journalctl -u fath-bot.service -n 50

# Service ni qayta ishga tushirish
sudo systemctl restart fath-bot.service

# Python versiyasini tekshirish
python3 --version
```

### Firestore ulanishi yo'q:
```bash
# Credentials faylini tekshirish
cat /opt/fath-bot/firebase_credentials.json

# Firestore ni test qilish
cd /opt/fath-bot
python3 init_firestore.py
```

### Port muammosi:
Bot polling ishlatadi, shuning uchun port ochish kerak emas.

## 15. Avtomatik Backup (Ixtiyoriy)

```bash
# Backup script yaratish
sudo nano /opt/fath-bot/backup.sh
```

Kontent:
```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/fath-bot"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Config va credentials backup
cp /opt/fath-bot/config.py $BACKUP_DIR/config_$DATE.py
cp /opt/fath-bot/firebase_credentials.json $BACKUP_DIR/firebase_credentials_$DATE.json

# Eski backuplarni o'chirish (7 kundan eski)
find $BACKUP_DIR -type f -mtime +7 -delete
```

```bash
chmod +x /opt/fath-bot/backup.sh

# Crontab ga qo'shish (har kuni ertalab)
crontab -e
# Qo'shing:
0 2 * * * /opt/fath-bot/backup.sh
```

## 16. Foydali Buyruqlar

```bash
# Botni to'xtatish
sudo systemctl stop fath-bot.service

# Botni ishga tushirish
sudo systemctl start fath-bot.service

# Botni qayta ishga tushirish
sudo systemctl restart fath-bot.service

# Botni avtomatik ishga tushirishdan olib tashlash
sudo systemctl disable fath-bot.service

# Botni avtomatik ishga tushirishga qo'shish
sudo systemctl enable fath-bot.service

# Bot holatini ko'rish
sudo systemctl status fath-bot.service
```

## 17. VPS Server Tavsiyalari

- **Minimum RAM:** 512 MB (1 GB tavsiya etiladi)
- **Minimum CPU:** 1 core
- **Disk:** 10 GB (20 GB tavsiya etiladi)
- **OS:** Ubuntu 20.04+ yoki Debian 11+
- **Python:** 3.9+ (3.10+ tavsiya etiladi)

## 18. Tezkor O'rnatish Script

Quyidagi scriptni VPS da ishga tushiring:

```bash
#!/bin/bash
# Quick setup script

# Paketlarni o'rnatish
sudo apt update
sudo apt install python3 python3-pip git screen -y

# Bot papkasini yaratish
sudo mkdir -p /opt/fath-bot
sudo chown $USER:$USER /opt/fath-bot
cd /opt/fath-bot

echo "✅ Paketlar o'rnatildi"
echo "📁 Bot papkasi yaratildi: /opt/fath-bot"
echo ""
echo "Keyingi qadamlar:"
echo "1. Bot kodlarini /opt/fath-bot ga ko'chiring"
echo "2. firebase_credentials.json ni ko'chiring"
echo "3. pip3 install -r requirements.txt"
echo "4. python3 init_firestore.py"
echo "5. python3 main.py"
```

---

**Muvaffaqiyatli deployment! 🚀**

