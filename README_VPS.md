# VPS Serverga Botni Ko'chirish - Qisqa Qo'llanma

## Tezkor Ko'chirish (3 qadam)

### 1. Bot kodlarini VPS ga ko'chirish

**Windows PowerShell dan:**
```powershell
# VPS ga ulanish va bot kodlarini ko'chirish
scp -r C:\Users\user\Desktop\fath_unified_bot\* root@your-vps-ip:/opt/fath-bot/
```

**Yoki WinSCP/FTP client ishlatish**

### 2. Firebase credentials ni ko'chirish

```powershell
scp C:\Users\user\Desktop\fath_unified_bot\firebase_credentials.json root@your-vps-ip:/opt/fath-bot/
```

### 3. VPS da botni ishga tushirish

```bash
# VPS ga ulanish
ssh root@your-vps-ip

# Bot papkasiga o'tish
cd /opt/fath-bot

# Paketlarni o'rnatish
pip3 install -r requirements.txt

# Firestore ni initialize qilish
python3 init_firestore.py

# Systemd service ni o'rnatish
sudo cp systemd/fath-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable fath-bot.service
sudo systemctl start fath-bot.service

# Bot holatini tekshirish
sudo systemctl status fath-bot.service
```

## Yoki Avtomatik Deployment Script

```bash
# VPS da
cd /opt/fath-bot
chmod +x deploy.sh
sudo ./deploy.sh
```

## Muhim Eslatmalar

1. ✅ Bot endi **Firestore** da ishlaydi - VPS da SQLite kerak emas
2. ✅ Barcha ma'lumotlar Firebase da saqlanadi
3. ✅ Bot VPS da ishlamasa ham, ma'lumotlar yo'qolmaydi
4. ✅ Bir nechta VPS dan bir xil botni ishga tushirish mumkin (load balancing)

## Botni Boshqarish

```bash
# Botni ishga tushirish
sudo systemctl start fath-bot.service

# Botni to'xtatish
sudo systemctl stop fath-bot.service

# Botni qayta ishga tushirish
sudo systemctl restart fath-bot.service

# Bot holatini ko'rish
sudo systemctl status fath-bot.service

# Loglarni ko'rish
sudo journalctl -u fath-bot.service -f
```

## Xavfsizlik

```bash
# Firebase credentials ni himoya qilish
chmod 600 /opt/fath-bot/firebase_credentials.json
chown root:root /opt/fath-bot/firebase_credentials.json
```

## Muammolarni Hal Qilish

### Bot ishlamayapti?
```bash
# Loglarni ko'rish
sudo journalctl -u fath-bot.service -n 100

# Firestore ni test qilish
cd /opt/fath-bot
python3 init_firestore.py
```

### Firestore ulanishi yo'q?
```bash
# Credentials faylini tekshirish
ls -la /opt/fath-bot/firebase_credentials.json

# Firestore ni test qilish
python3 init_firestore.py
```

---

**Batafsil qo'llanma:** `VPS_DEPLOYMENT.md` faylida

