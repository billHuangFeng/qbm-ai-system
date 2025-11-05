"""
文档上传实用示例
提供完整的文档上传示例代码，可以直接使用
"""

import requests
import sys
from pathlib import Path

BASE_URL = "http://localhost:8081"


def upload_image_file(image_path, title="测试图片", domain="cost_optimization"):
    """上传图片并OCR识别"""
    print(f"\n📤 上传图片: {image_path}")

    files = {"file": (Path(image_path).name, open(image_path, "rb"), "image/png")}

    data = {
        "title": title,
        "domain_category": domain,
        "problem_type": "optimization_problem",
        "knowledge_type": "tool_template",
        "summary": f"从图片 {Path(image_path).name} 导入的知识",
    }

    try:
        response = requests.post(
            f"{BASE_URL}/expert-knowledge/import", files=files, data=data, timeout=30
        )

        files["file"][1].close()

        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ 上传成功！")
            print(f"   知识ID: {result.get('knowledge_id')}")
            print(
                f"   提取的文本长度: {result.get('file_info', {}).get('extracted_text_length', 0)}"
            )
            print(f"   摘要: {result.get('extracted_summary', '')[:100]}...")
            return result
        else:
            print(f"❌ 上传失败: {response.status_code}")
            print(f"   错误: {response.text[:200]}")
            return None

    except Exception as e:
        print(f"❌ 错误: {e}")
        return None


def upload_word_document(docx_path, title="测试Word文档", domain="business_model"):
    """上传Word文档"""
    print(f"\n📤 上传Word文档: {docx_path}")

    if not Path(docx_path).exists():
        print(f"❌ 文件不存在: {docx_path}")
        return None

    files = {
        "file": (
            Path(docx_path).name,
            open(docx_path, "rb"),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    }

    data = {
        "title": title,
        "domain_category": domain,
        "problem_type": "decision_problem",
        "knowledge_type": "methodology",
        "summary": f"从Word文档 {Path(docx_path).name} 导入的知识",
    }

    try:
        response = requests.post(
            f"{BASE_URL}/expert-knowledge/import", files=files, data=data, timeout=30
        )

        files["file"][1].close()

        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ 上传成功！")
            print(f"   知识ID: {result.get('knowledge_id')}")
            print(
                f"   提取的文本长度: {result.get('file_info', {}).get('extracted_text_length', 0)}"
            )
            print(f"   提取的标签: {', '.join(result.get('extracted_tags', [])[:5])}")
            return result
        else:
            print(f"❌ 上传失败: {response.status_code}")
            print(f"   错误: {response.text[:200]}")
            return None

    except Exception as e:
        print(f"❌ 错误: {e}")
        return None


def upload_ppt_document(pptx_path, title="测试PPT文档", domain="resource_allocation"):
    """上传PPT文档"""
    print(f"\n📤 上传PPT文档: {pptx_path}")

    if not Path(pptx_path).exists():
        print(f"❌ 文件不存在: {pptx_path}")
        return None

    files = {
        "file": (
            Path(pptx_path).name,
            open(pptx_path, "rb"),
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        )
    }

    data = {
        "title": title,
        "domain_category": domain,
        "problem_type": "optimization_problem",
        "knowledge_type": "case_study",
        "summary": f"从PPT文档 {Path(pptx_path).name} 导入的知识",
    }

    try:
        response = requests.post(
            f"{BASE_URL}/expert-knowledge/import", files=files, data=data, timeout=30
        )

        files["file"][1].close()

        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ 上传成功！")
            print(f"   知识ID: {result.get('knowledge_id')}")
            print(
                f"   提取的文本长度: {result.get('file_info', {}).get('extracted_text_length', 0)}"
            )
            return result
        else:
            print(f"❌ 上传失败: {response.status_code}")
            print(f"   错误: {response.text[:200]}")
            return None

    except Exception as e:
        print(f"❌ 错误: {e}")
        return None


def search_uploaded_knowledge(keyword="测试"):
    """搜索上传的知识"""
    print(f"\n🔍 搜索知识: '{keyword}'")

    data = {"query": keyword, "limit": 10}

    try:
        response = requests.post(
            f"{BASE_URL}/expert-knowledge/search", json=data, timeout=10
        )

        if response.status_code == 200:
            results = response.json()
            if isinstance(results, list):
                count = len(results)
            else:
                count = (
                    len(results.get("results", [])) if isinstance(results, dict) else 0
                )

            print(f"✅ 找到 {count} 条知识")

            if isinstance(results, list) and results:
                print("\n前3条结果:")
                for i, knowledge in enumerate(results[:3], 1):
                    print(f"  {i}. {knowledge.get('title', '无标题')}")
                    print(f"     摘要: {knowledge.get('summary', '')[:50]}...")

            return results
        else:
            print(f"❌ 搜索失败: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ 错误: {e}")
        return None


def main():
    """主函数"""
    print("=" * 70)
    print("  文档上传实用示例")
    print("=" * 70)
    print(f"\n服务地址: {BASE_URL}")
    print("\n💡 使用方法:")
    print("  1. 准备要上传的文件（图片、Word、PPT）")
    print("  2. 调用对应的上传函数")
    print("  3. 检查上传结果")
    print("\n示例代码已在此脚本中，可以直接调用函数进行测试")

    # 示例：如果提供了文件路径，自动上传
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        file_ext = Path(file_path).suffix.lower()

        if file_ext in [".png", ".jpg", ".jpeg"]:
            upload_image_file(file_path)
        elif file_ext == ".docx":
            upload_word_document(file_path)
        elif file_ext == ".pptx":
            upload_ppt_document(file_path)
        else:
            print(f"❌ 不支持的文件格式: {file_ext}")
    else:
        print("\n📖 函数说明:")
        print("  - upload_image_file(image_path, title, domain)")
        print("  - upload_word_document(docx_path, title, domain)")
        print("  - upload_ppt_document(pptx_path, title, domain)")
        print("  - search_uploaded_knowledge(keyword)")
        print("\n💡 命令行使用:")
        print(f"  python {sys.argv[0]} <文件路径>")
        print("\n💡 或在Python中导入使用:")
        print(f"  from {Path(__file__).stem} import upload_image_file")
        print("  upload_image_file('test.png', '测试标题')")


if __name__ == "__main__":
    main()
