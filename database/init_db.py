# ============================================
# DATABASE INITIALIZATION (YANGILANGAN)
# ============================================

import sys
import os

# Python ga joriy papkani ko'rsatish
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database modellarini import qilish
from database.base import Base, trading_engine, license_engine
from database.trading_models import User, Analysis, EconomicData, InsiderNews
from database.license_models import License, PricingPlan, Referral, ReferralCode

def init_trading_database():
    """Trading database ni yaratish va boshlang'ich ma'lumotlar"""
    print("🔧 Trading database yaratilmoqda...")
    
    # Jadvallarni yaratish
    Base.metadata.create_all(bind=trading_engine)
    
    # Boshlang'ich iqtisodiy ma'lumotlar
    SessionLocal = sessionmaker(bind=trading_engine)
    session = SessionLocal()
    
    try:
        existing_data = session.query(EconomicData).first()
        if not existing_data:
            economic_data = EconomicData(
                inflation='3.2%',
                fed_rate='5.25-5.5%',
                dollar_index='104.8',
                unemployment='3.8%',
                gdp_growth='2.1%',
                btc_news='Bitcoin ETF oqimlari: So\'nggi haftada $500M kirim|FED raisi bayonoti: Foiz stavkalari barqaror|Global regulyator: Kripto qonunchiligi muhokamasi',
                gold_news='Oltin narxi: Markaziy banklar zaxira o\'sishi|Inflyatsiya: So\'nggi ma\'lumotlar ijobiy|Geosiyosiy: Yaqin Sharq vaziyati ta\'siri',
                updated_by=config.ADMINS[0]
            )
            session.add(economic_data)
            session.commit()
            print("✅ Boshlang'ich iqtisodiy ma'lumotlar qo'shildi")
    finally:
        session.close()
    
    print("✅ Trading database tayyor!")

def init_license_database():
    """License database ni yaratish va boshlang'ich ma'lumotlar"""
    print("🔧 License database yaratilmoqda...")
    
    # Jadvallarni yaratish
    Base.metadata.create_all(bind=license_engine)
    
    # Boshlang'ich tarif narxlari
    SessionLocal = sessionmaker(bind=license_engine)
    session = SessionLocal()
    
    try:
        existing_plans = session.query(PricingPlan).count()
        if existing_plans == 0:
            for plan_data in config.DEFAULT_PLANS:
                plan = PricingPlan(**plan_data)
                session.add(plan)
            session.commit()
            print(f"✅ {len(config.DEFAULT_PLANS)} ta tarif qo'shildi")
    finally:
        session.close()
    
    print("✅ License database tayyor!")

def initialize_all_databases():
    """Barcha databaselarni yaratish"""
    print("\n" + "="*50)
    print("📊 DATABASE INITIALIZATION")
    print("="*50 + "\n")
    
    init_trading_database()
    print()
    init_license_database()
    
    print("\n" + "="*50)
    print("🎉 BARCHA DATABASELAR TAYYOR!")
    print("="*50 + "\n")

if __name__ == "__main__":
    initialize_all_databases()