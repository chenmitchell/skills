---
name: pdf-ocr-tool
description: 使用 Ollama GLM-OCR 模型，根據內容類型（文字/表格/圖表）智能轉換 PDF 和圖片為 Markdown
metadata: {"openclaw":{"emoji":"📄","requires":{"bins":["uv","ollama","pdftoppm"],"anyBins":[],"env":[],"config":[]},"install":[{"id":"uv-env","kind":"uv","path":".","bins":["ocr_tool.py"]}]}}
---

# PDF OCR Tool - 智能 PDF 轉 Markdown 工具

使用 Ollama GLM-OCR 模型，智能識別 PDF 頁面中的文字、表格、圖表區域，並使用最適合的提示詞進行 OCR 處理，輸出結構化 Markdown 文件。

## 功能特點

- ✅ **智能內容檢測**：自動識別頁面主要內容（文字/表格/圖表）
- ✅ **混合模式**：將頁面分割成多個區域，分別處理不同類型的內容
- ✅ **多種處理模式**：支援 text、table、figure、mixed、auto 模式
- ✅ **PDF 逐頁處理**：自動將 PDF 轉為圖片後逐頁 OCR
- ✅ **圖片 OCR**：支援單一圖片的 OCR 處理
- ✅ **自訂提示詞**：可根據需求調整 OCR 提示詞
- ✅ **靈活配置**：支援自訂 Ollama 主機、端口、模型
- ✅ **uv 虛擬環境**：使用 uv 管理 Python 依賴

## 安裝

### 1. 必要條件

```bash
# 安裝 Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull glm-ocr:q8_0

# 安裝 poppler-utils（PDF 轉圖片）
sudo apt install poppler-utils  # Debian/Ubuntu
brew install poppler  # macOS

# 安裝 uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 使用 uv 安裝（推薦）

```bash
cd skills/pdf-ocr-tool
uv venv
source .venv/bin/activate
uv add requests Pillow
```

### 3. 使用 ClawHub 安裝

```bash
npx clawhub install pdf-ocr-tool
```

### 4. 手動安裝

```bash
# 複製技能目錄
git clone <repo> ~/.openclaw/workspace/skills/pdf-ocr-tool

# 建立虛擬環境並安裝依賴
cd ~/.openclaw/workspace/skills/pdf-ocr-tool
uv venv
source .venv/bin/activate
uv add requests Pillow

# 執行後安裝腳本
bash hooks/post-install.sh
```

## 使用方式

### 基本用法

```bash
# 自動檢測內容類型（推薦）
python ocr_tool.py --input document.pdf --output result.md

# 指定處理模式
python ocr_tool.py --input document.pdf --output result.md --mode text
python ocr_tool.py --input document.pdf --output result.md --mode table
python ocr_tool.py --input document.pdf --output result.md --mode figure

# 混合模式：將頁面分成多個區域處理
python ocr_tool.py --input document.pdf --output result.md --mode auto --granularity region

# 處理單一圖片
python ocr_tool.py --input image.png --output result.md --mode mixed
```

### 進階配置

```bash
# 指定 Ollama 主機和端口
python ocr_tool.py --input document.pdf --output result.md \
  --host localhost --port 11434

# 使用不同模型
python ocr_tool.py --input document.pdf --output result.md \
  --model glm-ocr:q8_0

# 自訂提示詞
python ocr_tool.py --input image.png --output result.md \
  --prompt "將此表格轉換為 Markdown 格式，保持行列對齊"

# 保存圖表區域的圖片
python ocr_tool.py --input document.pdf --output result.md --save-images
```

### 環境變數配置

```bash
# 設定預設配置
export OLLAMA_HOST="localhost"
export OLLAMA_PORT="11434"
export OCR_MODEL="glm-ocr:q8_0"

# 執行
python ocr_tool.py --input document.pdf --output result.md
```

## 處理模式說明

| 模式 | 說明 | 適用場景 |
|------|------|----------|
| `auto` | 自動檢測內容類型 | 一般使用（預設） |
| `text` | 純文字識別 | 學術論文、文章、報告 |
| `table` | 表格識別 | 數據表格、財務報表 |
| `figure` | 圖表識別 | 統計圖表、流程圖、示意圖 |
| `mixed` | 混合模式 | 包含多種元素的頁面 |

### 混合模式（Granularity）

當使用 `--granularity region` 時：
- 頁面會被垂直分割成多個區域（預設 3 個）
- 每個區域獨立進型類型檢測
- 使用對應的提示詞進行 OCR
- 最終結果按順序組合成完整的 Markdown

## 輸出格式

### PDF 輸出範例

```markdown
# PDF 轉 Markdown 結果

**總頁數**: 15
**模型**: glm-ocr:q8_0
**模式**: auto
**生成時間**: 2026-02-26T14:00:00+08:00

---

## 第 1 頁

*類型：mixed*

### 區域 1 (text)
[OCR 識別的文字內容]

### 區域 2 (table)
<table>
<tr><th>欄位 1</th><th>欄位 2</th></tr>
<tr><td>數據 1</td><td>數據 2</td></tr>
</table>

### 區域 3 (figure)
[圖表描述]

![圖表](./images/page_1_region_3.png)

---
```

### 圖片輸出範例

```markdown
# image.png 的 OCR 結果

模型：glm-ocr:q8_0
模式：table

---

[OCR 識別結果]
```

## 提示詞模板

工具內建四種提示詞模板，位於 `prompts/` 目錄：

### Text 模式 (`prompts/text.md`)
```
將此區域的文字轉換為 Markdown 格式。
- 保持段落結構和標題層級
- 正確處理列表（- 或 1.）
- 保留數學公式（使用 $ 或 $$）
- 保留引用和參考文獻格式
```

### Table 模式 (`prompts/table.md`)
```
將此區域的表格轉換為 Markdown 表格格式。
- 保持行列結構對齊
- 保留所有數據和數值
- 處理合併儲存格
- 如有多個表格，分別標註
```

### Figure 模式 (`prompts/figure.md`)
```
分析此區域的圖表或圖像：
1. 圖表類型（柱狀圖、折線圖、流程圖等）
2. 標題和坐標軸標籤
3. 數據趨勢和關鍵觀察
4. 重要數值和異常點

用 Markdown 格式描述。
```

## 在 OpenClaw 中使用

```python
import subprocess
from pathlib import Path

# 處理 PDF（自動模式）
subprocess.run([
    "python",
    "skills/pdf-ocr-tool/ocr_tool.py",
    "--input", "/path/to/document.pdf",
    "--output", "/tmp/result.md",
    "--mode", "auto"
])

# 讀取結果
with open("/tmp/result.md", "r") as f:
    markdown_content = f.read()

# 處理單一圖片（表格模式）
subprocess.run([
    "python",
    "skills/pdf-ocr-tool/ocr_tool.py",
    "--input", "/path/to/table.png",
    "--output", "/tmp/table.md",
    "--mode", "table"
])

# 混合模式處理複雜 PDF
subprocess.run([
    "python",
    "skills/pdf-ocr-tool/ocr_tool.py",
    "--input", "/path/to/mixed.pdf",
    "--output", "/tmp/mixed.md",
    "--granularity", "region",  # 分區處理
    "--save-images"  # 保存圖表圖片
])
```

## 故障排除

### 模型未安裝
```bash
ollama pull glm-ocr:q8_0
```

### 服務未運行
```bash
ollama serve
```

### 缺少 pdftoppm
```bash
sudo apt install poppler-utils  # Debian/Ubuntu
brew install poppler  # macOS
```

### OCR 結果不理想
- 嘗試不同模式：`--mode text` 或 `--mode mixed`
- 使用自訂提示詞：`--prompt "你的提示詞"`
- 檢查圖片品質（解析度、清晰度）
- 嘗試混合模式：`--granularity region`

### 依賴問題
```bash
cd skills/pdf-ocr-tool
source .venv/bin/activate
uv sync  # 重新安裝所有依賴
```

## 相關資源

- [Ollama API 文檔](https://docs.ollama.com/api/generate)
- [GLM-OCR 模型頁面](https://ollama.com/library/glm-ocr)
- [poppler-utils](https://poppler.freedesktop.org/)
- [uv 包管理器](https://github.com/astral-sh/uv)

## 版本歷史

- **v1.1.0** - 新增混合模式、分區處理、pyproject.toml
- **v1.0.0** - 初始版本，支援基礎 OCR 功能

## 開發者

此工具由 OpenClaw 社群開發和維護。
