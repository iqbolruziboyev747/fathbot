# ============================================
# TRADING DATABASE MODELS
# ============================================

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from datetime import datetime
from database.base import Base

class User(Base):
    """Foydalanuvchilar jadvali"""
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    is_vip = Column(Boolean, default=False)
    vip_until = Column(DateTime, nullable=True)  # 🔥 YANGI
    request_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Analysis(Base):
    """Tahlillar jadvali"""
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    analysis_type = Column(String)
    symbol = Column(String, nullable=True)
    analysis_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class EconomicData(Base):
    """Iqtisodiy ma'lumotlar jadvali"""
    __tablename__ = "economic_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    inflation = Column(String)
    fed_rate = Column(String)
    dollar_index = Column(String)
    unemployment = Column(String)
    gdp_growth = Column(String)
    btc_news = Column(Text)
    gold_news = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(Integer)

class InsiderNews(Base):
    """Insider yangiliklar jadvali"""
    __tablename__ = "insider_news"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    news_date = Column(String)
    news_name = Column(String)
    news_result = Column(String)
    accuracy = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer)