# ============================================
# HELPERS - Database objectlar bilan ishlash uchun helper funksiyalar
# ============================================

from datetime import datetime
from typing import Any, Optional

def get_user_attr(user: Any, attr: str, default: Any = None) -> Any:
    """User object yoki dict dan attribute olish"""
    if user is None:
        return default
    
    if isinstance(user, dict):
        return user.get(attr, default)
    else:
        return getattr(user, attr, default)

def get_license_attr(license: Any, attr: str, default: Any = None) -> Any:
    """License object yoki dict dan attribute olish"""
    if license is None:
        return default
    
    if isinstance(license, dict):
        return license.get(attr, default)
    else:
        return getattr(license, attr, default)

def get_plan_attr(plan: Any, attr: str, default: Any = None) -> Any:
    """Plan object yoki dict dan attribute olish"""
    if plan is None:
        return default
    
    if isinstance(plan, dict):
        return plan.get(attr, default)
    else:
        return getattr(plan, attr, default)

def get_datetime_from_obj(obj: Any, attr: str) -> Optional[datetime]:
    """Object yoki dict dan datetime olish"""
    value = None
    
    if isinstance(obj, dict):
        value = obj.get(attr)
    else:
        value = getattr(obj, attr, None)
    
    if value is None:
        return None
    
    if isinstance(value, datetime):
        return value
    
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except:
            return None
    
    # Firestore Timestamp
    if hasattr(value, 'timestamp'):
        return datetime.fromtimestamp(value.timestamp())
    
    return None

