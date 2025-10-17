"""
CRUD操作包
提供数据库的增删改查操作
"""

from .base import CRUDBase
from .user import user
from .customer import customer
from .product import product
from .contract import contract
from .order import order
from .financial import financial
from .analysis_result import analysis_result
from .data_import_log import data_import_log

__all__ = [
    'CRUDBase',
    'user',
    'customer', 
    'product',
    'contract',
    'order',
    'financial',
    'analysis_result',
    'data_import_log'
]
