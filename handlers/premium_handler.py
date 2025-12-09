# ============================================
# PREMIUM HANDLER - Premium strategiyalar va indikatorlar
# ============================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import json

import config


def load_json(file):
    """JSON faylni yuklash"""
    if not os.path.exists(file):
        return []
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def get_indicator_menu():
    """Indikatorlar menyusi"""
    indicators = load_json(config.INDICATORS_FILE)
    
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    
    if not indicators:
        kb.add(KeyboardButton("🔙 Asosiy Menyu"))
        return kb
    
    row = []
    for i, ind in enumerate(indicators, start=1):
        row.append(KeyboardButton(ind.get("name", f"Indicator {i}")))
        if i % 2 == 0:
            kb.row(*row)
            row = []
    
    if row:
        kb.row(*row)
    
    kb.row(KeyboardButton("🔙 Asosiy Menyu"))
    return kb


def get_strategy_menu():
    """Strategiyalar menyusi"""
    strategies = load_json(config.STRATEGIES_FILE)
    
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    
    if not strategies:
        kb.add(KeyboardButton("🔙 Asosiy Menyu"))
        return kb
    
    row = []
    for i, strat in enumerate(strategies, start=1):
        row.append(KeyboardButton(strat.get("name", f"Strategy {i}")))
        if i % 2 == 0:
            kb.row(*row)
            row = []
    
    if row:
        kb.row(*row)
    
    kb.row(KeyboardButton("🔙 Asosiy Menyu"))
    return kb


async def handle_premium_indicators(message: types.Message):
    """Premium indikatorlar tugmasi - FAQAT USER UCHUN"""
    user_id = message.from_user.id
    
    # Admin bo'lsa, admin_handler ishlatadi
    # Shu sababli bu yerda admin tekshiruvni OLIB TASHLAYMIZ
    
    indicators = load_json(config.INDICATORS_FILE)
    
    if not indicators:
        await message.answer(
            "⚠️ Hozircha premium indikatorlar mavjud emas.\n\n"
            "Tez orada qo'shiladi!"
        )
        return
    
    await message.answer(
        "📈 *PREMIUM INDIKATORLAR*\n\n"
        "Quyidagi indikatorlardan birini tanlang:",
        parse_mode="Markdown",
        reply_markup=get_indicator_menu()
    )


async def handle_premium_strategies(message: types.Message):
    """Premium strategiyalar tugmasi - FAQAT USER UCHUN"""
    user_id = message.from_user.id
    
    # Admin tekshiruvni OLIB TASHLAYMIZ
    
    strategies = load_json(config.STRATEGIES_FILE)
    
    if not strategies:
        await message.answer(
            "⚠️ Hozircha premium strategiyalar mavjud emas.\n\n"
            "Tez orada qo'shiladi!"
        )
        return
    
    await message.answer(
        "🧠 *PREMIUM STRATEGIYALAR*\n\n"
        "Quyidagi strategiyalardan birini tanlang:",
        parse_mode="Markdown",
        reply_markup=get_strategy_menu()
    )

async def handle_indicator_selection(message: types.Message):
    """Indikator tanlash"""
    if "🔙 Asosiy Menyu" in message.text:
        return
    
    name = message.text.strip()
    indicators = load_json(config.INDICATORS_FILE)
    
    selected = None
    for ind in indicators:
        if ind.get("name", "").lower() == name.lower():
            selected = ind
            break
    
    if not selected:
        await message.answer("⚠️ Indikator topilmadi.")
        return
    
    caption = f"📈 *{selected.get('name')}*\n\n{selected.get('caption', '')}"
    
    # Rasmni yuborish
    image = selected.get("image")
    if image:
        try:
            await message.answer_photo(
                photo=image,
                caption=caption,
                parse_mode="Markdown"
            )
        except:
            await message.answer(caption, parse_mode="Markdown")
    
    # Faylni yuborish
    file_id = selected.get("file_id") or selected.get("file")
    file_name = selected.get("file_name", "indicator.ex5")
    
    if file_id:
        try:
            if os.path.exists(file_id):
                with open(file_id, "rb") as f:
                    await message.answer_document(
                        document=f,
                        caption=f"📦 {file_name}"
                    )
            else:
                await message.answer_document(
                    document=file_id,
                    caption=f"📦 {file_name}"
                )
        except Exception as e:
            await message.answer(f"⚠️ Faylni yuborishda xatolik: {e}")
    else:
        await message.answer("ℹ️ Indikator fayli mavjud emas.")


async def handle_strategy_selection(message: types.Message):
    """Strategiya tanlash"""
    if "🔙 Asosiy Menyu" in message.text:
        return
    
    name = message.text.strip()
    strategies = load_json(config.STRATEGIES_FILE)
    
    selected = None
    for strat in strategies:
        if strat.get("name", "").lower() == name.lower():
            selected = strat
            break
    
    if not selected:
        await message.answer("⚠️ Strategiya topilmadi.")
        return
    
    caption = f"🧠 *{selected.get('name')}*\n\n{selected.get('caption', '')}"
    
    # Rasmni yuborish
    image = selected.get("image")
    if image:
        try:
            await message.answer_photo(
                photo=image,
                caption=caption,
                parse_mode="Markdown"
            )
        except:
            await message.answer(caption, parse_mode="Markdown")
    
    # Videoni yuborish
    video = selected.get("video")
    if video:
        try:
            await message.answer_video(
                video=video,
                caption="🎥 Strategiya video qo'llanma"
            )
        except Exception as e:
            await message.answer(f"⚠️ Videoni yuborishda xatolik: {e}")


def register_premium_handlers(dp: Dispatcher):
    """Premium handlerlarni ro'yxatdan o'tkazish"""
    
    # User uchun (priority = PAST, chunki admin birinchi tekshiriladi)
    dp.register_message_handler(
        handle_premium_indicators,
        lambda m: m.text == "📈 Premium indikatorlar",
        state="*"
    )
    
    dp.register_message_handler(
        handle_premium_strategies,
        lambda m: m.text == "🧠 Premium strategiyalar",
        state="*"
    )
    
    # Tanlash (pastroq prioritet)
    # Bu handlerlar faqat indicator/strategy menu ochilgandan keyin ishlaydi
    # Biz buni state bilan boshqarmaymiz, chunki oddiy