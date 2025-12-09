# ============================================
# ADMIN HANDLER - Admin panel
# ============================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import config
from keyboards import (
    get_admin_menu,
    get_vip_management_keyboard,
    get_economic_data_keyboard,
    get_insider_news_keyboard,
    get_main_menu
)
from services.database_service import trading_db, license_db


# FSM States
class AdminStates(StatesGroup):
    # VIP boshqaruvi
    waiting_vip_add_id = State()
    waiting_vip_remove_id = State()
    
    # Iqtisodiy ma'lumotlar
    waiting_indicators = State()
    waiting_btc_news = State()
    waiting_gold_news = State()
    
    # Insider yangiliklar
    waiting_news_data = State()
    waiting_news_delete = State()
    
    # Tarif narxlari
    waiting_new_price = State()
    
    # Litsenziya qo'shish
    waiting_license_account = State()
    waiting_telegram_id = State()     
    waiting_license_days = State()

    # Premium strategiyalar
    waiting_strategy_name = State()
    waiting_strategy_caption = State()
    waiting_strategy_image = State()
    waiting_strategy_video = State()
    waiting_strategy_delete = State()
    
    # Premium indikatorlar
    waiting_indicator_name = State()
    waiting_indicator_caption = State()
    waiting_indicator_image = State()
    waiting_indicator_file = State()
    waiting_indicator_delete = State()



def is_admin(user_id):
    """Admin tekshirish"""
    return user_id in config.ADMINS


import json

def load_strategies():
    """Strategiyalarni yuklash"""
    import config
    if not os.path.exists(config.STRATEGIES_FILE):
        return []
    try:
        with open(config.STRATEGIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_strategies(data):
    """Strategiyalarni saqlash"""
    import config
    with open(config.STRATEGIES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_indicators():
    """Indikatorlarni yuklash"""
    import config
    if not os.path.exists(config.INDICATORS_FILE):
        return []
    try:
        with open(config.INDICATORS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_indicators(data):
    """Indikatorlarni saqlash"""
    import config
    with open(config.INDICATORS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ==================== STRATEGIYALAR BOSHQARUVI ====================

async def handle_add_strategy(message: types.Message):
    """Yangi strategiya qo'shish"""
    if not is_admin(message.from_user.id):
        return
    
    await message.answer("📝 Strategiya nomini kiriting:")
    await AdminStates.waiting_strategy_name.set()


async def process_strategy_name(message: types.Message, state: FSMContext):
    """Strategiya nomini qabul qilish"""
    await state.update_data(name=message.text.strip())
    await message.answer("✏️ Strategiya tavsif matnini kiriting:")
    await AdminStates.waiting_strategy_caption.set()


async def process_strategy_caption(message: types.Message, state: FSMContext):
    """Strategiya tavsifini qabul qilish"""
    await state.update_data(caption=message.text.strip())
    await message.answer("📷 Endi strategiya rasmini yuboring:")
    await AdminStates.waiting_strategy_image.set()


async def process_strategy_image(message: types.Message, state: FSMContext):
    """Strategiya rasmini qabul qilish"""
    if not message.photo:
        await message.answer("❌ Iltimos, rasm yuboring!")
        return
    
    file_id = message.photo[-1].file_id
    await state.update_data(image=file_id)
    await message.answer("🎥 Endi strategiya videosini yuboring:")
    await AdminStates.waiting_strategy_video.set()


async def process_strategy_video(message: types.Message, state: FSMContext):
    """Strategiya videosini qabul qilish"""
    if not message.video:
        await message.answer("❌ Iltimos, video yuboring!")
        return
    
    data = await state.get_data()
    video_id = message.video.file_id
    
    strategy = {
        "name": data["name"],
        "caption": data["caption"],
        "image": data["image"],
        "video": video_id
    }
    
    strategies = load_strategies()
    strategies.append(strategy)
    save_strategies(strategies)
    
    await message.answer(
        f"✅ Strategiya '{data['name']}' muvaffaqiyatli qo'shildi!",
        reply_markup=get_admin_menu()
    )
    await state.finish()


async def handle_list_strategies(message: types.Message):
    """Strategiyalar ro'yxati"""
    if not is_admin(message.from_user.id):
        return
    
    strategies = load_strategies()
    
    if not strategies:
        await message.answer("⚠️ Hozircha strategiyalar yo'q.")
        return
    
    text = "📚 *MAVJUD STRATEGIYALAR:*\n\n"
    for i, s in enumerate(strategies, 1):
        text += f"{i}. {s['name']}\n"
    
    await message.answer(text, parse_mode="Markdown")


async def handle_delete_strategy(message: types.Message):
    """Strategiyani o'chirish"""
    if not is_admin(message.from_user.id):
        return
    
    strategies = load_strategies()
    
    if not strategies:
        await message.answer("📭 Hozircha strategiyalar mavjud emas.")
        return
    
    text = "🗑 *Qaysi strategiyani o'chirmoqchisiz?*\n\n"
    for s in strategies:
        text += f"• {s['name']}\n"
    text += "\n❗ Nomini to'liq yozib yuboring:"
    
    await message.answer(text, parse_mode="Markdown")
    await AdminStates.waiting_strategy_delete.set()


async def process_strategy_delete(message: types.Message, state: FSMContext):
    """Strategiyani o'chirish"""
    name_to_delete = message.text.strip()
    strategies = load_strategies()
    
    found = False
    for s in strategies:
        if s["name"].lower() == name_to_delete.lower():
            strategies.remove(s)
            save_strategies(strategies)
            await message.answer(
                f"✅ '{s['name']}' strategiyasi o'chirildi!",
                reply_markup=get_admin_menu()
            )
            found = True
            break
    
    if not found:
        await message.answer("❌ Bunday nomli strategiya topilmadi.")
    
    await state.finish()

# ==================== INDIKATORLAR BOSHQARUVI ====================

async def handle_add_indicator(message: types.Message):
    """Yangi indikator qo'shish"""
    if not is_admin(message.from_user.id):
        return
    
    await message.answer("🧾 Indikator nomini kiriting:")
    await AdminStates.waiting_indicator_name.set()


async def process_indicator_name(message: types.Message, state: FSMContext):
    """Indikator nomini qabul qilish"""
    await state.update_data(name=message.text.strip())
    await message.answer("✏️ Indikator tavsif matnini kiriting:")
    await AdminStates.waiting_indicator_caption.set()


async def process_indicator_caption(message: types.Message, state: FSMContext):
    """Indikator tavsifini qabul qilish"""
    await state.update_data(caption=message.text.strip())
    await message.answer("📸 Endi indikator rasmini yuboring:")
    await AdminStates.waiting_indicator_image.set()


async def process_indicator_image(message: types.Message, state: FSMContext):
    """Indikator rasmini qabul qilish"""
    if not message.photo:
        await message.answer("❌ Iltimos, rasm yuboring!")
        return
    
    file_id = message.photo[-1].file_id
    await state.update_data(image=file_id)
    await message.answer("📁 Endi indikator faylini yuboring (.ex4 yoki .ex5):")
    await AdminStates.waiting_indicator_file.set()


async def process_indicator_file(message: types.Message, state: FSMContext):
    """Indikator faylini qabul qilish"""
    if not message.document:
        await message.answer("❌ Iltimos, fayl yuboring!")
        return
    
    file = message.document
    allowed_ext = (".ex4", ".ex5", ".zip")
    
    if not any(file.file_name.endswith(ext) for ext in allowed_ext):
        await message.answer("❌ Faqat .ex4, .ex5 yoki .zip fayl yuboring.")
        return
    
    data = await state.get_data()
    
    indicator = {
        "name": data["name"],
        "caption": data["caption"],
        "image": data["image"],
        "file_id": file.file_id,
        "file_name": file.file_name
    }
    
    indicators = load_indicators()
    indicators.append(indicator)
    save_indicators(indicators)
    
    await message.answer(
        f"✅ '{data['name']}' indikatori muvaffaqiyatli qo'shildi!\n"
        f"📦 Fayl turi: {file.file_name.split('.')[-1].upper()}",
        reply_markup=get_admin_menu()
    )
    await state.finish()


async def handle_list_indicators(message: types.Message):
    """Indikatorlar ro'yxati"""
    if not is_admin(message.from_user.id):
        return
    
    indicators = load_indicators()
    
    if not indicators:
        await message.answer("⚠️ Hozircha indikatorlar yo'q.")
        return
    
    text = "📈 *MAVJUD INDIKATORLAR:*\n\n"
    for i, s in enumerate(indicators, 1):
        text += f"{i}. {s['name']}\n"
    
    await message.answer(text, parse_mode="Markdown")


async def handle_delete_indicator(message: types.Message):
    """Indikatorni o'chirish"""
    if not is_admin(message.from_user.id):
        return
    
    indicators = load_indicators()
    
    if not indicators:
        await message.answer("📭 Hozircha indikatorlar mavjud emas.")
        return
    
    text = "🗑 *Qaysi indikatorni o'chirmoqchisiz?*\n\n"
    for s in indicators:
        text += f"• {s['name']}\n"
    text += "\n❗ Nomini to'liq yozib yuboring:"
    
    await message.answer(text, parse_mode="Markdown")
    await AdminStates.waiting_indicator_delete.set()


async def process_indicator_delete(message: types.Message, state: FSMContext):
    """Indikatorni o'chirish"""
    name_to_delete = message.text.strip()
    indicators = load_indicators()
    
    found = False
    for s in indicators:
        if s["name"].lower() == name_to_delete.lower():
            indicators.remove(s)
            save_indicators(indicators)
            await message.answer(
                f"✅ '{s['name']}' indikatori o'chirildi!",
                reply_markup=get_admin_menu()
            )
            found = True
            break
    
    if not found:
        await message.answer("❌ Bunday nomli indikator topilmadi.")
    
    await state.finish()




# ==================== STATISTIKA ====================

async def handle_statistics(message: types.Message):
    """Statistika"""
    if not is_admin(message.from_user.id):
        return
    
    users = trading_db.get_all_users()
    total_users = len(users)
    vip_users = len([u for u in users if u.is_vip])
    
    from datetime import datetime
    active_vip = len([u for u in users if u.is_vip and u.vip_until and u.vip_until > datetime.now()])
    
    blocked_users = len([u for u in users if u.request_count >= config.FREE_REQUEST_LIMIT and not u.is_vip])
    total_requests = sum([u.request_count for u in users])
    
    # License statistika
    all_licenses = []
    for user in users:
        user_licenses = license_db.get_all_licenses(user.user_id)
        all_licenses.extend(user_licenses)
    
    total_licenses = len(all_licenses)
    active_licenses = len([l for l in all_licenses if not l.revoked and l.valid_until > datetime.now()])
    
    response = (
        "📊 *STATISTIKA*\n\n"
        "👥 *Foydalanuvchilar:*\n"
        f"• Jami: {total_users}\n"
        f"• VIP: {vip_users} ({active_vip} faol)\n"
        f"• Oddiy: {total_users - vip_users}\n"
        f"• Limit tugagan: {blocked_users}\n\n"
        "📜 *Litsenziyalar:*\n"
        f"• Jami: {total_licenses}\n"
        f"• Faol: {active_licenses}\n\n"
        "📊 *So'rovlar:*\n"
        f"• Umumiy: {total_requests}\n"
    )
    
    await message.answer(response, parse_mode="Markdown")


async def handle_users_list(message: types.Message):
    """Foydalanuvchilar ro'yxati"""
    if not is_admin(message.from_user.id):
        return
    
    users = trading_db.get_all_users()
    
    response = "👥 FOYDALANUVCHILAR (birinchi 15 ta):\n\n"
    
    for i, user in enumerate(users[:15], 1):
        vip_status = "⭐ VIP" if user.is_vip else "👤 Oddiy"
        status = "✅ Faol" if user.request_count < config.FREE_REQUEST_LIMIT or user.is_vip else "❌ Limit tugagan"
        
        # Username ni escape qilish (Markdown uchun)
        username = user.username if user.username else "username_yoq"
        first_name = user.first_name if user.first_name else "Ism_yoq"
        
        response += f"{i}. {first_name} (@{username})\n"
        response += f"   {vip_status} | {status}\n"
        response += f"   So'rovlar: {user.request_count}/{config.FREE_REQUEST_LIMIT}\n"
        response += f"   ID: {user.user_id}\n\n"
    
    # Markdown ni o'chirish
    await message.answer(response)


# ==================== VIP BOSHQARUVI ====================

async def handle_vip_management(message: types.Message):
    """VIP boshqaruvi menyusi"""
    if not is_admin(message.from_user.id):
        return
    
    await message.answer(
        "⭐ *VIP BOSHQARUVI*\n\n"
        "Tanlang:",
        parse_mode="Markdown",
        reply_markup=get_vip_management_keyboard()
    )


async def handle_vip_add(message: types.Message):
    """VIP qo'shish"""
    if not is_admin(message.from_user.id):
        return
    
    await message.answer(
        "⭐ *VIP QO'SHISH*\n\n"
        "User ID ni yuboring:",
        parse_mode="Markdown"
    )
    await AdminStates.waiting_vip_add_id.set()


async def process_vip_add(message: types.Message, state: FSMContext):
    """VIP qo'shish - ID qabul qilish"""
    try:
        user_id = int(message.text.strip())
        
        # 1 yillik VIP berish
        from datetime import datetime, timedelta
        vip_until = datetime.now() + timedelta(days=365)
        
        # 1. Trading DB ga yozish
        success = trading_db.set_vip_status(user_id, is_vip=True, vip_until=vip_until)
        
        if success:
            # 2. Request count ni 0 ga qaytarish
            trading_db.reset_request_count(user_id)
            
            # 3. ⭐ License DB ga ham litsenziya qo'shish (MUHIM!)
            try:
                # Agar foydalanuvchi avval litsenziya olgan bo'lsa, yangilaymiz
                # Aks holda yangi litsenziya yaratamiz
                license_db.create_license(
                    user_id=user_id,
                    account_number="ADMIN_VIP",
                    plan_name="VIP_ADMIN",
                    amount=0,
                    duration_days=365
                )
            except Exception as e:
                print(f"⚠️ License yaratishda xatolik: {e}")
                # Bu xatolik bo'lsa ham davom etadi, chunki trading_db da VIP berilgan
            
            await message.answer(
                f"✅ User {user_id} ga VIP status berildi!\n"
                f"📅 Muddat: {vip_until.strftime('%Y-%m-%d')} gacha\n"
                f"🔄 Request count reset qilindi\n"
                f"💾 License DB ga yozildi",
                reply_markup=get_admin_menu()
            )
            
            # User ga xabar yuborish
            try:
                from main import bot
                await bot.send_message(
                    user_id,
                    "🎉 *Tabriklaymiz!*\n\n"
                    "⭐ Sizga VIP status berildi!\n"
                    "📅 Muddat: 1 yil\n\n"
                    "🎁 VIP imkoniyatlari:\n"
                    "• ♾️ Cheksiz tahlillar\n"
                    "• 🔍 Pro Multi-Timeframe tahlil\n"
                    "• 📰 Insider yangiliklar\n\n"
                    "Foydalanish uchun /start ni bosing!",
                    parse_mode="Markdown"
                )
            except:
                pass
        else:
            await message.answer(
                f"❌ User {user_id} topilmadi!",
                reply_markup=get_admin_menu()
            )
        
        await state.finish()
        
    except ValueError:
        await message.answer("❌ Noto'g'ri ID! Faqat raqam kiriting.")


async def handle_vip_remove(message: types.Message):
    """VIP olib tashlash"""
    if not is_admin(message.from_user.id):
        return
    
    await message.answer(
        "🚫 *VIP OLIB TASHLASH*\n\n"
        "User ID ni yuboring:",
        parse_mode="Markdown"
    )
    await AdminStates.waiting_vip_remove_id.set()


async def process_vip_remove(message: types.Message, state: FSMContext):
    """VIP olib tashlash - ID qabul qilish"""
    try:
        user_id = int(message.text.strip())
        
        success = trading_db.set_vip_status(user_id, is_vip=False, vip_until=None)
        
        if success:
            await message.answer(
                f"✅ User {user_id} dan VIP status olib tashlandi!",
                reply_markup=get_admin_menu()
            )
            
            # User ga xabar
            try:
                from main import bot
                await bot.send_message(
                    user_id,
                    "⚠️ *VIP status o'chirildi*\n\n"
                    "Sizning VIP statusingiz admin tomonidan o'chirildi.\n\n"
                    "Yangi litsenziya olish uchun /start ni bosing.",
                    parse_mode="Markdown"
                )
            except:
                pass
        else:
            await message.answer(
                f"❌ User {user_id} topilmadi!",
                reply_markup=get_admin_menu()
            )
        
        await state.finish()
        
    except ValueError:
        await message.answer("❌ Noto'g'ri ID! Faqat raqam kiriting.")


# ==================== IQTISODIY MA'LUMOTLAR ====================

async def handle_economic_data(message: types.Message):
    """Iqtisodiy ma'lumotlar menyusi"""
    if not is_admin(message.from_user.id):
        return
    
    economic_data = trading_db.get_economic_data()
    
    if economic_data:
        response = (
            "💰 *IQTISODIY MA'LUMOTLAR*\n\n"
            "📊 *Ko'rsatkichlar:*\n"
            f"• Inflyatsiya: {economic_data.inflation}\n"
            f"• FED stavka: {economic_data.fed_rate}\n"
            f"• Dollar indeksi: {economic_data.dollar_index}\n"
            f"• Ishsizlik: {economic_data.unemployment}\n"
            f"• YaIM: {economic_data.gdp_growth}\n\n"
            f"🕐 Yangilangan: {economic_data.updated_at}"
        )
    else:
        response = "❌ Iqtisodiy ma'lumotlar topilmadi"
    
    await message.answer(
        response,
        parse_mode="Markdown",
        reply_markup=get_economic_data_keyboard()
    )


async def handle_update_indicators(message: types.Message):
    """Ko'rsatkichlarni yangilash"""
    if not is_admin(message.from_user.id):
        return
    
    await message.answer(
        "📊 *KO'RSATKICHLARNI YANGILASH*\n\n"
        "Quyidagi formatda yuboring (har biri yangi qatorda):\n\n"
        "3.2%\n"
        "5.25-5.5%\n"
        "104.8\n"
        "3.8%\n"
        "2.1%",
        parse_mode="Markdown"
    )
    await AdminStates.waiting_indicators.set()


async def process_indicators(message: types.Message, state: FSMContext):
    """Ko'rsatkichlarni qabul qilish"""
    lines = message.text.strip().split('\n')
    
    if len(lines) >= 5:
        try:
            trading_db.update_economic_data(
                user_id=message.from_user.id,
                inflation=lines[0].strip(),
                fed_rate=lines[1].strip(),
                dollar_index=lines[2].strip(),
                unemployment=lines[3].strip(),
                gdp_growth=lines[4].strip()
            )
            
            await message.answer(
                "✅ Ko'rsatkichlar muvaffaqiyatli yangilandi!",
                reply_markup=get_economic_data_keyboard()
            )
        except Exception as e:
            await message.answer(f"❌ Xatolik: {str(e)}")
    else:
        await message.answer("❌ Noto'g'ri format! Iltimos, 5 ta qiymat yuboring.")
    
    await state.finish()


# ==================== INSIDER YANGILIKLAR ====================

async def handle_insider_news_menu(message: types.Message):
    """Insider yangiliklar menyusi"""
    if not is_admin(message.from_user.id):
        return
    
    await message.answer(
        "📰 *INSIDER YANGILIKLAR BOSHQARUVI*\n\n"
        "Tanlang:",
        parse_mode="Markdown",
        reply_markup=get_insider_news_keyboard()
    )


async def handle_add_insider_news(message: types.Message):
    """Yangi insider yangilik qo'shish"""
    if not is_admin(message.from_user.id):
        return
    
    await message.answer(
        "📰 *YANGI INSIDER YANGILIK*\n\n"
        "Quyidagi formatda yuboring (har biri yangi qatorda):\n\n"
        "2024-12-25\n"
        "FED foiz stavkasi qarori\n"
        "Stavka 5.25% da saqlanadi\n"
        "95%",
        parse_mode="Markdown"
    )
    await AdminStates.waiting_news_data.set()


async def process_news_data(message: types.Message, state: FSMContext):
    """Insider yangilik ma'lumotlarini qabul qilish"""
    lines = message.text.strip().split('\n')
    
    if len(lines) >= 4:
        try:
            success = trading_db.add_insider_news(
                user_id=message.from_user.id,
                news_date=lines[0].strip(),
                news_name=lines[1].strip(),
                news_result=lines[2].strip(),
                accuracy=lines[3].strip()
            )
            
            if success:
                await message.answer(
                    "✅ Insider yangilik qo'shildi!",
                    reply_markup=get_insider_news_keyboard()
                )
            else:
                await message.answer("❌ Xatolik yuz berdi!")
        except Exception as e:
            await message.answer(f"❌ Xatolik: {str(e)}")
    else:
        await message.answer("❌ Noto'g'ri format!")
    
    await state.finish()


async def handle_all_insider_news(message: types.Message):
    """Barcha insider yangiliklarni ko'rish"""
    if not is_admin(message.from_user.id):
        return
    
    news_items = trading_db.get_all_insider_news()
    
    if not news_items:
        await message.answer("📰 Hozircha yangiliklar yo'q.")
        return
    
    response = "📰 *BARCHA INSIDER YANGILIKLAR*\n\n"
    
    for news in news_items[:10]:
        response += f"🆔 ID: {news.id}\n"
        response += f"📅 {news.news_date}\n"
        response += f"📋 {news.news_name}\n"
        response += f"📊 {news.news_result}\n"
        response += f"🎯 {news.accuracy}\n"
        response += "─" * 30 + "\n\n"
    
    await message.answer(response, parse_mode="Markdown")


async def handle_delete_insider_news(message: types.Message):
    """Insider yangilikni o'chirish"""
    if not is_admin(message.from_user.id):
        return
    
    await message.answer("🗑️ O'chirish uchun yangilik ID sini yuboring:")
    await AdminStates.waiting_news_delete.set()


async def process_news_delete(message: types.Message, state: FSMContext):
    """Yangilikni o'chirish"""
    try:
        news_id = int(message.text.strip())
        
        success = trading_db.delete_insider_news(news_id)
        
        if success:
            await message.answer(
                f"✅ Yangilik (ID: {news_id}) o'chirildi!",
                reply_markup=get_insider_news_keyboard()
            )
        else:
            await message.answer("❌ Yangilik topilmadi!")
        
        await state.finish()
        
    except ValueError:
        await message.answer("❌ Noto'g'ri ID!")


# ==================== TARIF NARXLARI ====================

async def handle_pricing_menu(message: types.Message):
    """Tarif narxlari menyusi"""
    if not is_admin(message.from_user.id):
        return
    
    plans = license_db.get_all_pricing_plans()
    
    response = "💵 *TARIF NARXLARI*\n\n"
    
    for plan in plans:
        status = "✅" if plan.is_active else "❌"
        price_text = "BEPUL" if plan.price == 0 else f"{plan.price:,} so'm"
        
        response += f"{status} *{plan.name}* ({plan.days} kun)\n"
        response += f"   💵 Narx: {price_text}\n"
        response += f"   🔑 Kod: `{plan.plan_code}`\n\n"
    
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✏️ Narxni o'zgartirish", callback_data="edit_pricing"))
    kb.add(InlineKeyboardButton("🔄 Yoqish/O'chirish", callback_data="toggle_plan"))
    
    await message.answer(response, parse_mode="Markdown", reply_markup=kb)


# ==================== LITSENZIYA QO'SHISH ====================

async def handle_add_license(message: types.Message):
    """Admin tomonidan litsenziya qo'shish"""
    if not is_admin(message.from_user.id):
        return
    
    await message.answer("📢 Hisob raqamini yuboring:")
    await AdminStates.waiting_license_account.set()


async def process_license_account(message: types.Message, state: FSMContext):
    """Litsenziya uchun account qabul qilish"""
    account = message.text.strip()
    
    if not account.isdigit():
        await message.answer("❌ Noto'g'ri raqam!")
        return
    
    await state.update_data(account=account)
    await message.answer(
        "👤 *Foydalanuvchi Telegram ID sini kiriting:*\n\n"
        "Agar ID noma'lum bo'lsa, 0 yozing yoki o'tkazib yuboring.",
        parse_mode="Markdown"
    )
    await AdminStates.waiting_telegram_id.set()  # Yangi state qo'shamiz


async def process_telegram_id(message: types.Message, state: FSMContext):
    """Telegram ID ni qabul qilish"""
    telegram_id = message.text.strip()
    
    # Agar 0 yoki bo'sh bo'lsa, None qilamiz
    if telegram_id in ['0', '']:
        telegram_id = None
    else:
        try:
            telegram_id = int(telegram_id)
        except ValueError:
            await message.answer("❌ Noto'g'ri ID! Faqat raqam kiriting yoki 0 ni bosing.")
            return
    
    await state.update_data(telegram_id=telegram_id)
    await message.answer("📅 Necha kunlik litsenziya? (7, 30, 90, 180, 365, 1095)")
    await AdminStates.waiting_license_days.set()


async def process_license_days(message: types.Message, state: FSMContext):
    """Litsenziya muddatini qabul qilish"""
    try:
        days = int(message.text.strip())
        data = await state.get_data()
        account = data['account']
        telegram_id = data.get('telegram_id')  # None bo'lishi mumkin
        
        # Tarifni aniqlash
        plan_code = "trial" if days == 7 else f"{days}d"
        
        license_obj, error = license_db.create_license(
            account_number=account,
            telegram_id=telegram_id,  # Endi Telegram ID ham yoziladi
            plan_code=plan_code,
            days=days,
            is_trial=(days == 7)
        )
        
        if error:
            await message.answer(f"❌ Xato: {error}")
        else:
            # Xabarni tayyorlash
            response = (
                f"✅ Litsenziya yaratildi!\n\n"
                f"🔑 Token: `{license_obj.token}`\n"
                f"💳 Account: {account}\n"
                f"📅 Muddat: {days} kun\n"
            )
            
            # Agar Telegram ID bo'lsa, qo'shamiz
            if telegram_id:
                response += f"👤 Telegram ID: {telegram_id}"
            else:
                response += "👤 Telegram ID: ❌ Yo'q (admin tomonidan yaratildi)"
            
            await message.answer(
                response,
                parse_mode="Markdown",
                reply_markup=get_admin_menu()
            )
        
        await state.finish()
        
    except ValueError:
        await message.answer("❌ Faqat raqam kiriting!")

def register_admin_handlers(dp: Dispatcher):
    """Admin handlerlarni ro'yxatdan o'tkazish"""


    # Premium strategiyalar (ADMIN UCHUN)
    dp.register_message_handler(
        handle_premium_strategies_menu,
        lambda m: m.text == "🧠 Premium strategiyalar" and is_admin(m.from_user.id),
        state="*"
    )
    
    # Premium indikatorlar (ADMIN UCHUN)
    dp.register_message_handler(
        handle_premium_indicators_menu,
        lambda m: m.text == "📈 Premium indikatorlar" and is_admin(m.from_user.id),
        state="*"
    )

    
    # Statistika
    dp.register_message_handler(
        handle_statistics,
        lambda m: m.text == "📈 Statistika" and is_admin(m.from_user.id),
        state="*"
    )
    
    dp.register_message_handler(
        handle_users_list,
        lambda m: m.text == "📊 Foydalanuvchilar" and is_admin(m.from_user.id),
        state="*"
    )
    
    # VIP boshqaruvi
    dp.register_message_handler(
        handle_vip_management,
        lambda m: m.text == "⭐ VIP boshqaruvi" and is_admin(m.from_user.id),
        state="*"
    )
    
    dp.register_message_handler(
        handle_vip_add,
        lambda m: m.text == "⭐ VIP qo'shish" and is_admin(m.from_user.id),
        state="*"
    )
    
    dp.register_message_handler(
        process_vip_add,
        state=AdminStates.waiting_vip_add_id
    )
    
    dp.register_message_handler(
        handle_vip_remove,
        lambda m: m.text == "🚫 VIP olib tashlash" and is_admin(m.from_user.id),
        state="*"
    )
    
    dp.register_message_handler(
        process_vip_remove,
        state=AdminStates.waiting_vip_remove_id
    )
    
    # Iqtisodiy ma'lumotlar
    dp.register_message_handler(
        handle_economic_data,
        lambda m: m.text == "💰 Iqtisodiy Ma'lumotlar" and is_admin(m.from_user.id),
        state="*"
    )
    
    dp.register_message_handler(
        handle_update_indicators,
        lambda m: m.text == "📊 Ko'rsatkichlarni Yangilash" and is_admin(m.from_user.id),
        state="*"
    )
    
    dp.register_message_handler(
        process_indicators,
        state=AdminStates.waiting_indicators
    )
    
    # Insider yangiliklar
    dp.register_message_handler(
        handle_insider_news_menu,
        lambda m: m.text == "📰 Insider Yangiliklar" and is_admin(m.from_user.id),
        state="*"
    )
    
    dp.register_message_handler(
        handle_add_insider_news,
        lambda m: m.text == "➕ Yangi Yangilik" and is_admin(m.from_user.id),
        state="*"
    )
    
    dp.register_message_handler(
        process_news_data,
        state=AdminStates.waiting_news_data
    )
    
    dp.register_message_handler(
        handle_all_insider_news,
        lambda m: m.text == "📋 Barcha Yangiliklar" and is_admin(m.from_user.id),
        state="*"
    )
    
    dp.register_message_handler(
        handle_delete_insider_news,
        lambda m: m.text == "🗑️ Yangilikni o'chirish" and is_admin(m.from_user.id),
        state="*"
    )
    
    dp.register_message_handler(
        process_news_delete,
        state=AdminStates.waiting_news_delete
    )
    
    # Tarif narxlari
    dp.register_message_handler(
        handle_pricing_menu,
        lambda m: m.text == "💵 Tarif narxlari" and is_admin(m.from_user.id),
        state="*"
    )
    
    # Litsenziya qo'shish
    dp.register_message_handler(
        handle_add_license,
        lambda m: m.text == "➕ Litsenziya qo'shish" and is_admin(m.from_user.id),
        state="*"
    )
    
    dp.register_message_handler(
        process_license_account,
        state=AdminStates.waiting_license_account
    )

    dp.register_message_handler(
        process_telegram_id,  # <- YANGI HANDLER
        state=AdminStates.waiting_telegram_id
    )
    
    dp.register_message_handler(
        process_license_days,
        state=AdminStates.waiting_license_days
    )

    # Premium boshqaruvi (Admin uchun)
    dp.register_message_handler(
        handle_premium_strategies_menu,
        lambda m: m.text == "🧠 Premium strategiyalar" and is_admin(m.from_user.id),
        state="*"
    )
    
    dp.register_message_handler(
        handle_premium_indicators_menu,
        lambda m: m.text == "📈 Premium indikatorlar" and is_admin(m.from_user.id),
        state="*"
    )

    # Bitcoin/Oltin yangiliklari
    dp.register_message_handler(
        handle_btc_news,
        lambda m: m.text == "📰 Bitcoin Yangiliklari" and is_admin(m.from_user.id),
        state="*"
    )

    dp.register_message_handler(
        process_btc_news,
        state=AdminStates.waiting_btc_news
    )

    dp.register_message_handler(
        handle_gold_news,
        lambda m: m.text == "🥇 Oltin Yangiliklari" and is_admin(m.from_user.id),
        state="*"
    )

    dp.register_message_handler(
        process_gold_news,
        state=AdminStates.waiting_gold_news
    )

    # Tarif narxlari callback handlers
    dp.register_callback_query_handler(
        callback_edit_pricing,
        lambda c: c.data == "edit_pricing"
    )
    
    dp.register_callback_query_handler(
        callback_toggle_plan,
        lambda c: c.data == "toggle_plan"
    )
    
    dp.register_callback_query_handler(
        callback_edit_plan_price,
        lambda c: c.data.startswith("edit_plan_")
    )
    
    dp.register_callback_query_handler(
        callback_toggle_plan_status,
        lambda c: c.data.startswith("toggle_")
    )
    
    # Yangi narx qabul qilish
    dp.register_message_handler(
        process_new_price,
        state=AdminStates.waiting_new_price
    )

    # 🔙 Orqaga tugmalari
    dp.register_message_handler(
        handle_back_to_admin,
        lambda m: m.text and ("Admin Panel" in m.text or "🔙 Admin" in m.text) and is_admin(m.from_user.id),
        state="*"
    )

    # ==================== STRATEGIYALAR ====================
    dp.register_message_handler(
        handle_add_strategy,
        lambda m: m.text == "➕ Yangi strategiya qo'shish" and is_admin(m.from_user.id),
        state="*"
    )
    
    dp.register_message_handler(
        process_strategy_name,
        state=AdminStates.waiting_strategy_name
    )
    
    dp.register_message_handler(
        process_strategy_caption,
        state=AdminStates.waiting_strategy_caption
    )
    
    dp.register_message_handler(
        process_strategy_image,
        content_types=types.ContentType.PHOTO,
        state=AdminStates.waiting_strategy_image
    )
    
    dp.register_message_handler(
        process_strategy_video,
        content_types=types.ContentType.VIDEO,
        state=AdminStates.waiting_strategy_video
    )
    
    dp.register_message_handler(
        handle_list_strategies,
        lambda m: m.text == "📜 Strategiyalar ro'yxati" and is_admin(m.from_user.id),
        state="*"
    )
    
    dp.register_message_handler(
        handle_delete_strategy,
        lambda m: m.text == "🗑 Strategiyani o'chirish" and is_admin(m.from_user.id),
        state="*"
    )
    
    dp.register_message_handler(
        process_strategy_delete,
        state=AdminStates.waiting_strategy_delete
    )
    
    # ==================== INDIKATORLAR ====================
    dp.register_message_handler(
        handle_add_indicator,
        lambda m: m.text == "➕ Yangi indikator qo'shish" and is_admin(m.from_user.id),
        state="*"
    )
    
    dp.register_message_handler(
        process_indicator_name,
        state=AdminStates.waiting_indicator_name
    )
    
    dp.register_message_handler(
        process_indicator_caption,
        state=AdminStates.waiting_indicator_caption
    )
    
    dp.register_message_handler(
        process_indicator_image,
        content_types=types.ContentType.PHOTO,
        state=AdminStates.waiting_indicator_image
    )
    
    dp.register_message_handler(
        process_indicator_file,
        content_types=types.ContentType.DOCUMENT,
        state=AdminStates.waiting_indicator_file
    )
    
    dp.register_message_handler(
        handle_list_indicators,
        lambda m: m.text == "📜 Indikatorlar ro'yxati" and is_admin(m.from_user.id),
        state="*"
    )
    
    dp.register_message_handler(
        handle_delete_indicator,
        lambda m: m.text == "🗑 Indikatorni o'chirish" and is_admin(m.from_user.id),
        state="*"
    )
    
    dp.register_message_handler(
        process_indicator_delete,
        state=AdminStates.waiting_indicator_delete
    )


async def handle_premium_strategies_menu(message: types.Message):
    """Admin - Premium strategiyalar menyusi"""
    if not is_admin(message.from_user.id):
        return
    
    from keyboards import get_strategy_management_keyboard
    
    await message.answer(
        "🧠 *PREMIUM STRATEGIYALAR BOSHQARUVI*\n\n"
        "Admin rejimi. Strategiyalarni qo'shish/o'chirish:",
        parse_mode="Markdown",
        reply_markup=get_strategy_management_keyboard()
    )


async def handle_premium_indicators_menu(message: types.Message):
    """Admin - Premium indikatorlar menyusi"""
    if not is_admin(message.from_user.id):
        return
    
    from keyboards import get_indicator_management_keyboard
    
    await message.answer(
        "📈 *PREMIUM INDIKATORLAR BOSHQARUVI*\n\n"
        "Admin rejimi. Indikatorlarni qo'shish/o'chirish:",
        parse_mode="Markdown",
        reply_markup=get_indicator_management_keyboard()
    )

async def handle_btc_news(message: types.Message):
    """Bitcoin yangiliklarini yangilash"""
    if not is_admin(message.from_user.id):
        return
    
    await message.answer(
        "📰 *BITCOIN YANGILIKLARINI YANGILASH*\n\n"
        "Har bir yangilikni yangi qatorda yozing (maksimal 3 ta):\n\n"
        "Misol:\n"
        "Bitcoin ETF oqimlari: So'nggi haftada $500M kirim\n"
        "FED raisi bayonoti: Foiz stavkalari barqaror\n"
        "Global regulyator: Kripto qonunchiligi muhokamasi",
        parse_mode="Markdown"
    )
    await AdminStates.waiting_btc_news.set()


async def process_btc_news(message: types.Message, state: FSMContext):
    """Bitcoin yangiliklarini qabul qilish"""
    news_items = [line.strip() for line in message.text.strip().split('\n') if line.strip()]
    
    if news_items:
        # | bilan birlashtirish
        news_text = '|'.join(news_items[:3])
        
        success = trading_db.update_economic_data(
            user_id=message.from_user.id,
            btc_news=news_text
        )
        
        if success:
            await message.answer(
                "✅ Bitcoin yangiliklari yangilandi!",
                reply_markup=get_economic_data_keyboard()
            )
        else:
            await message.answer("❌ Xatolik!")
    else:
        await message.answer("❌ Yangiliklar bo'sh!")
    
    await state.finish()


async def handle_gold_news(message: types.Message):
    """Oltin yangiliklarini yangilash"""
    if not is_admin(message.from_user.id):
        return
    
    await message.answer(
        "🥇 *OLTIN YANGILIKLARINI YANGILASH*\n\n"
        "Har bir yangilikni yangi qatorda yozing (maksimal 3 ta):\n\n"
        "Misol:\n"
        "Oltin narxi: Markaziy banklar zaxira o'sishi\n"
        "Inflyatsiya: So'nggi ma'lumotlar ijobiy\n"
        "Geosiyosiy: Yaqin Sharq vaziyati ta'siri",
        parse_mode="Markdown"
    )
    await AdminStates.waiting_gold_news.set()


async def process_gold_news(message: types.Message, state: FSMContext):
    """Oltin yangiliklarini qabul qilish"""
    news_items = [line.strip() for line in message.text.strip().split('\n') if line.strip()]
    
    if news_items:
        news_text = '|'.join(news_items[:3])
        
        success = trading_db.update_economic_data(
            user_id=message.from_user.id,
            gold_news=news_text
        )
        
        if success:
            await message.answer(
                "✅ Oltin yangiliklari yangilandi!",
                reply_markup=get_economic_data_keyboard()
            )
        else:
            await message.answer("❌ Xatolik!")
    else:
        await message.answer("❌ Yangiliklar bo'sh!")
    
    await state.finish()

async def handle_back_to_admin(message: types.Message):
    """Admin panelga qaytish"""
    if not is_admin(message.from_user.id):
        return
    
    await message.answer(
        "👑 *ADMIN PANEL*",
        parse_mode="Markdown",
        reply_markup=get_admin_menu()
    )

async def callback_edit_pricing(callback_query: types.CallbackQuery):
    """Narxni o'zgartirish callback"""
    if not is_admin(callback_query.from_user.id):
        return
    
    plans = license_db.get_all_pricing_plans()
    
    text = "✏️ *NARXNI O'ZGARTIRISH*\n\n"
    text += "Qaysi tarifni o'zgartirmoqchisiz?\n\n"
    
    kb = types.InlineKeyboardMarkup()
    for plan in plans:
        kb.add(types.InlineKeyboardButton(
            f"{plan.name} - {plan.price:,} so'm",
            callback_data=f"edit_plan_{plan.plan_code}"
        ))
    
    await callback_query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=kb
    )
    await callback_query.answer()


async def callback_toggle_plan(callback_query: types.CallbackQuery):
    """Tarifni yoqish/o'chirish callback"""
    if not is_admin(callback_query.from_user.id):
        return
    
    plans = license_db.get_all_pricing_plans()
    
    text = "🔄 *TARIFNI YOQISH/O'CHIRISH*\n\n"
    
    kb = types.InlineKeyboardMarkup()
    for plan in plans:
        status = "✅" if plan.is_active else "❌"
        kb.add(types.InlineKeyboardButton(
            f"{status} {plan.name}",
            callback_data=f"toggle_{plan.plan_code}"
        ))
    
    await callback_query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=kb
    )
    await callback_query.answer()


async def callback_edit_plan_price(callback_query: types.CallbackQuery, state: FSMContext):
    """Tarifni tanlash va narxni so'rash"""
    if not is_admin(callback_query.from_user.id):
        return
    
    plan_code = callback_query.data.replace("edit_plan_", "")
    plan = license_db.get_plan_by_code(plan_code)
    
    if not plan:
        await callback_query.answer("❌ Tarif topilmadi!")
        return
    
    await state.update_data(editing_plan=plan_code)
    await AdminStates.waiting_new_price.set()
    
    await callback_query.message.answer(
        f"📝 *{plan.name}* uchun yangi narxni kiriting (so'mda):\n\n"
        f"Hozirgi narx: {plan.price:,} so'm",
        parse_mode="Markdown"
    )
    await callback_query.answer()


async def callback_toggle_plan_status(callback_query: types.CallbackQuery):
    """Tarifni yoqish/o'chirish"""
    if not is_admin(callback_query.from_user.id):
        return
    
    plan_code = callback_query.data.replace("toggle_", "")
    
    success, new_status = license_db.toggle_plan_active(plan_code)
    
    if success:
        status_text = "yoqildi ✅" if new_status else "o'chirildi ❌"
        await callback_query.answer(f"Tarif {status_text}!")
        
        # Menyuni qayta yuklash
        await handle_pricing_menu(callback_query.message)
    else:
        await callback_query.answer("❌ Xatolik!")


async def process_new_price(message: types.Message, state: FSMContext):
    """Yangi narxni qabul qilish"""
    try:
        new_price = int(message.text.replace(" ", "").replace(",", ""))
        
        data = await state.get_data()
        plan_code = data["editing_plan"]
        
        success = license_db.update_plan_price(plan_code, new_price)
        
        if success:
            await message.answer(
                f"✅ Narx muvaffaqiyatli o'zgartirildi!\n"
                f"💵 Yangi narx: {new_price:,} so'm",
                reply_markup=get_admin_menu()
            )
        else:
            await message.answer("❌ Xatolik!")
        
        await state.finish()
        
    except ValueError:
        await message.answer("❌ Noto'g'ri format! Faqat raqam kiriting.")