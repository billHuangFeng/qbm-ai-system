"""
客户CRUD操作
"""
from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from decimal import Decimal

from .base import CRUDBase
from ..models.customer import Customer
from ..schemas.customer import CustomerCreate, CustomerUpdate

class CRUDCustomer(CRUDBase[Customer, CustomerCreate, CustomerUpdate]):
    """客户CRUD操作类"""
    
    def get_by_code(self, db: Session, *, customer_code: str) -> Optional[Customer]:
        """根据客户编码获取客户"""
        return db.query(Customer).filter(Customer.customer_code == customer_code).first()
    
    def get_by_name(self, db: Session, *, customer_name: str) -> Optional[Customer]:
        """根据客户名称获取客户"""
        return db.query(Customer).filter(Customer.customer_name == customer_name).first()
    
    def get_vip_customers(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Customer]:
        """获取VIP客户列表"""
        return db.query(Customer).filter(Customer.is_vip == True).offset(skip).limit(limit).all()
    
    def get_active_customers(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Customer]:
        """获取活跃客户列表"""
        return db.query(Customer).filter(Customer.status == "active").offset(skip).limit(limit).all()
    
    def get_by_industry(self, db: Session, *, industry: str, skip: int = 0, limit: int = 100) -> List[Customer]:
        """根据行业获取客户列表"""
        return db.query(Customer).filter(Customer.industry == industry).offset(skip).limit(limit).all()
    
    def get_by_company_size(self, db: Session, *, company_size: str, skip: int = 0, limit: int = 100) -> List[Customer]:
        """根据公司规模获取客户列表"""
        return db.query(Customer).filter(Customer.company_size == company_size).offset(skip).limit(limit).all()
    
    def search_customers(
        self, 
        db: Session, 
        *, 
        search_term: str,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Customer]:
        """搜索客户"""
        return db.query(Customer).filter(
            or_(
                Customer.customer_code.ilike(f"%{search_term}%"),
                Customer.customer_name.ilike(f"%{search_term}%"),
                Customer.contact_person.ilike(f"%{search_term}%"),
                Customer.industry.ilike(f"%{search_term}%")
            )
        ).offset(skip).limit(limit).all()
    
    def get_high_value_customers(
        self, 
        db: Session, 
        *, 
        min_value: Decimal = Decimal("100000"),
        skip: int = 0, 
        limit: int = 100
    ) -> List[Customer]:
        """获取高价值客户"""
        return db.query(Customer).filter(
            Customer.customer_lifetime_value >= min_value
        ).offset(skip).limit(limit).all()
    
    def get_customer_stats(self, db: Session) -> Dict[str, Any]:
        """获取客户统计信息"""
        total_customers = db.query(Customer).count()
        active_customers = db.query(Customer).filter(Customer.status == "active").count()
        vip_customers = db.query(Customer).filter(Customer.is_vip == True).count()
        
        # 计算平均值
        avg_value_score = db.query(func.avg(Customer.customer_value_score)).scalar()
        avg_lifetime_value = db.query(func.avg(Customer.customer_lifetime_value)).scalar()
        avg_satisfaction = db.query(func.avg(Customer.customer_satisfaction)).scalar()
        avg_retention_rate = db.query(func.avg(Customer.customer_retention_rate)).scalar()
        
        return {
            "total_customers": total_customers,
            "active_customers": active_customers,
            "vip_customers": vip_customers,
            "average_value_score": float(avg_value_score) if avg_value_score else None,
            "average_lifetime_value": float(avg_lifetime_value) if avg_lifetime_value else None,
            "average_satisfaction": float(avg_satisfaction) if avg_satisfaction else None,
            "average_retention_rate": float(avg_retention_rate) if avg_retention_rate else None,
        }
    
    def get_customers_by_region(
        self, 
        db: Session, 
        *, 
        province: Optional[str] = None,
        city: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Customer]:
        """根据地区获取客户列表"""
        query = db.query(Customer)
        
        if province:
            query = query.filter(Customer.province == province)
        if city:
            query = query.filter(Customer.city == city)
        
        return query.offset(skip).limit(limit).all()
    
    def update_customer_value_metrics(
        self,
        db: Session,
        *,
        customer_id: int,
        value_score: Optional[Decimal] = None,
        lifetime_value: Optional[Decimal] = None,
        satisfaction: Optional[Decimal] = None,
        retention_rate: Optional[Decimal] = None
    ) -> Optional[Customer]:
        """更新客户价值指标"""
        customer = self.get(db, id=customer_id)
        if not customer:
            return None
        
        if value_score is not None:
            customer.customer_value_score = value_score
        if lifetime_value is not None:
            customer.customer_lifetime_value = lifetime_value
        if satisfaction is not None:
            customer.customer_satisfaction = satisfaction
        if retention_rate is not None:
            customer.customer_retention_rate = retention_rate
        
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer

# 创建客户CRUD实例
customer = CRUDCustomer(Customer)
