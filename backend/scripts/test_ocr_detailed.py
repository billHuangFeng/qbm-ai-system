"""
详细的OCR测试脚本
测试OCR功能并诊断问题
"""

import sys
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import tempfile
import asyncio

# 添加项目路径
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

async def test_ocr_directly():
    """直接测试OCR功能"""
    print("=" * 70)
    print("  直接OCR测试")
    print("=" * 70)
    
    try:
        from src.services.expert_knowledge.document_processing_service import DocumentProcessingService
        
        service = DocumentProcessingService()
        
        # 创建测试图片
        print("\n1. 创建测试图片...")
        img = Image.new('RGB', (1000, 300), color='white')
        draw = ImageDraw.Draw(img)
        
        # 尝试使用系统字体
        font = None
        font_paths = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/simsun.ttc",
        ]
        
        for path in font_paths:
            if os.path.exists(path):
                try:
                    font = ImageFont.truetype(path, 60)  # 更大的字号
                    print(f"   使用字体: {path}")
                    break
                except:
                    continue
        
        if font is None:
            font = ImageFont.load_default()
            print("   使用默认字体")
        
        # 绘制多个文本行
        texts = [
            "Test OCR Recognition",
            "测试OCR文字识别",
            "2025-01-31"
        ]
        
        y_position = 50
        for text in texts:
            draw.text((50, y_position), text, fill='black', font=font)
            y_position += 80
        
        # 保存图片
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        img.save(temp_file.name, 'PNG', quality=100)
        temp_file.close()
        
        print(f"   测试图片已保存: {temp_file.name}")
        print(f"   图片大小: {img.size}")
        
        # 测试OCR
        print("\n2. 执行OCR识别...")
        result = await service.extract_text_from_image(temp_file.name)
        
        print(f"\n3. OCR结果:")
        print(f"   成功: {result.get('success')}")
        print(f"   完整文本: {result.get('full_text', '')[:200]}")
        print(f"   文本长度: {len(result.get('full_text', ''))}")
        print(f"   单词数: {result.get('word_count', 0)}")
        print(f"   平均置信度: {result.get('average_confidence', 'N/A')}")
        
        if result.get('words'):
            print(f"   识别的单词数: {len(result.get('words', []))}")
            print(f"   前3个单词:")
            for word in result.get('words', [])[:3]:
                print(f"     - '{word.get('text')}' (置信度: {word.get('confidence')}%)")
        
        # 清理
        try:
            os.unlink(temp_file.name)
        except:
            pass
        
        return result.get('success') and len(result.get('full_text', '')) > 0
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_api_upload_with_ocr():
    """通过API测试图片上传和OCR"""
    print("\n" + "=" * 70)
    print("  API上传测试（带OCR验证）")
    print("=" * 70)
    
    try:
        import requests
        
        # 创建测试图片
        print("\n1. 创建测试图片...")
        img = Image.new('RGB', (800, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        font = None
        font_paths = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/simsun.ttc",
        ]
        
        for path in font_paths:
            if os.path.exists(path):
                try:
                    font = ImageFont.truetype(path, 48)
                    break
                except:
                    continue
        
        if font is None:
            font = ImageFont.load_default()
        
        draw.text((50, 70), "API OCR Test 2025", fill='black', font=font)
        
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        img.save(temp_file.name, 'PNG', quality=95)
        temp_file.close()
        
        print(f"   图片路径: {temp_file.name}")
        
        # 上传到API
        print("\n2. 上传到API...")
        files = {
            'file': ('test_ocr.png', open(temp_file.name, 'rb'), 'image/png')
        }
        
        data = {
            'title': 'API OCR测试',
            'domain_category': 'cost_optimization',
            'problem_type': 'optimization_problem',
            'knowledge_type': 'tool_template',
            'summary': '通过API上传的OCR测试图片'
        }
        
        response = requests.post(
            'http://localhost:8081/expert-knowledge/import',
            files=files,
            data=data,
            timeout=30
        )
        
        files['file'][1].close()
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"\n3. API响应:")
            print(f"   成功: {result.get('success')}")
            print(f"   知识ID: {result.get('knowledge_id')}")
            
            file_info = result.get('file_info', {})
            print(f"   文件信息: {file_info}")
            print(f"   提取的文本长度: {file_info.get('extracted_text_length', 0)}")
            
            if result.get('knowledge_id'):
                # 获取知识详情
                print("\n4. 获取知识详情...")
                knowledge_id = result.get('knowledge_id')
                detail_response = requests.get(
                    f'http://localhost:8081/expert-knowledge/{knowledge_id}',
                    timeout=10
                )
                
                if detail_response.status_code == 200:
                    knowledge = detail_response.json().get('knowledge', {})
                    content = knowledge.get('content', '')
                    print(f"   内容长度: {len(content)}")
                    if content:
                        print(f"   内容预览: {content[:200]}...")
                    else:
                        print("   ⚠️ 内容为空")
            
            # 清理
            try:
                os.unlink(temp_file.name)
            except:
                pass
            
            return True
        else:
            print(f"\n❌ 上传失败: {response.status_code}")
            print(f"   响应: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("  详细OCR测试")
    print("=" * 70)
    
    results = {}
    
    # 直接测试OCR
    results["直接OCR测试"] = await test_ocr_directly()
    
    # API上传测试
    results["API上传测试"] = await test_api_upload_with_ocr()
    
    # 总结
    print("\n" + "=" * 70)
    print("  测试总结")
    print("=" * 70)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} | {test_name}")
    
    passed = sum(1 for r in results.values() if r)
    print(f"\n总计: {passed}/{len(results)} 个测试通过")
    
    if passed == len(results):
        print("\n🎉 所有OCR测试通过！")
    else:
        print("\n⚠️ 部分测试失败，请检查OCR配置")

if __name__ == "__main__":
    asyncio.run(main())


