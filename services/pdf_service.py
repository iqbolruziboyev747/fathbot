# ============================================
# PDF SERVICE - Litsenziya PDF yaratish
# ============================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

def create_license_pdf(license_obj, filename="license.pdf"):
    """Litsenziya shartnomasi PDF yaratish"""
    
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # 🔹 Sarlavha
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 80, "📜 Litsenziya Shartnomasi")

    # 🔹 Kirish
    c.setFont("Helvetica", 12)
    text = c.beginText(50, height - 120)
    text.textLines(
        """
Hurmatli mijoz,

🎉 Sizni Fath EA jamoasi nomidan tabriklaymiz! Siz bizning avtomatlashtirilgan savdo 
yechimimizdan foydalanish huquqini qo'lga kiritdingiz. 

Fath EA – bu Forex bozorida yordamchi vosita bo'lib, foydalanuvchilarga algoritmik 
savdo imkoniyatlarini taqdim etadi. Shuni unutmangki, moliyaviy bozorlar yuqori 
xavf darajasiga ega va barcha risklar foydalanuvchining zimmasida bo'ladi.
        """
    )

    # 🔹 Litsenziya tafsilotlari
    text.textLine("")
    text.textLine("--------- Litsenziya Tafsilotlari ---------")
    text.textLine(f"🔑 Litsenziya ID: {license_obj.license_id}")
    text.textLine(f"📝 Token: {license_obj.token}")
    text.textLine(f"📅 Berilgan sana: {license_obj.issued_at.strftime('%Y-%m-%d %H:%M:%S')}")
    text.textLine(f"⏳ Tugash sanasi: {license_obj.valid_until.strftime('%Y-%m-%d %H:%M:%S')}")
    text.textLine(f"💳 Hisob raqami: {license_obj.device_fp}")
    text.textLine(f"👤 Telegram ID: {license_obj.telegram_id if license_obj.telegram_id else 'N/A'}")

    # 🔹 Yakuniy eslatma
    text.textLine("")
    text.textLines(
        """
❗ Muhim eslatma:
- Ushbu dasturdan foydalanish orqali siz barcha risklarni o'zingiz qabul qilasiz.
- Fath EA jamoasi foydalanuvchilarning moliyaviy natijalari uchun javobgar emas.
- Foydalanish shartlari va qoidalari bot ichida to'liq keltirilgan.

📌 Bizning jamoamiz sizni muvaffaqiyatga yetaklashi uchun doimo qo'llab-quvvatlashga tayyor!
        """
    )

    c.drawText(text)

    # 🔹 Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(width / 2, 40, f"© {datetime.utcnow().year} Fath EA Team. Barcha huquqlar himoyalangan.")

    c.showPage()
    c.save()

    return filename