# Windows 安装 Tesseract-OCR 引擎指南

## 安装步骤

### 方法一：使用官方安装包（推荐）

#### 1. 下载安装包

访问 Tesseract-OCR 的 Windows 安装包下载页面：

**下载链接**: https://github.com/UB-Mannheim/tesseract/wiki

**推荐版本**: 
- **最新稳定版**: 选择最新的 `tesseract-ocr-w64-setup-v*.exe`（64位系统）
- **或者**: `tesseract-ocr-w32-setup-v*.exe`（32位系统）

**直接下载链接（最新版本）**:
- 64位: https://digi.bib.uni-mannheim.de/tesseract/
  - 查找最新版本，例如: `tesseract-ocr-w64-setup-5.x.x.exe`

#### 2. 运行安装程序

1. 双击下载的 `.exe` 安装文件
2. 按照安装向导进行安装
3. **重要**: 记住安装路径（默认通常是 `C:\Program Files\Tesseract-OCR`）

#### 3. 配置环境变量

安装完成后，需要将 Tesseract-OCR 添加到系统 PATH 环境变量中：

**步骤A：查找安装路径**
- 默认路径：`C:\Program Files\Tesseract-OCR`
- 确认该路径下存在 `tesseract.exe` 文件

**步骤B：添加到系统PATH**

**方法1：通过图形界面（推荐）**

1. 按 `Win + R`，输入 `sysdm.cpl`，按回车
2. 点击"高级"选项卡
3. 点击"环境变量"按钮
4. 在"系统变量"区域，找到 `Path` 变量，点击"编辑"
5. 点击"新建"，输入 Tesseract-OCR 的安装路径：
   ```
   C:\Program Files\Tesseract-OCR
   ```
6. 点击"确定"保存所有更改
7. **重要**: 关闭并重新打开所有命令行窗口（PowerShell、CMD）使更改生效

**方法2：通过PowerShell（管理员权限）**

以管理员身份打开 PowerShell，运行：

```powershell
# 添加到系统PATH
$tesseractPath = "C:\Program Files\Tesseract-OCR"
$currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
[Environment]::SetEnvironmentVariable("Path", "$currentPath;$tesseractPath", "Machine")

# 刷新当前会话的PATH
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
```

#### 4. 安装中文语言包（可选但推荐）

**方法1：通过安装程序**
- 在安装过程中，选择安装"Additional language data (download)"
- 勾选中文简体（`chi_sim`）和中文繁体（`chi_tra`）

**方法2：手动下载语言包**
1. 访问：https://github.com/tesseract-ocr/tessdata
2. 下载 `chi_sim.traineddata`（简体中文）
3. 下载 `chi_tra.traineddata`（繁体中文）
4. 将文件复制到：`C:\Program Files\Tesseract-OCR\tessdata\`

#### 5. 验证安装

打开新的 PowerShell 或 CMD 窗口，运行：

```powershell
# 检查Tesseract版本
tesseract --version

# 检查可用语言
tesseract --list-langs
```

**预期输出**:
```
tesseract 5.x.x
 leptonica-x.x.x
  libgif x.x.x : libjpeg x.x.x : libpng x.x.x : libtiff x.x.x : zlib x.x.x : libwebp x.x.x

List of available languages (x):
eng
chi_sim  # 如果安装了中文
chi_tra  # 如果安装了繁体中文
...
```

### 方法二：使用 Chocolatey（如果已安装）

如果你已经安装了 Chocolatey 包管理器：

```powershell
# 以管理员身份运行 PowerShell
choco install tesseract
```

### 方法三：使用 Scoop（如果已安装）

如果你已经安装了 Scoop：

```powershell
scoop install tesseract
```

## 在Python中配置（如果pytesseract找不到tesseract）

如果安装后 Python 仍然找不到 Tesseract，可以在代码中指定路径：

```python
import pytesseract

# Windows 默认路径
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 或者在你的环境变量中设置
# TESSDATA_PREFIX=C:\Program Files\Tesseract-OCR\tessdata
```

或者修改 `src/services/expert_knowledge/document_processing_service.py`：

```python
import pytesseract

# 自动检测或手动指定路径
if os.name == 'nt':  # Windows
    default_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    if os.path.exists(default_path):
        pytesseract.pytesseract.tesseract_cmd = default_path
```

## 测试安装

运行我们的测试脚本验证安装：

```powershell
cd backend
python scripts/test_expert_knowledge_dependencies.py
```

或者直接测试：

```powershell
python -c "import pytesseract; from PIL import Image; print('Tesseract版本:', pytesseract.get_tesseract_version())"
```

## 常见问题

### 问题1：`tesseract is not installed or it's not in your PATH`

**解决方案**:
1. 确认 Tesseract 已正确安装
2. 确认已添加到系统 PATH
3. **重新打开**所有命令行窗口
4. 运行 `tesseract --version` 验证

### 问题2：找不到中文语言

**解决方案**:
1. 确认已下载中文语言包（`chi_sim.traineddata`）
2. 将文件放在 `tessdata` 目录下
3. 运行 `tesseract --list-langs` 确认

### 问题3：Python仍然找不到tesseract

**解决方案**:
1. 在代码中手动指定路径（见上方）
2. 或者在系统环境变量中设置 `TESSERACT_CMD`

### 问题4：安装程序无法运行

**可能原因**:
- 缺少 Visual C++ Redistributable
- 权限不足（尝试以管理员身份运行）

**解决方案**:
1. 下载并安装 [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
2. 以管理员身份运行安装程序

## 安装完成后的下一步

1. **测试OCR功能**:
   ```python
   from PIL import Image
   import pytesseract
   
   # 测试英文
   image = Image.open("test_image.png")
   text = pytesseract.image_to_string(image, lang='eng')
   print(text)
   
   # 测试中文（如果安装了中文语言包）
   text_cn = pytesseract.image_to_string(image, lang='chi_sim')
   print(text_cn)
   ```

2. **验证专家知识库系统**:
   - 启动 FastAPI 服务
   - 上传一张包含文字的图片
   - 查看是否能正确提取文本

## 快速检查清单

- [ ] Tesseract-OCR 安装包已下载
- [ ] 安装程序已运行完成
- [ ] 已添加到系统 PATH 环境变量
- [ ] 已安装中文语言包（可选）
- [ ] `tesseract --version` 命令可正常运行
- [ ] `tesseract --list-langs` 显示可用语言
- [ ] Python `pytesseract` 可以找到 Tesseract
- [ ] 测试脚本显示 OCR 功能可用

## 支持的语言

安装后默认支持英语（eng）。如果需要其他语言，需要下载对应的语言包。

**常用语言包下载**: https://github.com/tesseract-ocr/tessdata

**中文语言包**:
- `chi_sim.traineddata` - 简体中文
- `chi_tra.traineddata` - 繁体中文

## 更多资源

- **官方文档**: https://tesseract-ocr.github.io/
- **GitHub仓库**: https://github.com/tesseract-ocr/tesseract
- **Windows安装包**: https://github.com/UB-Mannheim/tesseract/wiki
- **语言包**: https://github.com/tesseract-ocr/tessdata

