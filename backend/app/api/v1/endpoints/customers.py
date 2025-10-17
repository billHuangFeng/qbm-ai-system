"""
客户管理API端点
"""
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....database import get_db
from ....crud import customer
from ....schemas import Customer, CustomerCreate, CustomerUpdate, CustomerStats, PaginationParams, ResponseModel
from .auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=ResponseModel)
def read_customers(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    pagination: PaginationParams = Depends(),
    industry: Optional[str] = Query(None, description="行业筛选"),
    company_size: Optional[str] = Query(None, description="公司规模筛选"),
    is_vip: Optional[bool] = Query(None, description="VIP客户筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
) -> Any:
    """
    获取客户列表
    """
    # 构建过滤条件
    filters = {}
    if industry:
        filters["industry"] = industry
    if company_size:
        filters["company_size"] = company_size
    if is_vip is not None:
        filters["is_vip"] = is_vip
    if status:
        filters["status"] = status
    
    if filters:
        customers = customer.filter_by(
            db,
            filters=filters,
            skip=(pagination.page - 1) * pagination.size,
            limit=pagination.size
        )
    else:
        customers = customer.get_multi(
            db,
            skip=(pagination.page - 1) * pagination.size,
            limit=pagination.size
        )
    
    total = customer.count(db)
    
    return ResponseModel(
        data={
            "items": customers,
            "total": total,
            "page": pagination.page,
            "size": pagination.size,
            "pages": (total + pagination.size - 1) // pagination.size
        }
    )

@router.post("/", response_model=Customer)
def create_customer(
    *,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    customer_in: CustomerCreate,
) -> Any:
    """
    创建新客户
    """
    # 检查客户编码是否已存在
    existing_customer = customer.get_by_code(db, customer_code=customer_in.customer_code)
    if existing_customer:
        raise HTTPException(
            status_code=400,
            detail="客户编码已存在"
        )
    
    customer_obj = customer.create(db, obj_in=customer_in)
    return customer_obj

@router.get("/{customer_id}", response_model=Customer)
def read_customer_by_id(
    customer_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    根据ID获取客户信息
    """
    customer_obj = customer.get(db, id=customer_id)
    if not customer_obj:
        raise HTTPException(
            status_code=404,
            detail="客户不存在"
        )
    
    return customer_obj

@router.put("/{customer_id}", response_model=Customer)
def update_customer(
    *,
    db: Session = Depends(get_db),
    customer_id: int,
    customer_in: CustomerUpdate,
    current_user = Depends(get_current_active_user),
) -> Any:
    """
    更新客户信息
    """
    customer_obj = customer.get(db, id=customer_id)
    if not customer_obj:
        raise HTTPException(
            status_code=404,
            detail="客户不存在"
        )
    
    customer_obj = customer.update(db, db_obj=customer_obj, obj_in=customer_in)
    return customer_obj

@router.delete("/{customer_id}")
def delete_customer(
    *,
    db: Session = Depends(get_db),
    customer_id: int,
    current_user = Depends(get_current_active_user),
) -> Any:
    """
    删除客户
    """
    customer_obj = customer.get(db, id=customer_id)
    if not customer_obj:
        raise HTTPException(
            status_code=404,
            detail="客户不存在"
        )
    
    customer.remove(db, id=customer_id)
    return {"message": "客户删除成功"}

@router.get("/search/", response_model=ResponseModel)
def search_customers(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    q: str = Query(..., description="搜索关键词"),
    pagination: PaginationParams = Depends(),
) -> Any:
    """
    搜索客户
    """
    customers = customer.search_customers(
        db,
        search_term=q,
        skip=(pagination.page - 1) * pagination.size,
        limit=pagination.size
    )
    
    return ResponseModel(
        data={
            "items": customers,
            "total": len(customers),
            "page": pagination.page,
            "size": pagination.size,
            "pages": (len(customers) + pagination.size - 1) // pagination.size
        }
    )

@router.get("/vip/list", response_model=ResponseModel)
def get_vip_customers(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    pagination: PaginationParams = Depends(),
) -> Any:
    """
    获取VIP客户列表
    """
    customers = customer.get_vip_customers(
        db,
        skip=(pagination.page - 1) * pagination.size,
        limit=pagination.size
    )
    
    return ResponseModel(
        data={
            "items": customers,
            "total": len(customers),
            "page": pagination.page,
            "size": pagination.size,
            "pages": (len(customers) + pagination.size - 1) // pagination.size
        }
    )

@router.get("/high-value/list", response_model=ResponseModel)
def get_high_value_customers(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    min_value: float = Query(100000, description="最小价值"),
    pagination: PaginationParams = Depends(),
) -> Any:
    """
    获取高价值客户列表
    """
    from decimal import Decimal
    customers = customer.get_high_value_customers(
        db,
        min_value=Decimal(str(min_value)),
        skip=(pagination.page - 1) * pagination.size,
        limit=pagination.size
    )
    
    return ResponseModel(
        data={
            "items": customers,
            "total": len(customers),
            "page": pagination.page,
            "size": pagination.size,
            "pages": (len(customers) + pagination.size - 1) // pagination.size
        }
    )

@router.get("/stats/overview", response_model=ResponseModel)
def get_customer_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
) -> Any:
    """
    获取客户统计信息
    """
    stats = customer.get_customer_stats(db)
    return ResponseModel(data=stats)

@router.get("/by-industry/{industry}", response_model=ResponseModel)
def get_customers_by_industry(
    industry: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    pagination: PaginationParams = Depends(),
) -> Any:
    """
    根据行业获取客户列表
    """
    customers = customer.get_by_industry(
        db,
        industry=industry,
        skip=(pagination.page - 1) * pagination.size,
        limit=pagination.size
    )
    
    return ResponseModel(
        data={
            "items": customers,
            "total": len(customers),
            "page": pagination.page,
            "size": pagination.size,
            "pages": (len(customers) + pagination.size - 1) // pagination.size
        }
    )

@router.get("/by-region/", response_model=ResponseModel)
def get_customers_by_region(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    province: Optional[str] = Query(None, description="省份"),
    city: Optional[str] = Query(None, description="城市"),
    pagination: PaginationParams = Depends(),
) -> Any:
    """
    根据地区获取客户列表
    """
    customers = customer.get_customers_by_region(
        db,
        province=province,
        city=city,
        skip=(pagination.page - 1) * pagination.size,
        limit=pagination.size
    )
    
    return ResponseModel(
        data={
            "items": customers,
            "total": len(customers),
            "page": pagination.page,
            "size": pagination.size,
            "pages": (len(customers) + pagination.size - 1) // pagination.size
        }
    )
