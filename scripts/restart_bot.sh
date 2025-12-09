#!/bin/bash
# Botni qayta ishga tushirish scripti

sudo systemctl restart fath-bot.service
echo "Bot qayta ishga tushirildi"
sudo systemctl status fath-bot.service

