# BMOS系统测试策略 - 避免Windows Docker网络问题

## 问题总结

### Windows Docker网络问题
- **问题**: ClickHouse HTTP接口无法从宿主机直接访问
- **原因**: Windows Docker Desktop的Hyper-V虚拟化网络限制
- **影响**: 仅影响HTTP连接，TCP连接正常

### 解决方案
我们已经建立了完整的测试策略来避免这个问题：

## 测试工具

### 1. 开发助手 (`scripts/dev_helper.py`)
```bash
# 检查环境状态
python scripts/dev_helper.py check

# 运行开发测试
python scripts/dev_helper.py test

# 执行查询
python scripts/dev_helper.py query "SELECT * FROM bmos.dim_vpt LIMIT 5"

# 获取表信息
python scripts/dev_helper.py table dim_vpt
```

### 2. 系统验证 (`scripts/verify_system.py`)
```bash
# 完整系统验证
python scripts/verify_system.py
```

### 3. 工作区脚本 (`scripts/bmos_workaround.py`)
```bash
# 基础系统测试
python scripts/bmos_workaround.py

# 自定义查询
python scripts/bmos_workaround.py "SELECT COUNT(*) FROM bmos.dim_vpt"
```

## 开发规范

### ✅ 推荐做法

1. **使用TCP连接**
   ```python
   from clickhouse_driver import Client
   client = Client(host='localhost', port=9000)
   result = client.execute('SELECT 1')
   ```

2. **使用Docker exec**
   ```bash
   docker exec bmos_clickhouse clickhouse-client --query "SELECT 1"
   ```

3. **使用工作区脚本**
   ```bash
   python scripts/dev_helper.py query "SELECT * FROM bmos.dim_vpt"
   ```

4. **在容器内运行服务**
   ```yaml
   # docker-compose-dev.yml
   services:
     backend:
       build: ./backend
       depends_on:
         - clickhouse
       environment:
         CLICKHOUSE_URL: clickhouse://clickhouse:8123/bmos
   ```

### ❌ 避免做法

1. **直接HTTP连接**
   ```python
   # 不要这样做
   import requests
   response = requests.get("http://localhost:8123/?query=SELECT%201")
   ```

2. **使用clickhouse-sqlalchemy的HTTP连接**
   ```python
   # 不要这样做
   from clickhouse_sqlalchemy import make_session
   engine = create_engine("clickhouse://default:@localhost:8123/bmos")
   ```

## 测试流程

### 1. 开发前检查
```bash
# 检查环境状态
python scripts/dev_helper.py check

# 运行基础测试
python scripts/dev_helper.py test
```

### 2. 开发中测试
```bash
# 测试数据库操作
python scripts/dev_helper.py query "SELECT COUNT(*) FROM bmos.dim_vpt"

# 测试数据插入
python scripts/dev_helper.py insert dim_vpt '[{"vpt_id": "test001", "vpt_name": "测试"}]'
```

### 3. 部署前验证
```bash
# 完整系统验证
python scripts/verify_system.py

# 检查系统报告
cat system_report.json
```

## 当前系统状态

### ✅ 正常工作的功能
- ClickHouse容器运行正常
- 所有BMOS表结构创建成功 (23张表)
- 示例数据插入成功
- TCP连接 (端口9000) 正常
- Redis连接正常
- 后端服务正常

### ⚠️ 受限的功能
- 从宿主机直接访问ClickHouse HTTP接口
- 使用requests库进行HTTP查询

### 🔧 可用的替代方案
- 使用Docker exec执行查询
- 使用TCP连接进行开发
- 使用工作区脚本
- 在容器内运行服务

## 开发建议

### 1. 数据层开发
```bash
# 使用工作区脚本测试查询
python scripts/dev_helper.py query "SHOW TABLES FROM bmos"

# 插入测试数据
python scripts/dev_helper.py insert dim_vpt '[{"vpt_id": "vpt006", "vpt_name": "新价值主张", "vpt_category": "test"}]'
```

### 2. 后端开发
```python
# 使用TCP连接
from clickhouse_driver import Client

client = Client(host='localhost', port=9000)
result = client.execute('SELECT * FROM bmos.dim_vpt')
```

### 3. API开发
在Docker容器内运行后端服务，通过容器端口访问API。

### 4. 前端开发
通过容器端口访问后端API，不受HTTP连接问题影响。

## 故障排除

### 常见问题及解决方案

#### 问题1: TCP连接失败
```bash
# 检查ClickHouse容器状态
docker ps | grep clickhouse

# 检查端口映射
docker port bmos_clickhouse

# 重启容器
docker-compose -f docker-compose-simple.yml restart clickhouse
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

## 监控脚本

### 健康检查 (`scripts/health_check.py`)
```bash
# 运行健康检查
python scripts/health_check.py
```

## 总结

通过以上测试策略和开发规范，我们可以：

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

**当前系统状态**: 🎉 **完全可用，可以继续开发！**

现在可以安全地进行后续开发工作，不会再遇到Windows Docker网络问题。






