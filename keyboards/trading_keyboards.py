# ============================================
# TRADING MENYULARI
# ============================================

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_fundamental_keyboard():
    """Fundamental tahlil uchun"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(
        KeyboardButton("₿ Bitcoin (BTC)"),
        KeyboardButton("🥇 Gold (Oltin)")
    )
    kb.add(KeyboardButton("🔙 Asosiy Menyu"))
    return kb

def get_technical_keyboard():
    """Texnik tahlil uchun"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton("📸 Grafik yuklash"),
        KeyboardButton("🔙 Asosiy Menyu")
    )
    return kb

def get_pro_analysis_keyboard():
    """Pro tahlil uchun"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton("📸 3 ta grafik yuklash"),
        KeyboardButton("🔙 Asosiy Menyu")
    )
    return kb

def get_after_analysis_keyboard():
    """Tahlil tugagandan keyin"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(
        KeyboardButton("🔍 Pro Tahlil"),
        KeyboardButton("🔄 Yangi Tahlil")
    )
    kb.add(KeyboardButton("🔙 Asosiy Menyu"))
    return kb