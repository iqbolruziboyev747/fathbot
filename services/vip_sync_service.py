# ============================================
# VIP SYNC SERVICE - Litsenziya va VIP sinxronizatsiya (TUZATILGAN)
# ============================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from services.database_service import trading_db, license_db

class VIPSyncService:
    """VIP va Litsenziya sinxronizatsiyasi"""
    
    def __init__(self):
        self.trading_db = trading_db
        self.license_db = license_db
    
    async def sync_user_vip_status(self, user_id):
        """
        User uchun VIP statusni litsenziya bilan sinxronlashtirish
        
        Returns:
            tuple: (is_vip: bool, message: str, vip_until: datetime)
        """
        # Debug logging
        print(f"\n[VIP_SYNC] User {user_id} uchun VIP tekshirilmoqda...")
        
        # Aktiv litsenziyani tekshirish
        license = self.license_db.get_active_license(user_id)
        print(f"[VIP_SYNC] License DB: {license}")
        
        if license and not license.revoked:
            # Muddat tugamaganmi?
            if license.valid_until > datetime.now():
                # VIP statusni litsenziya muddatigacha berish
                self.trading_db.set_vip_status(
                    user_id, 
                    is_vip=True,
                    vip_until=license.valid_until
                )
                
                # Request count ni 0 ga qaytarish (VIP bo'lganda)
                self.trading_db.reset_request_count(user_id)
                
                days_left = (license.valid_until - datetime.now()).days
                print(f"[VIP_SYNC] ✅ License topildi: {days_left} kun")
                return True, f"✅ VIP faol: {license.valid_until.strftime('%Y-%m-%d')} gacha ({days_left} kun)", license.valid_until
            else:
                # Muddat tugagan
                print(f"[VIP_SYNC] ⚠️ License muddati tugagan")
                self.trading_db.set_vip_status(user_id, is_vip=False, vip_until=None)
                return False, "⚠️ VIP muddat tugadi! Yangi litsenziya sotib oling.", None
        else:
            # ⭐ MUHIM: Litsenziya yo'q bo'lsa, Trading DB ni tekshirish
            # Admin to'g'ridan-to'g'ri VIP bergan bo'lishi mumkin
            print(f"[VIP_SYNC] License DB da topilmadi, Trading DB tekshirilmoqda...")
            user = self.trading_db.get_user(user_id)
            
            if user and user.is_vip:
                # Trading DB da VIP bor, lekin License DB da yo'q
                # Bu admin to'g'ridan-to'g'ri VIP bergan degani
                # Shuning uchun o'chirmaymiz!
                print(f"[VIP_SYNC] Trading DB da VIP topildi: is_vip={user.is_vip}, vip_until={user.vip_until}")
                
                if user.vip_until and user.vip_until > datetime.now():
                    days_left = (user.vip_until - datetime.now()).days
                    print(f"[VIP_SYNC] ✅ Admin VIP: {days_left} kun")
                    
                    # Request count ni reset qilish
                    self.trading_db.reset_request_count(user_id)
                    
                    return True, f"✅ VIP faol (Admin): {user.vip_until.strftime('%Y-%m-%d')} gacha ({days_left} kun)", user.vip_until
                else:
                    print(f"[VIP_SYNC] ⚠️ VIP muddati tugagan")
            
            # Agar Trading DB da ham VIP yo'q bo'lsa, yo'q deb qaytarish
            print(f"[VIP_SYNC] ❌ VIP yo'q")
            return False, "❌ Sizda aktiv litsenziya yo'q", None
    
    async def check_vip_and_notify(self, user_id):
        """
        VIP statusni tekshirish va agar kerak bo'lsa ogohlantirish
        
        Returns:
            tuple: (is_vip: bool, can_use_features: bool, message: str)
        """
        # AVVAL sinxronlashtirish - bu muhim!
        await self.sync_user_vip_status(user_id)
        
        # Yangilangan ma'lumotni olish
        user = self.trading_db.get_user(user_id)
        
        if not user:
            # Yangi user yaratish
            self.trading_db.create_or_update_user(user_id, None, None)
            return False, True, "✅ Yangi foydalanuvchi - 3 ta bepul so'rov"
        
        if user.is_vip:
            # VIP muddat tekshirish
            if user.vip_until and user.vip_until < datetime.now():
                self.trading_db.set_vip_status(user_id, is_vip=False, vip_until=None)
                return False, False, "⚠️ VIP muddat tugadi!"
            
            days_left = (user.vip_until - datetime.now()).days if user.vip_until else 0
            
            # Ogohlantirish - 3 kun qolganda
            if days_left <= 3:
                warning = f"\n\n⚠️ Diqqat! VIP muddatingiz {days_left} kun ichida tugaydi!"
                return True, True, f"✅ VIP faol{warning}"
            
            return True, True, f"✅ VIP faol: {user.vip_until.strftime('%Y-%m-%d')} gacha"
        
        # Oddiy foydalanuvchi - bepul limitni tekshirish
        can_request, message = self.trading_db.can_make_request(user_id)
        return False, can_request, message
    
    async def auto_sync_all_expired(self):
        """
        Barcha foydalanuvchilarning VIP statusini tekshirish
        (Background task uchun)
        """
        all_users = self.trading_db.get_all_users()
        expired_count = 0
        
        for user in all_users:
            if user.is_vip and user.vip_until:
                if user.vip_until < datetime.now():
                    self.trading_db.set_vip_status(user.user_id, is_vip=False, vip_until=None)
                    expired_count += 1
        
        return expired_count


# Global instance
vip_sync = VIPSyncService()
