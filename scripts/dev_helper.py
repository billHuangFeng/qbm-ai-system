#!/usr/bin/env python3
"""
BMOS开发助手 - 确保使用正确的连接方式
"""
import subprocess
import sys
import json
from typing import List, Dict, Any

class BMOSDevHelper:
    """BMOS开发助手类"""
    
    def __init__(self):
        self.container_name = "bmos_clickhouse"
        self.backend_url = "http://localhost:8000"
    
    def check_environment(self) -> Dict[str, bool]:
        """检查开发环境状态"""
        print("=== BMOS开发环境检查 ===\n")
        
        checks = {
            "ClickHouse容器": self._check_clickhouse_container(),
            "ClickHouse TCP连接": self._check_clickhouse_tcp(),
            "ClickHouse HTTP连接": self._check_clickhouse_http(),
            "Redis容器": self._check_redis_container(),
            "后端服务": self._check_backend_service(),
            "BMOS数据库": self._check_bmos_database(),
            "BMOS表结构": self._check_bmos_tables()
        }
        
        for name, status in checks.items():
            status_icon = "✓" if status else "✗"
            print(f"{status_icon} {name}")
        
        print(f"\n=== 环境状态 ===")
        all_ok = all(checks.values())
        if all_ok:
            print("✓ 开发环境就绪")
        else:
            print("✗ 部分服务异常，请检查")
        
        return checks
    
    def _check_clickhouse_container(self) -> bool:
        """检查ClickHouse容器状态"""
        try:
            result = subprocess.run(
                f"docker ps --filter name={self.container_name} --format '{{{{.Names}}}}'",
                shell=True, capture_output=True, text=True, timeout=5
            )
            return self.container_name in result.stdout
        except:
            return False
    
    def _check_clickhouse_tcp(self) -> bool:
        """检查ClickHouse TCP连接"""
        try:
            result = subprocess.run(
                f'docker exec {self.container_name} clickhouse-client --query "SELECT 1"',
                shell=True, capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0 and "1" in result.stdout
        except:
            return False
    
    def _check_clickhouse_http(self) -> bool:
        """检查ClickHouse HTTP连接（预期会失败）"""
        try:
            import requests
            response = requests.get("http://localhost:8123/?query=SELECT%201", timeout=5)
            return response.status_code == 200
        except:
            return False  # 预期失败
    
    def _check_redis_container(self) -> bool:
        """检查Redis容器状态"""
        try:
            result = subprocess.run(
                "docker ps --filter name=bmos_redis --format '{{.Names}}'",
                shell=True, capture_output=True, text=True, timeout=5
            )
            return "bmos_redis" in result.stdout
        except:
            return False
    
    def _check_backend_service(self) -> bool:
        """检查后端服务状态"""
        try:
            import requests
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _check_bmos_database(self) -> bool:
        """检查BMOS数据库是否存在"""
        try:
            result = subprocess.run(
                f'docker exec {self.container_name} clickhouse-client --query "SHOW DATABASES"',
                shell=True, capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0 and "bmos" in result.stdout
        except:
            return False
    
    def _check_bmos_tables(self) -> bool:
        """检查BMOS表结构是否存在"""
        try:
            result = subprocess.run(
                f'docker exec {self.container_name} clickhouse-client --query "SHOW TABLES FROM bmos"',
                shell=True, capture_output=True, text=True, timeout=10
            )
            # 检查关键表是否存在
            key_tables = ['dim_vpt', 'dim_pft', 'fact_order', 'fact_voice']
            return result.returncode == 0 and all(table in result.stdout for table in key_tables)
        except:
            return False
    
    def safe_query(self, query: str) -> List[tuple]:
        """安全的数据库查询（使用TCP连接）"""
        print(f"执行查询: {query}")
        try:
            result = subprocess.run(
                f'docker exec {self.container_name} clickhouse-client --query "{query}"',
                shell=True, capture_output=True, text=True, timeout=30, encoding='utf-8', errors='ignore'
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if not lines or lines == ['']:
                    return []
                return [tuple(line.split('\t')) for line in lines if line.strip()]
            else:
                print(f"查询失败: {result.stderr}")
                return []
        except Exception as e:
            print(f"执行错误: {e}")
            return []
    
    def safe_insert(self, table: str, data: List[Dict]) -> bool:
        """安全的数据插入"""
        if not data:
            return True
        
        print(f"插入数据到表: {table}")
        print(f"数据量: {len(data)} 条")
        
        # 构建INSERT语句
        columns = list(data[0].keys())
        columns_str = ', '.join(columns)
        
        values_list = []
        for row in data:
            values = []
            for col in columns:
                value = row[col]
                if isinstance(value, str):
                    values.append(f"'{value}'")
                elif value is None:
                    values.append('NULL')
                else:
                    values.append(str(value))
            values_list.append(f"({', '.join(values)})")
        
        query = f"INSERT INTO bmos.{table} ({columns_str}) VALUES {', '.join(values_list)}"
        
        try:
            result = subprocess.run(
                f'docker exec {self.container_name} clickhouse-client --query "{query}"',
                shell=True, capture_output=True, text=True, timeout=30, encoding='utf-8', errors='ignore'
            )
            
            if result.returncode == 0:
                print("✓ 插入成功")
                return True
            else:
                print(f"✗ 插入失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"✗ 插入错误: {e}")
            return False
    
    def get_table_info(self, table: str) -> Dict[str, Any]:
        """获取表信息"""
        print(f"获取表信息: {table}")
        
        # 获取表结构
        structure_query = f"DESCRIBE bmos.{table}"
        structure = self.safe_query(structure_query)
        
        # 获取数据量
        count_query = f"SELECT COUNT(*) FROM bmos.{table}"
        count_result = self.safe_query(count_query)
        row_count = int(count_result[0][0]) if count_result else 0
        
        # 获取示例数据
        sample_query = f"SELECT * FROM bmos.{table} LIMIT 3"
        sample_data = self.safe_query(sample_query)
        
        return {
            "table_name": table,
            "structure": structure,
            "row_count": row_count,
            "sample_data": sample_data
        }
    
    def run_development_test(self) -> bool:
        """运行开发测试"""
        print("=== 运行开发测试 ===\n")
        
        # 测试1: 基础查询
        print("1. 测试基础查询...")
        result = self.safe_query("SELECT 1")
        if not result or result[0][0] != "1":
            print("✗ 基础查询失败")
            return False
        print("✓ 基础查询成功")
        
        # 测试2: 表查询
        print("\n2. 测试表查询...")
        result = self.safe_query("SHOW TABLES FROM bmos")
        if not result:
            print("✗ 表查询失败")
            return False
        print(f"✓ 找到 {len(result)} 个表")
        
        # 测试3: 数据插入
        print("\n3. 测试数据插入...")
        test_data = [{
            'vpt_id': 'dev_test_001',
            'vpt_name': '开发测试价值主张',
            'vpt_category': 'dev_test'
        }]
        
        if not self.safe_insert('dim_vpt', test_data):
            print("✗ 数据插入失败")
            return False
        print("✓ 数据插入成功")
        
        # 测试4: 数据验证
        print("\n4. 测试数据验证...")
        result = self.safe_query("SELECT * FROM bmos.dim_vpt WHERE vpt_id = 'dev_test_001'")
        if not result:
            print("✗ 数据验证失败")
            return False
        print("✓ 数据验证成功")
        
        print("\n=== 开发测试完成 ===")
        print("✓ 所有测试通过，开发环境正常")
        return True
    
    def show_usage_examples(self):
        """显示使用示例"""
        print("=== BMOS开发助手使用示例 ===\n")
        
        print("1. 检查环境状态:")
        print("   python scripts/dev_helper.py check")
        
        print("\n2. 运行开发测试:")
        print("   python scripts/dev_helper.py test")
        
        print("\n3. 查询数据:")
        print("   python scripts/dev_helper.py query 'SELECT * FROM bmos.dim_vpt LIMIT 5'")
        
        print("\n4. 获取表信息:")
        print("   python scripts/dev_helper.py table dim_vpt")
        
        print("\n5. 插入测试数据:")
        print("   python scripts/dev_helper.py insert dim_vpt '[{\"vpt_id\": \"test001\", \"vpt_name\": \"测试\"}]'")
        
        print("\n=== 开发规范 ===")
        print("✓ 使用TCP连接 (端口9000) - 稳定可靠")
        print("✓ 使用Docker exec - 绕过网络问题")
        print("✓ 在容器内运行后端服务")
        print("✗ 避免直接HTTP连接 (端口8123) - Windows Docker有问题")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        helper = BMOSDevHelper()
        helper.show_usage_examples()
        return
    
    command = sys.argv[1]
    helper = BMOSDevHelper()
    
    if command == "check":
        helper.check_environment()
    
    elif command == "test":
        helper.run_development_test()
    
    elif command == "query":
        if len(sys.argv) < 3:
            print("请提供SQL查询")
            return
        query = sys.argv[2]
        results = helper.safe_query(query)
        for row in results:
            print('\t'.join(str(cell) for cell in row))
    
    elif command == "table":
        if len(sys.argv) < 3:
            print("请提供表名")
            return
        table_name = sys.argv[2]
        info = helper.get_table_info(table_name)
        print(f"表名: {info['table_name']}")
        print(f"行数: {info['row_count']}")
        print(f"结构: {info['structure']}")
        print(f"示例数据: {info['sample_data']}")
    
    elif command == "insert":
        if len(sys.argv) < 4:
            print("请提供表名和JSON数据")
            return
        table_name = sys.argv[2]
        json_data = json.loads(sys.argv[3])
        success = helper.safe_insert(table_name, json_data)
        print("操作完成" if success else "操作失败")
    
    else:
        print(f"未知命令: {command}")
        helper.show_usage_examples()

if __name__ == "__main__":
    main()
