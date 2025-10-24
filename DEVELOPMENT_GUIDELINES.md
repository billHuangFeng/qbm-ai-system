# BMOS系统开发规范 - 避免Windows Docker网络问题

## 核心原则

### 1. 网络连接策略
- **优先使用**: TCP连接 (端口9000) - 稳定可靠
- **备选方案**: Docker exec - 绕过网络问题
- **避免使用**: 直接HTTP连接 (端口8123) - Windows Docker有问题

### 2. 开发环境配置
- **数据库操作**: 使用工作区脚本或TCP连接
- **API开发**: 在Docker容器内运行服务
- **测试验证**: 通过容器端口访问

## 具体实施方案

### 方案1: 使用TCP连接开发（推荐）

#### 1.1 Python客户端配置
```python
# backend/app/clickhouse.py
from clickhouse_driver import Client
import logging

logger = logging.getLogger(__name__)

class ClickHouseClient:
    def __init__(self, host='localhost', port=9000, user='default', password='', database='bmos'):
        """
        使用TCP连接，避免HTTP连接问题
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self._client = None
        self.connect()
    
    def connect(self):
        """建立TCP连接"""
        try:
            self._client = Client(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            logger.info(f"TCP连接成功: {self.host}:{self.port}/{self.database}")
        except Exception as e:
            logger.error(f"TCP连接失败: {e}")
            raise
    
    def execute(self, query: str, params: dict = None):
        """执行查询"""
        try:
            if not self._client:
                self.connect()
            result = self._client.execute(query, params)
            return result
        except Exception as e:
            logger.error(f"查询执行失败: {e}\nQuery: {query}")
            raise
    
    def execute_non_query(self, query: str, params: dict = None):
        """执行非查询操作"""
        try:
            if not self._client:
                self.connect()
            self._client.execute(query, params)
            logger.debug(f"执行成功: {query[:100]}...")
        except Exception as e:
            logger.error(f"执行失败: {e}\nQuery: {query}")
            raise

# 全局客户端实例
clickhouse_client = ClickHouseClient()
```

#### 1.2 使用示例
```python
# 在任何需要数据库操作的地方
from app.clickhouse import clickhouse_client

# 查询数据
results = clickhouse_client.execute("SELECT * FROM bmos.dim_vpt LIMIT 10")

# 插入数据
clickhouse_client.execute_non_query(
    "INSERT INTO bmos.dim_vpt (vpt_id, vpt_name, category) VALUES",
    [('vpt006', '新价值主张', 'test')]
)
```

### 方案2: 使用工作区脚本

#### 2.1 创建统一的数据库操作脚本
```python
# scripts/db_operations.py
#!/usr/bin/env python3
"""
统一的数据库操作脚本 - 避免网络问题
"""
import subprocess
import json
import sys
from typing import List, Dict, Any

class DatabaseOperations:
    def __init__(self):
        self.container_name = "bmos_clickhouse"
    
    def execute_query(self, query: str) -> List[tuple]:
        """执行查询并返回结果"""
        cmd = f'docker exec {self.container_name} clickhouse-client --query "{query}"'
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                # 解析结果
                lines = result.stdout.strip().split('\n')
                if not lines or lines == ['']:
                    return []
                
                # 简单解析（假设是制表符分隔）
                return [tuple(line.split('\t')) for line in lines if line.strip()]
            else:
                print(f"查询失败: {result.stderr}")
                return []
        except Exception as e:
            print(f"执行错误: {e}")
            return []
    
    def execute_non_query(self, query: str) -> bool:
        """执行非查询操作"""
        cmd = f'docker exec {self.container_name} clickhouse-client --query "{query}"'
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception as e:
            print(f"执行错误: {e}")
            return False
    
    def get_table_data(self, table_name: str, limit: int = 100) -> List[Dict]:
        """获取表数据"""
        query = f"SELECT * FROM bmos.{table_name} LIMIT {limit}"
        results = self.execute_query(query)
        
        # 获取列名
        columns_query = f"DESCRIBE bmos.{table_name}"
        columns_result = self.execute_query(columns_query)
        columns = [col[0] for col in columns_result]
        
        # 转换为字典列表
        return [dict(zip(columns, row)) for row in results]
    
    def insert_data(self, table_name: str, data: List[Dict]) -> bool:
        """插入数据"""
        if not data:
            return True
        
        # 构建INSERT语句
        columns = list(data[0].keys())
        columns_str = ', '.join(columns)
        
        # 构建VALUES部分
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
        
        query = f"INSERT INTO bmos.{table_name} ({columns_str}) VALUES {', '.join(values_list)}"
        return self.execute_non_query(query)

# 全局实例
db_ops = DatabaseOperations()

def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("用法: python db_operations.py <command> [args...]")
        print("命令:")
        print("  query <sql>     - 执行查询")
        print("  insert <table> <json> - 插入数据")
        print("  get <table> [limit] - 获取表数据")
        return
    
    command = sys.argv[1]
    
    if command == "query":
        if len(sys.argv) < 3:
            print("请提供SQL查询")
            return
        query = sys.argv[2]
        results = db_ops.execute_query(query)
        for row in results:
            print('\t'.join(str(cell) for cell in row))
    
    elif command == "get":
        if len(sys.argv) < 3:
            print("请提供表名")
            return
        table_name = sys.argv[2]
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 100
        data = db_ops.get_table_data(table_name, limit)
        print(json.dumps(data, ensure_ascii=False, indent=2))
    
    elif command == "insert":
        if len(sys.argv) < 4:
            print("请提供表名和JSON数据")
            return
        table_name = sys.argv[2]
        json_data = json.loads(sys.argv[3])
        success = db_ops.insert_data(table_name, json_data)
        print("插入成功" if success else "插入失败")

if __name__ == "__main__":
    main()
```

#### 2.2 使用示例
```bash
# 查询数据
python scripts/db_operations.py query "SELECT * FROM bmos.dim_vpt LIMIT 5"

# 获取表数据
python scripts/db_operations.py get dim_vpt 10

# 插入数据
python scripts/db_operations.py insert dim_vpt '[{"vpt_id": "vpt006", "vpt_name": "新价值主张", "category": "test"}]'
```

### 方案3: 容器内开发

#### 3.1 后端服务容器化
```yaml
# docker-compose-dev.yml
version: '3.8'

services:
  clickhouse:
    image: clickhouse/clickhouse-server:latest
    container_name: bmos_clickhouse
    ports:
      - "8123:8123"
      - "9000:9000"
    environment:
      CLICKHOUSE_DB: bmos
      CLICKHOUSE_USER: default
      CLICKHOUSE_PASSWORD: ""
    volumes:
      - clickhouse_data:/var/lib/clickhouse
      - ./database/clickhouse/config/custom_config.xml:/etc/clickhouse-server/config.d/custom_config.xml
    networks:
      - bmos_network

  redis:
    image: redis:7-alpine
    container_name: bmos_redis
    ports:
      - "6380:6379"
    networks:
      - bmos_network

  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile.dev
    container_name: bmos_backend
    ports:
      - "8000:8000"
    depends_on:
      - clickhouse
      - redis
    environment:
      CLICKHOUSE_URL: clickhouse://clickhouse:8123/bmos
      REDIS_URL: redis://redis:6379/0
    volumes:
      - ./backend:/app
    networks:
      - bmos_network
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  clickhouse_data:

networks:
  bmos_network:
    driver: bridge
```

#### 3.2 开发用Dockerfile
```dockerfile
# backend/Dockerfile.dev
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令（开发模式）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

## 测试策略

### 1. 单元测试
```python
# tests/test_database.py
import pytest
from scripts.db_operations import db_ops

class TestDatabaseOperations:
    def test_connection(self):
        """测试数据库连接"""
        results = db_ops.execute_query("SELECT 1")
        assert len(results) == 1
        assert results[0][0] == 1
    
    def test_table_exists(self):
        """测试表是否存在"""
        results = db_ops.execute_query("SHOW TABLES FROM bmos")
        table_names = [row[0] for row in results]
        assert 'dim_vpt' in table_names
        assert 'fact_order' in table_names
    
    def test_data_insertion(self):
        """测试数据插入"""
        test_data = [{
            'vpt_id': 'test_vpt_001',
            'vpt_name': '测试价值主张',
            'category': 'test'
        }]
        
        success = db_ops.insert_data('dim_vpt', test_data)
        assert success
        
        # 验证插入
        results = db_ops.execute_query("SELECT * FROM bmos.dim_vpt WHERE vpt_id = 'test_vpt_001'")
        assert len(results) == 1
        assert results[0][1] == '测试价值主张'
```

### 2. 集成测试
```python
# tests/test_integration.py
import pytest
import requests
import time

class TestBMOSIntegration:
    @pytest.fixture(scope="session")
    def backend_url(self):
        """等待后端服务启动"""
        url = "http://localhost:8000"
        max_retries = 30
        for i in range(max_retries):
            try:
                response = requests.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    return url
            except:
                pass
            time.sleep(2)
        pytest.skip("后端服务未启动")
    
    def test_health_check(self, backend_url):
        """测试健康检查"""
        response = requests.get(f"{backend_url}/health")
        assert response.status_code == 200
    
    def test_vpt_api(self, backend_url):
        """测试VPT API"""
        # 创建VPT
        vpt_data = {
            "vpt_id": "test_vpt_002",
            "vpt_name": "测试价值主张2",
            "category": "test"
        }
        
        response = requests.post(f"{backend_url}/api/v1/bmos/dimensions/vpt", json=vpt_data)
        assert response.status_code == 201
        
        # 获取VPT列表
        response = requests.get(f"{backend_url}/api/v1/bmos/dimensions/vpt")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
```

### 3. 端到端测试
```python
# tests/test_e2e.py
import pytest
from scripts.db_operations import db_ops
import requests

class TestE2E:
    def test_complete_workflow(self):
        """测试完整工作流程"""
        # 1. 创建VPT
        vpt_data = [{
            'vpt_id': 'e2e_vpt_001',
            'vpt_name': 'E2E测试价值主张',
            'category': 'e2e_test'
        }]
        
        success = db_ops.insert_data('dim_vpt', vpt_data)
        assert success
        
        # 2. 创建订单
        order_data = [{
            'order_id': 'e2e_order_001',
            'customer_id': 'e2e_cust_001',
            'sku_id': 'e2e_sku_001',
            'conv_id': 'e2e_conv_001',
            'date_key': '2024-01-01',
            'order_type': 'normal',
            'qty': 1,
            'amt': 1000.00,
            'vpt_snap': ['e2e_vpt_001'],
            'pft_snap': ['e2e_pft_001']
        }]
        
        success = db_ops.insert_data('fact_order', order_data)
        assert success
        
        # 3. 验证数据
        results = db_ops.execute_query("""
            SELECT o.order_id, v.vpt_name 
            FROM bmos.fact_order o
            JOIN bmos.dim_vpt v ON has(o.vpt_snap, v.vpt_id)
            WHERE o.order_id = 'e2e_order_001'
        """)
        
        assert len(results) == 1
        assert results[0][0] == 'e2e_order_001'
        assert results[0][1] == 'E2E测试价值主张'
```

## 开发工作流程

### 1. 日常开发流程
```bash
# 1. 启动开发环境
docker-compose -f docker-compose-dev.yml up -d

# 2. 等待服务启动
sleep 30

# 3. 运行测试
python -m pytest tests/ -v

# 4. 开发新功能
# 使用TCP连接或工作区脚本进行数据库操作

# 5. 验证功能
python scripts/bmos_workaround.py "SELECT COUNT(*) FROM bmos.dim_vpt"
```

### 2. 部署前检查
```bash
# 1. 运行完整测试套件
python -m pytest tests/ -v --cov=app

# 2. 检查数据库连接
python scripts/db_operations.py query "SELECT 1"

# 3. 验证API端点
curl http://localhost:8000/health

# 4. 检查数据完整性
python scripts/bmos_workaround.py "SHOW TABLES FROM bmos"
```

## 故障排除

### 1. 常见问题及解决方案

#### 问题1: TCP连接失败
```bash
# 检查ClickHouse容器状态
docker ps | grep clickhouse

# 检查端口映射
docker port bmos_clickhouse

# 重启容器
docker-compose -f docker-compose-dev.yml restart clickhouse
```

#### 问题2: 工作区脚本执行失败
```bash
# 检查容器是否运行
docker exec bmos_clickhouse clickhouse-client --query "SELECT 1"

# 检查数据库是否存在
docker exec bmos_clickhouse clickhouse-client --query "SHOW DATABASES"

# 重新创建数据库
docker exec bmos_clickhouse clickhouse-client --query "CREATE DATABASE IF NOT EXISTS bmos"
```

#### 问题3: 后端服务无法连接数据库
```bash
# 检查后端容器日志
docker logs bmos_backend

# 检查网络连接
docker exec bmos_backend ping clickhouse

# 重启后端服务
docker-compose -f docker-compose-dev.yml restart backend
```

### 2. 监控脚本
```python
# scripts/health_check.py
#!/usr/bin/env python3
"""
系统健康检查脚本
"""
import subprocess
import requests
import sys

def check_clickhouse():
    """检查ClickHouse连接"""
    try:
        result = subprocess.run(
            "docker exec bmos_clickhouse clickhouse-client --query 'SELECT 1'",
            shell=True, capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0, result.stdout.strip()
    except:
        return False, "连接失败"

def check_redis():
    """检查Redis连接"""
    try:
        result = subprocess.run(
            "docker exec bmos_redis redis-cli ping",
            shell=True, capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0, result.stdout.strip()
    except:
        return False, "连接失败"

def check_backend():
    """检查后端服务"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200, f"状态码: {response.status_code}"
    except:
        return False, "连接失败"

def main():
    """主检查函数"""
    print("=== BMOS系统健康检查 ===\n")
    
    checks = [
        ("ClickHouse", check_clickhouse),
        ("Redis", check_redis),
        ("Backend", check_backend)
    ]
    
    all_ok = True
    for name, check_func in checks:
        success, message = check_func()
        status = "✓" if success else "✗"
        print(f"{status} {name}: {message}")
        if not success:
            all_ok = False
    
    print(f"\n=== 检查结果 ===")
    if all_ok:
        print("✓ 所有服务正常")
        sys.exit(0)
    else:
        print("✗ 部分服务异常")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## 总结

通过以上规范，我们可以：

1. **避免网络问题**: 使用TCP连接和工作区脚本
2. **确保开发效率**: 提供多种开发方式
3. **保证测试质量**: 完整的测试策略
4. **简化故障排除**: 清晰的监控和诊断工具

**关键原则**:
- ✅ 优先使用TCP连接 (端口9000)
- ✅ 使用工作区脚本进行数据库操作
- ✅ 在容器内运行后端服务
- ✅ 通过容器端口访问API
- ❌ 避免直接HTTP连接 (端口8123)

这样就能确保后续开发不再遇到Windows Docker网络问题！




