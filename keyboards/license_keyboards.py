# ============================================
# LITSENZIYA MENYULARI
# ============================================

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_license_plans_keyboard(plans):
    """Tarif tanlash menyusi - Database dan dinamik"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    
    for plan in plans:
        if plan.is_active:
            if plan.price == 0:
                label = f"{plan.name} (BEPUL - Admin beradi)"
            else:
                label = f"{plan.name} ({plan.days} kun, {plan.price:,} so'm)"
            kb.add(KeyboardButton(label))
    
    kb.add(KeyboardButton("❌ Bekor qilish"))
    return kb

def get_confirm_keyboard():
    """Tasdiqlash tugmalari"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.row(
        KeyboardButton("✅ Ha, tasdiqlayman"),
        KeyboardButton("❌ Yo'q, qaytadan kiritaman")
    )
    return kb

def get_terms_keyboard():
    """Shartnoma rozilik tugmalari"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.row(
        KeyboardButton("✅ Roziman"),
        KeyboardButton("❌ Rozi emasman")
    )
    return kb