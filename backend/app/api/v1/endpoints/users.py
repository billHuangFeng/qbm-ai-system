"""
用户管理API端点
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....database import get_db
from ....crud import user
from ....schemas import User, UserCreate, UserUpdate, PaginationParams, ResponseModel
from .auth import get_current_active_user, get_current_active_admin

router = APIRouter()

@router.get("/", response_model=ResponseModel)
def read_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
    pagination: PaginationParams = Depends(),
) -> Any:
    """
    获取用户列表（管理员权限）
    """
    users = user.get_multi(
        db, 
        skip=(pagination.page - 1) * pagination.size, 
        limit=pagination.size
    )
    total = user.count(db)
    
    return ResponseModel(
        data={
            "items": users,
            "total": total,
            "page": pagination.page,
            "size": pagination.size,
            "pages": (total + pagination.size - 1) // pagination.size
        }
    )

@router.post("/", response_model=User)
def create_user(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
    user_in: UserCreate,
) -> Any:
    """
    创建新用户（管理员权限）
    """
    # 检查用户名是否已存在
    existing_user = user.get_by_username(db, username=user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    existing_user = user.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="邮箱已存在"
        )
    
    user_obj = user.create(db, obj_in=user_in)
    return user_obj

@router.get("/{user_id}", response_model=User)
def read_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    根据ID获取用户信息
    """
    user_obj = user.get(db, id=user_id)
    if not user_obj:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )
    
    # 非管理员只能查看自己的信息
    if not user.is_admin(current_user) and user_obj.id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="权限不足"
        )
    
    return user_obj

@router.put("/{user_id}", response_model=User)
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    更新用户信息
    """
    user_obj = user.get(db, id=user_id)
    if not user_obj:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )
    
    # 非管理员只能更新自己的信息，且不能修改管理员权限
    if not user.is_admin(current_user):
        if user_obj.id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="权限不足"
            )
        # 移除管理员权限相关字段
        if hasattr(user_in, 'is_admin'):
            user_in.is_admin = None
    
    user_obj = user.update(db, db_obj=user_obj, obj_in=user_in)
    return user_obj

@router.delete("/{user_id}")
def delete_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user: User = Depends(get_current_active_admin),
) -> Any:
    """
    删除用户（管理员权限）
    """
    user_obj = user.get(db, id=user_id)
    if not user_obj:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )
    
    # 不能删除自己
    if user_obj.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="不能删除自己的账户"
        )
    
    user.remove(db, id=user_id)
    return {"message": "用户删除成功"}

@router.get("/search/", response_model=ResponseModel)
def search_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
    q: str = Query(..., description="搜索关键词"),
    pagination: PaginationParams = Depends(),
) -> Any:
    """
    搜索用户（管理员权限）
    """
    users = user.search_users(
        db,
        search_term=q,
        skip=(pagination.page - 1) * pagination.size,
        limit=pagination.size
    )
    
    return ResponseModel(
        data={
            "items": users,
            "total": len(users),
            "page": pagination.page,
            "size": pagination.size,
            "pages": (len(users) + pagination.size - 1) // pagination.size
        }
    )

@router.get("/stats/overview")
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
) -> Any:
    """
    获取用户统计信息（管理员权限）
    """
    total_users = user.count(db)
    active_users = len(user.get_active_users(db))
    admin_users = len(user.get_admin_users(db))
    
    return ResponseModel(
        data={
            "total_users": total_users,
            "active_users": active_users,
            "admin_users": admin_users,
            "inactive_users": total_users - active_users
        }
    )
