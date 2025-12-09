from fastapi import FastAPI, Form
from fastapi.responses import PlainTextResponse
from datetime import datetime, timedelta
import uuid

from models import SessionLocal, License

app = FastAPI(title="MT5 License Server")

# -------------------------
# Token yaratish funksiyasi
# -------------------------
def make_token(payload: dict) -> str:
    return "TKN-" + uuid.uuid4().hex[:16].upper()

# -------------------------
# Litsenziya yaratish funksiyasi
# -------------------------
def create_license(account_number: str, telegram_id: int, days: int = 30, is_trial: bool = False):
    sess = SessionLocal()
    try:
        if is_trial:
            # ❌ Endi trialni faqat account bo‘yicha emas, balki telegram_id bo‘yicha ham cheklaymiz
            existing = sess.query(License).filter(
                ((License.device_fp == account_number) | (License.telegram_id == telegram_id)),
                License.is_trial == True
            ).first()
            if existing:
                return None, "Trial allaqachon olingan."

        lic_id = ("TRIAL-" if is_trial else "LIC-") + uuid.uuid4().hex[:12].upper()
        issued = datetime.utcnow()
        valid = issued + timedelta(days=days)
        payload = {"license_id": lic_id, "account": account_number, "exp": valid.isoformat()}
        token = make_token(payload)

        lic = License(
            license_id=lic_id,
            token=token,
            issued_at=issued,
            valid_until=valid,
            revoked=False,
            is_trial=is_trial,
            device_fp=account_number.strip(),
            telegram_id=telegram_id
        )
        sess.add(lic)
        sess.commit()
        return token, None
    except Exception as e:
        sess.rollback()
        return None, str(e)
    finally:
        sess.close()

# -------------------------
# Token tekshirish funksiyasi
# -------------------------
def verify_license(token: str, account_number: str) -> (bool, str):
    sess = SessionLocal()
    try:
        lic = sess.query(License).filter_by(token=token).first()
        if not lic:
            return False, "Token topilmadi."
        if lic.revoked:
            return False, "Litsenziya bekor qilingan."
        if lic.valid_until < datetime.utcnow():
            return False, "Litsenziya muddati tugagan."

        # 🔹 Normalize qilish (NULL va bo‘sh joylarni olib tashlash)
        db_acc = str(lic.device_fp).strip().replace("\x00", "")
        cli_acc = str(account_number).strip().replace("\x00", "")

        if db_acc != cli_acc:
            return False, "Hisob raqam mos emas."

        return True, "Litsenziya tasdiqlandi."
    finally:
        sess.close()

# -------------------------
# HTTP endpointlar
# -------------------------
@app.post("/create", response_class=PlainTextResponse)
async def create(account: str = Form(...), telegram_id: int = Form(...), plan: str = Form(...)):
    is_trial = plan.lower() == "trial"
    days = 3 if is_trial else 30
    token, err = create_license(account, telegram_id, days, is_trial)
    if err:
        return f"ERROR: {err}"
    return f"TOKEN:{token}"

@app.post("/verify", response_class=PlainTextResponse)
async def verify(token: str = Form(...), account: str = Form(...)):
    valid, msg = verify_license(token, account)
    if valid:
        return "VALID"
    else:
        return f"INVALID: {msg}"


