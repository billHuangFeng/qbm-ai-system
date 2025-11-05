"""
测试专家知识库可选依赖是否可用
"""

import sys


def test_dependencies():
    """测试所有可选依赖"""
    results = {}

    # 1. python-docx (Word文档处理)
    try:
        from docx import Document

        results["python-docx"] = {"status": "✅ 可用", "version": "已安装"}
        print("✅ python-docx: Word文档处理可用")
    except ImportError as e:
        results["python-docx"] = {"status": "❌ 不可用", "error": str(e)}
        print(f"❌ python-docx: 不可用 - {e}")

    # 2. python-pptx (PPT文档处理)
    try:
        from pptx import Presentation

        results["python-pptx"] = {"status": "✅ 可用", "version": "已安装"}
        print("✅ python-pptx: PPT文档处理可用")
    except ImportError as e:
        results["python-pptx"] = {"status": "❌ 不可用", "error": str(e)}
        print(f"❌ python-pptx: 不可用 - {e}")

    # 3. pytesseract (图片OCR)
    try:
        import pytesseract
        import os

        # Windows 下自动检测路径
        if os.name == "nt":  # Windows
            possible_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                os.path.join(
                    os.environ.get("ProgramFiles", ""), "Tesseract-OCR", "tesseract.exe"
                ),
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break

        # 尝试检查Tesseract-OCR是否可用
        try:
            version = pytesseract.get_tesseract_version()
            results["pytesseract"] = {"status": "✅ 可用", "version": str(version)}
            print(f"✅ pytesseract: 图片OCR可用 (Tesseract版本: {version})")
        except Exception as e:
            # 尝试手动指定路径
            default_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            if os.path.exists(default_path):
                try:
                    pytesseract.pytesseract.tesseract_cmd = default_path
                    version = pytesseract.get_tesseract_version()
                    results["pytesseract"] = {
                        "status": "✅ 可用",
                        "version": str(version),
                        "note": "已自动配置路径",
                    }
                    print(
                        f"✅ pytesseract: 图片OCR可用 (已自动配置路径, 版本: {version})"
                    )
                except Exception as e2:
                    results["pytesseract"] = {
                        "status": "⚠️ 部分可用",
                        "note": f"Tesseract-OCR已安装但无法访问: {e2}",
                    }
                    print(f"⚠️ pytesseract: Tesseract-OCR已安装但无法访问 - {e2}")
            else:
                results["pytesseract"] = {
                    "status": "⚠️ 部分可用",
                    "note": f"pytesseract已安装，但Tesseract-OCR引擎不可用: {e}",
                }
                print(f"⚠️ pytesseract: 已安装，但需要Tesseract-OCR引擎 - {e}")
    except ImportError as e:
        results["pytesseract"] = {"status": "❌ 不可用", "error": str(e)}
        print(f"❌ pytesseract: 不可用 - {e}")

    # 4. sentence-transformers (语义搜索)
    try:
        from sentence_transformers import SentenceTransformer

        results["sentence-transformers"] = {"status": "✅ 可用", "version": "已安装"}
        print("✅ sentence-transformers: 语义搜索可用")

        # 尝试加载模型（这会下载模型，可能需要时间）
        try:
            model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
            results["sentence-transformers"]["model"] = "模型加载成功"
            print("  ✅ 语义搜索模型可以加载")
        except Exception as e:
            results["sentence-transformers"]["model"] = f"模型加载失败: {e}"
            print(f"  ⚠️ 语义搜索模型加载失败: {e}")
    except ImportError as e:
        results["sentence-transformers"] = {"status": "❌ 不可用", "error": str(e)}
        print(f"❌ sentence-transformers: 不可用 - {e}")

    # 5. 测试服务导入
    try:
        import sys
        from pathlib import Path

        backend_dir = Path(__file__).parent.parent
        if str(backend_dir) not in sys.path:
            sys.path.insert(0, str(backend_dir))

        from src.services.expert_knowledge import (
            DocumentProcessingService,
            KnowledgeSearchService,
        )

        results["services"] = {"status": "✅ 可用", "note": "服务可以正常导入"}
        print("\n✅ 专家知识库服务可以正常导入")
    except Exception as e:
        results["services"] = {"status": "⚠️ 部分可用", "error": str(e)}
        print(f"\n⚠️ 专家知识库服务导入失败（可能是路径问题）: {e}")

    return results


if __name__ == "__main__":
    print("=" * 60)
    print("专家知识库可选依赖测试")
    print("=" * 60)
    print()

    results = test_dependencies()

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    available = sum(1 for r in results.values() if "✅" in r.get("status", ""))
    total = len(results)

    print(f"✅ 可用: {available}/{total}")

    if available == total:
        print("\n🎉 所有可选依赖都已安装并可用！")
    else:
        print(f"\n⚠️ {total - available} 个依赖需要安装或配置")

    sys.exit(0 if available == total else 1)
