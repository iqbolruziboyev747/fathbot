# ============================================
# FIRESTORE SERVICE - Firebase Firestore database operatsiyalari
# ============================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from typing import Optional, List, Dict, Any
import firebase_admin
from firebase_admin import credentials, firestore
import config

# Firebase initialization
_firestore_client = None

def get_firestore_client():
    """Firestore client ni olish yoki yaratish"""
    global _firestore_client
    
    if _firestore_client is None:
        try:
            # Agar Firebase allaqachon initialize qilingan bo'lsa
            _firestore_client = firestore.client()
        except ValueError:
            # Initialize qilish kerak
            # Environment variable dan olish (Cloud Run uchun)
            if os.getenv('FIREBASE_CREDENTIALS'):
                import json
                creds_json = os.getenv('FIREBASE_CREDENTIALS')
                # Agar base64 bo'lsa
                if len(creds_json) > 1000:  # Base64 bo'lsa katta bo'ladi
                    try:
                        import base64
                        creds_json = base64.b64decode(creds_json).decode('utf-8')
                    except:
                        pass
                creds_dict = json.loads(creds_json)
                cred = credentials.Certificate(creds_dict)
                firebase_admin.initialize_app(cred)
                _firestore_client = firestore.client()
            elif os.path.exists(config.FIREBASE_CREDENTIALS_PATH):
                cred = credentials.Certificate(config.FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred)
                _firestore_client = firestore.client()
            else:
                raise FileNotFoundError(
                    f"Firebase credentials topilmadi!\n"
                    "Iltimos, FIREBASE_CREDENTIALS environment variable yoki "
                    f"{config.FIREBASE_CREDENTIALS_PATH} faylini qo'ying."
                )
    
    return _firestore_client


class FirestoreTradingDB:
    """Trading database operatsiyalari - Firestore"""
    
    def __init__(self):
        self.db = get_firestore_client()
        self.users_collection = self.db.collection(config.FIRESTORE_COLLECTIONS["users"])
        self.analyses_collection = self.db.collection(config.FIRESTORE_COLLECTIONS["analyses"])
        self.economic_data_collection = self.db.collection(config.FIRESTORE_COLLECTIONS["economic_data"])
        self.insider_news_collection = self.db.collection(config.FIRESTORE_COLLECTIONS["insider_news"])
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Foydalanuvchini olish"""
        try:
            doc = self.users_collection.document(str(user_id)).get()
            if doc.exists:
                data = doc.to_dict()
                data['user_id'] = int(user_id)
                # DateTime ni convert qilish
                if 'created_at' in data and isinstance(data['created_at'], datetime):
                    pass  # Already datetime
                elif 'created_at' in data:
                    data['created_at'] = data['created_at']
                if 'vip_until' in data and data['vip_until']:
                    if isinstance(data['vip_until'], datetime):
                        pass
                    else:
                        data['vip_until'] = datetime.fromisoformat(str(data['vip_until']))
                return data
            return None
        except Exception as e:
            print(f"Firestore get_user error: {e}")
            return None
    
    def create_or_update_user(self, user_id: int, username: Optional[str], first_name: Optional[str]) -> Dict[str, Any]:
        """Foydalanuvchi yaratish yoki yangilash"""
        try:
            doc_ref = self.users_collection.document(str(user_id))
            doc = doc_ref.get()
            
            if doc.exists:
                # Yangilash
                doc_ref.update({
                    'username': username,
                    'first_name': first_name,
                    'updated_at': firestore.SERVER_TIMESTAMP
                })
                user_data = doc_ref.get().to_dict()
            else:
                # Yaratish
                user_data = {
                    'user_id': user_id,
                    'username': username,
                    'first_name': first_name,
                    'is_vip': False,
                    'request_count': 0,
                    'created_at': firestore.SERVER_TIMESTAMP,
                    'vip_until': None
                }
                doc_ref.set(user_data)
                user_data = doc_ref.get().to_dict()
            
            # Convert Firestore Timestamp to datetime
            if 'created_at' in user_data:
                if hasattr(user_data['created_at'], 'timestamp'):
                    user_data['created_at'] = datetime.fromtimestamp(user_data['created_at'].timestamp())
            
            user_data['user_id'] = user_id
            return user_data
        except Exception as e:
            print(f"Firestore create_or_update_user error: {e}")
            return {}
    
    def set_vip_status(self, user_id: int, is_vip: bool, vip_until: Optional[datetime] = None) -> bool:
        """VIP statusni o'rnatish"""
        try:
            doc_ref = self.users_collection.document(str(user_id))
            update_data = {
                'is_vip': is_vip,
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            
            if vip_until:
                update_data['vip_until'] = vip_until
            else:
                update_data['vip_until'] = None
            
            doc_ref.update(update_data)
            return True
        except Exception as e:
            print(f"Firestore set_vip_status error: {e}")
            return False
    
    def increment_request(self, user_id: int) -> int:
        """So'rov sonini oshirish"""
        try:
            doc_ref = self.users_collection.document(str(user_id))
            doc = doc_ref.get()
            
            if doc.exists:
                current_count = doc.get('request_count', 0)
                new_count = current_count + 1
                doc_ref.update({
                    'request_count': new_count,
                    'updated_at': firestore.SERVER_TIMESTAMP
                })
                return new_count
            else:
                # User yo'q bo'lsa yaratish
                self.create_or_update_user(user_id, None, None)
                doc_ref.update({'request_count': 1})
                return 1
        except Exception as e:
            print(f"Firestore increment_request error: {e}")
            return 0
    
    def can_make_request(self, user_id: int) -> tuple[bool, str]:
        """Foydalanuvchi so'rov yubora oladimi?"""
        user = self.get_user(user_id)
        if not user:
            return True, "✅ Yangi foydalanuvchi"
        
        # VIP tekshirish
        if user.get('is_vip', False):
            vip_until = user.get('vip_until')
            if vip_until:
                if isinstance(vip_until, str):
                    vip_until = datetime.fromisoformat(vip_until)
                if vip_until < datetime.now():
                    return False, "⚠️ VIP muddat tugadi! Yangi litsenziya sotib oling."
            return True, "✅ VIP foydalanuvchi"
        
        # Oddiy foydalanuvchi - 3 ta bepul
        request_count = user.get('request_count', 0)
        if request_count < config.FREE_REQUEST_LIMIT:
            return True, f"✅ So'rovlar: {request_count}/{config.FREE_REQUEST_LIMIT}"
        else:
            return False, f"❌ Bepul so'rovlar tugadi! ({request_count}/{config.FREE_REQUEST_LIMIT})"
    
    def save_analysis(self, user_id: int, analysis_type: str, symbol: Optional[str], analysis_text: str) -> bool:
        """Tahlilni saqlash"""
        try:
            analysis_data = {
                'user_id': user_id,
                'analysis_type': analysis_type,
                'symbol': symbol,
                'analysis_text': analysis_text,
                'created_at': firestore.SERVER_TIMESTAMP
            }
            self.analyses_collection.add(analysis_data)
            return True
        except Exception as e:
            print(f"Firestore save_analysis error: {e}")
            return False
    
    def get_economic_data(self) -> Optional[Dict[str, Any]]:
        """Iqtisodiy ma'lumotlarni olish"""
        try:
            docs = self.economic_data_collection.order_by('updated_at', direction=firestore.Query.DESCENDING).limit(1).stream()
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
        except Exception as e:
            print(f"Firestore get_economic_data error: {e}")
            return None
    
    def update_economic_data(self, user_id: int, **kwargs) -> bool:
        """Iqtisodiy ma'lumotlarni yangilash"""
        try:
            docs = list(self.economic_data_collection.limit(1).stream())
            
            if docs:
                doc_ref = docs[0].reference
                update_data = {
                    'updated_at': firestore.SERVER_TIMESTAMP,
                    'updated_by': user_id
                }
                update_data.update(kwargs)
                doc_ref.update(update_data)
            else:
                # Yaratish
                data = {
                    'updated_by': user_id,
                    'updated_at': firestore.SERVER_TIMESTAMP
                }
                data.update(kwargs)
                self.economic_data_collection.add(data)
            
            return True
        except Exception as e:
            print(f"Firestore update_economic_data error: {e}")
            return False
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Barcha foydalanuvchilar"""
        try:
            users = []
            docs = self.users_collection.order_by('created_at', direction=firestore.Query.DESCENDING).stream()
            for doc in docs:
                data = doc.to_dict()
                data['user_id'] = int(doc.id)
                users.append(data)
            return users
        except Exception as e:
            print(f"Firestore get_all_users error: {e}")
            return []
    
    def add_insider_news(self, user_id: int, news_date: str, news_name: str, news_result: str, accuracy: str) -> bool:
        """Insider yangilik qo'shish"""
        try:
            news_data = {
                'news_date': news_date,
                'news_name': news_name,
                'news_result': news_result,
                'accuracy': accuracy,
                'created_by': user_id,
                'created_at': firestore.SERVER_TIMESTAMP
            }
            self.insider_news_collection.add(news_data)
            return True
        except Exception as e:
            print(f"Firestore add_insider_news error: {e}")
            return False
    
    def get_current_insider_news(self) -> List[Dict[str, Any]]:
        """Kelajakdagi insider yangiliklari"""
        try:
            from datetime import date
            today_str = str(date.today())
            
            news_list = []
            docs = self.insider_news_collection.where('news_date', '>=', today_str).order_by('news_date').stream()
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                news_list.append(data)
            return news_list
        except Exception as e:
            print(f"Firestore get_current_insider_news error: {e}")
            return []
    
    def get_all_insider_news(self) -> List[Dict[str, Any]]:
        """Barcha insider yangiliklar"""
        try:
            news_list = []
            docs = self.insider_news_collection.order_by('news_date', direction=firestore.Query.DESCENDING).stream()
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                news_list.append(data)
            return news_list
        except Exception as e:
            print(f"Firestore get_all_insider_news error: {e}")
            return []
    
    def delete_insider_news(self, news_id: str) -> bool:
        """Insider yangilikni o'chirish"""
        try:
            self.insider_news_collection.document(news_id).delete()
            return True
        except Exception as e:
            print(f"Firestore delete_insider_news error: {e}")
            return False


class FirestoreLicenseDB:
    """License database operatsiyalari - Firestore"""
    
    def __init__(self):
        self.db = get_firestore_client()
        self.licenses_collection = self.db.collection(config.FIRESTORE_COLLECTIONS["licenses"])
        self.pricing_plans_collection = self.db.collection(config.FIRESTORE_COLLECTIONS["pricing_plans"])
    
    def get_active_license(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Aktiv litsenziyani olish"""
        try:
            now = datetime.now()
            docs = self.licenses_collection.where('telegram_id', '==', user_id)\
                                          .where('revoked', '==', False)\
                                          .where('valid_until', '>', now)\
                                          .order_by('valid_until', direction=firestore.Query.DESCENDING)\
                                          .limit(1)\
                                          .stream()
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                # Convert timestamps
                if 'issued_at' in data and hasattr(data['issued_at'], 'timestamp'):
                    data['issued_at'] = datetime.fromtimestamp(data['issued_at'].timestamp())
                if 'valid_until' in data and hasattr(data['valid_until'], 'timestamp'):
                    data['valid_until'] = datetime.fromtimestamp(data['valid_until'].timestamp())
                return data
            return None
        except Exception as e:
            print(f"Firestore get_active_license error: {e}")
            return None
    
    def get_all_licenses(self, user_id: int) -> List[Dict[str, Any]]:
        """Barcha litsenziyalarni olish"""
        try:
            licenses = []
            docs = self.licenses_collection.where('telegram_id', '==', user_id)\
                                          .order_by('issued_at', direction=firestore.Query.DESCENDING)\
                                          .stream()
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                # Convert timestamps
                if 'issued_at' in data and hasattr(data['issued_at'], 'timestamp'):
                    data['issued_at'] = datetime.fromtimestamp(data['issued_at'].timestamp())
                if 'valid_until' in data and hasattr(data['valid_until'], 'timestamp'):
                    data['valid_until'] = datetime.fromtimestamp(data['valid_until'].timestamp())
                licenses.append(data)
            return licenses
        except Exception as e:
            print(f"Firestore get_all_licenses error: {e}")
            return []
    
    def create_license(self, account_number: str, telegram_id: int, plan_code: str, days: int, is_trial: bool = False) -> tuple:
        """Yangi litsenziya yaratish"""
        import uuid
        from datetime import timedelta
        
        try:
            license_id = ("TRIAL-" if is_trial else "LIC-") + uuid.uuid4().hex[:12].upper()
            issued = datetime.now()
            valid = issued + timedelta(days=days)
            token = "TKN-" + uuid.uuid4().hex[:16].upper()
            
            license_data = {
                'license_id': license_id,
                'token': token,
                'issued_at': issued,
                'valid_until': valid,
                'revoked': False,
                'is_trial': is_trial,
                'device_fp': account_number,
                'telegram_id': telegram_id,
                'plan_code': plan_code,
                'created_at': firestore.SERVER_TIMESTAMP
            }
            
            doc_ref = self.licenses_collection.add(license_data)
            license_data['id'] = doc_ref[1].id
            
            # Convert datetime objects
            license_data['issued_at'] = issued
            license_data['valid_until'] = valid
            
            return license_data, None
        except Exception as e:
            return None, str(e)
    
    def get_all_pricing_plans(self) -> List[Dict[str, Any]]:
        """Barcha tariflar"""
        try:
            plans = []
            docs = self.pricing_plans_collection.stream()
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                plans.append(data)
            return plans
        except Exception as e:
            print(f"Firestore get_all_pricing_plans error: {e}")
            return []
    
    def get_active_pricing_plans(self) -> List[Dict[str, Any]]:
        """Faol tariflar"""
        try:
            plans = []
            docs = self.pricing_plans_collection.where('is_active', '==', True).stream()
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                plans.append(data)
            return plans
        except Exception as e:
            print(f"Firestore get_active_pricing_plans error: {e}")
            return []
    
    def get_plan_by_code(self, plan_code: str) -> Optional[Dict[str, Any]]:
        """Tarifni kod bo'yicha olish"""
        try:
            docs = self.pricing_plans_collection.where('plan_code', '==', plan_code).limit(1).stream()
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
        except Exception as e:
            print(f"Firestore get_plan_by_code error: {e}")
            return None
    
    def update_plan_price(self, plan_code: str, new_price: int) -> bool:
        """Tarif narxini yangilash"""
        try:
            docs = list(self.pricing_plans_collection.where('plan_code', '==', plan_code).limit(1).stream())
            if docs:
                docs[0].reference.update({'price': new_price})
                return True
            return False
        except Exception as e:
            print(f"Firestore update_plan_price error: {e}")
            return False
    
    def toggle_plan_active(self, plan_code: str) -> tuple:
        """Tarifni yoqish/o'chirish"""
        try:
            docs = list(self.pricing_plans_collection.where('plan_code', '==', plan_code).limit(1).stream())
            if docs:
                doc_ref = docs[0].reference
                current_data = docs[0].to_dict()
                new_status = not current_data.get('is_active', True)
                doc_ref.update({'is_active': new_status})
                return True, new_status
            return False, None
        except Exception as e:
            print(f"Firestore toggle_plan_active error: {e}")
            return False, None
    
    def init_default_plans(self):
        """Default tariflarni yaratish (agar yo'q bo'lsa)"""
        try:
            existing_plans = self.get_all_pricing_plans()
            if existing_plans:
                return  # Already initialized
            
            for plan in config.DEFAULT_PLANS:
                plan_data = {
                    'plan_code': plan['plan_code'],
                    'name': plan['name'],
                    'days': plan['days'],
                    'price': plan['price'],
                    'is_active': True,
                    'description': plan.get('description', ''),
                    'created_at': firestore.SERVER_TIMESTAMP
                }
                self.pricing_plans_collection.add(plan_data)
        except Exception as e:
            print(f"Firestore init_default_plans error: {e}")


class FirestoreReferralService:
    """Referral tizimi - Firestore"""
    
    def __init__(self):
        self.db = get_firestore_client()
        self.referrals_collection = self.db.collection(config.FIRESTORE_COLLECTIONS["referrals"])
        self.referral_codes_collection = self.db.collection(config.FIRESTORE_COLLECTIONS["referral_codes"])
    
    def get_or_create_code(self, user_id: int) -> str:
        """Referral kodni olish yoki yaratish"""
        try:
            doc = self.referral_codes_collection.document(str(user_id)).get()
            if doc.exists:
                return doc.get('code')
            else:
                code = f"ref{user_id}"
                self.referral_codes_collection.document(str(user_id)).set({'code': code})
                return code
        except Exception as e:
            print(f"Firestore get_or_create_code error: {e}")
            return f"ref{user_id}"
    
    def get_referral_count(self, user_id: int) -> int:
        """Referrallar sonini olish"""
        try:
            docs = self.referrals_collection.where('referrer_id', '==', user_id).stream()
            return len(list(docs))
        except Exception as e:
            print(f"Firestore get_referral_count error: {e}")
            return 0
    
    def add_referral(self, referrer_id: int, referred_id: int) -> tuple:
        """Yangi referral qo'shish"""
        if referrer_id == referred_id:
            return False, "O'zingizni referral qila olmaysiz"
        
        try:
            # Tekshirish - allaqachon mavjudmi?
            existing = list(self.referrals_collection.where('referred_id', '==', referred_id).limit(1).stream())
            if existing:
                return False, "Bu foydalanuvchi allaqachon referral"
            
            # Qo'shish
            referral_data = {
                'referrer_id': referrer_id,
                'referred_id': referred_id,
                'created_at': firestore.SERVER_TIMESTAMP
            }
            self.referrals_collection.add(referral_data)
            return True, "Referral qo'shildi"
        except Exception as e:
            return False, f"Xato: {str(e)}"
    
    def calculate_discount(self, user_id: int) -> int:
        """Referral asosida chegirma hisoblash"""
        count = self.get_referral_count(user_id)
        # Har bir referral uchun 2% chegirma, maksimal 80%
        discount = min(count * 2, 80)
        return discount
    
    def apply_discount(self, user_id: int, base_price: int) -> tuple:
        """Narxga chegirma qo'llash"""
        discount_percent = self.calculate_discount(user_id)
        
        if discount_percent > 0:
            discount_amount = int(base_price * discount_percent / 100)
            final_price = base_price - discount_amount
            return final_price, discount_percent
        
        return base_price, 0
    
    def get_referrer_from_code(self, code: str) -> Optional[int]:
        """Kod orqali referrer_id ni topish"""
        try:
            docs = self.referral_codes_collection.where('code', '==', code).limit(1).stream()
            for doc in docs:
                return int(doc.id)
            return None
        except Exception as e:
            print(f"Firestore get_referrer_from_code error: {e}")
            return None


# Global instances
firestore_trading_db = FirestoreTradingDB()
firestore_license_db = FirestoreLicenseDB()
firestore_referral_service = FirestoreReferralService()

