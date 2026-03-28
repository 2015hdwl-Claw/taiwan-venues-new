# 活動大師爬蟲與檢視完整流程

**建立日期**: 2026-03-26
**專案**: 活動大師 Activity Master
**目的**: 完整記錄爬蟲、資料庫、驗證的整個流程

---

## 📊 系統架構概覽

```
┌─────────────────────────────────────────────────────────────┐
│                    活動大師系統架構                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐      ┌────────────┐│
│  │  資料來源     │─────▶│  爬蟲系統     │─────▶│  資料庫    ││
│  │  (官方網站)   │      │  (Scrapers)   │      │ (venues.json)│
│  └──────────────┘      └──────────────┘      └────────────┘│
│                                 │                   │      │
│                                 ▼                   ▼      │
│                          ┌──────────────┐      ┌────────────┐│
│                          │  驗證系統     │◀─────│  檢視工具  ││
│                          │  (Verifiers) │      │ (Checkers) ││
│                          └──────────────┘      └────────────┘│
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗄️ 資料庫

### 主要資料庫檔案

**檔案位置**: `venues.json`

**資料結構**:
```json
{
  "id": 1128,                    // 場地唯一 ID
  "name": "集思台大會議中心",      // 場地名稱
  "venueType": "會議中心",        // 場地類型
  "url": "https://...",          // 官網 URL
  "verified": true,               // 是否已驗證

  // 基本資訊
  "address": "台北市羅斯福路四段85號B1",
  "city": "台北市",
  "phone": "+886-2-3366-4504",
  "email": "ntu.service@meeting.com.tw",

  // 容量資訊
  "maxCapacityTheater": 400,
  "maxCapacityClassroom": 150,

  // 會議室資料
  "rooms": [
    {
      "id": "1128-國際會議廳",
      "name": "國際會議廳",
      "nameEn": "International Conference Hall",
      "capacity": {"theater": 400, "classroom": 400},
      "area": 253.6,
      "areaUnit": "坪",
      "floor": "3樓",
      "price": {"weekday": 44000, "holiday": 48000},
      "source": "gis_official_pdf"
    }
  ],

  // 交通資訊
  "transportation": {
    "mrt": "公館站",
    "bus": ["1", "207", "643"],
    "parking": "倍思地下停車場"
  },

  // 聯絡人
  "contactPerson": "...",
  "contactPhone": "...",
  "contactEmail": "...",

  // 價格資訊
  "priceHalfDay": 22000,
  "priceFullDay": 44000,

  // 設備資訊
  "equipment": "...",

  // 照片
  "images": {
    "cover": "...",
    "gallery": ["...", "..."]
  },

  // 爬蟲元數據
  "scraped_at": "2026-03-25T10:30:00",
  "scrape_version": "V4_PDF",
  "success": true,

  // 資料清理元數據
  "cleanedAt": "2026-03-25T11:00:00",
  "cleanVersion": "v1.0",

  // 最後更新
  "lastUpdated": "2026-03-25T11:00:00",

  // 詳細元數據
  "metadata": {
    "lastScrapedAt": "2026-03-25T10:30:00",
    "scrapeVersion": "V4_PDF",
    "scrapeConfidenceScore": 85,
    "totalRooms": 12,
    "source": "official_pdf"
  }
}
```

### 資料庫統計 (2026-03-26)

```
總場地數: 45
有會議室資料: 43 (95.6%)
總會議室數: 399

場地類型分佈:
  - 會議中心: 23 個
  - 婚宴場地: 11 個
  - 飯店場地: 10 個
  - 運動場地: 4 個
  - 展演場地: 3 個
  - 其他: 3 個
```

### 備份檔案

**備份命名規則**:
```
venues.json.backup.{描述}_{時間戳}
例如: venues.json.backup.removed_hotels_20260325_225621
```

**備份類型**:
1. **自動備份**: 爬蟲更新前自動建立
2. **手動備份**: 重要操作前手動建立
3. **移除備份**: 下架場地前建立

---

## 🔧 爬蟲系統

### 爬蟲版本與用途

| 版本 | 檔案名稱 | 用途 | 速度 | 完整度 | 推薦場景 |
|------|----------|------|------|--------|----------|
| **V2** | `deep_scraper_v2.py` | 完整六階段爬蟲 | 🐢 慢 | 🟢 最完整 | 重要場地、需要完整資料 |
| **V4** | `full_site_scraper_v4.py` | 全站爬蟲 | 🐢 慢 | 🟢 完整 | 一般場地、深度爬取 |
| **Parallel** | `parallel_venue_scraper.py` | 並行快速爬蟲 | ⚡ 快 | 🟡 基本 | 快速更新大量場地 |
| **WordPress** | `scraper_wordpress_ticc.py` | WordPress 專用 | ⚡ 快 | 🟢 針對性 | WordPress 網站 |

### 爬蟲選擇決策樹

```
需要爬取新場地？
│
├─ 是 → 場地很重要？
│        │
│        ├─ 是 → 使用 deep_scraper_v2.py (完整六階段)
│        │         - 首頁 → 會議室 → 價格 → 規則 → 交通 → 平面圖
│        │         - 支援指定 URL
│        │         - 處理會議室細分
│        │
│        └─ 否 → 使用 full_site_scraper_v4.py (全站爬蟲)
│                  - 自動發現頁面
│                  - 包含 PDF 處理
│
└─ 否 → 更新現有資料？
          │
          ├─ 是 → 場地數量？
          │        │
          │        ├─ 少量 (<5) → 使用 deep_scraper_v2.py
          │        │
          │        └─ 大量 (>5) → 使用 parallel_venue_scraper.py
          │
          └─ 否 → 使用檢視工具驗證資料
```

### 爬蟲執行流程

#### 完整爬蟲流程 (deep_scraper_v2.py)

```
[1/6] 爬取首頁
  ├─ 檢測網頁技術類型
  ├─ 提取基本資訊
  └─ 發現所有連結

[2/6] 爬取會議室頁面
  ├─ 尋找會議室列表
  ├─ 爬取每個會議室詳情
  └─ 處理會議室細分 (101→101A, 101B...)

[3/6] 爬取價格頁面
  ├─ 提取價格資訊
  ├─ 半日/全日價格
  └─ 平日/假日價格

[4/6] 爬取場地規則頁面
  ├─ 使用規則
  ├─ 付款方式
  └─ 取消政策

[5/6] 爬取交通資訊頁面
  ├─ 捷運資訊
  ├─ 公車路線
  └─ 停車資訊

[6/6] 爬取平面圖頁面
  └─ 提取平面圖資訊

└─ 更新 venues.json
```

### 爬蟲使用範例

```bash
# 完整爬取單一場地
python deep_scraper_v2.py --url https://example.com --batch

# 批次爬取多個場地
python deep_scraper_v2.py --batch --sample 5

# 全站爬蟲
python full_site_scraper_v4.py --batch --sample 3

# 並行快速爬蟲
python parallel_venue_scraper.py --batch --sample 10
```

---

## ✅ 驗證系統

### 驗證工具

| 工具名稱 | 檔案 | 用途 |
|----------|------|------|
| **資料品質檢查** | `check_data_quality.py` | 檢查資料完整性、格式正確性 |
| **場地詳情檢視** | `check_venue_details.py` | 檢視單一場地完整資料 |
| **進度檢查** | `check_progress.py` | 檢查爬蟲進度 |
| **狀態檢查** | `check_status.py` | 檢查場地爬取狀態 |
| **資料庫狀態** | `check_db_status.py` | 檢查資料庫整體狀態 |

### 驗證流程

```
1. 資料完整性檢查
   ├─ 必需欄位檢查 (id, name, rooms, capacity, area)
   ├─ 資料類型檢查
   └─ 格式驗證 (電話、Email)

2. 資料準確性檢查
   ├─ 容量合理性 (5-5000人)
   ├─ 面積合理性 (>0坪)
   └─ 價格合理性 (>0元)

3. 資料一致性檢查
   ├─ 會議室數量一致
   ├─ 最大容量一致
   └─ 資料來源標記

4. 生成報告
   └─ 統計與問題清單
```

### 驗證使用範例

```bash
# 檢查資料品質
python check_data_quality.py

# 檢視特定場地
python check_venue_details.py --id 1128

# 檢查資料庫狀態
python check_db_status.py

# 檢查爬蟲進度
python check_progress.py
```

---

## 🔄 完整工作流程

### 新場地處理流程

```
1. 發現場地
   └─ 收集官網 URL

2. 技術檢測
   └─ 檢測網頁類型 (Static/JS/WordPress)

3. 選擇爬蟲
   ├─ 重要場地 → deep_scraper_v2.py
   └─ 一般場地 → full_site_scraper_v4.py

4. 執行爬蟲
   ├─ 單一場地: python deep_scraper_v2.py --url <URL>
   └─ 批次處理: python deep_scraper_v2.py --batch --sample 5

5. 資料驗證
   ├─ python check_data_quality.py
   └─ python check_venue_details.py --id <ID>

6. 資料清理
   └─ 格式統一、欄位補充

7. 更新資料庫
   └─ 自動備份 → 更新 venues.json

8. 生成報告
   └─ 記錄處理結果
```

### PDF 資料處理流程

```
1. 發現 PDF
   └─ 從官網找到 PDF 連結

2. 下載 PDF
   └─ python download_pdf.py <URL>

3. 提取文字
   └─ 使用 PyPDF2 提取文字內容

4. 查看格式
   └─ 打開 .txt 檔案查看實際格式

5. 設計解析器
   ├─ 自動解析 (正則表達式)
   └─ 手動提取 (複雜格式)

6. 驗證資料
   └─ 對照 PDF 檢查準確性

7. 更新資料庫
   └─ 更新 venues.json
```

### 資料更新流程

```
1. 檢查待更新場地
   └─ 檢查 metadata.lastScrapedAt

2. 批次處理
   ├─ python parallel_venue_scraper.py --batch --sample 10
   └─ 自動跳過 7 天內已更新的場地

3. 驗證更新
   └─ python check_data_quality.py

4. 生成報告
   └─ 統計更新結果
```

---

## 📁 檔案組織

### 主要檔案分類

```
taiwan-venues-new/
├── 資料庫
│   ├── venues.json                      # 主資料庫
│   ├── venues.json.backup.*             # 備份檔案
│   └── removed_*.json                   # 下架場地記錄
│
├── 爬蟲系統
│   ├── deep_scraper_v2.py               # 完整六階段爬蟲
│   ├── full_site_scraper_v4.py          # 全站爬蟲
│   ├── parallel_venue_scraper.py        # 並行快速爬蟲
│   └── scraper_wordpress_ticc.py        # WordPress 專用
│
├── 驗證工具
│   ├── check_data_quality.py            # 資料品質檢查
│   ├── check_venue_details.py           # 場地詳情檢視
│   ├── check_progress.py                # 進度檢查
│   └── check_db_status.py               # 資料庫狀態
│
├── 更新工具
│   ├── batch_update_priority.py         # 批次優先更新
│   └── update_*.py                      # 各種更新腳本
│
├── PDF 處理
│   ├── download_gis_pdfs.py             # PDF 下載
│   ├── parse_*.py                       # PDF 解析
│   └── *_text.txt                       # 提取的文字
│
├── 文檔
│   ├── CLAUDE.md                        # 專案配置
│   ├── KNOWLEDGE_BASE.md                # 知識庫
│   ├── PDF_SCRAPING_SOP.md              # PDF 爬蟲 SOP
│   └── *_REPORT.md                      # 各種報告
│
└── 記憶體系統
    └── memory/
        ├── MEMORY.md                    # 記憶體索引
        ├── venue_scraping_process_lessons.md
        └── pdf_parsing_lessons.md
```

---

## 🎯 使用場景

### 場景 1: 新增場地

```bash
# 1. 檢測網頁技術
python detect_web_tech.py --url https://example.com

# 2. 執行爬蟲
python deep_scraper_v2.py --url https://example.com --batch

# 3. 驗證資料
python check_venue_details.py --id <NEW_ID>

# 4. 檢查資料品質
python check_data_quality.py
```

### 場景 2: 批次更新

```bash
# 1. 檢查待更新場地
python check_progress.py

# 2. 執行批次更新
python parallel_venue_scraper.py --batch --sample 10

# 3. 驗證更新結果
python check_db_status.py
```

### 場景 3: PDF 資料處理

```bash
# 1. 下載 PDF
python download_gis_pdfs.py

# 2. 提取文字
python extract_pdf_text.py <PDF_FILE>

# 3. 查看格式 (手動打開 .txt 檔案)

# 4. 解析資料
python parse_pdf_data.py <TXT_FILE>

# 5. 更新資料庫
python update_venues.py

# 6. 驗證
python verify_update.py
```

### 場景 4: 問題排查

```bash
# 1. 檢查特定場地
python check_venue_details.py --id <PROBLEM_ID>

# 2. 檢查資料品質
python check_data_quality.py

# 3. 查看爬蟲記錄
cat logs/scraper_*.log

# 4. 參考知識庫
# 查看 KNOWLEDGE_BASE.md 尋找類似問題
```

---

## 📊 資料流向

```
┌─────────────────────────────────────────────────────────────┐
│                        資料流向                              │
└─────────────────────────────────────────────────────────────┘

[來源]                [處理]              [儲存]
  │                    │                   │
  ▼                    ▼                   ▼
官網 ─────────────▶ 爬蟲系統 ───────────▶ venues.json
PDF                  驗證工具            備份檔案
手動輸入            資料清理              報告文檔

                      │
                      ▼
                 [品質檢查]
                      │
                      ▼
                 [問題回報]
                      │
                      ▼
                 [修正更新]
```

---

## 🔍 監控與維護

### 定期檢查項目

**每日**:
- [ ] 檢查爬蟲執行狀態
- [ ] 查看錯誤日誌
- [ ] 驗證新增資料

**每週**:
- [ ] 檢查資料品質
- [ ] 更新過期資料
- [ ] 清理備份檔案

**每月**:
- [ ] 批次更新所有場地
- [ ] 檢查官網連線
- [ ] 統計資料完整度

**每季**:
- [ ] 檢查無法連線的場地
- [ ] 更新知識庫
- [ ] 優化爬蟲效率

### 常見問題處理

**問題 1: 爬蟲失敗**
```bash
# 檢查網站是否可連線
curl -I https://example.com

# 檢查爬蟲日誌
tail -f logs/scraper.log

# 參考知識庫
# KNOWLEDGE_BASE.md → 問題 5: TICC 404 錯誤
```

**問題 2: 資料不完整**
```bash
# 檢查資料品質
python check_data_quality.py

# 使用完整爬蟲重新爬取
python deep_scraper_v2.py --url <URL> --batch

# 檢查是否有 PDF
# 參考 PDF_SCRAPING_SOP.md
```

**問題 3: 資料格式錯誤**
```bash
# 檢查特定場地
python check_venue_details.py --id <ID>

# 手動修正
python update_specific_venues.py --id <ID>
```

---

## 📚 相關文檔

### 核心文檔

| 文檔 | 說明 |
|------|------|
| [CLAUDE.md](CLAUDE.md) | 專案配置與使用說明 |
| [KNOWLEDGE_BASE.md](KNOWLEDGE_BASE.md) | 問題與解決方案知識庫 |
| [PDF_SCRAPING_SOP.md](PDF_SCRAPING_SOP.md) | PDF 爬蟲標準作業程序 |

### 記憶體系統

| 檔案 | 內容 |
|------|------|
| [memory/MEMORY.md](memory/MEMORY.md) | 記憶體索引 |
| [memory/venue_scraping_process_lessons.md](memory/venue_scraping_process_lessons.md) | 爬蟲流程教訓 |
| [memory/pdf_parsing_lessons.md](memory/pdf_parsing_lessons.md) | PDF 解析教訓 |

### 報告文檔

- 各種 *_REPORT.md 檔案記錄了處理過程與結果

---

## 🎓 最佳實踐

### 爬蟲使用

1. **選擇正確的爬蟲**
   - 重要場地 → deep_scraper_v2.py
   - 一般場地 → full_site_scraper_v4.py
   - 快速更新 → parallel_venue_scraper.py

2. **批次處理**
   - 每次處理 3-5 個場地 (完整爬蟲)
   - 每次處理 10-20 個場地 (快速爬蟲)

3. **備份習慣**
   - 更新前自動備份
   - 重要操作手動備份

### 資料驗證

1. **爬取後立即驗證**
   - 檢查資料完整性
   - 查看資料準確性

2. **定期品質檢查**
   - 每週執行 check_data_quality.py
   - 每月檢查所有場地

3. **問題記錄**
   - 記錄到 KNOWLEDGE_BASE.md
   - 更新記憶體系統

### PDF 處理

1. **遵循 SOP**
   - 按照 PDF_SCRAPING_SOP.md 執行
   - 不要跳過驗證步驟

2. **保存文字檔案**
   - 必須保存 .txt 檔案
   - 用於後續分析

3. **手動驗證**
   - 對照 PDF 檢查資料
   - 確保準確性

---

## 📞 技術支援

### 遇到問題時

1. **查看知識庫**
   - KNOWLEDGE_BASE.md
   - memory/ 目錄

2. **檢查日誌**
   - logs/ 目錄
   - 爬蟲輸出

3. **使用檢查工具**
   - check_*.py 系列工具
   - 診斷問題原因

---

**文檔版本**: v1.0
**最後更新**: 2026-03-26
**維護者**: le202
**專案**: 活動大師 Activity Master
