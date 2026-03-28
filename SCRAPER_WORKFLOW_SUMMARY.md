# 場地爬蟲流程總覽

**生成時間**: 2026-03-24

---

## 🎯 主要爬蟲框架

### 1. **enhanced_venue_scraper.py** ⭐⭐⭐
**用途**: 通用場地爬蟲框架（主要使用）

**特點**:
- 配置驅動（configuration-driven）
- 支援多種提取器（CSS、文字模式、表格）
- 批次處理支援
- 自動化驗證

**使用方式**:
```bash
# 測試單個場地
python enhanced_venue_scraper.py --venue-id 1076

# 批次處理
python enhanced_venue_scraper.py --batch
```

**配置檔案**:
- `venue_scraper_config.json` - 基本配置（52 場地）
- `venue_scraper_config_expanded.json` - 進階配置範例

---

### 2. **universal_venue_scraper.py**
**用途**: 萬取版通用爬蟲

**特點**:
- 更簡化的配置
- 快速處理
- 適合批量驗證

---

## 🏨 飯店專用爬蟲

### 3. **hotel_scraper.py**
**用途**: 專門處理飯店場地

**特點**:
- 針對飯店官網結構優化
- 提取會議室資訊
- 提取照片和價格

---

## 🔧 單一功能爬蟲

### 4. **scraper_with_images.py**
**用途**: 專門提取照片

**特點**:
- 下載會議室照片
- 驗證照片 URL
- 儲存照片資訊

### 5. **precise_scraper.py**
**用途**: 精確資料提取

**特點**:
- 高精度提取
- 驗證資料完整性
- 錯誤處理

---

## 🤖 自動化爬蟲

### 6. **auto_scraper.py**
**用途**: 全自動爬蟲

**特點**:
- 自動發現資料
- 自動提取
- 無需配置

### 7. **smart_scraper.py**
**用途**: 智能爬蟲

**特點**:
- AI 輔助識別
- 自動修正錯誤
- 學習優化

---

## 📦 批次處理工具

### 8. **batch_verify_5hotels.py** ⭐⭐⭐
**用途**: 批次驗證 5 家飯店

**功能**:
- 抓取官網
- 提取聯絡資訊（電話、Email）
- 按樓層分組顯示會議室
- 計算資料品質分數
- 生成驗證報告

**使用方式**:
```bash
python batch_verify_5hotels.py
```

### 9. **batch2_verify_hotels.py**
**用途**: 批次 2 驗證腳本

### 10. **batch3_select_10hotels.py**
**用途**: 批次 3 驗證腳本（10 家飯店）

---

## 🔄 資料更新工具

### 11. **update_xxx.py 系列腳本**
**用途**: 更新特定飯店資料

主要腳本:
- `update_grand_hotel_from_pdf.py` - 圓山大飯店 PDF 提取
- `update_victoria_from_pdf.py` - 維多麗亞酒店 PDF 提取
- `fix_lemeridien_floor_formats.py` - 寒舍艾美樓層修正
- `update_batch2_extracted.py` - 批次 2 資料更新
- `update_batch2_corrections.py` - 批次 2 修正

---

## 📊 資料驗證工具

### 12. **verify_lemeridien_floors.py**
**用途**: 驗證樓層資料

### 13. **quickstart.py**
**用途**: 快速入門指南

---

## 🛠️ 技術堆疊

### 核心工具
- **Scrapling** - 現代化爬蟲框架
  - Fetcher - HTTP 請求
  - StealthyFetcher - 反爬蟲
  - DynamicFetcher - JavaScript 渲染
  - AsyncFetcher - 並發處理

### 輔助工具
- **PyPDF2** - PDF 解析
- **requests** - HTTP 請求
- **BeautifulSoup4** - HTML 解析（間接使用）
- **json** - 資料處理

---

## 🎯 推薦工作流程

### 流程 1：單一飯店完整處理
```bash
# 1. 批次驗證
python batch_verify_5hotels.py

# 2. 下載並解析官方 PDF（如果有）
# 手動下載 PDF → 使用 PyPDF2 提取

# 3. 更新資料
python update_[hotel_name]_from_pdf.py

# 4. 樓層格式標準化
python fix_lemeridien_floor_formats.py

# 5. 生成檢查報告
python batch2_detailed_report.py
```

### 流程 2：批量處理多間飯店
```bash
# 1. 選擇飯店並執行批次驗證
python batch3_select_10hotels.py

# 2. 檢查報告
python [batch_report_script].py

# 3. 人工檢查後修正
python update_[batch]_corrections.py
```

### 流程 3：使用通用框架（新場地）
```bash
# 1. 生成配置
python universal_venue_scraper.py --generate-config

# 2. 編輯配置（如需要）
# 編輯 venue_scraper_config.json

# 3. 執行爬蟲
python enhanced_venue_scraper.py --batch
```

---

## 📈 效能比較

| 工具 | 速度 | 準確度 | 易用性 | 推薦度 |
|------|------|--------|--------|--------|
| enhanced_venue_scraper.py | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| batch_verify_5hotels.py | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| universal_venue_scraper.py | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| hotel_scraper.py | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |

---

## 🎓 最佳實踐

### 1. 批次驗證流程（推薦）
```bash
# 批次驗證 5-10 家飯店
python batch_verify_5hotels.py
```

**優點**:
- ✅ 快速驗證官網
- ✅ 提取聯絡資訊
- ✅ 計算資料品質
- ✅ 生成完整報告

### 2. PDF 資料提取
```bash
# 手動下載 PDF → 提取資料
python -c "
import PyPDF2
with open('file.pdf', 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    text = reader.pages[0].extract_text()
    print(text)
"
```

### 3. 樓層格式標準化
```bash
# 統一為 XF 格式（2F, 3F, 5F, B1, B2）
python fix_lemeridien_floor_formats.py
```

---

## 🚀 快速開始

### 查看快速入門
```bash
python quickstart.py
```

### 查看完整說明
```bash
# 查看 README
cat README_SCRAPER.md
```

---

## 📝 總結

**主要使用**:
1. **batch_verify_5hotels.py** - 批次驗證（最常用）
2. **update_xxx.py** - 資料更新
3. **enhanced_venue_scraper.py** - 通用框架

**技術**:
- Scrapling（主要）
- PyPDF2（PDF 解析）
- requests（HTTP）
- json（資料處理）

**流程**:
批次驗證 → PDF 提取 → 資料更新 → 人工檢查 → 修正
