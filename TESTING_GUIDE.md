# QBM AI System 测试指南

## 概述

本指南将帮助您全面测试QBM AI System的各个功能模块，确保系统正常运行。

## 测试环境准备

### 1. 系统要求检查
```bash
# 检查Docker版本
docker --version
docker-compose --version

# 检查Python版本
python --version

# 检查Node.js版本
node --version
npm --version
```

### 2. 启动测试环境
```bash
# 进入项目目录
cd qbm-ai-system

# 启动所有服务
python scripts/start.py start

# 等待服务启动（约30-60秒）
sleep 60

# 检查服务状态
python scripts/start.py status
```

## 自动化测试

### 1. 运行完整测试套件
```bash
# 运行所有测试
python scripts/run_tests.py

# 运行后端测试
cd backend
pytest tests/ -v

# 运行前端测试
cd frontend
npm test
```

### 2. 健康检查测试
```bash
# 运行健康检查
python scripts/health_check.py

# 带等待的健康检查
python scripts/health_check.py --wait --timeout 300
```

## 手动功能测试

### 1. 系统访问测试

#### 前端访问测试
```bash
# 测试前端页面
curl -I http://localhost:8080
# 预期结果: HTTP/1.1 200 OK

# 在浏览器中访问
# http://localhost:8080
```

#### 后端API测试
```bash
# 测试后端健康检查
curl http://localhost:8000/health
# 预期结果: {"status":"healthy","timestamp":...,"version":"1.0.0"}

# 测试API文档
curl -I http://localhost:8000/docs
# 预期结果: HTTP/1.1 200 OK
```

### 2. 用户认证测试

#### 登录测试
```bash
# 测试用户登录
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# 预期结果: 包含access_token的JSON响应
```

#### 获取用户信息测试
```bash
# 使用登录获得的token
TOKEN="your_access_token_here"

curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"

# 预期结果: 用户信息JSON
```

### 3. 数据管理测试

#### 客户管理测试
```bash
# 创建客户
curl -X POST http://localhost:8000/api/v1/customers/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试客户",
    "contact_person": "张三",
    "contact_email": "zhangsan@example.com",
    "contact_phone": "13800138001",
    "industry": "科技",
    "region": "北京"
  }'

# 获取客户列表
curl -X GET http://localhost:8000/api/v1/customers/ \
  -H "Authorization: Bearer $TOKEN"

# 预期结果: 包含客户列表的JSON响应
```

#### 产品管理测试
```bash
# 创建产品
curl -X POST http://localhost:8000/api/v1/products/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试产品",
    "description": "这是一个测试产品",
    "price": 99.99,
    "category": "软件",
    "stock_quantity": 100
  }'

# 获取产品列表
curl -X GET http://localhost:8000/api/v1/products/ \
  -H "Authorization: Bearer $TOKEN"
```

### 4. 数据分析测试

#### 客户分析测试
```bash
# 运行客户分析
curl -X POST http://localhost:8000/api/v1/analysis/customers \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_type": "segmentation",
    "parameters": {
      "n_clusters": 3
    }
  }'

# 预期结果: 分析结果JSON
```

#### 产品分析测试
```bash
# 运行产品分析
curl -X POST http://localhost:8000/api/v1/analysis/products \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_type": "recommendation",
    "parameters": {
      "top_n": 5
    }
  }'
```

### 5. 数据导入测试

#### 准备测试数据
```bash
# 创建测试CSV文件
cat > test_customers.csv << EOF
name,contact_person,contact_email,contact_phone,industry,region
测试客户1,张三,zhangsan@example.com,13800138001,科技,北京
测试客户2,李四,lisi@example.com,13800138002,金融,上海
测试客户3,王五,wangwu@example.com,13800138003,教育,广州
EOF
```

#### 测试数据导入
```bash
# 上传测试文件
curl -X POST http://localhost:8000/api/v1/data-import/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_customers.csv" \
  -F "data_type=customers"

# 预期结果: 上传成功响应
```

### 6. 系统监控测试

#### 系统状态测试
```bash
# 获取系统状态
curl -X GET http://localhost:8000/api/v1/system/status \
  -H "Authorization: Bearer $TOKEN"

# 预期结果: 系统状态信息
```

#### 性能指标测试
```bash
# 获取性能指标
curl -X GET http://localhost:8000/api/v1/system/metrics \
  -H "Authorization: Bearer $TOKEN"

# 预期结果: 性能指标数据
```

## 前端界面测试

### 1. 登录页面测试
1. 访问 http://localhost:8080
2. 输入用户名: `admin`
3. 输入密码: `admin123`
4. 点击登录按钮
5. 验证是否成功跳转到仪表盘

### 2. 导航测试
1. 测试侧边栏菜单点击
2. 验证页面跳转是否正确
3. 测试面包屑导航
4. 验证页面标题显示

### 3. 数据管理测试
1. **客户管理**:
   - 点击"客户管理"菜单
   - 点击"新增客户"按钮
   - 填写客户信息并保存
   - 验证客户列表是否更新
   - 测试编辑和删除功能

2. **产品管理**:
   - 点击"产品管理"菜单
   - 测试产品的增删改查功能
   - 验证数据验证规则

### 4. 数据分析测试
1. **客户分析**:
   - 点击"数据分析"菜单
   - 选择"客户分析"
   - 点击"综合分析"按钮
   - 验证图表是否正确显示
   - 测试不同分析类型的切换

2. **产品分析**:
   - 切换到"产品分析"
   - 验证产品分析图表
   - 测试分析结果展示

### 5. 数据导入测试
1. 点击"数据导入"菜单
2. 点击"导入数据"按钮
3. 选择数据类型（如客户数据）
4. 上传测试文件
5. 预览数据并确认导入
6. 验证导入结果

### 6. 系统设置测试
1. 点击"系统设置"菜单
2. 测试各个设置标签页
3. 修改设置并保存
4. 验证设置是否生效

## 性能测试

### 1. 负载测试
```bash
# 安装Apache Bench
# Ubuntu/Debian: sudo apt install apache2-utils
# CentOS/RHEL: sudo yum install httpd-tools

# 测试登录接口
ab -n 100 -c 10 -p login_data.json -T application/json http://localhost:8000/api/v1/auth/login

# 测试客户列表接口
ab -n 100 -c 10 -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/customers/
```

### 2. 并发测试
```bash
# 使用wrk进行并发测试
# 安装: https://github.com/wg/wrk

# 测试API并发性能
wrk -t12 -c400 -d30s http://localhost:8000/api/v1/customers/
```

### 3. 数据库性能测试
```bash
# 连接数据库
docker exec -it qbm-mysql mysql -u root -p

# 测试查询性能
SELECT COUNT(*) FROM customers;
SELECT * FROM customers LIMIT 1000;
```

## 安全测试

### 1. 认证安全测试
```bash
# 测试无效凭据
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=wrongpassword"

# 预期结果: 401 Unauthorized

# 测试无token访问
curl -X GET http://localhost:8000/api/v1/customers/

# 预期结果: 401 Unauthorized
```

### 2. 输入验证测试
```bash
# 测试SQL注入
curl -X POST http://localhost:8000/api/v1/customers/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "test\"; DROP TABLE customers; --"}'

# 预期结果: 数据验证错误，不会执行SQL注入
```

### 3. CORS测试
```bash
# 测试跨域请求
curl -X OPTIONS http://localhost:8000/api/v1/customers/ \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET"

# 预期结果: 包含CORS头部的响应
```

## 错误处理测试

### 1. 网络错误测试
```bash
# 停止数据库服务
docker-compose stop mysql

# 测试API调用
curl http://localhost:8000/api/v1/customers/

# 预期结果: 适当的错误响应

# 重启数据库服务
docker-compose start mysql
```

### 2. 数据验证错误测试
```bash
# 测试无效数据
curl -X POST http://localhost:8000/api/v1/customers/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "", "contact_email": "invalid-email"}'

# 预期结果: 验证错误信息
```

## 浏览器兼容性测试

### 1. 现代浏览器测试
- Chrome (最新版本)
- Firefox (最新版本)
- Safari (最新版本)
- Edge (最新版本)

### 2. 移动端测试
- 响应式设计验证
- 触摸操作测试
- 移动端性能测试

## 测试报告

### 1. 创建测试报告
```bash
# 运行测试并生成报告
python scripts/run_tests.py > test_report.txt 2>&1

# 查看测试结果
cat test_report.txt
```

### 2. 测试检查清单
- [ ] 系统启动正常
- [ ] 用户认证功能正常
- [ ] 数据管理功能正常
- [ ] 数据分析功能正常
- [ ] 数据导入功能正常
- [ ] 系统监控功能正常
- [ ] 前端界面正常
- [ ] API接口正常
- [ ] 数据库连接正常
- [ ] 性能指标正常

## 故障排除

### 1. 常见问题
```bash
# 服务启动失败
docker-compose logs

# 数据库连接失败
docker exec qbm-mysql mysqladmin -u root -p status

# 前端无法访问
docker exec qbm-frontend nginx -t
```

### 2. 日志查看
```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs backend
docker-compose logs frontend
docker-compose logs mysql
```

### 3. 重置系统
```bash
# 停止所有服务
docker-compose down

# 清理数据卷
docker-compose down -v

# 重新启动
docker-compose up -d
```

## 持续集成测试

### 1. GitHub Actions测试
```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: python scripts/run_tests.py
```

### 2. 自动化测试脚本
```bash
#!/bin/bash
# test_automation.sh

echo "开始自动化测试..."

# 启动服务
python scripts/start.py start

# 等待服务启动
sleep 60

# 运行健康检查
python scripts/health_check.py

# 运行功能测试
python scripts/run_tests.py

# 运行性能测试
# ab -n 100 -c 10 http://localhost:8000/api/v1/customers/

echo "自动化测试完成"
```

## 测试最佳实践

1. **测试前准备**: 确保测试环境干净，数据一致
2. **测试数据管理**: 使用独立的测试数据，避免影响生产数据
3. **测试覆盖**: 确保所有功能模块都有测试覆盖
4. **回归测试**: 每次代码变更后运行完整的测试套件
5. **性能基准**: 建立性能基准，监控性能变化
6. **安全测试**: 定期进行安全测试，确保系统安全

---

通过以上测试指南，您可以全面验证QBM AI System的各个功能模块，确保系统稳定可靠地运行。





