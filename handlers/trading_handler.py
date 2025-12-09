# ============================================
# TRADING HANDLER - Texnik, Fundamental, Pro tahlil
# ============================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import config
from keyboards import (
    get_technical_keyboard, get_fundamental_keyboard,
    get_pro_analysis_keyboard, get_after_analysis_keyboard,
    get_main_menu
)
from services.database_service import trading_db
from services.vip_sync_service import vip_sync
from services.analyzer_service import analyzer
from services.helpers import get_user_attr, get_datetime_from_obj


# FSM States
class TradingStates(StatesGroup):
    waiting_technical_image = State()
    waiting_fundamental_choice = State()
    waiting_pro_images = State()


async def handle_technical_analysis(message: types.Message, state: FSMContext):
    """Texnik tahlil tugmasi bosilganda"""
    user_id = message.from_user.id
    
    # VIP va limit tekshirish
    is_vip, can_use, status_msg = await vip_sync.check_vip_and_notify(user_id)
    
    if not can_use:
        await message.answer(
            f"{status_msg}\n\n"
            f"💳 *VIP bo'lish uchun:*\n"
            f"🎁 Litsenziya sotib oling\n\n"
            f"📞 Admin: {config.ADMIN_USERNAME}",
            parse_mode="Markdown"
        )
        return
    
    await message.answer(
        "📊 *TEXNIK TAHLIL*\n\n"
        "📸 Iltimos, grafik rasmini yuboring...\n\n"
        "ℹ️ *Tavsiya:*\n"
        "• Aniq va sifatli grafik yuboring\n"
        "• Timeframe ko'rinsin\n"
        "• Indikatorlar (agar kerak bo'lsa)\n\n"
        f"📊 {status_msg}",
        parse_mode="Markdown",
        reply_markup=get_technical_keyboard()
    )
    
    await TradingStates.waiting_technical_image.set()


async def handle_technical_image(message: types.Message, state: FSMContext):
    """Texnik tahlil uchun rasm qabul qilish"""
    user_id = message.from_user.id

    # Agar "Asosiy Menyu" bosilsa
    if message.text and "Asosiy Menyu" in message.text:
        await state.finish()
        
        user_id = message.from_user.id
        is_vip, _, _ = await vip_sync.check_vip_and_notify(user_id)
        user = trading_db.get_user(user_id)
        
        await message.answer(
            "🏠 Asosiy menyu",
            reply_markup=get_main_menu(is_vip, get_datetime_from_obj(user, 'vip_until'))
        )
        return
    
    # Rasm tekshirish
    if not message.photo:
        await message.answer("❌ Iltimos, rasm yuboring!")
        return
    
    # Yana bir marta limit tekshirish (xavfsizlik)
    is_vip, can_use, status_msg = await vip_sync.check_vip_and_notify(user_id)
    
    if not can_use:
        await state.finish()
        await message.answer(
            f"{status_msg}\n\n"
            "Yangi tahlil uchun /start ni bosing"
        )
        return
    
    # Rasmni yuklab olish
    try:
        photo = message.photo[-1]
        file = await photo.download(destination_dir=config.ANALYSES_DIR)
        image_path = file.name
        
        # Progress xabari
        progress_msg = await message.answer("🔍 Tahlil boshlandi...")
        
        # AI tahlil
        analysis_result = await analyzer.analyze_price_action(image_path)
        
        # So'rov sonini oshirish (faqat VIP bo'lmasa)
        if not is_vip:
            trading_db.increment_request(user_id)
        
        # Natijani bo'laklab yuborish
        message_parts = analyzer.split_message(analysis_result)
        for i, part in enumerate(message_parts):
            if i == 0:
                await progress_msg.edit_text(part)
            else:
                await message.answer(part)
        
        # Tahlilni saqlash
        trading_db.save_analysis(user_id, "price_action", "chart", analysis_result)
        
        # Yangilangan limit
        user = trading_db.get_user(user_id)
        request_count = get_user_attr(user, 'request_count', 0)
        remaining = max(0, config.FREE_REQUEST_LIMIT - request_count)
        
        if is_vip:
            final_msg = "✅ Tahlil yakunlandi!\n⭐ VIP - cheksiz so'rovlar"
        else:
            final_msg = f"✅ Tahlil yakunlandi!\n📊 Qolgan so'rovlar: {remaining}/{config.FREE_REQUEST_LIMIT}"
        
        await message.answer(
            final_msg,
            reply_markup=get_after_analysis_keyboard()
        )
        
        await state.finish()
        
    except Exception as e:
        await message.answer(f"❌ Xatolik: {str(e)}")
        await state.finish()


async def handle_fundamental_analysis(message: types.Message, state: FSMContext):
    """Fundamental tahlil tugmasi bosilganda"""
    user_id = message.from_user.id
    
    # VIP va limit tekshirish
    is_vip, can_use, status_msg = await vip_sync.check_vip_and_notify(user_id)
    
    if not can_use:
        await message.answer(
            f"{status_msg}\n\n"
            f"💳 *VIP bo'lish uchun:*\n"
            f"🎁 Litsenziya sotib oling\n\n"
            f"📞 Admin: {config.ADMIN_USERNAME}",
            parse_mode="Markdown"
        )
        return
    
    await message.answer(
        "💼 *FUNDAMENTAL TAHLIL*\n\n"
        "Qaysi aktiv uchun tahlil kerak?\n\n"
        f"📊 {status_msg}",
        parse_mode="Markdown",
        reply_markup=get_fundamental_keyboard()
    )
    
    await TradingStates.waiting_fundamental_choice.set()


async def handle_fundamental_choice(message: types.Message, state: FSMContext):
    """Fundamental tahlil uchun aktiv tanlash"""
    user_id = message.from_user.id
    text = message.text
    
    # AVVAL state ni finish qilish kerak!
    if "🔙 Asosiy Menyu" in text or "Asosiy Menyu" in text:
        await state.finish()  # ← State ni to'xtatish
        
        # Keyin menu
        is_vip, _, _ = await vip_sync.check_vip_and_notify(user_id)
        user = trading_db.get_user(user_id)
        
        await message.answer(
            "🏠 Asosiy menyu",
            reply_markup=get_main_menu(is_vip, get_datetime_from_obj(user, 'vip_until'))
        )
        return  # ← Funksiyani to'xtatish
    
    # Symbol aniqlash
    symbol = None
    if "Bitcoin" in text or "BTC" in text:
        symbol = "BTC"
    elif "Gold" in text or "Oltin" in text:
        symbol = "GOLD"
    
    if not symbol:
        await message.answer("❌ Noto'g'ri tanlov! Iltimos, tugmalardan foydalaning.")
        return
    
    # Yana limit tekshirish
    is_vip, can_use, status_msg = await vip_sync.check_vip_and_notify(user_id)
    
    if not can_use:
        await state.finish()
        await message.answer(f"{status_msg}\n\nYangi tahlil uchun /start ni bosing")
        return
    
    # Progress
    progress_msg = await message.answer(f"🔍 {symbol} uchun fundamental tahlil boshlandi...")
    
    try:
        # AI tahlil
        analysis_result = await analyzer.analyze_fundamental(symbol)
        
        # So'rov sonini oshirish (faqat VIP bo'lmasa)
        if not is_vip:
            trading_db.increment_request(user_id)
        
        # Natijani bo'laklab yuborish
        message_parts = analyzer.split_message(analysis_result)
        for i, part in enumerate(message_parts):
            if i == 0:
                await progress_msg.edit_text(part)
            else:
                await message.answer(part)
        
        # Saqlash
        trading_db.save_analysis(user_id, "fundamental", symbol, analysis_result)
        
        # Limit
        user = trading_db.get_user(user_id)
        remaining = max(0, config.FREE_REQUEST_LIMIT - user.request_count)
        
        if is_vip:
            final_msg = "✅ Tahlil yakunlandi!\n⭐ VIP - cheksiz so'rovlar"
        else:
            final_msg = f"✅ Tahlil yakunlandi!\n📊 Qolgan so'rovlar: {remaining}/{config.FREE_REQUEST_LIMIT}"
        
        await message.answer(
            final_msg,
            reply_markup=get_after_analysis_keyboard()
        )
        
        await state.finish()
        
    except Exception as e:
        await message.answer(f"❌ Xatolik: {str(e)}")
        await state.finish()


async def handle_pro_analysis(message: types.Message, state: FSMContext):
    """Pro tahlil tugmasi bosilganda"""
    user_id = message.from_user.id
    
    # VIP tekshirish (Pro faqat VIP uchun!)
    is_vip, can_use, status_msg = await vip_sync.check_vip_and_notify(user_id)
    
    if not is_vip:
        await message.answer(
            "❌ *Pro Tahlil faqat VIP foydalanuvchilar uchun!*\n\n"
            "⭐ Siz hozirda VIP foydalanuvchi emassiz\n\n"
            "💳 *VIP status olish uchun:*\n"
            "🎁 Litsenziya sotib oling\n\n"
            f"📞 Admin: {config.ADMIN_USERNAME}\n\n"
            "📌 *VIP imkoniyatlari:*\n"
            "• 🔍 Pro Multi-Timeframe Tahlil\n"
            "• ♾️ Cheksiz so'rovlar\n"
            "• 📰 Insider yangiliklar\n"
            "• ⚡ Tezkor javoblar",
            parse_mode="Markdown"
        )
        return
    
    await message.answer(
        "🔍 *PRO MULTI-TIMEFRAME TAHLIL*\n\n"
        "📸 Iltimos, HAR XIL TIMEFRAME LARDA olingan *3 TA GRAFIK* rasm yuboring:\n\n"
        "1️⃣ Kichik timeframe (5M, 15M, 30M)\n"
        "2️⃣ O'rta timeframe (1H, 4H)\n"
        "3️⃣ Katta timeframe (1D, 1W)\n\n"
        "Barcha 3 ta rasm yuborilgandan so'ng chuqur tahlil boshlanadi.\n\n"
        "⭐ VIP - cheksiz so'rovlar",
        parse_mode="Markdown",
        reply_markup=get_pro_analysis_keyboard()
    )
    
    await state.update_data(pro_images=[])
    await TradingStates.waiting_pro_images.set()


async def handle_pro_images(message: types.Message, state: FSMContext):
    """Pro tahlil uchun rasmlar qabul qilish"""
    user_id = message.from_user.id
    
    # VIP tekshirish
    is_vip, _, _ = await vip_sync.check_vip_and_notify(user_id)
    if not is_vip:
        await state.finish()
        await message.answer("❌ Pro tahlil faqat VIP uchun!")
        return
    
    try:
        # Rasmni yuklab olish
        photo = message.photo[-1]
        file = await photo.download(destination_dir=config.PRO_ANALYSES_DIR)
        image_path = file.name
        
        # Ro'yxatga qo'shish
        data = await state.get_data()
        pro_images = data.get('pro_images', [])
        pro_images.append(image_path)
        
        images_count = len(pro_images)
        
        if images_count == 1:
            await message.answer("✅ 1-rasm qabul qilindi.\n📸 2-rasmni yuboring...")
            await state.update_data(pro_images=pro_images)
            
        elif images_count == 2:
            await message.answer("✅ 2-rasm qabul qilindi.\n📸 3-rasmni yuboring...")
            await state.update_data(pro_images=pro_images)
            
        elif images_count >= 3:
            await message.answer("✅ Barcha 3 ta rasm qabul qilindi!\n🔍 Pro tahlil boshlandi...")
            
            # Pro tahlil
            analysis_result = await analyzer.analyze_pro_multi_timeframe(pro_images)
            
            # Natijani bo'laklab yuborish
            message_parts = analyzer.split_message(analysis_result)
            for part in message_parts:
                await message.answer(part)
            
            # Saqlash
            trading_db.save_analysis(user_id, "pro_multi_timeframe", "multiple_charts", analysis_result)
            
            await message.answer(
                "✅ Pro tahlil yakunlandi!\n⭐ VIP - cheksiz so'rovlar",
                reply_markup=get_after_analysis_keyboard()
            )
            
            await state.finish()
            
    except Exception as e:
        await message.answer(f"❌ Xatolik: {str(e)}")
        await state.finish()


async def handle_insider_news(message: types.Message):
    """Insider yangiliklar (VIP uchun)"""
    user_id = message.from_user.id
    
    # VIP tekshirish
    is_vip, _, _ = await vip_sync.check_vip_and_notify(user_id)
    
    if not is_vip:
        await message.answer(
            "❌ *Insider Yangiliklar faqat VIP uchun!*\n\n"
            f"💳 VIP bo'lish: {config.ADMIN_USERNAME}",
            parse_mode="Markdown"
        )
        return
    
    # Insider yangiliklarni olish
    news_items = trading_db.get_current_insider_news()
    
    if not news_items:
        await message.answer(
            "📰 *INSIDER YANGILIKLAR*\n\n"
            "🤷 Hozircha yangiliklar mavjud emas.\n\n"
            "Tez orada yangi yangiliklar qo'shiladi.",
            parse_mode="Markdown"
        )
        return
    
    response = "📰 *INSIDER YANGILIKLAR*\n\n"
    response += "🕐 *Kelajakdagi voqealar:*\n\n"
    
    for news in news_items:
        response += f"📅 *Sana:* {news.news_date}\n"
        response += f"📋 *Nomi:* {news.news_name}\n"
        response += f"📊 *Natija:* {news.news_result}\n"
        response += f"🎯 *Aniqlik:* {news.accuracy}\n"
        response += "─" * 30 + "\n\n"
    
    await message.answer(response, parse_mode="Markdown")


def register_trading_handlers(dp: Dispatcher):
    """Trading handlerlarni ro'yxatdan o'tkazish"""
    
    # Tugmalar
    dp.register_message_handler(
        handle_technical_analysis,
        lambda m: m.text == "📊 Texnik Tahlil",
        state="*"
    )
    
    dp.register_message_handler(
        handle_fundamental_analysis,
        lambda m: m.text == "💼 Fundamental Tahlil",
        state="*"
    )
    
    dp.register_message_handler(
        handle_pro_analysis,
        lambda m: m.text == "🔍 Pro Tahlil",
        state="*"
    )
    
    dp.register_message_handler(
        handle_insider_news,
        lambda m: m.text == "📰 Insider News",
        state="*"
    )
    
    # FSM States
    dp.register_message_handler(
        handle_technical_image,
        content_types=types.ContentType.PHOTO,
        state=TradingStates.waiting_technical_image
    )
    
    dp.register_message_handler(
        handle_fundamental_choice,
        state=TradingStates.waiting_fundamental_choice
    )
    
    dp.register_message_handler(
        handle_pro_images,
        content_types=types.ContentType.PHOTO,
        state=TradingStates.waiting_pro_images
    )