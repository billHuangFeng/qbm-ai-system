#!/usr/bin/env python3
"""
快速测试脚本 - QBM AI System
"""
import requests
import time
import json
import sys
from pathlib import Path

class QBMTestSuite:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:8080"
        self.token = None
        self.test_results = []
        
    def log(self, message, status="INFO"):
        """记录测试日志"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] [{status}] {message}")
        
    def test_health_check(self):
        """测试系统健康检查"""
        self.log("测试系统健康检查...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ 系统健康检查通过: {data['status']}", "SUCCESS")
                return True
            else:
                self.log(f"❌ 健康检查失败: HTTP {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ 健康检查异常: {e}", "ERROR")
            return False
    
    def test_user_login(self):
        """测试用户登录"""
        self.log("测试用户登录...")
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                data={"username": "admin", "password": "admin123"},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.log("✅ 用户登录成功", "SUCCESS")
                return True
            else:
                self.log(f"❌ 登录失败: HTTP {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ 登录异常: {e}", "ERROR")
            return False
    
    def test_get_user_info(self):
        """测试获取用户信息"""
        if not self.token:
            self.log("❌ 无有效token，跳过用户信息测试", "WARNING")
            return False
            
        self.log("测试获取用户信息...")
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{self.base_url}/api/v1/auth/me", headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ 获取用户信息成功: {data.get('username', 'Unknown')}", "SUCCESS")
                return True
            else:
                self.log(f"❌ 获取用户信息失败: HTTP {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ 获取用户信息异常: {e}", "ERROR")
            return False
    
    def test_customer_crud(self):
        """测试客户CRUD操作"""
        if not self.token:
            self.log("❌ 无有效token，跳过客户CRUD测试", "WARNING")
            return False
            
        self.log("测试客户CRUD操作...")
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            # 创建客户
            customer_data = {
                "name": "测试客户",
                "contact_person": "张三",
                "contact_email": "zhangsan@example.com",
                "contact_phone": "13800138001",
                "industry": "科技",
                "region": "北京"
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/customers/",
                json=customer_data,
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                customer = response.json()
                customer_id = customer.get("id")
                self.log("✅ 客户创建成功", "SUCCESS")
                
                # 获取客户列表
                response = requests.get(f"{self.base_url}/api/v1/customers/", headers=headers, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    self.log(f"✅ 获取客户列表成功: {data.get('total', 0)} 个客户", "SUCCESS")
                    
                    # 删除测试客户
                    if customer_id:
                        response = requests.delete(f"{self.base_url}/api/v1/customers/{customer_id}", headers=headers, timeout=5)
                        if response.status_code == 200:
                            self.log("✅ 客户删除成功", "SUCCESS")
                            return True
                        else:
                            self.log(f"❌ 客户删除失败: HTTP {response.status_code}", "ERROR")
                            return False
                    else:
                        self.log("❌ 无法获取客户ID", "ERROR")
                        return False
                else:
                    self.log(f"❌ 获取客户列表失败: HTTP {response.status_code}", "ERROR")
                    return False
            else:
                self.log(f"❌ 客户创建失败: HTTP {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ 客户CRUD测试异常: {e}", "ERROR")
            return False
    
    def test_product_crud(self):
        """测试产品CRUD操作"""
        if not self.token:
            self.log("❌ 无有效token，跳过产品CRUD测试", "WARNING")
            return False
            
        self.log("测试产品CRUD操作...")
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            # 创建产品
            product_data = {
                "name": "测试产品",
                "description": "这是一个测试产品",
                "price": 99.99,
                "category": "软件",
                "stock_quantity": 100
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/products/",
                json=product_data,
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                product = response.json()
                product_id = product.get("id")
                self.log("✅ 产品创建成功", "SUCCESS")
                
                # 获取产品列表
                response = requests.get(f"{self.base_url}/api/v1/products/", headers=headers, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    self.log(f"✅ 获取产品列表成功: {data.get('total', 0)} 个产品", "SUCCESS")
                    
                    # 删除测试产品
                    if product_id:
                        response = requests.delete(f"{self.base_url}/api/v1/products/{product_id}", headers=headers, timeout=5)
                        if response.status_code == 200:
                            self.log("✅ 产品删除成功", "SUCCESS")
                            return True
                        else:
                            self.log(f"❌ 产品删除失败: HTTP {response.status_code}", "ERROR")
                            return False
                    else:
                        self.log("❌ 无法获取产品ID", "ERROR")
                        return False
                else:
                    self.log(f"❌ 获取产品列表失败: HTTP {response.status_code}", "ERROR")
                    return False
            else:
                self.log(f"❌ 产品创建失败: HTTP {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ 产品CRUD测试异常: {e}", "ERROR")
            return False
    
    def test_system_status(self):
        """测试系统状态"""
        if not self.token:
            self.log("❌ 无有效token，跳过系统状态测试", "WARNING")
            return False
            
        self.log("测试系统状态...")
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.get(f"{self.base_url}/api/v1/system/status", headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log("✅ 系统状态获取成功", "SUCCESS")
                
                # 检查关键服务状态
                services = data.get("services", {})
                for service, status in services.items():
                    if status == "running" or status == "connected" or status == "ready":
                        self.log(f"  ✅ {service}: {status}", "SUCCESS")
                    else:
                        self.log(f"  ❌ {service}: {status}", "ERROR")
                
                return True
            else:
                self.log(f"❌ 系统状态获取失败: HTTP {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ 系统状态测试异常: {e}", "ERROR")
            return False
    
    def test_frontend_access(self):
        """测试前端访问"""
        self.log("测试前端访问...")
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                self.log("✅ 前端访问成功", "SUCCESS")
                return True
            else:
                self.log(f"❌ 前端访问失败: HTTP {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ 前端访问异常: {e}", "ERROR")
            return False
    
    def test_api_docs(self):
        """测试API文档"""
        self.log("测试API文档...")
        try:
            response = requests.get(f"{self.base_url}/docs", timeout=5)
            if response.status_code == 200:
                self.log("✅ API文档访问成功", "SUCCESS")
                return True
            else:
                self.log(f"❌ API文档访问失败: HTTP {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ API文档访问异常: {e}", "ERROR")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        self.log("🚀 开始QBM AI System快速测试...")
        self.log("=" * 50)
        
        tests = [
            ("系统健康检查", self.test_health_check),
            ("用户登录", self.test_user_login),
            ("获取用户信息", self.test_get_user_info),
            ("客户CRUD操作", self.test_customer_crud),
            ("产品CRUD操作", self.test_product_crud),
            ("系统状态", self.test_system_status),
            ("前端访问", self.test_frontend_access),
            ("API文档", self.test_api_docs),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            self.log(f"\n📋 执行测试: {test_name}")
            try:
                if test_func():
                    passed += 1
                    self.test_results.append((test_name, "PASS"))
                else:
                    self.test_results.append((test_name, "FAIL"))
            except Exception as e:
                self.log(f"❌ 测试异常: {e}", "ERROR")
                self.test_results.append((test_name, "ERROR"))
        
        # 输出测试结果
        self.log("\n" + "=" * 50)
        self.log("📊 测试结果汇总:")
        self.log(f"总测试数: {total}")
        self.log(f"通过测试: {passed}")
        self.log(f"失败测试: {total - passed}")
        self.log(f"成功率: {(passed/total)*100:.1f}%")
        
        self.log("\n📋 详细结果:")
        for test_name, result in self.test_results:
            status_icon = "✅" if result == "PASS" else "❌"
            self.log(f"  {status_icon} {test_name}: {result}")
        
        if passed == total:
            self.log("\n🎉 所有测试通过！系统运行正常。", "SUCCESS")
            return True
        else:
            self.log(f"\n⚠️  有 {total - passed} 个测试失败，请检查系统状态。", "WARNING")
            return False

def main():
    """主函数"""
    print("QBM AI System 快速测试工具")
    print("=" * 50)
    
    # 检查服务是否启动
    print("正在检查服务状态...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=3)
        if response.status_code != 200:
            print("❌ 后端服务未启动，请先运行: python scripts/start.py start")
            sys.exit(1)
    except:
        print("❌ 无法连接到后端服务，请先启动系统")
        print("启动命令: python scripts/start.py start")
        sys.exit(1)
    
    # 运行测试
    test_suite = QBMTestSuite()
    success = test_suite.run_all_tests()
    
    # 输出访问信息
    print("\n" + "=" * 50)
    print("🌐 系统访问地址:")
    print(f"前端界面: http://localhost:8080")
    print(f"后端API: http://localhost:8000")
    print(f"API文档: http://localhost:8000/docs")
    print(f"默认账户: admin / admin123")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()


