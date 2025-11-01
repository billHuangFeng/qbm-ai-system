"""
BMOS系统 - 测试数据生成脚本
生成各种测试场景的模拟数据
"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd
import numpy as np

class TestDataGenerator:
    """测试数据生成器"""
    
    def __init__(self, random_seed: int = 42):
        random.seed(random_seed)
        np.random.seed(random_seed)
    
    def generate_sales_data(
        self,
        n_days: int = 365,
        n_products: int = 10,
        start_date: str = "2023-01-01"
    ) -> pd.DataFrame:
        """生成销售数据"""
        dates = pd.date_range(start=start_date, periods=n_days, freq='D')
        products = [f"产品_{i+1}" for i in range(n_products)]
        
        data = []
        for date in dates:
            for product in products:
                # 添加趋势和季节性
                trend = 0.001 * (date - dates[0]).days
                seasonal = 0.1 * np.sin(2 * np.pi * (date - dates[0]).days / 365)
                
                base_price = random.uniform(50, 200)
                quantity = max(1, int(random.uniform(10, 100) + trend * 100 + seasonal * 50))
                amount = base_price * quantity
                
                data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'product': product,
                    'category': f"类别_{random.randint(1, 3)}",
                    'price': round(base_price, 2),
                    'quantity': quantity,
                    'amount': round(amount, 2),
                    'channel': random.choice(['线上', '线下', '分销']),
                    'region': random.choice(['华东', '华南', '华北', '西南'])
                })
        
        df = pd.DataFrame(data)
        return df
    
    def generate_customer_data(self, n_customers: int = 1000) -> pd.DataFrame:
        """生成客户数据"""
        data = []
        for i in range(n_customers):
            data.append({
                'customer_id': f"CUST_{i+1:05d}",
                'name': f"客户_{i+1}",
                'email': f"customer_{i+1}@example.com",
                'phone': f"1{random.randint(3000000000, 3999999999)}",
                'category': random.choice(['企业', '个人', '代理商']),
                'level': random.choice(['VIP', '普通', '潜力']),
                'region': random.choice(['华东', '华南', '华北', '西南']),
                'registration_date': (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d'),
                'total_order_value': round(random.uniform(1000, 100000), 2),
                'order_count': random.randint(1, 50),
                'last_order_date': (datetime.now() - timedelta(days=random.randint(0, 90))).strftime('%Y-%m-%d')
            })
        
        df = pd.DataFrame(data)
        return df
    
    def generate_order_data(
        self,
        n_orders: int = 10000,
        start_date: str = "2023-01-01"
    ) -> pd.DataFrame:
        """生成订单数据"""
        dates = pd.date_range(start=start_date, periods=365, freq='D')
        
        data = []
        for i in range(n_orders):
            order_date = random.choice(dates)
            products_in_order = random.randint(1, 5)
            
            order_amount = 0
            order_items = []
            
            for j in range(products_in_order):
                product_id = f"产品_{random.randint(1, 10)}"
                price = random.uniform(50, 500)
                quantity = random.randint(1, 10)
                item_amount = price * quantity
                order_amount += item_amount
                
                order_items.append({
                    'product_id': product_id,
                    'quantity': quantity,
                    'price': round(price, 2),
                    'amount': round(item_amount, 2)
                })
            
            data.append({
                'order_id': f"ORD_{i+1:06d}",
                'customer_id': f"CUST_{random.randint(1, 1000):05d}",
                'order_date': order_date.strftime('%Y-%m-%d'),
                'order_amount': round(order_amount, 2),
                'order_status': random.choice(['已完成', '处理中', '已取消']),
                'payment_method': random.choice(['支付宝', '微信', '银行卡', '货到付款']),
                'region': random.choice(['华东', '华南', '华北', '西南']),
                'items': json.dumps(order_items, ensure_ascii=False)
            })
        
        df = pd.DataFrame(data)
        return df
    
    def generate_asset_data(self, n_assets: int = 100) -> pd.DataFrame:
        """生成资产数据"""
        data = []
        for i in range(n_assets):
            asset_value = random.uniform(10000, 500000)
            depreciation_rate = random.uniform(0.05, 0.20)
            
            data.append({
                'asset_id': f"AST_{i+1:05d}",
                'asset_name': f"资产_{i+1}",
                'asset_type': random.choice(['设备', '厂房', '车辆', '系统']),
                'purchase_date': (datetime.now() - timedelta(days=random.randint(1, 3650))).strftime('%Y-%m-%d'),
                'purchase_cost': round(asset_value * 1.2, 2),
                'current_value': round(asset_value, 2),
                'depreciation_rate': round(depreciation_rate, 4),
                'useful_life': random.randint(5, 20),
                'location': random.choice(['上海', '北京', '深圳', '杭州']),
                'status': random.choice(['使用中', '闲置', '维修中', '已报废'])
            })
        
        df = pd.DataFrame(data)
        return df
    
    def generate_capability_data(self, n_capabilities: int = 50) -> pd.DataFrame:
        """生成能力数据"""
        data = []
        for i in range(n_capabilities):
            data.append({
                'capability_id': f"CAP_{i+1:05d}",
                'capability_name': f"能力_{i+1}",
                'capability_type': random.choice(['技术', '管理', '市场', '运营']),
                'level': random.choice(['初级', '中级', '高级', '专家']),
                'evaluation_date': (datetime.now() - timedelta(days=random.randint(1, 180))).strftime('%Y-%m-%d'),
                'proficiency_score': round(random.uniform(0, 100), 2),
                'contribution_value': round(random.uniform(10000, 100000), 2),
                'team_size': random.randint(1, 20),
                'department': random.choice(['研发', '市场', '销售', '运营'])
            })
        
        df = pd.DataFrame(data)
        return df
    
    def generate_financial_data(
        self,
        n_months: int = 12,
        start_date: str = "2023-01"
    ) -> pd.DataFrame:
        """生成财务数据"""
        dates = pd.date_range(start=start_date, periods=n_months, freq='M')
        
        data = []
        base_revenue = 1000000
        for i, date in enumerate(dates):
            # 添加增长趋势
            growth_rate = 0.05 * i
            revenue = base_revenue * (1 + growth_rate) * (1 + random.uniform(-0.1, 0.1))
            cost = revenue * random.uniform(0.6, 0.8)
            profit = revenue - cost
            
            data.append({
                'period': date.strftime('%Y-%m'),
                'revenue': round(revenue, 2),
                'cost': round(cost, 2),
                'profit': round(profit, 2),
                'profit_margin': round(profit / revenue * 100, 2) if revenue > 0 else 0,
                'sales_expense': round(revenue * random.uniform(0.1, 0.2), 2),
                'admin_expense': round(revenue * random.uniform(0.05, 0.1), 2),
                'rd_expense': round(revenue * random.uniform(0.05, 0.15), 2)
            })
        
        df = pd.DataFrame(data)
        return df
    
    def generate_marketing_data(self, n_campaigns: int = 100) -> pd.DataFrame:
        """生成营销活动数据"""
        data = []
        for i in range(n_campaigns):
            campaign_duration = random.randint(7, 90)
            start_date = datetime.now() - timedelta(days=random.randint(1, 180))
            end_date = start_date + timedelta(days=campaign_duration)
            
            budget = random.uniform(10000, 500000)
            roi = random.uniform(0.5, 5.0)
            revenue = budget * roi
            
            data.append({
                'campaign_id': f"CAMP_{i+1:05d}",
                'campaign_name': f"营销活动_{i+1}",
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'channel': random.choice(['线上', '线下', '社交媒体', '电视']),
                'budget': round(budget, 2),
                'revenue': round(revenue, 2),
                'roi': round(roi, 2),
                'reach': random.randint(10000, 1000000),
                'conversion_rate': round(random.uniform(0.01, 0.1), 4),
                'status': random.choice(['进行中', '已完成', '已暂停'])
            })
        
        df = pd.DataFrame(data)
        return df
    
    def generate_supplier_data(self, n_suppliers: int = 50) -> pd.DataFrame:
        """生成供应商数据"""
        data = []
        for i in range(n_suppliers):
            data.append({
                'supplier_id': f"SUP_{i+1:05d}",
                'supplier_name': f"供应商_{i+1}",
                'industry': random.choice(['制造业', '服务业', '贸易', '科技']),
                'country': random.choice(['中国', '美国', '日本', '德国']),
                'relationship_duration': random.randint(1, 10),
                'total_purchase_value': round(random.uniform(100000, 5000000), 2),
                'order_count': random.randint(10, 500),
                'average_delivery_time': random.randint(1, 30),
                'quality_rating': round(random.uniform(3.0, 5.0), 1),
                'payment_terms': random.choice(['货到付款', '30天', '60天', '预付']),
                'status': random.choice(['活跃', '暂停', '终止'])
            })
        
        df = pd.DataFrame(data)
        return df
    
    def generate_competitor_data(self, n_competitors: int = 20) -> pd.DataFrame:
        """生成竞争对手数据"""
        data = []
        for i in range(n_competitors):
            data.append({
                'competitor_id': f"COMP_{i+1:05d}",
                'competitor_name': f"竞争对手_{i+1}",
                'market_share': round(random.uniform(0.01, 0.3), 4),
                'revenue': round(random.uniform(1000000, 100000000), 2),
                'main_products': random.choice(['产品A', '产品B', '产品C', '产品D']),
                'pricing_strategy': random.choice(['低价', '中价', '高价', '溢价']),
                'strength': random.choice(['产品', '渠道', '品牌', '技术']),
                'threat_level': random.choice(['低', '中', '高']),
                'last_update': (datetime.now() - timedelta(days=random.randint(1, 180))).strftime('%Y-%m-%d')
            })
        
        df = pd.DataFrame(data)
        return df
    
    def generate_all_test_data(self) -> Dict[str, pd.DataFrame]:
        """生成所有测试数据"""
        return {
            'sales_data': self.generate_sales_data(),
            'customer_data': self.generate_customer_data(),
            'order_data': self.generate_order_data(),
            'asset_data': self.generate_asset_data(),
            'capability_data': self.generate_capability_data(),
            'financial_data': self.generate_financial_data(),
            'marketing_data': self.generate_marketing_data(),
            'supplier_data': self.generate_supplier_data(),
            'competitor_data': self.generate_competitor_data()
        }
    
    def save_to_excel(self, data: Dict[str, pd.DataFrame], filename: str):
        """保存为Excel文件"""
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            for sheet_name, df in data.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"数据已保存到 {filename}")
    
    def save_to_csv(self, data: Dict[str, pd.DataFrame], output_dir: str = "test_data"):
        """保存为CSV文件"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        for filename, df in data.items():
            filepath = os.path.join(output_dir, f"{filename}.csv")
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"已保存: {filepath}")

# 使用示例
if __name__ == "__main__":
    generator = TestDataGenerator(random_seed=42)
    
    # 生成所有测试数据
    print("正在生成测试数据...")
    all_data = generator.generate_all_test_data()
    
    # 保存为Excel
    generator.save_to_excel(all_data, "bmos_test_data.xlsx")
    
    # 保存为CSV
    generator.save_to_csv(all_data, "test_data")
    
    # 打印数据概览
    print("\n数据概览:")
    for name, df in all_data.items():
        print(f"{name}: {len(df)} 行, {len(df.columns)} 列")
    
    print("\n测试数据生成完成！")