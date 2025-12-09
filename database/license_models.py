# ============================================
# LICENSE DATABASE MODELS
# ============================================

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from datetime import datetime
from database.base import Base

class License(Base):
    """Litsenziyalar jadvali"""
    __tablename__ = "licenses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    license_id = Column(String, unique=True, index=True)
    token = Column(String, unique=True, index=True)
    issued_at = Column(DateTime)
    valid_until = Column(DateTime)
    revoked = Column(Boolean, default=False)
    is_trial = Column(Boolean, default=False)
    device_fp = Column(String, index=True)  # Account raqami
    telegram_id = Column(Integer, index=True)
    plan_code = Column(String, nullable=True)  # 🔥 YANGI

class PricingPlan(Base):
    """Tarif narxlari jadvali"""
    __tablename__ = "pricing_plans"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_code = Column(String, unique=True)
    name = Column(String)
    days = Column(Integer)
    price = Column(Integer)
    is_active = Column(Boolean, default=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Referral(Base):
    """Referral jadvali"""
    __tablename__ = "referrals"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    referrer_id = Column(Integer)
    referred_id = Column(Integer, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ReferralCode(Base):
    """Referral kodlari jadvali"""
    __tablename__ = "referral_codes"
    
    referrer_id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)