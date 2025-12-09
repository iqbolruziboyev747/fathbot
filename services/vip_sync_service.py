# ============================================
# VIP SYNC SERVICE - Litsenziya va VIP sinxronizatsiya
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
        # Aktiv litsenziyani tekshirish
        license = self.license_db.get_active_license(user_id)
        
        # License dict yoki object bo'lishi mumkin
        if license:
            revoked = license.get('revoked', False) if isinstance(license, dict) else license.revoked
            if not revoked:
                # Valid until ni olish
                valid_until = license.get('valid_until') if isinstance(license, dict) else license.valid_until
                
                # Datetime ga convert qilish
                if isinstance(valid_until, str):
                    valid_until = datetime.fromisoformat(valid_until)
                
                # Muddat tugamaganmi?
                if valid_until and valid_until > datetime.now():
                    # VIP statusni litsenziya muddatigacha berish
                    self.trading_db.set_vip_status(
                        user_id, 
                        is_vip=True,
                        vip_until=valid_until
                    )
                    
                    days_left = (valid_until - datetime.now()).days
                    return True, f"✅ VIP faol: {valid_until.strftime('%Y-%m-%d')} gacha ({days_left} kun)", valid_until
                else:
                    # Muddat tugagan
                    self.trading_db.set_vip_status(user_id, is_vip=False, vip_until=None)
                    return False, "⚠️ VIP muddat tugadi! Yangi litsenziya sotib oling.", None
        
        # Litsenziya yo'q
        self.trading_db.set_vip_status(user_id, is_vip=False, vip_until=None)
        return False, "❌ Sizda aktiv litsenziya yo'q", None
    
    async def check_vip_and_notify(self, user_id):
        """
        VIP statusni tekshirish va agar kerak bo'lsa ogohlantirish
        
        Returns:
            tuple: (is_vip: bool, can_use_features: bool, message: str)
        """
        user = self.trading_db.get_user(user_id)
        
        if not user:
            return False, True, "✅ Yangi foydalanuvchi - 3 ta bepul so'rov"
        
        # Avval sinxronlashtirish
        await self.sync_user_vip_status(user_id)
        
        # Yangilangan ma'lumotni olish
        user = self.trading_db.get_user(user_id)
        
        # User dict yoki object bo'lishi mumkin
        is_vip = user.get('is_vip', False) if isinstance(user, dict) else (user.is_vip if user else False)
        
        if is_vip:
            # VIP muddat tekshirish
            vip_until = user.get('vip_until') if isinstance(user, dict) else (user.vip_until if user else None)
            
            # Datetime ga convert qilish
            if isinstance(vip_until, str):
                vip_until = datetime.fromisoformat(vip_until)
            
            if vip_until and vip_until < datetime.now():
                self.trading_db.set_vip_status(user_id, is_vip=False, vip_until=None)
                return False, False, "⚠️ VIP muddat tugadi!"
            
            days_left = (vip_until - datetime.now()).days if vip_until else 0
            
            # Ogohlantirish - 3 kun qolganda
            if days_left <= 3:
                warning = f"\n\n⚠️ Diqqat! VIP muddatingiz {days_left} kun ichida tugaydi!"
                return True, True, f"✅ VIP faol{warning}"
            
            return True, True, f"✅ VIP faol: {vip_until.strftime('%Y-%m-%d')} gacha" if vip_until else "✅ VIP faol"
        
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
            # User dict yoki object bo'lishi mumkin
            user_id = user.get('user_id') if isinstance(user, dict) else user.user_id
            is_vip = user.get('is_vip', False) if isinstance(user, dict) else user.is_vip
            vip_until = user.get('vip_until') if isinstance(user, dict) else user.vip_until
            
            if is_vip and vip_until:
                # Datetime ga convert qilish
                if isinstance(vip_until, str):
                    vip_until = datetime.fromisoformat(vip_until)
                
                if vip_until < datetime.now():
                    self.trading_db.set_vip_status(user_id, is_vip=False, vip_until=None)
                    expired_count += 1
        
        return expired_count


# Global instance
vip_sync = VIPSyncService()