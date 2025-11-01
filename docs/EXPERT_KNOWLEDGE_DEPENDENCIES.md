# 专家知识库系统依赖说明

## 核心依赖 ✅

以下依赖是系统运行必需的，已在 `requirements.txt` 中：

- ✅ `python-multipart` - FastAPI文件上传支持
- ✅ `fastapi` - Web框架
- ✅ `pydantic` - 数据验证
- ✅ `sqlalchemy` - ORM
- ✅ `pandas` - 数据处理
- ✅ `numpy` - 数值计算

## 可选依赖状态

### 1. python-docx ✅ 已安装

**用途**: Word文档（.docx）文本提取和结构化处理

**状态**: ✅ 已安装并可用

**功能**:
- 提取Word文档中的文本内容
- 解析文档结构（标题、段落、列表、表格）
- 提取元数据（作者、创建时间等）

**使用示例**:
```python
from docx import Document

doc = Document("example.docx")
for paragraph in doc.paragraphs:
    print(paragraph.text)
```

### 2. python-pptx ✅ 已安装

**用途**: PowerPoint文档（.pptx）文本提取

**状态**: ✅ 已安装并可用

**功能**:
- 提取PPT中的幻灯片文本
- 提取标题、内容、备注
- 提取图片说明（如果有）

**使用示例**:
```python
from pptx import Presentation

prs = Presentation("example.pptx")
for slide in prs.slides:
    for shape in slide.shapes:
        if hasattr(shape, "text"):
            print(shape.text)
```

### 3. pytesseract ⚠️ 已安装，但需要系统级依赖

**用途**: 图片OCR（光学字符识别）

**状态**: ⚠️ Python包已安装，但需要安装 **Tesseract-OCR 引擎**

**系统依赖**: 
- Windows: 需要从 [GitHub Releases](https://github.com/UB-Mannheim/tesseract/wiki) 下载并安装 Tesseract-OCR
- Linux: `sudo apt-get install tesseract-ocr` (Ubuntu/Debian) 或 `sudo yum install tesseract` (CentOS/RHEL)
- macOS: `brew install tesseract`

**功能**:
- 识别图片中的文字（支持中英文）
- 处理扫描文档
- 提取图片中的文字内容

**安装Tesseract-OCR后使用示例**:
```python
import pytesseract
from PIL import Image

image = Image.open("example.png")
text = pytesseract.image_to_string(image, lang='chi_sim+eng')
print(text)
```

**注意**: 如果未安装Tesseract-OCR引擎，系统会自动降级，跳过OCR功能，但仍可使用其他文档处理功能。

### 4. sentence-transformers ✅ 已安装并可用

**用途**: 语义搜索（基于向量嵌入的相似度搜索）

**状态**: ✅ 已安装，模型已成功加载

**功能**:
- 将文本转换为向量嵌入
- 语义相似度搜索
- 多语言支持（包括中文）

**已加载模型**: `paraphrase-multilingual-MiniLM-L12-v2`

**使用示例**:
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
embeddings = model.encode(["文本1", "文本2"])
similarity = cosine_similarity([embeddings[0]], [embeddings[1]])
```

**模型下载**: 首次使用时，模型会自动从 Hugging Face 下载并缓存。

## 依赖测试

运行以下命令测试所有依赖：

```bash
cd backend
python scripts/test_expert_knowledge_dependencies.py
```

## 安装命令总结

### 已安装 ✅
```bash
pip install python-docx python-pptx pytesseract sentence-transformers python-multipart
```

### 系统级依赖（可选）

**Windows - Tesseract-OCR**:
1. 从 [GitHub Releases](https://github.com/UB-Mannheim/tesseract/wiki) 下载安装包
2. 安装到系统路径（通常为 `C:\Program Files\Tesseract-OCR`）
3. 确保 `tesseract.exe` 在系统 PATH 中

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim  # 中文支持
```

**macOS**:
```bash
brew install tesseract tesseract-lang  # 包含中文语言包
```

## 功能降级策略

系统设计为**优雅降级**，即使某些可选依赖不可用，核心功能仍然可用：

1. **Word文档处理**: 如果 `python-docx` 不可用 → 提示用户手动输入文本
2. **PPT文档处理**: 如果 `python-pptx` 不可用 → 提示用户手动输入文本
3. **图片OCR**: 如果 `pytesseract` 或 Tesseract-OCR 不可用 → 跳过OCR，提示用户手动输入文本
4. **语义搜索**: 如果 `sentence-transformers` 不可用 → 降级为关键词搜索（PostgreSQL全文搜索）

## 当前系统状态

✅ **python-docx**: 已安装并可用  
✅ **python-pptx**: 已安装并可用  
⚠️ **pytesseract**: 已安装，但需要安装Tesseract-OCR引擎  
✅ **sentence-transformers**: 已安装，模型已成功加载  

**系统功能**: 专家知识库系统可以完整运行，包括：
- Word/PPT文档自动提取 ✅
- 语义搜索 ✅
- 图片OCR ⚠️ (需要Tesseract-OCR)

## 下一步

如果需要完整的OCR功能，请安装Tesseract-OCR引擎（见上方安装说明）。


