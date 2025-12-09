# ============================================
# REFERRAL SERVICE - Referral tizimi
# ============================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3

class ReferralService:
    """Referral tizimi (referrals.db bilan ishlash)"""
    
    def __init__(self):
        import config
        self.db_path = config.REFERRAL_DB_PATH
        self._init_db()
    
    def _init_db(self):
        """Database yaratish"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cur = conn.cursor()
        
        # Referrals jadvali
        cur.execute("""
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_id INTEGER NOT NULL,
            referred_id INTEGER UNIQUE NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
        """)
        
        # Referral kodlari jadvali
        cur.execute("""
        CREATE TABLE IF NOT EXISTS referral_codes (
            referrer_id INTEGER PRIMARY KEY,
            code TEXT NOT NULL
        )
        """)
        
        conn.commit()
        conn.close()
    
    def get_or_create_code(self, user_id):
        """Referral kodni olish yoki yaratish"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute("SELECT code FROM referral_codes WHERE referrer_id = ?", (user_id,))
        row = cur.fetchone()
        
        if row and row[0]:
            code = row[0]
        else:
            code = f"ref{user_id}"
            try:
                cur.execute("INSERT OR REPLACE INTO referral_codes (referrer_id, code) VALUES (?, ?)",
                           (user_id, code))
                conn.commit()
            except Exception:
                pass
        
        conn.close()
        return code
    
    def get_referral_count(self, user_id):
        """Referrallar sonini olish"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (user_id,))
        count = cur.fetchone()[0]
        
        conn.close()
        return count
    
    def add_referral(self, referrer_id, referred_id):
        """Yangi referral qo'shish"""
        if referrer_id == referred_id:
            return False, "O'zingizni referral qila olmaysiz"
        
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        try:
            cur.execute("INSERT INTO referrals (referrer_id, referred_id) VALUES (?, ?)",
                       (referrer_id, referred_id))
            conn.commit()
            conn.close()
            return True, "Referral qo'shildi"
        except sqlite3.IntegrityError:
            conn.close()
            return False, "Bu foydalanuvchi allaqachon referral"
        except Exception as e:
            conn.close()
            return False, f"Xato: {str(e)}"
    
    def calculate_discount(self, user_id):
        """Referral asosida chegirma hisoblash"""
        count = self.get_referral_count(user_id)
        
        # Har bir referral uchun 2% chegirma, maksimal 80%
        discount = min(count * 2, 80)
        
        return discount
    
    def apply_discount(self, user_id, base_price):
        """Narxga chegirma qo'llash"""
        discount_percent = self.calculate_discount(user_id)
        
        if discount_percent > 0:
            discount_amount = int(base_price * discount_percent / 100)
            final_price = base_price - discount_amount
            return final_price, discount_percent
        
        return base_price, 0
    
    def get_referrer_from_code(self, code):
        """Kod orqali referrer_id ni topish"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute("SELECT referrer_id FROM referral_codes WHERE code = ?", (code,))
        row = cur.fetchone()
        
        conn.close()
        
        if row:
            return row[0]
        return None


# Global instance
referral_service = ReferralService()