#!/usr/bin/env python3
"""
测试前端到后端的连接
"""
import subprocess
import json
import time

def run_command(cmd, timeout=30):
    """运行命令"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, 
            timeout=timeout, encoding='utf-8', errors='ignore'
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_frontend_backend_connection():
    """测试前端到后端连接"""
    print("=== 测试前端到后端连接 ===")
    
    # 测试前端容器内访问后端
    print("1. 测试前端容器内访问后端...")
    success, stdout, stderr = run_command(
        'docker exec bmos_frontend node -e "const http = require(\'http\'); http.get(\'http://backend:8000/health\', (res) => { let data = \'\'; res.on(\'data\', chunk => data += chunk); res.on(\'end\', () => { console.log(data); process.exit(0); }); }).on(\'error\', (err) => { console.error(err.message); process.exit(1); });"'
    )
    
    if success and "healthy" in stdout:
        print("✅ 前端容器可以访问后端API")
        try:
            health_data = json.loads(stdout.strip())
            print(f"   后端状态: {health_data.get('status', 'unknown')}")
            print(f"   ClickHouse状态: {health_data.get('clickhouse', {}).get('status', 'unknown')}")
        except:
            print(f"   响应内容: {stdout.strip()}")
    else:
        print("❌ 前端容器无法访问后端API")
        print(f"   错误: {stderr}")
        return False
    
    # 测试前端服务状态
    print("\n2. 测试前端服务状态...")
    success, stdout, stderr = run_command(
        'docker exec bmos_frontend ps aux'
    )
    
    if success and ("vite" in stdout or "node" in stdout):
        print("✅ 前端服务运行正常")
        print(f"   进程信息: {stdout.strip()}")
    else:
        print("❌ 前端服务异常")
        print(f"   进程信息: {stdout}")
        return False
    
    # 测试端口映射
    print("\n3. 测试端口映射...")
    success, stdout, stderr = run_command(
        'docker port bmos_frontend'
    )
    
    if success and "3000" in stdout:
        print("✅ 前端端口映射正常")
        print(f"   端口映射: {stdout.strip()}")
    else:
        print("❌ 前端端口映射异常")
        return False
    
    return True

def test_full_system():
    """测试完整系统"""
    print("\n=== 测试完整系统 ===")
    
    # 检查所有容器状态
    containers = ['bmos_clickhouse', 'bmos_redis', 'bmos_backend', 'bmos_frontend']
    
    for container in containers:
        success, stdout, stderr = run_command(f'docker ps --filter "name={container}" --format "{{{{.Names}}}}"')
        if success and container in stdout:
            print(f"✅ {container} 运行中")
        else:
            print(f"❌ {container} 未运行")
            return False
    
    print("\n✅ 所有容器运行正常")
    
    # 测试服务连通性
    print("\n4. 测试服务连通性...")
    
    # 后端健康检查
    success, stdout, stderr = run_command(
        'docker exec bmos_backend python -c "import requests; print(requests.get(\'http://localhost:8000/health\').text)"'
    )
    if success and "healthy" in stdout:
        print("✅ 后端服务健康")
    else:
        print("❌ 后端服务异常")
        return False
    
    # ClickHouse连接
    success, stdout, stderr = run_command(
        'docker exec bmos_clickhouse clickhouse-client --query "SELECT 1"'
    )
    if success and "1" in stdout:
        print("✅ ClickHouse连接正常")
    else:
        print("❌ ClickHouse连接异常")
        return False
    
    return True

def main():
    """主函数"""
    print("=== BMOS前端后端连接测试 ===\n")
    
    # 测试前端到后端连接
    frontend_ok = test_frontend_backend_connection()
    
    # 测试完整系统
    system_ok = test_full_system()
    
    print("\n=== 测试结果 ===")
    if frontend_ok and system_ok:
        print("🎉 所有测试通过！")
        print("\n✅ 系统状态:")
        print("   - 前端服务运行正常 (端口3000)")
        print("   - 后端服务运行正常 (端口8000)")
        print("   - 前端可以访问后端API")
        print("   - 所有容器网络连通")
        print("\n🌐 访问地址:")
        print("   - 前端界面: http://localhost:3000")
        print("   - 后端API: http://localhost:8000")
        print("   - 健康检查: http://localhost:8000/health")
    else:
        print("❌ 部分测试失败，请检查系统状态")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
