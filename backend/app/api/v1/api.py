"""
API v1路由汇总
"""
from fastapi import APIRouter

from .endpoints import auth, users, customers, products, contracts, orders, financials, analysis, data_import

api_router = APIRouter()

# 认证相关路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 用户管理路由
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])

# 客户管理路由
api_router.include_router(customers.router, prefix="/customers", tags=["客户管理"])

# 产品管理路由
api_router.include_router(products.router, prefix="/products", tags=["产品管理"])

# 合同管理路由
api_router.include_router(contracts.router, prefix="/contracts", tags=["合同管理"])

# 订单管理路由
api_router.include_router(orders.router, prefix="/orders", tags=["订单管理"])

# 财务管理路由
api_router.include_router(financials.router, prefix="/financials", tags=["财务管理"])

# 分析结果路由
api_router.include_router(analysis.router, prefix="/analysis", tags=["分析结果"])

# 数据导入路由
api_router.include_router(data_import.router, prefix="/data-import", tags=["数据导入"])
