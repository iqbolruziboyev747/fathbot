#!/bin/bash
# Bot loglarini ko'rish scripti

echo "Bot loglari (oxirgi 50 qator):"
echo "================================"
sudo journalctl -u fath-bot.service -n 50

echo ""
echo "Real-time loglar uchun: sudo journalctl -u fath-bot.service -f"

