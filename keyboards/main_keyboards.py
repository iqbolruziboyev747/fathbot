# ============================================
# ASOSIY MENYULAR
# ============================================

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu(is_vip=False, vip_until=None):
    """Asosiy menyu - VIP statusiga qarab"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    
    # 📊 TRADING BO'LIMI
    kb.row(
        KeyboardButton("📊 Texnik Tahlil"),
        KeyboardButton("💼 Fundamental Tahlil")
    )
    
    # VIP foydalanuvchilar uchun qo'shimcha
    if is_vip:
        kb.row(
            KeyboardButton("🔍 Pro Tahlil"),
            KeyboardButton("📰 Insider News")
        )
        
        # VIP status ko'rsatish
        if vip_until:
            kb.row(KeyboardButton(f"⭐ VIP: {vip_until.strftime('%Y-%m-%d')} gacha"))
    
    # 💳 LITSENZIYA BO'LIMI
    kb.row(
        KeyboardButton("🎁 Litsenziya olish"),
        KeyboardButton("📜 Mening litsenziyalarim")
    )
    
    # 📈 PREMIUM BO'LIMI
    kb.row(
        KeyboardButton("📈 Premium indikatorlar"),
        KeyboardButton("🤝 Referral")
    )
    
    # ℹ️ INFO BO'LIMI
    kb.row(
        KeyboardButton("🤖 FATH haqida"),
        KeyboardButton("❓ Yordam")
    )
    
    return kb

def get_back_to_menu():
    """Asosiy menyuga qaytish tugmasi"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🔙 Asosiy Menyu"))
    return kb

def get_cancel_keyboard():
    """Bekor qilish tugmasi"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("❌ Bekor qilish"))
    return kb