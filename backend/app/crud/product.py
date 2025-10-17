"""
产品CRUD操作
"""
from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from decimal import Decimal

from .base import CRUDBase
from ..models.product import Product
from ..schemas.product import ProductCreate, ProductUpdate

class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    """产品CRUD操作类"""
    
    def get_by_code(self, db: Session, *, product_code: str) -> Optional[Product]:
        """根据产品编码获取产品"""
        return db.query(Product).filter(Product.product_code == product_code).first()
    
    def get_by_name(self, db: Session, *, product_name: str) -> Optional[Product]:
        """根据产品名称获取产品"""
        return db.query(Product).filter(Product.product_name == product_name).first()
    
    def get_by_category(self, db: Session, *, category: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """根据产品类别获取产品列表"""
        return db.query(Product).filter(Product.product_category == category).offset(skip).limit(limit).all()
    
    def get_by_type(self, db: Session, *, product_type: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """根据产品类型获取产品列表"""
        return db.query(Product).filter(Product.product_type == product_type).offset(skip).limit(limit).all()
    
    def get_featured_products(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Product]:
        """获取推荐产品列表"""
        return db.query(Product).filter(Product.is_featured == True).offset(skip).limit(limit).all()
    
    def get_active_products(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Product]:
        """获取活跃产品列表"""
        return db.query(Product).filter(Product.status == "active").offset(skip).limit(limit).all()
    
    def get_by_lifecycle_stage(self, db: Session, *, stage: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """根据生命周期阶段获取产品列表"""
        return db.query(Product).filter(Product.lifecycle_stage == stage).offset(skip).limit(limit).all()
    
    def search_products(
        self, 
        db: Session, 
        *, 
        search_term: str,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Product]:
        """搜索产品"""
        return db.query(Product).filter(
            or_(
                Product.product_code.ilike(f"%{search_term}%"),
                Product.product_name.ilike(f"%{search_term}%"),
                Product.description.ilike(f"%{search_term}%"),
                Product.product_category.ilike(f"%{search_term}%")
            )
        ).offset(skip).limit(limit).all()
    
    def get_high_profit_products(
        self, 
        db: Session, 
        *, 
        min_margin: Decimal = Decimal("30.0"),
        skip: int = 0, 
        limit: int = 100
    ) -> List[Product]:
        """获取高利润产品"""
        return db.query(Product).filter(
            Product.profit_margin >= min_margin
        ).offset(skip).limit(limit).all()
    
    def get_products_by_price_range(
        self, 
        db: Session, 
        *, 
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Product]:
        """根据价格范围获取产品"""
        query = db.query(Product)
        
        if min_price is not None:
            query = query.filter(Product.base_price >= min_price)
        if max_price is not None:
            query = query.filter(Product.base_price <= max_price)
        
        return query.offset(skip).limit(limit).all()
    
    def get_product_stats(self, db: Session) -> Dict[str, Any]:
        """获取产品统计信息"""
        total_products = db.query(Product).count()
        active_products = db.query(Product).filter(Product.status == "active").count()
        featured_products = db.query(Product).filter(Product.is_featured == True).count()
        
        # 计算汇总数据
        total_revenue = db.query(func.sum(Product.revenue)).scalar()
        total_sales_volume = db.query(func.sum(Product.sales_volume)).scalar()
        avg_profit_margin = db.query(func.avg(Product.profit_margin)).scalar()
        avg_quality_score = db.query(func.avg(Product.quality_score)).scalar()
        avg_customer_satisfaction = db.query(func.avg(Product.customer_satisfaction)).scalar()
        
        return {
            "total_products": total_products,
            "active_products": active_products,
            "featured_products": featured_products,
            "total_revenue": float(total_revenue) if total_revenue else None,
            "total_sales_volume": total_sales_volume if total_sales_volume else None,
            "average_profit_margin": float(avg_profit_margin) if avg_profit_margin else None,
            "average_quality_score": float(avg_quality_score) if avg_quality_score else None,
            "average_customer_satisfaction": float(avg_customer_satisfaction) if avg_customer_satisfaction else None,
        }
    
    def get_products_by_target_market(
        self, 
        db: Session, 
        *, 
        target_market: str,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Product]:
        """根据目标市场获取产品"""
        return db.query(Product).filter(
            Product.target_market.ilike(f"%{target_market}%")
        ).offset(skip).limit(limit).all()
    
    def update_product_metrics(
        self,
        db: Session,
        *,
        product_id: int,
        quality_score: Optional[Decimal] = None,
        customer_satisfaction: Optional[Decimal] = None,
        market_share: Optional[Decimal] = None,
        sales_volume: Optional[int] = None,
        revenue: Optional[Decimal] = None
    ) -> Optional[Product]:
        """更新产品指标"""
        product = self.get(db, id=product_id)
        if not product:
            return None
        
        if quality_score is not None:
            product.quality_score = quality_score
        if customer_satisfaction is not None:
            product.customer_satisfaction = customer_satisfaction
        if market_share is not None:
            product.market_share = market_share
        if sales_volume is not None:
            product.sales_volume = sales_volume
        if revenue is not None:
            product.revenue = revenue
        
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

# 创建产品CRUD实例
product = CRUDProduct(Product)
