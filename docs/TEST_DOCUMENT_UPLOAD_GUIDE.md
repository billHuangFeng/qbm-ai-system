# 文档上传功能测试指南

## 📝 测试文档上传功能

本文档介绍如何测试专家知识库系统的文档上传功能，包括Word文档、PPT文档和图片的OCR识别。

---

## 🚀 快速开始

### 方法1：使用API文档界面（推荐）

1. **打开API文档**
   - 访问: http://localhost:8081/docs
   - 找到 `POST /expert-knowledge/import` 端点

2. **测试上传**
   - 点击 "Try it out"
   - 填写表单字段
   - 选择文件（.docx, .pptx, .png, .jpg等）
   - 点击 "Execute"

### 方法2：使用curl命令

```bash
# 上传图片（OCR识别）
curl -X POST http://localhost:8081/expert-knowledge/import \
  -F "file=@test_image.png" \
  -F "title=测试图片" \
  -F "domain_category=cost_optimization" \
  -F "problem_type=optimization_problem" \
  -F "knowledge_type=tool_template" \
  -F "summary=这是一个测试图片"

# 上传Word文档
curl -X POST http://localhost:8081/expert-knowledge/import \
  -F "file=@document.docx" \
  -F "title=测试Word文档" \
  -F "domain_category=business_model" \
  -F "problem_type=decision_problem" \
  -F "knowledge_type=methodology" \
  -F "summary=文档摘要"

# 上传PPT文档
curl -X POST http://localhost:8081/expert-knowledge/import \
  -F "file=@presentation.pptx" \
  -F "title=测试PPT文档" \
  -F "domain_category=resource_allocation" \
  -F "problem_type=optimization_problem" \
  -F "knowledge_type=case_study" \
  -F "summary=演示文稿摘要"
```

### 方法3：使用Python脚本

```python
import requests

# 准备文件和数据
files = {
    'file': ('test_image.png', open('test_image.png', 'rb'), 'image/png')
}

data = {
    'title': '测试图片',
    'domain_category': 'cost_optimization',
    'problem_type': 'optimization_problem',
    'knowledge_type': 'tool_template',
    'summary': '这是一个测试图片'
}

# 上传文件
response = requests.post(
    'http://localhost:8081/expert-knowledge/import',
    files=files,
    data=data
)

# 检查结果
if response.status_code in [200, 201]:
    result = response.json()
    print(f"成功！知识ID: {result.get('id')}")
    print(f"提取的文本: {result.get('content', '')[:200]}")
else:
    print(f"失败: {response.status_code}")
    print(response.text)
```

---

## 📋 支持的文档格式

### 1. Word文档 (.docx)

**功能**:
- ✅ 自动提取文本内容
- ✅ 解析段落结构
- ✅ 提取表格数据
- ✅ 提取标题和列表

**测试方法**:
1. 创建一个简单的Word文档
2. 添加一些文字、段落、标题
3. 保存为 .docx 格式
4. 通过API上传

**示例Word文档内容**:
```
# 成本优化方法论

## 概述
成本优化是企业持续改进的重要方向。

## 核心原则
1. 识别成本驱动因素
2. 优化资源配置
3. 提高运营效率

## 实践案例
在实际项目中，我们通过以下方式优化成本...
```

### 2. PPT文档 (.pptx)

**功能**:
- ✅ 自动提取幻灯片文本
- ✅ 提取标题和内容
- ✅ 提取备注
- ✅ 提取图片说明

**测试方法**:
1. 创建一个PowerPoint演示文稿
2. 添加几页幻灯片，包含文字内容
3. 保存为 .pptx 格式
4. 通过API上传

**示例PPT内容**:
- 幻灯片1: 标题 - "商业模式优化"
- 幻灯片2: 内容 - "成本结构分析"
- 幻灯片3: 内容 - "优化方案"

### 3. 图片文件 (.png, .jpg, .jpeg)

**功能**:
- ✅ OCR文字识别（支持中英文）
- ✅ 提取文字位置信息
- ✅ 计算识别置信度
- ✅ 支持多语言识别

**测试方法**:

**方法A: 使用测试脚本自动生成**
```bash
cd backend
python scripts/test_document_upload.py
```

**方法B: 手动创建测试图片**
1. 创建一个包含文字的图片
2. 确保文字清晰可见
3. 保存为 .png 或 .jpg 格式
4. 通过API上传

**方法C: 使用真实图片**
- 扫描文档图片
- 截图包含文字
- 任何包含文字的图片文件

---

## 🧪 测试脚本

### 运行测试脚本

```bash
cd backend
python scripts/test_document_upload.py
```

**测试脚本功能**:
1. ✅ 自动创建测试图片
2. ✅ 测试图片上传和OCR识别
3. ✅ 验证Word/PPT文档处理功能
4. ✅ 检查服务状态
5. ✅ 提供API文档链接

---

## 📊 测试示例

### 示例1: 上传图片并OCR识别

```python
import requests
from PIL import Image, ImageDraw, ImageFont

# 创建测试图片
img = Image.new('RGB', (800, 200), color='white')
draw = ImageDraw.Draw(img)
draw.text((50, 70), "测试OCR文字识别", fill='black')
img.save('test_image.png')

# 上传图片
files = {'file': ('test_image.png', open('test_image.png', 'rb'), 'image/png')}
data = {
    'title': 'OCR测试图片',
    'domain_category': 'cost_optimization',
    'problem_type': 'optimization_problem',
    'knowledge_type': 'tool_template'
}

response = requests.post(
    'http://localhost:8081/expert-knowledge/import',
    files=files,
    data=data
)

print(response.json())
```

### 示例2: 上传Word文档

```python
import requests

files = {
    'file': ('document.docx', open('document.docx', 'rb'), 
             'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
}

data = {
    'title': '成本优化方法论',
    'domain_category': 'cost_optimization',
    'problem_type': 'optimization_problem',
    'knowledge_type': 'methodology',
    'summary': '成本优化的核心方法论',
    'author': '作者名称',
    'publication_date': '2025-01-01'
}

response = requests.post(
    'http://localhost:8081/expert-knowledge/import',
    files=files,
    data=data
)

result = response.json()
print(f"知识ID: {result.get('id')}")
print(f"提取的文本长度: {len(result.get('content', ''))}")
```

### 示例3: 上传PPT文档

```python
import requests

files = {
    'file': ('presentation.pptx', open('presentation.pptx', 'rb'),
             'application/vnd.openxmlformats-officedocument.presentationml.presentation')
}

data = {
    'title': '商业模式分析演示',
    'domain_category': 'business_model',
    'problem_type': 'decision_problem',
    'knowledge_type': 'case_study',
    'summary': '商业模式分析案例'
}

response = requests.post(
    'http://localhost:8081/expert-knowledge/import',
    files=files,
    data=data
)

result = response.json()
print(f"提取的文本: {result.get('content', '')[:500]}")
```

---

## ✅ 验证上传结果

### 检查上传的知识

```bash
# 搜索上传的知识
curl -X POST http://localhost:8081/expert-knowledge/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "测试",
    "domain_category": "cost_optimization",
    "limit": 10
  }'

# 获取知识详情（使用返回的ID）
curl http://localhost:8081/expert-knowledge/{knowledge_id}
```

### 验证OCR识别结果

```python
import requests

# 获取知识详情
response = requests.get(f'http://localhost:8081/expert-knowledge/{knowledge_id}')
knowledge = response.json()

# 检查OCR结果
content = knowledge.get('content', '')
print(f"提取的文本长度: {len(content)}")
print(f"提取的文本预览: {content[:200]}")

# 如果有OCR元数据
if 'ocr_metadata' in knowledge:
    metadata = knowledge['ocr_metadata']
    print(f"平均置信度: {metadata.get('average_confidence')}%")
    print(f"识别单词数: {metadata.get('word_count')}")
```

---

## 🔍 常见问题

### 问题1: 上传失败（400错误）

**可能原因**:
- 文件格式不支持
- 文件太大
- 必填字段缺失

**解决方案**:
- 检查文件格式（.docx, .pptx, .png, .jpg）
- 检查文件大小（建议 < 10MB）
- 确保填写所有必填字段（title, domain_category, problem_type）

### 问题2: OCR识别结果为空

**可能原因**:
- 图片文字不清晰
- 字体太小
- 图片质量问题

**解决方案**:
- 使用清晰、大字的图片
- 确保文字与背景对比度高
- 使用高质量图片（分辨率 > 300 DPI）

### 问题3: Word/PPT文档提取失败

**可能原因**:
- 文档格式损坏
- 文档受密码保护
- python-docx/python-pptx未安装

**解决方案**:
- 检查文档是否可以正常打开
- 移除文档密码保护
- 确认已安装python-docx和python-pptx

---

## 📚 更多资源

- **API文档**: http://localhost:8081/docs
- **测试脚本**: `backend/scripts/test_document_upload.py`
- **功能测试报告**: `docs/EXPERT_KNOWLEDGE_TEST_REPORT.md`
- **API测试报告**: `docs/EXPERT_KNOWLEDGE_API_TEST_REPORT.md`

---

## 🎯 测试清单

- [ ] 服务正常运行（http://localhost:8081）
- [ ] API文档可访问（http://localhost:8081/docs）
- [ ] 准备测试文件（Word/PPT/图片）
- [ ] 测试图片上传和OCR识别
- [ ] 测试Word文档上传
- [ ] 测试PPT文档上传
- [ ] 验证提取的文本内容
- [ ] 检查知识是否正确创建
- [ ] 验证搜索功能（搜索上传的知识）

---

**测试完成！** 🎉

