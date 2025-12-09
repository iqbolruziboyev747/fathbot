# ============================================
# DATABASE SERVICE - Barcha DB operatsiyalari
# ============================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from sqlalchemy.orm import sessionmaker
from database.base import trading_engine, license_engine
from database.trading_models import User, Analysis, EconomicData, InsiderNews
from database.license_models import License, PricingPlan, Referral, ReferralCode

class TradingDB:
    """Trading database operatsiyalari"""
    
    def __init__(self):
        self.SessionLocal = sessionmaker(bind=trading_engine)
    
    def get_user(self, user_id):
        """Foydalanuvchini olish"""
        session = self.SessionLocal()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            return user
        finally:
            session.close()
    
    def create_or_update_user(self, user_id, username, first_name):
        """Foydalanuvchi yaratish yoki yangilash"""
        session = self.SessionLocal()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            
            if not user:
                user = User(
                    user_id=user_id,
                    username=username,
                    first_name=first_name,
                    is_vip=False,
                    request_count=0
                )
                session.add(user)
            else:
                user.username = username
                user.first_name = first_name
            
            session.commit()
            session.refresh(user)
            return user
        finally:
            session.close()
    
    def set_vip_status(self, user_id, is_vip, vip_until=None):
        """VIP statusni o'rnatish"""
        session = self.SessionLocal()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if user:
                user.is_vip = is_vip
                user.vip_until = vip_until
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def increment_request(self, user_id):
        """So'rov sonini oshirish"""
        session = self.SessionLocal()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if user:
                user.request_count += 1
                session.commit()
                return user.request_count
            return 0
        finally:
            session.close()
    
    def can_make_request(self, user_id):
        """Foydalanuvchi so'rov yubora oladimi?"""
        user = self.get_user(user_id)
        if not user:
            return True, "✅ Yangi foydalanuvchi"
        
        # VIP tekshirish
        if user.is_vip:
            if user.vip_until and user.vip_until < datetime.now():
                # VIP muddati tugagan
                return False, "⚠️ VIP muddat tugadi! Yangi litsenziya sotib oling."
            return True, "✅ VIP foydalanuvchi"
        
        # Oddiy foydalanuvchi - 3 ta bepul
        import config
        if user.request_count < config.FREE_REQUEST_LIMIT:
            return True, f"✅ So'rovlar: {user.request_count}/{config.FREE_REQUEST_LIMIT}"
        else:
            return False, f"❌ Bepul so'rovlar tugadi! ({user.request_count}/{config.FREE_REQUEST_LIMIT})"
    
    def reset_request_count(self, user_id):
        """So'rov sonini 0 ga qaytarish (VIP bo'lganda)"""
        session = self.SessionLocal()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if user:
                user.request_count = 0
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def save_analysis(self, user_id, analysis_type, symbol, analysis_text):
        """Tahlilni saqlash"""
        session = self.SessionLocal()
        try:
            analysis = Analysis(
                user_id=user_id,
                analysis_type=analysis_type,
                symbol=symbol,
                analysis_text=analysis_text
            )
            session.add(analysis)
            session.commit()
            return True
        except Exception as e:
            print(f"Analysis save error: {e}")
            return False
        finally:
            session.close()
    
    def get_economic_data(self):
        """Iqtisodiy ma'lumotlarni olish"""
        session = self.SessionLocal()
        try:
            data = session.query(EconomicData).order_by(EconomicData.updated_at.desc()).first()
            return data
        finally:
            session.close()
    
    def update_economic_data(self, user_id, **kwargs):
        """Iqtisodiy ma'lumotlarni yangilash"""
        session = self.SessionLocal()
        try:
            data = session.query(EconomicData).first()
            
            if not data:
                data = EconomicData(updated_by=user_id)
                session.add(data)
            
            # Yangilash
            for key, value in kwargs.items():
                if hasattr(data, key):
                    setattr(data, key, value)
            
            data.updated_at = datetime.now()
            data.updated_by = user_id
            
            session.commit()
            return True
        except Exception as e:
            print(f"Economic data update error: {e}")
            return False
        finally:
            session.close()
    
    def get_all_users(self):
        """Barcha foydalanuvchilar"""
        session = self.SessionLocal()
        try:
            users = session.query(User).order_by(User.created_at.desc()).all()
            return users
        finally:
            session.close()
    
    def add_insider_news(self, user_id, news_date, news_name, news_result, accuracy):
        """Insider yangilik qo'shish"""
        session = self.SessionLocal()
        try:
            news = InsiderNews(
                news_date=news_date,
                news_name=news_name,
                news_result=news_result,
                accuracy=accuracy,
                created_by=user_id
            )
            session.add(news)
            session.commit()
            return True
        except Exception as e:
            print(f"Insider news add error: {e}")
            return False
        finally:
            session.close()
    
    def get_current_insider_news(self):
        """Kelajakdagi insider yangiliklari"""
        session = self.SessionLocal()
        try:
            from datetime import date
            news = session.query(InsiderNews).filter(
                InsiderNews.news_date >= str(date.today())
            ).order_by(InsiderNews.news_date.asc()).all()
            return news
        finally:
            session.close()
    
    def get_all_insider_news(self):
        """Barcha insider yangiliklar"""
        session = self.SessionLocal()
        try:
            news = session.query(InsiderNews).order_by(InsiderNews.news_date.desc()).all()
            return news
        finally:
            session.close()
    
    def delete_insider_news(self, news_id):
        """Insider yangilikni o'chirish"""
        session = self.SessionLocal()
        try:
            news = session.query(InsiderNews).filter(InsiderNews.id == news_id).first()
            if news:
                session.delete(news)
                session.commit()
                return True
            return False
        finally:
            session.close()


class LicenseDB:
    """License database operatsiyalari"""
    
    def __init__(self):
        self.SessionLocal = sessionmaker(bind=license_engine)
    
    def get_active_license(self, user_id):
        """Aktiv litsenziyani olish"""
        session = self.SessionLocal()
        try:
            license = session.query(License).filter(
                License.telegram_id == user_id,
                License.revoked == False,
                License.valid_until > datetime.now()
            ).order_by(License.valid_until.desc()).first()
            return license
        finally:
            session.close()
    
    def get_all_licenses(self, user_id):
        """Barcha litsenziyalarni olish"""
        session = self.SessionLocal()
        try:
            licenses = session.query(License).filter(
                License.telegram_id == user_id
            ).order_by(License.issued_at.desc()).all()
            return licenses
        finally:
            session.close()
    

    def get_license_by_token(self, token):
        """Token orqali licenseni topish (MT5 uchun)"""
        session = self.SessionLocal()
        try:
            license = session.query(License).filter(
                License.token == token
            ).first()
            return license
        finally:
            session.close()

    def create_license(self, account_number, telegram_id, plan_code, days, is_trial=False):
        """Yangi litsenziya yaratish"""
        import uuid
        from datetime import timedelta
        
        session = self.SessionLocal()
        try:
            license_id = ("TRIAL-" if is_trial else "LIC-") + uuid.uuid4().hex[:12].upper()
            issued = datetime.utcnow()
            valid = issued + timedelta(days=days)
            token = "TKN-" + uuid.uuid4().hex[:16].upper()
            
            license = License(
                license_id=license_id,
                token=token,
                issued_at=issued,
                valid_until=valid,
                revoked=False,
                is_trial=is_trial,
                device_fp=account_number,
                telegram_id=telegram_id,
                plan_code=plan_code
            )
            
            session.add(license)
            session.commit()
            session.refresh(license)
            return license, None
        except Exception as e:
            session.rollback()
            return None, str(e)
        finally:
            session.close()
    
    def get_all_pricing_plans(self):
        """Barcha tariflar"""
        session = self.SessionLocal()
        try:
            plans = session.query(PricingPlan).all()
            return plans
        finally:
            session.close()
    
    def get_active_pricing_plans(self):
        """Faol tariflar"""
        session = self.SessionLocal()
        try:
            plans = session.query(PricingPlan).filter(
                PricingPlan.is_active == True
            ).all()
            return plans
        finally:
            session.close()
    
    def get_plan_by_code(self, plan_code):
        """Tarifni kod bo'yicha olish"""
        session = self.SessionLocal()
        try:
            plan = session.query(PricingPlan).filter(
                PricingPlan.plan_code == plan_code
            ).first()
            return plan
        finally:
            session.close()
    
    def update_plan_price(self, plan_code, new_price):
        """Tarif narxini yangilash"""
        session = self.SessionLocal()
        try:
            plan = session.query(PricingPlan).filter(
                PricingPlan.plan_code == plan_code
            ).first()
            
            if plan:
                plan.price = new_price
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def toggle_plan_active(self, plan_code):
        """Tarifni yoqish/o'chirish"""
        session = self.SessionLocal()
        try:
            plan = session.query(PricingPlan).filter(
                PricingPlan.plan_code == plan_code
            ).first()
            
            if plan:
                plan.is_active = not plan.is_active
                session.commit()
                return True, plan.is_active
            return False, None
        finally:
            session.close()


# Global instances
trading_db = TradingDB()
license_db = LicenseDB()
