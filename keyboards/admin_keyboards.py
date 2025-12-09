# ============================================
# ADMIN MENYULARI
# ============================================

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_admin_menu():
    """Admin asosiy menyu"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    
    # TRADING ADMIN
    kb.row(
        KeyboardButton("📊 Foydalanuvchilar"),
        KeyboardButton("⭐ VIP boshqaruvi")
    )
    
    kb.row(
        KeyboardButton("💰 Iqtisodiy Ma'lumotlar"),
        KeyboardButton("📰 Insider Yangiliklar")
    )
    
    # LICENSE ADMIN
    kb.row(
        KeyboardButton("➕ Litsenziya qo'shish"),
        KeyboardButton("💵 Tarif narxlari")
    )
    
    kb.row(
        KeyboardButton("🧠 Premium strategiyalar"),
        KeyboardButton("📈 Premium indikatorlar")
    )
    
    # STATISTIKA
    kb.row(
        KeyboardButton("📈 Statistika"),
        KeyboardButton("🔙 Asosiy Menyu")
    )
    
    return kb

def get_vip_management_keyboard():
    """VIP boshqaruvi menyusi"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton("⭐ VIP qo'shish"),
        KeyboardButton("🚫 VIP olib tashlash")
    )
    kb.add(KeyboardButton("🔙 Admin Panel"))
    return kb

def get_economic_data_keyboard():
    """Iqtisodiy ma'lumotlar menyusi"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton("📊 Ko'rsatkichlarni Yangilash"),
        KeyboardButton("📰 Bitcoin Yangiliklari")
    )
    kb.add(
        KeyboardButton("🥇 Oltin Yangiliklari"),
        KeyboardButton("🔙 Admin Panel")
    )
    return kb

def get_pricing_management_keyboard():
    """Tarif narxlari boshqaruvi"""
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✏️ Narxni o'zgartirish", callback_data="edit_pricing"))
    kb.add(InlineKeyboardButton("🔄 Tarifni yoqish/o'chirish", callback_data="toggle_plan"))
    kb.add(InlineKeyboardButton("➕ Yangi tarif qo'shish", callback_data="add_plan"))
    return kb

def get_insider_news_keyboard():
    """Insider yangiliklar menyusi"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton("➕ Yangi Yangilik"),
        KeyboardButton("📋 Barcha Yangiliklar")
    )
    kb.add(
        KeyboardButton("🗑️ Yangilikni o'chirish"),
        KeyboardButton("🔙 Admin Panel")
    )
    return kb

def get_strategy_management_keyboard():
    """Strategiya boshqaruvi"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton("➕ Yangi strategiya qo'shish"),
        KeyboardButton("📜 Strategiyalar ro'yxati")
    )
    kb.add(
        KeyboardButton("🗑 Strategiyani o'chirish"),
        KeyboardButton("🔙 Admin Panel")
    )
    return kb

def get_indicator_management_keyboard():
    """Indikator boshqaruvi"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton("➕ Yangi indikator qo'shish"),
        KeyboardButton("📜 Indikatorlar ro'yxati")
    )
    kb.add(
        KeyboardButton("🗑 Indikatorni o'chirish"),
        KeyboardButton("🔙 Admin Panel")
    )
    return kb