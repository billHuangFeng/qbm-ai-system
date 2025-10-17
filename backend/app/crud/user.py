"""
用户CRUD操作
"""
from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from .base import CRUDBase
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """用户CRUD操作类"""
    
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return db.query(User).filter(User.username == username).first()
    
    def get_by_email_or_username(
        self, db: Session, *, email_or_username: str
    ) -> Optional[User]:
        """根据邮箱或用户名获取用户"""
        return db.query(User).filter(
            or_(User.email == email_or_username, User.username == email_or_username)
        ).first()
    
    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """创建用户"""
        # 这里应该对密码进行哈希处理
        # 在实际应用中，您需要使用passlib等库来哈希密码
        db_obj = User(
            username=obj_in.username,
            email=obj_in.email,
            password_hash=obj_in.password,  # 实际应用中应该哈希密码
            full_name=obj_in.full_name,
            phone=obj_in.phone,
            is_active=obj_in.is_active,
            is_admin=obj_in.is_admin,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self,
        db: Session,
        *,
        db_obj: User,
        obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """更新用户"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        # 如果更新密码，需要哈希处理
        if "password" in update_data:
            # 实际应用中应该哈希密码
            update_data["password_hash"] = update_data.pop("password")
        
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def authenticate(self, db: Session, *, username: str, password: str) -> Optional[User]:
        """用户认证"""
        user = self.get_by_email_or_username(db, email_or_username=username)
        if not user:
            return None
        # 实际应用中应该验证密码哈希
        if user.password_hash == password:  # 这里应该使用密码验证
            return user
        return None
    
    def is_active(self, user: User) -> bool:
        """检查用户是否激活"""
        return user.is_active
    
    def is_admin(self, user: User) -> bool:
        """检查用户是否为管理员"""
        return user.is_admin
    
    def get_active_users(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[User]:
        """获取激活用户列表"""
        return db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()
    
    def get_admin_users(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[User]:
        """获取管理员用户列表"""
        return db.query(User).filter(User.is_admin == True).offset(skip).limit(limit).all()
    
    def search_users(
        self, 
        db: Session, 
        *, 
        search_term: str,
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """搜索用户"""
        return db.query(User).filter(
            or_(
                User.username.ilike(f"%{search_term}%"),
                User.email.ilike(f"%{search_term}%"),
                User.full_name.ilike(f"%{search_term}%")
            )
        ).offset(skip).limit(limit).all()

# 创建用户CRUD实例
user = CRUDUser(User)
