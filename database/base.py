# ============================================
# DATABASE BASE - Asosiy database sozlamalari
# ============================================

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import config

# Trading database
trading_engine = create_engine(
    f"sqlite:///{config.TRADING_DB_PATH}", 
    echo=False
)
TradingSessionLocal = sessionmaker(bind=trading_engine)

# License database
license_engine = create_engine(
    f"sqlite:///{config.LICENSE_DB_PATH}", 
    echo=False
)
LicenseSessionLocal = sessionmaker(bind=license_engine)

# Base class
Base = declarative_base()