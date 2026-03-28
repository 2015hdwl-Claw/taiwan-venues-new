# 當前系統架構與流程（整合版）

**日期**: 2026-03-26
**目的**: 整合說明現有系統，不新增工具

---

## 📊 系統架構

```
┌─────────────────────────────────────────────────────────────┐
│                    活動大師系統架構                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐      ┌────────────┐│
│  │  資料來源     │─────▶│  爬蟲系統     │─────▶│  資料庫    ││
│  │  (官網/PDF)   │      │  (4個爬蟲)   │      │(venues.json)│
│  └──────────────┘      └──────────────┘      └────────────┘│
│                                 │                   │      │
│                                 ▼                   ▼      │
│                          ┌──────────────┐      ┌────────────┐│
│                          │  驗證系統     │◀─────│  檢視工具  ││
│                          │  (5個工具)   │      │ (check_*.py)│
│                          └──────────────┘      └────────────┘│
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗄️ 資料庫

### 單一資料庫
- **檔案**: `venues.json`
- **場地數**: 45 個
- **會議室數**: 399 個
- **備份**: `venues.json.backup.{timestamp}`

### 資料結構
```json
{
  "id": 1128,
  "name": "集思台大會議中心",
  "venueType": "會議中心",
  "url": "https://...",
  "rooms": [
    {
      "id": "1128-01",
      "name": "國際會議廳",
      "capacity": {"theater": 400},
      "area": 253.6,
      "areaUnit": "坪",
      "price": {"weekday": 44000, "holiday": 48000}
    }
  ],
  "metadata": {
    "lastScrapedAt": "2026-03-25T10:30:00",
    "scrapeVersion": "V4_PDF",
    "scrapeConfidenceScore": 85,
    "totalRooms": 12
  }
}
```

---

## 🔧 爬蟲系統（4個核心爬蟲）

### 1. deep_scraper_v2.py - 完整六階段爬蟲

**用途**: 重要場地，需要完整資料

**六階段流程**:
```
[1/6] 爬取首頁 → 發現所有連結
[2/6] 爬取會議室頁面 → 深入爬取詳細資料
[3/6] 爬取價格頁面 → 提取價格資訊
[4/6] 爬取場地規則頁面 → 提取所有規則
[5/6] 爬取交通資訊頁面 → 提取交通資訊
[6/6] 爬取平面圖頁面 → 提取平面圖資訊
```

**使用方式**:
```bash
# 單一場地
python deep_scraper_v2.py --url https://example.com --batch

# 批次處理
python deep_scraper_v2.py --batch --sample 5
```

**特色**:
- ✅ 支援指定 URL 優先處理
- ✅ 處理會議室細分（101→101A, 101B...）
- ✅ 提取完整欄位（accessInfo, rules, floorPlan）

### 2. full_site_scraper_v4.py - 全站爬蟲

**用途**: 一般場地，深度爬取

**功能**:
- 自動發現頁面（導航、Footer、URL模式）
- 頁面分類（會議/交通/規則/照片）
- PDF 處理

**使用方式**:
```bash
# 批次處理
python full_site_scraper_v4.py --batch --sample 3
```

**特色**:
- ✅ 使用 Scrapling + BeautifulSoup
- ✅ 包含 PDF 下載與解析
- ✅ 適合大多數場地

### 3. parallel_venue_scraper.py - 並行快速爬蟲

**用途**: 快速更新大量場地

**功能**:
- 並行處理（8個線程）
- 自動跳過7天內已更新的場地
- 快速更新基本資料

**使用方式**:
```bash
# 批次處理
python parallel_venue_scraper.py
```

**特色**:
- ✅ 速度快（並行處理）
- ✅ 自動檢查更新時間
- ✅ 適合大量場地更新

### 4. scraper_wordpress_ticc.py - WordPress專用

**用途**: WordPress網站

**使用方式**:
```bash
python scraper_wordpress_ticc.py
```

---

## ✅ 驗證系統（5個驗證工具）

### 1. check_data_quality.py - 資料品質檢查

**功能**:
- 檢查資料完整性
- 檢查格式正確性
- 生成品質報告

**使用方式**:
```bash
python check_data_quality.py
```

### 2. check_venue_details.py - 場地詳情檢視

**功能**:
- 檢視單一場地完整資料
- 顯示所有會議室
- 檢查欄位完整性

**使用方式**:
```bash
python check_venue_details.py --id 1128
```

### 3. check_progress.py - 進度檢查

**功能**:
- 檢查爬蟲進度
- 統計已完成/未完成場地

**使用方式**:
```bash
python check_progress.py
```

### 4. check_db_status.py - 資料庫狀態

**功能**:
- 檢查資料庫整體狀態
- 統計場地數量、會議室數量

**使用方式**:
```bash
python check_db_status.py
```

### 5. data_validator.py - 資料驗證器

**功能**:
- 驗證電話格式（台灣）
- 驗證Email格式
- 驗證容量範圍（5-5000人）
- 驗證面積範圍（1-10000坪）

**特色**（Phase 2已修正）:
- ✅ 支援新舊欄位（contact.phone + contactPhone）
- ✅ 支援多種電話格式
- ✅ Email垃圾過濾

---

## 🔄 標準工作流程

### 流程圖

```
開始
  │
  ▼
┌─────────────────┐
│  1. 技術檢測     │ （可選，遇到問題時）
│  detect_web_tech │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2. 選擇爬蟲     │
│  ┌───────────┐  │
│  │重要場地？  │  │
│  └─┬──────┬─┘  │
│    │是    │否  │
│    ▼      ▼    │
│  V2爬蟲  V4爬蟲 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  3. 執行爬取     │
│  自動備份        │
│  更新 venues.json│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  4. 資料驗證     │
│  check_data_quality│
│  check_venue_details│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  5. PDF處理     │ （如有PDF）
│  下載→提取→解析  │
└────────┬────────┘
         │
         ▼
      完成
```

### 場景1: 新增重要場地

```bash
# 1. 技術檢測（如果需要）
python detect_web_tech.py --url https://example.com

# 2. 執行完整爬蟲
python deep_scraper_v2.py --url https://example.com --batch

# 3. 驗證資料
python check_venue_details.py --id <NEW_ID>
python check_data_quality.py
```

### 場景2: 批次更新場地

```bash
# 1. 檢查待更新場地
python check_progress.py

# 2. 執行批次更新
python parallel_venue_scraper.py

# 3. 驗證更新
python check_db_status.py
```

### 場景3: PDF資料處理

```bash
# 1. 下載PDF（手動或爬蟲自動）
# 2. 提取文字
python extract_pdf_text.py <PDF_FILE>
# 3. 查看格式（手動打開.txt）
# 4. 解析資料
python parse_pdf_data.py <TXT_FILE>
# 5. 更新資料庫
python update_venues.py
# 6. 驗證
python verify_update.py
```

---

## 🛑 停止新增工具

### 不需要的工具（已刪除或歸檔）

❌ **已歸檔的工具**:
- phase3_quality_booster.py（不需要）
- phase3_hotel_banquet_booster.py（不需要）
- complete_room_extractor.py（已有類似功能）
- 其他19個舊版本爬蟲

### 使用現有工具即可

✅ **爬蟲**: 4個核心爬蟲已足夠
✅ **驗證**: 5個驗證工具已足夠
✅ **資料庫**: 單一 venues.json 已足夠

---

## 📋 核心原則

### 1. 不重複造輪子

- ✅ 使用現有的 4 個爬蟲
- ✅ 使用現有的 5 個驗證工具
- ❌ 不創造新工具

### 2. 遵循標準流程

- ✅ 技術檢測 → 選擇爬蟲 → 執行爬取 → 驗證
- ✅ PDF處理遵循六步驟
- ✅ 記錄到知識庫

### 3. 參考知識庫

- ✅ KNOWLEDGE_BASE.md - 問題與解決方案
- ✅ COMPLETE_WORKFLOW_GUIDE.md - 完整工作流程
- ✅ CLAUDE.md - 專案配置

---

## 📚 參考文檔

| 文檔 | 用途 |
|------|------|
| [KNOWLEDGE_BASE.md](KNOWLEDGE_BASE.md) | 問題與解決方案知識庫 |
| [COMPLETE_WORKFLOW_GUIDE.md](COMPLETE_WORKFLOW_GUIDE.md) | 完整工作流程 |
| [CLAUDE.md](CLAUDE.md) | 專案配置 |
| [memory/MEMORY.md](memory/MEMORY.md) | 記憶體索引 |

---

## 🎯 快速查詢

### 我需要... → 使用...

| 需求 | 工具 |
|------|------|
| 爬取重要場地 | `deep_scraper_v2.py` |
| 爬取一般場地 | `full_site_scraper_v4.py` |
| 快速更新大量場地 | `parallel_venue_scraper.py` |
| 檢查資料品質 | `check_data_quality.py` |
| 檢視單一場地 | `check_venue_details.py` |
| 檢查資料庫狀態 | `check_db_status.py` |
| 處理PDF | 參考 KNOWLEDGE_BASE.md 問題4 |

---

**最後更新**: 2026-03-26
**維護者**: le202
**原則**: 整合現有工具，不新增
