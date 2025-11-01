# Windows Tesseract-OCR 快速安装指南

## 📥 下载与安装（5分钟）

### 步骤1：下载安装包

**方式A：直接下载（推荐）**
- 访问: https://digi.bib.uni-mannheim.de/tesseract/
- 下载最新版本，例如: `tesseract-ocr-w64-setup-5.x.x.exe` (64位系统)

**方式B：GitHub Releases**
- 访问: https://github.com/UB-Mannheim/tesseract/wiki
- 点击 "Latest Release"
- 下载 `tesseract-ocr-w64-setup-v*.exe`

### 步骤2：运行安装程序

1. 双击下载的 `.exe` 文件
2. 安装向导界面：
   - 点击 "Next"
   - 选择安装路径（**记住这个路径**，默认: `C:\Program Files\Tesseract-OCR`）
   - 选择组件：
     - ✅ **Additional language data (download)** （重要：勾选此选项）
     - 在语言列表中勾选：
       - ✅ **English** (默认已选)
       - ✅ **Chinese (Simplified)** - 简体中文
       - ✅ **Chinese (Traditional)** - 繁体中文（可选）
   - 点击 "Install"
   - 等待安装完成（可能需要几分钟下载语言包）
   - 点击 "Finish"

### 步骤3：配置环境变量（重要）

#### 方法1：图形界面（最简单）

1. 按 `Win + R`，输入 `sysdm.cpl`，按回车
2. 点击 "**高级**" 选项卡
3. 点击 "**环境变量**" 按钮
4. 在 "**系统变量**" 区域：
   - 找到 `Path` 变量
   - 点击 "**编辑**"
   - 点击 "**新建**"
   - 输入：`C:\Program Files\Tesseract-OCR` （或你的实际安装路径）
   - 点击 "**确定**" 保存所有更改

#### 方法2：PowerShell（管理员权限）

以**管理员身份**打开 PowerShell，运行：

```powershell
# 添加到系统PATH（请根据实际安装路径修改）
$tesseractPath = "C:\Program Files\Tesseract-OCR"
$currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
[Environment]::SetEnvironmentVariable("Path", "$currentPath;$tesseractPath", "Machine")

# 刷新当前会话
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
```

### 步骤4：验证安装

**⚠️ 重要：关闭所有已打开的 PowerShell/CMD 窗口，重新打开一个新的**

在新的 PowerShell 窗口中运行：

```powershell
# 检查版本
tesseract --version

# 检查可用语言（应该包含 eng 和 chi_sim）
tesseract --list-langs
```

**预期输出**:
```
tesseract 5.x.x
...

List of available languages (3):
eng
chi_sim
chi_tra
```

### 步骤5：测试 Python 集成

```powershell
# 切换到项目目录
cd D:\BaiduSyncdisk\QBM\qbm-ai-system\backend

# 测试 pytesseract 是否能找到 Tesseract
python -c "import pytesseract; print('Tesseract版本:', pytesseract.get_tesseract_version())"
```

如果显示版本号，说明安装成功！

## 🔧 如果遇到问题

### 问题1：`tesseract is not installed or it's not in your PATH`

**解决方案**：
1. 确认安装路径正确
2. 确认已添加到系统 PATH
3. **关闭并重新打开**所有命令行窗口
4. 如果还不行，尝试重启电脑

### 问题2：找不到中文语言

**解决方案**：
1. 重新运行安装程序
2. 勾选 "Additional language data"
3. 勾选中文语言包
4. 或者手动下载：
   - 访问: https://github.com/tesseract-ocr/tessdata
   - 下载 `chi_sim.traineddata`
   - 复制到: `C:\Program Files\Tesseract-OCR\tessdata\`

### 问题3：Python仍然找不到tesseract

**临时解决方案**（在代码中指定路径）：

在 `src/services/expert_knowledge/document_processing_service.py` 中添加：

```python
import pytesseract
import os

# Windows 下指定路径
if os.name == 'nt':  # Windows
    default_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    if os.path.exists(default_path):
        pytesseract.pytesseract.tesseract_cmd = default_path
```

## ✅ 安装完成检查清单

- [ ] Tesseract-OCR 安装包已下载
- [ ] 安装程序已成功运行
- [ ] 已勾选安装中文语言包
- [ ] 已添加到系统 PATH 环境变量
- [ ] `tesseract --version` 可以运行
- [ ] `tesseract --list-langs` 显示 `chi_sim`
- [ ] Python 可以找到 tesseract
- [ ] 测试脚本显示 OCR 功能可用

## 🧪 运行测试验证

```powershell
cd D:\BaiduSyncdisk\QBM\qbm-ai-system\backend
python scripts/test_expert_knowledge_dependencies.py
```

如果看到：
```
✅ pytesseract: 图片OCR可用（需要Tesseract-OCR引擎）
```

说明安装成功！

## 📚 更多信息

- 详细安装指南: `docs/INSTALL_TESSERACT_WINDOWS.md`
- 官方文档: https://tesseract-ocr.github.io/
- Windows安装包: https://github.com/UB-Mannheim/tesseract/wiki

---

**安装完成后，专家知识库系统即可完整使用图片OCR功能！** 🎉

