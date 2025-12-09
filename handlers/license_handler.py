# ============================================
# LICENSE HANDLER - Litsenziya olish va boshqarish
# ============================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import LabeledPrice

import config
from keyboards import (
    get_license_plans_keyboard,
    get_confirm_keyboard,
    get_terms_keyboard,
    get_main_menu
)
from services.database_service import license_db
from services.vip_sync_service import vip_sync
from services.referral_service import referral_service
from services.pdf_service import create_license_pdf
import time


# FSM States
class LicenseStates(StatesGroup):
    waiting_account = State()
    waiting_confirm = State()
    waiting_terms = State()
    waiting_plan = State()


async def handle_get_license(message: types.Message, state: FSMContext):
    """Litsenziya olish tugmasi"""
    await message.answer(
        "🎁 *LITSENZIYA OLISH*\n\n"
        "📢 Iltimos, MetaTrader hisob raqamingizni (Account number) kiriting:",
        parse_mode="Markdown",
        reply_markup=types.ReplyKeyboardRemove()
    )
    
    await LicenseStates.waiting_account.set()


async def process_account(message: types.Message, state: FSMContext):
    """Account raqamini qabul qilish"""
    account = message.text.strip()
    
    if not account.isdigit():
        await message.answer("❌ Noto'g'ri account raqam. Faqat raqam kiriting:")
        return
    
    await state.update_data(account=account)
    
    await message.answer(
        f"📌 Siz kiritgan hisob raqami: *{account}*\n\nTasdiqlaysizmi?",
        parse_mode="Markdown",
        reply_markup=get_confirm_keyboard()
    )
    
    await LicenseStates.waiting_confirm.set()


async def process_confirm(message: types.Message, state: FSMContext):
    """Tasdiqlash"""
    text = message.text.lower()
    
    if "yo'q" in text or "yoq" in text or "qayta" in text:
        await message.answer(
            "🔄 Iltimos, qayta hisob raqamingizni kiriting:",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await LicenseStates.waiting_account.set()
        return
    
    if "ha" in text or "tasdiq" in text:
        await message.answer(
            "📜 *Foydalanish shartlariga* rozilik bildirishingiz kerak.",
            parse_mode="Markdown",
            reply_markup=get_terms_keyboard()
        )
        await LicenseStates.waiting_terms.set()
        return
    
    # Fallback
    await message.answer(
        "Iltimos, tugmalardan birini bosing:",
        reply_markup=get_confirm_keyboard()
    )


async def process_terms(message: types.Message, state: FSMContext):
    """Shartlarga rozilik"""
    text = message.text.lower()
    
    if "rozi emas" in text or "roziemas" in text:
        await state.finish()
        await message.answer(
            "❌ Siz foydalanish shartlariga rozi bo'lmadingiz.\n"
            "Jarayon bekor qilindi.",
            reply_markup=get_main_menu()
        )
        return
    
    if "roziman" in text or "rozi" in text:
        # Tarif rejalarini olish
        plans = license_db.get_active_pricing_plans()
        
        if not plans:
            await state.finish()
            await message.answer(
                "❌ Hozirda mavjud tariflar yo'q.\n"
                "Iltimos, keyinroq urinib ko'ring."
            )
            return
        
        await message.answer(
            "📌 *Litsenziya turini tanlang:*",
            parse_mode="Markdown",
            reply_markup=get_license_plans_keyboard(plans)
        )
        await LicenseStates.waiting_plan.set()
        return
    
    # Fallback
    await message.answer(
        "Iltimos, tugmalardan birini tanlang:",
        reply_markup=get_terms_keyboard()
    )


async def process_plan(message: types.Message, state: FSMContext):
    """Tarif tanlash va to'lov"""
    text = message.text
    user_id = message.from_user.id
    
    if "bekor" in text.lower():
        await state.finish()
        await message.answer(
            "❌ Jarayon bekor qilindi.",
            reply_markup=get_main_menu()
        )
        return
    
    # Data olish
    data = await state.get_data()
    account = data.get("account")
    
    if not account:
        await state.finish()
        await message.answer("❌ Xatolik! Qayta /start ni bosing")
        return
    
    # Tarifni aniqlash
    plans = license_db.get_active_pricing_plans()
    selected_plan = None
    
    for plan in plans:
        if plan.name in text:
            selected_plan = plan
            break
    
    if not selected_plan:
        await message.answer("❌ Noto'g'ri tanlov! Iltimos, tugmalardan foydalaning.")
        return
    
    # Agar TRIAL bo'lsa - admin beradi
    if selected_plan.plan_code == "trial":
        await state.finish()
        await message.answer(
            "ℹ️ *TRIAL litsenziya faqat admin tomonidan beriladi.*\n\n"
            f"📞 Admin bilan bog'laning: {config.ADMIN_USERNAME}\n\n"
            f"🆔 Sizning hisob raqamingiz: `{account}`",
            parse_mode="Markdown",
            reply_markup=get_main_menu()
        )
        return
    
    # Referral chegirmasini hisoblash
    ref_count = referral_service.get_referral_count(user_id)
    base_price = selected_plan.price
    final_price, discount_percent = referral_service.apply_discount(user_id, base_price)
    
    # To'lov invoice
    amount_tiyin = final_price * 100
    payload = f"license_{user_id}_{account}_{selected_plan.plan_code}_{int(time.time())}"
    
    description = f"{selected_plan.name} (Account: {account})"
    if discount_percent > 0:
        description += f" - {discount_percent}% chegirma (referrals: {ref_count})"
    
    prices = [LabeledPrice(
        label=f"{selected_plan.name} ({selected_plan.days} kun)",
        amount=amount_tiyin
    )]
    
    try:
        await message.bot.send_invoice(
            chat_id=message.chat.id,
            title="FATH Robot Litsenziyasi",
            description=description,
            payload=payload,
            provider_token=config.PAYME_TOKEN,
            currency="UZS",
            prices=prices,
            start_parameter="license"
        )
        
        await state.finish()
        
    except Exception as e:
        await message.answer(f"❌ To'lov xatosi: {str(e)}")
        await state.finish()


async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    """Pre-checkout tekshirish"""
    await pre_checkout_q.bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


async def successful_payment(message: types.Message):
    """Muvaffaqiyatli to'lov"""
    sp = message.successful_payment
    user_id = message.from_user.id
    
    # Payload dan ma'lumotlarni olish
    payload = getattr(sp, "invoice_payload", "")
    paid_tiyin = getattr(sp, "total_amount", 0)
    paid_amount = int(paid_tiyin // 100) if paid_tiyin else 0
    
    # Default values
    account = "UNKNOWN"
    plan_code = None
    
    # Payload parse qilish: license_{user_id}_{account}_{plan_code}_{timestamp}
    if payload:
        parts = payload.split("_", 4)
        if len(parts) >= 4 and parts[0] == "license":
            try:
                account = parts[2]
                if len(parts) >= 4:
                    plan_code = parts[3]
            except:
                pass
    
    # Tarifni topish
    if plan_code:
        plan = license_db.get_plan_by_code(plan_code)
        if plan:
            days = plan.days
            is_trial = (plan_code == "trial")
        else:
            days = 30
            is_trial = False
    else:
        days = 30
        is_trial = False
    
    # Litsenziya yaratish
    try:
        license_obj, error = license_db.create_license(
            account_number=account,
            telegram_id=user_id,
            plan_code=plan_code,
            days=days,
            is_trial=is_trial
        )
        
        if error:
            await message.answer(f"❌ Litsenziya yaratishda xato: {error}")
            return
        
        # PDF yaratish
        try:
            pdf_path = create_license_pdf(license_obj, f"license_{license_obj.license_id}.pdf")
        except:
            pdf_path = None
        
        # VIP statusni sinxronlashtirish
        await vip_sync.sync_user_vip_status(user_id)
        
        # Muvaffaqiyat xabari
        await message.answer(
            f"✅ *TO'LOV QABUL QILINDI!*\n\n"
            f"🔑 *Litsenziya:*\n"
            f"`{license_obj.token}`\n\n"
            f"📌 *Account:* {account}\n"
            f"📅 *Muddat:* {days} kun\n"
            f"💳 *To'lov:* {paid_amount:,} so'm\n\n"
            f"⭐ VIP statusingiz faollashtirildi!\n"
            f"🎯 Endi cheksiz tahlillardan foydalanishingiz mumkin!",
            parse_mode="Markdown",
            reply_markup=get_main_menu(is_vip=True, vip_until=license_obj.valid_until)
        )
        
        # PDF yuborish
        if pdf_path and os.path.exists(pdf_path):
            try:
                with open(pdf_path, "rb") as f:
                    await message.answer_document(
                        document=f,
                        caption="📜 Sizning litsenziya kontraktingiz"
                    )
            except Exception as e:
                print(f"PDF yuborishda xato: {e}")
        
        # Robot faylini yuborish
        try:
            if os.path.exists("FATH.ex5"):
                with open("FATH.ex5", "rb") as f:
                    await message.answer_document(
                        document=f,
                        caption="📦 Robot fayli (FATH.ex5)"
                    )
        except Exception as e:
            print(f"Robot faylini yuborishda xato: {e}")
            await message.answer(
                "⚠️ Robot faylini yuborib bo'lmadi.\n"
                f"Iltimos, admin bilan bog'laning: {config.ADMIN_USERNAME}"
            )
        
    except Exception as e:
        await message.answer(f"❌ Xatolik: {str(e)}")


async def handle_my_licenses(message: types.Message):
    """Mening litsenziyalarim"""
    user_id = message.from_user.id
    
    licenses = license_db.get_all_licenses(user_id)
    
    if not licenses:
        await message.answer(
            "❌ Sizda litsenziyalar topilmadi.\n\n"
            "🎁 Litsenziya olish uchun tegishli tugmani bosing.",
            reply_markup=get_main_menu()
        )
        return
    
    response = "📜 *MENING LITSENZIYALARIM*\n\n"
    
    for lic in licenses:
        status = "❌ Bekor qilingan" if lic.revoked else (
            "✅ Faol" if lic.valid_until > datetime.now() else "⏰ Muddati tugagan"
        )
        
        response += f"🔑 *{lic.license_id}*\n"
        response += f"💳 Account: `{lic.device_fp}`\n"
        response += f"📝 Token: `{lic.token}`\n"
        response += f"📅 Tugash: {lic.valid_until.strftime('%Y-%m-%d %H:%M')}\n"
        response += f"📌 Status: {status}\n"
        response += f"🏷 Tur: {'Trial' if lic.is_trial else 'Full'}\n"
        response += "─" * 30 + "\n\n"
    
    await message.answer(response, parse_mode="Markdown")


def register_license_handlers(dp: Dispatcher):
    """License handlerlarni ro'yxatdan o'tkazish"""
    
    # Tugmalar
    dp.register_message_handler(
        handle_get_license,
        lambda m: m.text == "🎁 Litsenziya olish",
        state="*"
    )
    
    dp.register_message_handler(
        handle_my_licenses,
        lambda m: m.text == "📜 Mening litsenziyalarim",
        state="*"
    )
    
    # FSM States
    dp.register_message_handler(
        process_account,
        state=LicenseStates.waiting_account
    )
    
    dp.register_message_handler(
        process_confirm,
        state=LicenseStates.waiting_confirm
    )
    
    dp.register_message_handler(
        process_terms,
        state=LicenseStates.waiting_terms
    )
    
    dp.register_message_handler(
        process_plan,
        state=LicenseStates.waiting_plan
    )
    
    # Payment
    dp.register_pre_checkout_query_handler(pre_checkout_query)
    dp.register_message_handler(
        successful_payment,
        content_types=types.ContentType.SUCCESSFUL_PAYMENT
    )


# Import datetime (faylning yuqori qismida qo'shish kerak)
from datetime import datetime

# YANGILANGAN REGISTRATSIYA FUNKSIYASI
def register_license_handlers_fixed(dp: Dispatcher):
    """License handlerlarni to'g'ri tartibda ro'yxatdan o'tkazish"""
    
    # Tugmalar (state yoq - yuqori prioritet)
    dp.register_message_handler(
        handle_get_license,
        lambda m: m.text == "🎁 Litsenziya olish",
        state=None  # Faqat state yo'q bo'lganda
    )
    
    dp.register_message_handler(
        handle_my_licenses,
        lambda m: m.text == "📜 Mening litsenziyalarim",
        state=None  # Faqat state yo'q bo'lganda
    )
    
    # FSM States (pastroq prioritet)
    dp.register_message_handler(
        process_account,
        state=LicenseStates.waiting_account
    )
    
    dp.register_message_handler(
        process_terms,
        state=LicenseStates.waiting_terms
    )
    
    dp.register_message_handler(
        process_plan,
        state=LicenseStates.waiting_plan
    )
    
    dp.register_message_handler(
        process_confirm,
        state=LicenseStates.waiting_confirm
    )
