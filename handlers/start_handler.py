# ============================================
# START HANDLER - /start va asosiy menyu
# ============================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import types
from aiogram.dispatcher import Dispatcher

import config
from keyboards import get_main_menu
from services.database_service import trading_db
from services.vip_sync_service import vip_sync
from services.referral_service import referral_service
from services.helpers import get_user_attr, get_datetime_from_obj


async def cmd_start(message: types.Message):
    """
    /start buyrug'i
    - Referral kodini tekshirish
    - Foydalanuvchini yaratish
    - VIP statusni sinxronlashtirish
    """
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    # Foydalanuvchini yaratish/yangilash
    trading_db.create_or_update_user(user_id, username, first_name)
    
    # Referral kodni tekshirish
    text_parts = message.text.split(maxsplit=1)
    args = text_parts[1] if len(text_parts) > 1 else ""
    
    if args and args.startswith("ref"):
        try:
            referrer_id = referral_service.get_referrer_from_code(args)
            if referrer_id and referrer_id != user_id:
                success, msg = referral_service.add_referral(referrer_id, user_id)
                if success:
                    # Referrer ga xabar yuborish
                    try:
                        from main import bot
                        ref_count = referral_service.get_referral_count(referrer_id)
                        await bot.send_message(
                            referrer_id,
                            f"🎉 Siz yangi foydalanuvchini taklif qildingiz!\n"
                            f"👤 UserID: {user_id}\n"
                            f"📢 Jami referrals: {ref_count}\n"
                            f"💰 Sizning chegirmangiz: {ref_count * 2}%"
                        )
                    except:
                        pass
        except Exception as e:
            print(f"Referral xatosi: {e}")
    
    # VIP statusni sinxronlashtirish
    is_vip, can_use, status_msg = await vip_sync.check_vip_and_notify(user_id)
    
    # User ma'lumotlarini olish
    user = trading_db.get_user(user_id)
    
    # Welcome xabari
    welcome_text = (
        "👋 *Assalomu alaykum!* va xush kelibsiz!\n\n"
        "🤖 Bu bot orqali siz *FATH savdo robotini* ishga tushirishingiz, "
        "o'z hisobingizga *avtomatik treyding*ni qo'shishingiz va "
        "*barqaror passiv daromad* olish imkoniga ega bo'lasiz.\n\n"
    )
    
    if is_vip:
        welcome_text += f"⭐ *Sizning statusingiz:* VIP\n"
        vip_until = get_datetime_from_obj(user, 'vip_until')
        if vip_until:
            welcome_text += f"📅 *Muddat:* {vip_until.strftime('%Y-%m-%d')} gacha\n\n"
        welcome_text += (
            "🎁 *VIP imkoniyatlari:*\n"
            " • ♾️ Cheksiz tahlil so'rovlari\n"
            " • 🔍 Pro Multi-Timeframe tahlil\n"
            " • 📰 Eksklyuziv Insider yangiliklari\n"
            " • ⚡ Tezkor javoblar\n\n"
        )
    else:
        request_count = get_user_attr(user, 'request_count', 0)
        welcome_text += (
            f"📊 *Sizning statusingiz:* Oddiy foydalanuvchi\n"
            f"📢 *Bepul so'rovlar:* {config.FREE_REQUEST_LIMIT - request_count}/{config.FREE_REQUEST_LIMIT}\n\n"
            "💡 *VIP bo'lish uchun:*\n"
            " • Litsenziya sotib oling\n"
            " • Cheksiz tahlillardan foydalaning\n"
            " • Pro funksiyalarga ega bo'ling\n\n"
        )
    
    welcome_text += "💡 Boshlash uchun pastdagi menyudan kerakli bo'limni tanlang 👇"
    
    # Welcome banner bilan yuborish
    try:
        with open("welcome_banner.jpg", "rb") as photo:
            await message.answer_photo(
                photo=photo,
                caption=welcome_text,
                parse_mode="Markdown",
                reply_markup=get_main_menu(is_vip, get_datetime_from_obj(user, 'vip_until'))
            )
    except:
        await message.answer(
            welcome_text,
            parse_mode="Markdown",
            reply_markup=get_main_menu(is_vip, user.vip_until if user else None)
        )


async def cmd_admin(message: types.Message):
    """Admin panel"""
    user_id = message.from_user.id
    
    if user_id not in config.ADMINS:
        await message.answer("❌ Siz admin emassiz!")
        return
    
    from keyboards import get_admin_menu
    
    await message.answer(
        "👑 *ADMIN PANEL*\n\n"
        f"🆔 Sizning ID: {user_id}\n\n"
        "Admin funksiyalari:",
        parse_mode="Markdown",
        reply_markup=get_admin_menu()
    )


async def handle_back_to_menu(message: types.Message):
    """Asosiy menyuga qaytish"""
    user_id = message.from_user.id
    
    # VIP statusni tekshirish
    is_vip, _, _ = await vip_sync.check_vip_and_notify(user_id)
    user = trading_db.get_user(user_id)
    
    await message.answer(
        "🏠 Asosiy menyu",
        reply_markup=get_main_menu(is_vip, user.vip_until if user else None)
    )


async def handle_help(message: types.Message):
    """Yordam bo'limi"""
    help_text = (
        "❓ *YORDAM BO'LIMI*\n\n"
        "📌 Quyidagi bo'limlardan foydalanishingiz mumkin:\n\n"
        "1️⃣ *📊 Texnik Tahlil* – Price Action tahlil\n"
        "2️⃣ *💼 Fundamental Tahlil* – Iqtisodiy tahlil\n"
        "3️⃣ *🔍 Pro Tahlil* – Multi-timeframe tahlil (VIP)\n"
        "4️⃣ *📰 Insider News* – Eksklyuziv yangiliklar (VIP)\n"
        "5️⃣ *🎁 Litsenziya olish* – Robot litsenziyasini sotib olish\n"
        "6️⃣ *🤝 Referral* – Do'stlaringizni taklif qiling va chegirma oling\n\n"
        "📞 *Qo'shimcha savol:*\n"
        f"📱 Telefon: +998930012284\n"
        f"💬 Telegram: {config.ADMIN_USERNAME}\n\n"
        "✅ FATH BOT sizga yordam berishga tayyor!"
    )
    
    await message.answer(help_text, parse_mode="Markdown")


async def handle_about_fath(message: types.Message):
    """FATH haqida"""
    about_text = (
        "🤖 *FATH Robot* – Sizning shaxsiy treyding yordamchingiz! 💹\n\n"
        "📊 Robot bozorni *Gann strategiyasi* asosida tahlil qiladi.\n"
        "🧠 Sun'iy intellekt algoritmlari orqali prognoz qiladi.\n"
        "📈 Fundamental tahlil bilan yangiliklar va iqtisodiy voqealarni hisobga oladi.\n"
        "⚡ Faqat aniq va xavfsiz signallarni tanlab, *hissiyotsiz savdo* amalga oshiradi.\n"
        "🛡 Kapitalni himoya qilish uchun kuchli *risk-menejment* tizimi mavjud.\n\n"
        "📌 *FATH qanday ishlaydi?*\n"
        " • 24/7 bozor monitoringi\n"
        " • Muhim darajalarni aniqlash\n"
        " • AI asosida trendlarni prognoz qilish\n"
        " • Fundamental yangiliklarni hisobga olish\n"
        " • Stop-Loss va Take-Profit avtomatik\n\n"
        "💰 *O'rtacha oylik daromad:* 30% – 150%\n"
        "🔥 Siz uxlaysiz – *FATH* ishlashda davom etadi!\n\n"
        "📞 Qo'shimcha ma'lumot: +998930012284"
    )
    
    await message.answer(about_text, parse_mode="Markdown")
    
    # Performance rasmi
    try:
        with open("fath_performance.jpg", "rb") as photo:
            await message.answer_photo(
                photo=photo,
                caption="📊 *FATH Robot real natijalari*",
                parse_mode="Markdown"
            )
    except:
        pass


async def handle_setup_guide(message: types.Message):
    """O'rnatish qo'llanma"""
    guide_text = (
        "⚙️ *FATH Robotni o'rnatish bo'yicha qo'llanma:*\n\n"
        "1️⃣ MetaTrader 5 ni yuklab oling\n"
        "   📥 https://www.metatrader5.com\n\n"
        "2️⃣ Bot sizga yuborgan `FATH.ex5` faylini:\n"
        "   ➡️ MT5: *File → Open Data Folder*\n"
        "   ➡️ *MQL5 → Experts* papkasiga joylashtiring\n\n"
        "3️⃣ MT5 ni qayta ishga tushiring\n\n"
        "4️⃣ *Navigator → Expert Advisors → FATH*\n"
        "   Grafikka tashlang\n\n"
        "5️⃣ Sozlamalar:\n"
        "   🔑 *License Token* – botdan olingan kod\n"
        "   📈 *LotSize* – boshlang'ich lot (0.01)\n\n"
        "6️⃣ *Tools → Options → Expert Advisors*\n"
        "   ✅ Allow Algo Trading\n"
        "   ✅ Allow WebRequest\n\n"
        "7️⃣ *AutoTrading* tugmasi yashil bo'lishi kerak\n\n"
        "🎉 Tayyor! FATH avtomatik ishlay boshlaydi!\n\n"
        "ℹ️ Yordam kerak bo'lsa: +998930012284"
    )
    
    await message.answer(guide_text, parse_mode="Markdown")
    
    # Video qo'llanma
    try:
        with open("fath_setup.mp4", "rb") as video:
            await message.answer_video(
                video=video,
                caption="🎥 Video qo'llanma: FATH robotni o'rnatish"
            )
    except:
        pass


async def handle_terms(message: types.Message):
    """Foydalanish shartnomasi"""
    terms_text = (
        "📜 *FOYDALANISH SHARTNOMASI*\n\n"
        "Ushbu hujjat FATH robotidan foydalanish tartibini belgilaydi.\n\n"
        "📹 *1️⃣ Umumiy qoidalar*\n"
        "• FATH robotini sotib olish orqali Siz ushbu shartlarga rozi bo'lasiz.\n"
        "• Robotni uchinchi shaxslarga sotish yoki tarqatish taqiqlanadi.\n\n"
        "📹 *2️⃣ Foydalanuvchi huquqlari*\n"
        "• Robotdan shaxsiy va tijorat maqsadida foydalanish.\n"
        "• Yangilanishlarni bepul olish.\n\n"
        "📹 *3️⃣ Risk va javobgarlik*\n"
        "• Forex savdosi yuqori riskli faoliyat.\n"
        "• Robot foyda kafolatlamaydi.\n"
        "• Foydalanuvchi o'z qarorlari uchun javobgar.\n\n"
        "✅ Bu shartnoma foydalanuvchi va ishlab chiquvchi o'rtasidagi huquq va majburiyatlarni tartibga soladi."
    )
    
    await message.answer(terms_text, parse_mode="Markdown")
    
    # PDF guvohnoma
    try:
        with open("guvohnoma.pdf", "rb") as doc:
            await message.answer_document(
                document=doc,
                caption="📄 FATH robotini sotish uchun rasmiy guvohnoma"
            )
    except:
        pass


def register_start_handlers(dp: Dispatcher):
    """Start handlerlarni ro'yxatdan o'tkazish"""
    dp.register_message_handler(cmd_start, commands=["start"])
    dp.register_message_handler(cmd_admin, commands=["admin"])
    
    # Tugmalar
    dp.register_message_handler(
        handle_back_to_menu, 
        lambda m: m.text and "Asosiy Menyu" in m.text,  # ← YANGI
        state="*"  # ← YANGI
    )
    dp.register_message_handler(handle_help, lambda m: m.text == "❓ Yordam")
    dp.register_message_handler(handle_about_fath, lambda m: m.text == "🤖 FATH haqida")
    dp.register_message_handler(handle_setup_guide, lambda m: m.text == "⚙️ O'rnatish qo'llanma")
    dp.register_message_handler(handle_terms, lambda m: m.text == "📜 Foydalanish shartnomasi")
    dp.register_message_handler(handle_referral, lambda m: m.text == "🤝 Referral")

async def handle_back_to_menu(message: types.Message):
    """Asosiy menyuga qaytish - ISTALGAN JOYDAN"""
    user_id = message.from_user.id
    
    # VIP statusni tekshirish
    is_vip, _, _ = await vip_sync.check_vip_and_notify(user_id)
    user = trading_db.get_user(user_id)
    
    await message.answer(
        "🏠 Asosiy menyu",
        reply_markup=get_main_menu(is_vip, user.vip_until if user else None)
    )

async def handle_referral(message: types.Message):
    """Referral tugmasi"""
    user_id = message.from_user.id
    
    # Referral kodni olish
    code = referral_service.get_or_create_code(user_id)
    ref_count = referral_service.get_referral_count(user_id)
    
    # Bot username
    try:
        me = await message.bot.get_me()
        bot_username = me.username
    except:
        bot_username = "fathanalitik_bot"
    
    invite_link = f"https://t.me/{bot_username}?start={code}"
    
    text = (
        f"🤝 *REFERRAL TIZIMI*\n\n"
        f"📢 Sizning shaxsiy havola:\n"
        f"`{invite_link}`\n\n"
        f"📊 Sizning referrallaringiz: *{ref_count}*\n"
        f"💰 Sizning chegirmangiz: *{ref_count * 2}%* (max 80%)\n\n"
        f"📌 *Qanday ishlaydi?*\n"
        f"• Do'stlaringizga yuqoridagi havolani yuboring\n"
        f"• Ular havolani bosib botni ishga tushiradi\n"
        f"• Har bir do'st uchun *2% chegirma* olasiz\n"
        f"• Maksimal *80% gacha chegirma*\n\n"
        f"🎁 Qancha ko'p do'st taklif qilsangiz, shuncha ko'p tejaysiz!"
    )
    
    await message.answer(text, parse_mode="Markdown")