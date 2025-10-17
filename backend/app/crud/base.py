"""
基础CRUD操作类
"""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """基础CRUD操作类"""
    
    def __init__(self, model: Type[ModelType]):
        """
        CRUD对象，具有默认的创建、读取、更新和删除操作。
        
        **参数**
        * `model`: SQLAlchemy模型类
        * `schema`: Pydantic模型（模式）类
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """根据ID获取单个记录"""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """获取多个记录"""
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """创建新记录"""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """更新记录"""
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        """删除记录"""
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def count(self, db: Session) -> int:
        """统计记录总数"""
        return db.query(self.model).count()

    def search(
        self, 
        db: Session, 
        *, 
        search_term: str, 
        search_fields: List[str],
        skip: int = 0, 
        limit: int = 100
    ) -> List[ModelType]:
        """搜索记录"""
        if not search_term or not search_fields:
            return self.get_multi(db, skip=skip, limit=limit)
        
        # 构建搜索条件
        search_conditions = []
        for field in search_fields:
            if hasattr(self.model, field):
                search_conditions.append(
                    getattr(self.model, field).ilike(f"%{search_term}%")
                )
        
        if search_conditions:
            return db.query(self.model).filter(
                or_(*search_conditions)
            ).offset(skip).limit(limit).all()
        else:
            return []

    def filter_by(
        self, 
        db: Session, 
        *, 
        filters: Dict[str, Any],
        skip: int = 0, 
        limit: int = 100
    ) -> List[ModelType]:
        """根据条件过滤记录"""
        query = db.query(self.model)
        
        for field, value in filters.items():
            if hasattr(self.model, field) and value is not None:
                query = query.filter(getattr(self.model, field) == value)
        
        return query.offset(skip).limit(limit).all()

    def get_by_field(
        self, 
        db: Session, 
        *, 
        field: str, 
        value: Any
    ) -> Optional[ModelType]:
        """根据字段值获取记录"""
        if hasattr(self.model, field):
            return db.query(self.model).filter(
                getattr(self.model, field) == value
            ).first()
        return None
