"""
产品管理API端点
"""
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....database import get_db
from ....crud import product
from ....schemas import Product, ProductCreate, ProductUpdate, ProductStats, PaginationParams, ResponseModel
from .auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=ResponseModel)
def read_products(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    pagination: PaginationParams = Depends(),
    category: Optional[str] = Query(None, description="产品类别筛选"),
    product_type: Optional[str] = Query(None, description="产品类型筛选"),
    is_featured: Optional[bool] = Query(None, description="推荐产品筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
) -> Any:
    """
    获取产品列表
    """
    # 构建过滤条件
    filters = {}
    if category:
        filters["product_category"] = category
    if product_type:
        filters["product_type"] = product_type
    if is_featured is not None:
        filters["is_featured"] = is_featured
    if status:
        filters["status"] = status
    
    if filters:
        products = product.filter_by(
            db,
            filters=filters,
            skip=(pagination.page - 1) * pagination.size,
            limit=pagination.size
        )
    else:
        products = product.get_multi(
            db,
            skip=(pagination.page - 1) * pagination.size,
            limit=pagination.size
        )
    
    total = product.count(db)
    
    return ResponseModel(
        data={
            "items": products,
            "total": total,
            "page": pagination.page,
            "size": pagination.size,
            "pages": (total + pagination.size - 1) // pagination.size
        }
    )

@router.post("/", response_model=Product)
def create_product(
    *,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    product_in: ProductCreate,
) -> Any:
    """
    创建新产品
    """
    # 检查产品编码是否已存在
    existing_product = product.get_by_code(db, product_code=product_in.product_code)
    if existing_product:
        raise HTTPException(
            status_code=400,
            detail="产品编码已存在"
        )
    
    product_obj = product.create(db, obj_in=product_in)
    return product_obj

@router.get("/{product_id}", response_model=Product)
def read_product_by_id(
    product_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    根据ID获取产品信息
    """
    product_obj = product.get(db, id=product_id)
    if not product_obj:
        raise HTTPException(
            status_code=404,
            detail="产品不存在"
        )
    
    return product_obj

@router.put("/{product_id}", response_model=Product)
def update_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    product_in: ProductUpdate,
    current_user = Depends(get_current_active_user),
) -> Any:
    """
    更新产品信息
    """
    product_obj = product.get(db, id=product_id)
    if not product_obj:
        raise HTTPException(
            status_code=404,
            detail="产品不存在"
        )
    
    product_obj = product.update(db, db_obj=product_obj, obj_in=product_in)
    return product_obj

@router.delete("/{product_id}")
def delete_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    current_user = Depends(get_current_active_user),
) -> Any:
    """
    删除产品
    """
    product_obj = product.get(db, id=product_id)
    if not product_obj:
        raise HTTPException(
            status_code=404,
            detail="产品不存在"
        )
    
    product.remove(db, id=product_id)
    return {"message": "产品删除成功"}

@router.get("/stats/overview", response_model=ResponseModel)
def get_product_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
) -> Any:
    """
    获取产品统计信息
    """
    stats = product.get_product_stats(db)
    return ResponseModel(data=stats)

@router.get("/featured/list", response_model=ResponseModel)
def get_featured_products(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    pagination: PaginationParams = Depends(),
) -> Any:
    """
    获取推荐产品列表
    """
    products = product.get_featured_products(
        db,
        skip=(pagination.page - 1) * pagination.size,
        limit=pagination.size
    )
    
    return ResponseModel(
        data={
            "items": products,
            "total": len(products),
            "page": pagination.page,
            "size": pagination.size,
            "pages": (len(products) + pagination.size - 1) // pagination.size
        }
    )
