"""
示例数据种子文件
"""
import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.app.database import SessionLocal
from backend.app.models import *

def create_sample_users():
    """创建示例用户数据"""
    db = SessionLocal()
    try:
        # 检查是否已有用户数据
        if db.query(User).count() > 0:
            print("用户数据已存在，跳过创建")
            return
        
        users = [
            User(
                username="admin",
                email="admin@qbm-ai.com",
                password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8K8K8K8",  # password: admin123
                full_name="系统管理员",
                phone="13800138000",
                is_active=True,
                is_admin=True
            ),
            User(
                username="analyst1",
                email="analyst1@qbm-ai.com",
                password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8K8K8K8",  # password: analyst123
                full_name="数据分析师1",
                phone="13800138001",
                is_active=True,
                is_admin=False
            ),
            User(
                username="manager1",
                email="manager1@qbm-ai.com",
                password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8K8K8K8",  # password: manager123
                full_name="项目经理1",
                phone="13800138002",
                is_active=True,
                is_admin=False
            )
        ]
        
        for user in users:
            db.add(user)
        
        db.commit()
        print(f"创建了 {len(users)} 个示例用户")
        
    except Exception as e:
        db.rollback()
        print(f"创建用户数据时出错: {e}")
        raise
    finally:
        db.close()

def create_sample_customers():
    """创建示例客户数据"""
    db = SessionLocal()
    try:
        # 检查是否已有客户数据
        if db.query(Customer).count() > 0:
            print("客户数据已存在，跳过创建")
            return
        
        customers = [
            Customer(
                customer_code="CUST001",
                customer_name="北京科技有限公司",
                customer_type="企业客户",
                industry="信息技术",
                company_size="中型",
                contact_person="张经理",
                phone="010-12345678",
                email="zhang@beijing-tech.com",
                address="北京市海淀区中关村大街1号",
                city="北京",
                province="北京",
                customer_value_score=Decimal("85.5"),
                customer_lifetime_value=Decimal("500000.00"),
                customer_satisfaction=Decimal("4.2"),
                customer_retention_rate=Decimal("92.5"),
                status="active",
                is_vip=True,
                first_contact_date=datetime.now() - timedelta(days=365),
                last_contact_date=datetime.now() - timedelta(days=7)
            ),
            Customer(
                customer_code="CUST002",
                customer_name="上海制造有限公司",
                customer_type="企业客户",
                industry="制造业",
                company_size="大型",
                contact_person="李总",
                phone="021-87654321",
                email="li@shanghai-manufacturing.com",
                address="上海市浦东新区张江高科技园区",
                city="上海",
                province="上海",
                customer_value_score=Decimal("78.3"),
                customer_lifetime_value=Decimal("800000.00"),
                customer_satisfaction=Decimal("4.0"),
                customer_retention_rate=Decimal("88.0"),
                status="active",
                is_vip=True,
                first_contact_date=datetime.now() - timedelta(days=500),
                last_contact_date=datetime.now() - timedelta(days=3)
            ),
            Customer(
                customer_code="CUST003",
                customer_name="深圳创新企业",
                customer_type="企业客户",
                industry="互联网",
                company_size="小型",
                contact_person="王总监",
                phone="0755-11223344",
                email="wang@shenzhen-innovation.com",
                address="深圳市南山区科技园",
                city="深圳",
                province="广东",
                customer_value_score=Decimal("72.1"),
                customer_lifetime_value=Decimal("200000.00"),
                customer_satisfaction=Decimal("3.8"),
                customer_retention_rate=Decimal("75.0"),
                status="active",
                is_vip=False,
                first_contact_date=datetime.now() - timedelta(days=200),
                last_contact_date=datetime.now() - timedelta(days=1)
            )
        ]
        
        for customer in customers:
            db.add(customer)
        
        db.commit()
        print(f"创建了 {len(customers)} 个示例客户")
        
    except Exception as e:
        db.rollback()
        print(f"创建客户数据时出错: {e}")
        raise
    finally:
        db.close()

def create_sample_products():
    """创建示例产品数据"""
    db = SessionLocal()
    try:
        # 检查是否已有产品数据
        if db.query(Product).count() > 0:
            print("产品数据已存在，跳过创建")
            return
        
        products = [
            Product(
                product_code="PROD001",
                product_name="AI数据分析平台",
                product_category="软件产品",
                product_type="软件",
                description="基于人工智能的数据分析平台，提供智能数据挖掘和预测分析功能",
                key_features=json.dumps([
                    "智能数据挖掘",
                    "预测分析",
                    "可视化报表",
                    "实时监控",
                    "多数据源支持"
                ]),
                technical_specs=json.dumps({
                    "cpu_requirements": "8核心以上",
                    "memory_requirements": "16GB以上",
                    "storage_requirements": "500GB以上",
                    "os_support": ["Windows", "Linux", "macOS"]
                }),
                competitive_advantages="领先的AI算法，用户友好的界面，强大的扩展性",
                base_price=Decimal("50000.00"),
                cost_price=Decimal("20000.00"),
                profit_margin=Decimal("60.0"),
                pricing_strategy="价值定价",
                target_market="中大型企业",
                market_position="高端市场",
                competitive_position="领导者",
                lifecycle_stage="成熟",
                launch_date=datetime.now() - timedelta(days=730),
                quality_score=Decimal("4.5"),
                customer_satisfaction=Decimal("4.3"),
                market_share=Decimal("15.2"),
                sales_volume=150,
                revenue=Decimal("7500000.00"),
                status="active",
                is_featured=True
            ),
            Product(
                product_code="PROD002",
                product_name="企业管理系统",
                product_category="软件产品",
                product_type="软件",
                description="全面的企业管理系统，包括财务管理、人力资源、项目管理等功能",
                key_features=json.dumps([
                    "财务管理",
                    "人力资源",
                    "项目管理",
                    "客户关系管理",
                    "供应链管理"
                ]),
                technical_specs=json.dumps({
                    "cpu_requirements": "4核心以上",
                    "memory_requirements": "8GB以上",
                    "storage_requirements": "200GB以上",
                    "os_support": ["Windows", "Linux"]
                }),
                competitive_advantages="功能全面，易于使用，性价比高",
                base_price=Decimal("30000.00"),
                cost_price=Decimal("15000.00"),
                profit_margin=Decimal("50.0"),
                pricing_strategy="竞争定价",
                target_market="中小企业",
                market_position="中端市场",
                competitive_position="挑战者",
                lifecycle_stage="成长",
                launch_date=datetime.now() - timedelta(days=365),
                quality_score=Decimal("4.2"),
                customer_satisfaction=Decimal("4.1"),
                market_share=Decimal("8.5"),
                sales_volume=200,
                revenue=Decimal("6000000.00"),
                status="active",
                is_featured=False
            ),
            Product(
                product_code="PROD003",
                product_name="云服务解决方案",
                product_category="服务产品",
                product_type="服务",
                description="基于云计算的IT服务解决方案，提供基础设施、平台和软件服务",
                key_features=json.dumps([
                    "基础设施即服务",
                    "平台即服务",
                    "软件即服务",
                    "弹性扩展",
                    "高可用性"
                ]),
                technical_specs=json.dumps({
                    "availability": "99.9%",
                    "scalability": "自动扩展",
                    "security": "企业级安全",
                    "compliance": ["ISO27001", "SOC2"]
                }),
                competitive_advantages="高可用性，弹性扩展，企业级安全",
                base_price=Decimal("10000.00"),
                cost_price=Decimal("5000.00"),
                profit_margin=Decimal("50.0"),
                pricing_strategy="订阅定价",
                target_market="各类企业",
                market_position="中高端市场",
                competitive_position="跟随者",
                lifecycle_stage="成长",
                launch_date=datetime.now() - timedelta(days=180),
                quality_score=Decimal("4.0"),
                customer_satisfaction=Decimal("4.0"),
                market_share=Decimal("5.8"),
                sales_volume=100,
                revenue=Decimal("1000000.00"),
                status="active",
                is_featured=False
            )
        ]
        
        for product in products:
            db.add(product)
        
        db.commit()
        print(f"创建了 {len(products)} 个示例产品")
        
    except Exception as e:
        db.rollback()
        print(f"创建产品数据时出错: {e}")
        raise
    finally:
        db.close()

def create_sample_contracts():
    """创建示例合同数据"""
    db = SessionLocal()
    try:
        # 检查是否已有合同数据
        if db.query(Contract).count() > 0:
            print("合同数据已存在，跳过创建")
            return
        
        # 获取用户、客户和产品数据
        users = db.query(User).all()
        customers = db.query(Customer).all()
        products = db.query(Product).all()
        
        if not users or not customers or not products:
            print("缺少必要的关联数据，跳过合同创建")
            return
        
        contracts = [
            Contract(
                contract_code="CONT001",
                contract_name="AI数据分析平台销售合同",
                contract_type="销售合同",
                customer_id=customers[0].id,
                product_id=products[0].id,
                user_id=users[0].id,
                contract_value=Decimal("500000.00"),
                currency="CNY",
                payment_terms="30%预付款，70%验收后付款",
                delivery_terms="30天内交付",
                contract_terms="标准销售合同条款",
                special_conditions="提供3年免费技术支持",
                risk_assessment="低风险，客户信用良好",
                contract_date=datetime.now() - timedelta(days=30),
                effective_date=datetime.now() - timedelta(days=30),
                expiry_date=datetime.now() + timedelta(days=335),
                delivery_date=datetime.now() + timedelta(days=15),
                status="active",
                execution_progress=Decimal("60.0"),
                invoiced_amount=Decimal("150000.00"),
                paid_amount=Decimal("150000.00"),
                outstanding_amount=Decimal("350000.00"),
                risk_level="low",
                quality_score=Decimal("4.5"),
                customer_satisfaction=Decimal("4.3")
            ),
            Contract(
                contract_code="CONT002",
                contract_name="企业管理系统实施合同",
                contract_type="服务合同",
                customer_id=customers[1].id,
                product_id=products[1].id,
                user_id=users[1].id,
                contract_value=Decimal("300000.00"),
                currency="CNY",
                payment_terms="50%预付款，50%验收后付款",
                delivery_terms="60天内完成实施",
                contract_terms="标准服务合同条款",
                special_conditions="提供6个月免费维护",
                risk_assessment="中等风险，需要关注实施进度",
                contract_date=datetime.now() - timedelta(days=15),
                effective_date=datetime.now() - timedelta(days=15),
                expiry_date=datetime.now() + timedelta(days=350),
                delivery_date=datetime.now() + timedelta(days=45),
                status="active",
                execution_progress=Decimal("30.0"),
                invoiced_amount=Decimal("150000.00"),
                paid_amount=Decimal("150000.00"),
                outstanding_amount=Decimal("150000.00"),
                risk_level="medium",
                quality_score=Decimal("4.2"),
                customer_satisfaction=Decimal("4.1")
            )
        ]
        
        for contract in contracts:
            db.add(contract)
        
        db.commit()
        print(f"创建了 {len(contracts)} 个示例合同")
        
    except Exception as e:
        db.rollback()
        print(f"创建合同数据时出错: {e}")
        raise
    finally:
        db.close()

def create_sample_orders():
    """创建示例订单数据"""
    db = SessionLocal()
    try:
        # 检查是否已有订单数据
        if db.query(Order).count() > 0:
            print("订单数据已存在，跳过创建")
            return
        
        # 获取用户、客户、产品和合同数据
        users = db.query(User).all()
        customers = db.query(Customer).all()
        products = db.query(Product).all()
        contracts = db.query(Contract).all()
        
        if not users or not customers or not products:
            print("缺少必要的关联数据，跳过订单创建")
            return
        
        orders = [
            Order(
                order_code="ORDER001",
                order_name="AI数据分析平台订单",
                order_type="销售订单",
                customer_id=customers[0].id,
                product_id=products[0].id,
                contract_id=contracts[0].id if contracts else None,
                user_id=users[0].id,
                order_quantity=1,
                unit_price=Decimal("500000.00"),
                total_amount=Decimal("500000.00"),
                currency="CNY",
                order_description="AI数据分析平台标准版",
                special_requirements="需要定制化配置",
                delivery_address="北京市海淀区中关村大街1号",
                contact_info="张经理 010-12345678",
                order_date=datetime.now() - timedelta(days=30),
                required_delivery_date=datetime.now() + timedelta(days=15),
                status="in_progress",
                priority="high",
                execution_progress=Decimal("60.0"),
                quality_check_status="pending",
                delivery_status="preparing",
                payment_status="partial",
                invoiced_amount=Decimal("150000.00"),
                paid_amount=Decimal("150000.00"),
                outstanding_amount=Decimal("350000.00"),
                cost_amount=Decimal("200000.00"),
                profit_amount=Decimal("300000.00"),
                profit_margin=Decimal("60.0"),
                customer_satisfaction=Decimal("4.3"),
                customer_feedback="对产品功能很满意，期待交付"
            ),
            Order(
                order_code="ORDER002",
                order_name="企业管理系统订单",
                order_type="服务订单",
                customer_id=customers[1].id,
                product_id=products[1].id,
                contract_id=contracts[1].id if len(contracts) > 1 else None,
                user_id=users[1].id,
                order_quantity=1,
                unit_price=Decimal("300000.00"),
                total_amount=Decimal("300000.00"),
                currency="CNY",
                order_description="企业管理系统标准版",
                special_requirements="需要数据迁移服务",
                delivery_address="上海市浦东新区张江高科技园区",
                contact_info="李总 021-87654321",
                order_date=datetime.now() - timedelta(days=15),
                required_delivery_date=datetime.now() + timedelta(days=45),
                status="confirmed",
                priority="normal",
                execution_progress=Decimal("30.0"),
                quality_check_status="pending",
                delivery_status="planning",
                payment_status="partial",
                invoiced_amount=Decimal("150000.00"),
                paid_amount=Decimal("150000.00"),
                outstanding_amount=Decimal("150000.00"),
                cost_amount=Decimal("150000.00"),
                profit_amount=Decimal("150000.00"),
                profit_margin=Decimal("50.0"),
                customer_satisfaction=Decimal("4.1"),
                customer_feedback="对服务态度满意"
            )
        ]
        
        for order in orders:
            db.add(order)
        
        db.commit()
        print(f"创建了 {len(orders)} 个示例订单")
        
    except Exception as e:
        db.rollback()
        print(f"创建订单数据时出错: {e}")
        raise
    finally:
        db.close()

def create_sample_financials():
    """创建示例财务数据"""
    db = SessionLocal()
    try:
        # 检查是否已有财务数据
        if db.query(Financial).count() > 0:
            print("财务数据已存在，跳过创建")
            return
        
        # 获取用户、客户、产品、合同和订单数据
        users = db.query(User).all()
        customers = db.query(Customer).all()
        products = db.query(Product).all()
        contracts = db.query(Contract).all()
        orders = db.query(Order).all()
        
        if not users:
            print("缺少必要的关联数据，跳过财务数据创建")
            return
        
        financials = [
            Financial(
                financial_code="FIN001",
                financial_name="AI数据分析平台销售收入",
                financial_type="收入",
                customer_id=customers[0].id if customers else None,
                product_id=products[0].id if products else None,
                contract_id=contracts[0].id if contracts else None,
                order_id=orders[0].id if orders else None,
                user_id=users[0].id,
                amount=Decimal("150000.00"),
                currency="CNY",
                category="主营业务收入",
                subcategory="软件销售收入",
                account_code="6001",
                account_name="主营业务收入",
                transaction_date=datetime.now() - timedelta(days=30),
                accounting_date=datetime.now() - timedelta(days=30),
                status="confirmed",
                payment_status="paid",
                approval_status="approved",
                description="AI数据分析平台预付款",
                reference_number="INV001",
                invoice_number="INV001",
                cost_center="销售部",
                profit_center="产品线A",
                budget_category="销售收入",
                cash_flow_type="经营",
                cash_flow_impact=Decimal("150000.00"),
                tax_amount=Decimal("19500.00"),
                tax_rate=Decimal("13.0"),
                tax_type="增值税"
            ),
            Financial(
                financial_code="FIN002",
                financial_name="企业管理系统销售收入",
                financial_type="收入",
                customer_id=customers[1].id if len(customers) > 1 else None,
                product_id=products[1].id if len(products) > 1 else None,
                contract_id=contracts[1].id if len(contracts) > 1 else None,
                order_id=orders[1].id if len(orders) > 1 else None,
                user_id=users[1].id if len(users) > 1 else users[0].id,
                amount=Decimal("150000.00"),
                currency="CNY",
                category="主营业务收入",
                subcategory="软件销售收入",
                account_code="6001",
                account_name="主营业务收入",
                transaction_date=datetime.now() - timedelta(days=15),
                accounting_date=datetime.now() - timedelta(days=15),
                status="confirmed",
                payment_status="paid",
                approval_status="approved",
                description="企业管理系统预付款",
                reference_number="INV002",
                invoice_number="INV002",
                cost_center="销售部",
                profit_center="产品线B",
                budget_category="销售收入",
                cash_flow_type="经营",
                cash_flow_impact=Decimal("150000.00"),
                tax_amount=Decimal("19500.00"),
                tax_rate=Decimal("13.0"),
                tax_type="增值税"
            ),
            Financial(
                financial_code="FIN003",
                financial_name="研发人员工资",
                financial_type="支出",
                user_id=users[0].id,
                amount=Decimal("-50000.00"),
                currency="CNY",
                category="研发费用",
                subcategory="人员费用",
                account_code="5301",
                account_name="研发费用",
                transaction_date=datetime.now() - timedelta(days=1),
                accounting_date=datetime.now() - timedelta(days=1),
                status="confirmed",
                payment_status="paid",
                approval_status="approved",
                description="研发部门人员工资",
                cost_center="研发部",
                profit_center="产品线A",
                budget_category="人员费用",
                cash_flow_type="经营",
                cash_flow_impact=Decimal("-50000.00"),
                tax_amount=Decimal("0.00"),
                tax_rate=Decimal("0.0"),
                tax_type="无"
            )
        ]
        
        for financial in financials:
            db.add(financial)
        
        db.commit()
        print(f"创建了 {len(financials)} 个示例财务记录")
        
    except Exception as e:
        db.rollback()
        print(f"创建财务数据时出错: {e}")
        raise
    finally:
        db.close()

def main():
    """主函数"""
    print("开始创建示例数据...")
    
    try:
        # 按顺序创建示例数据
        create_sample_users()
        create_sample_customers()
        create_sample_products()
        create_sample_contracts()
        create_sample_orders()
        create_sample_financials()
        
        print("示例数据创建完成！")
        
    except Exception as e:
        print(f"创建示例数据时出错: {e}")
        raise

if __name__ == "__main__":
    main()
