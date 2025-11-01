"""
BMOS系统 - 简化API测试
测试基础API功能，不依赖复杂的ML库
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import httpx
from datetime import datetime

# 创建简化的FastAPI应用
app = FastAPI(
    title="BMOS API Test",
    description="BMOS系统API测试",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "BMOS API Test Server",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/test")
async def test_endpoint():
    """测试端点"""
    return {
        "message": "Test endpoint working",
        "data": {
            "test_id": "test_001",
            "test_time": datetime.now().isoformat()
        }
    }

@app.post("/test/post")
async def test_post(data: dict):
    """测试POST端点"""
    return {
        "message": "POST test successful",
        "received_data": data,
        "timestamp": datetime.now().isoformat()
    }

class APITester:
    """API测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
    
    async def test_all_endpoints(self):
        """测试所有端点"""
        print("开始BMOS API测试...")
        print("=" * 50)
        
        async with httpx.AsyncClient() as client:
            # 测试根路径
            print("1. 测试根路径...")
            try:
                response = await client.get(f"{self.base_url}/")
                print(f"   状态码: {response.status_code}")
                print(f"   响应: {response.json()}")
            except Exception as e:
                print(f"   错误: {e}")
            
            # 测试健康检查
            print("\n2. 测试健康检查...")
            try:
                response = await client.get(f"{self.base_url}/health")
                print(f"   状态码: {response.status_code}")
                print(f"   响应: {response.json()}")
            except Exception as e:
                print(f"   错误: {e}")
            
            # 测试GET端点
            print("\n3. 测试GET端点...")
            try:
                response = await client.get(f"{self.base_url}/test")
                print(f"   状态码: {response.status_code}")
                print(f"   响应: {response.json()}")
            except Exception as e:
                print(f"   错误: {e}")
            
            # 测试POST端点
            print("\n4. 测试POST端点...")
            try:
                test_data = {"test": "data", "number": 123}
                response = await client.post(f"{self.base_url}/test/post", json=test_data)
                print(f"   状态码: {response.status_code}")
                print(f"   响应: {response.json()}")
            except Exception as e:
                print(f"   错误: {e}")
        
        print("=" * 50)
        print("测试完成!")

async def run_server():
    """运行测试服务器"""
    print("启动BMOS测试服务器...")
    config = uvicorn.Config(
        app=app,
        host="127.0.0.1",
        port=8001,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()

async def run_tests():
    """运行测试"""
    # 等待服务器启动
    await asyncio.sleep(2)
    
    tester = APITester()
    await tester.test_all_endpoints()

async def main():
    """主函数"""
    print("自动运行模式3: 启动服务器并运行测试")
    
    # 在后台启动服务器
    server_task = asyncio.create_task(run_server())
    # 等待一下让服务器启动
    await asyncio.sleep(3)
    # 运行测试
    await run_tests()
    # 停止服务器
    server_task.cancel()

if __name__ == "__main__":
    asyncio.run(main())
