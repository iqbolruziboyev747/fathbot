# ============================================
# HANDLERS PACKAGE
# ============================================

from .start_handler import register_start_handlers
from .trading_handler import register_trading_handlers
from .license_handler import register_license_handlers
from .premium_handler import register_premium_handlers  # ← YANGI
from .admin_handler import register_admin_handlers

__all__ = [
    'register_start_handlers',
    'register_trading_handlers',
    'register_license_handlers',
    'register_premium_handlers',  # ← YANGI
    'register_admin_handlers',
]