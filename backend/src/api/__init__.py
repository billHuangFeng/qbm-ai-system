"""
API包初始化
"""

from .router import api_router
from .middleware import setup_middleware

__all__ = ["api_router", "setup_middleware"]


