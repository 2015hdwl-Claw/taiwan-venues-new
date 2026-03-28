# 活動大師系統架構重設

**設計日期**: 2026-03-26
**設計原則**: 職責分離、資料追蹤、可重複執行

---

## 🏗️ 新架構設計

### 系統架構圖

```
┌─────────────────────────────────────────────────────────────────┐
│                     活動大師系統架構 v2.0                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐      ┌──────────────────┐               │
│  │ 來源資料庫        │─────▶│ 爬蟲系統         │               │
│  │ (sources.json)   │      │ (Scrapers)       │               │
│  │                  │      │                  │               │
│  │ - 地區           │      │ - HTML 爬蟲      │               │
│  │ - 場地類別       │      │ - PDF 解析       │               │
│  │ - 場地名稱       │      │ - 自動發現       │               │
│  │ - 官網網址       │      │                  │               │
│  │ - 網頁技術       │      │                  │               │
│  │ - 優先級         │      │                  │               │
│  │ - 狀態           │      │                  │               │
│  └──────────────────┘      └──────────────────┘               │
│                                  │                              │
│                                  ▼                              │
│                      ┌──────────────────┐                      │
│                      │ 初步資料庫      │                      │
│                      │ (raw.json)      │                      │
│                      │                  │                      │
│                      │ - 原始爬取資料   │                      │
│                      │ - 未經驗證       │                      │
│                      │ - 包含錯誤       │                      │
│                      │ - 元數據         │                      │
│                      └──────────────────┘                      │
│                                  │                              │
│                                  ▼                              │
│                      ┌──────────────────┐                      │
│                      │ 檢視工具         │                      │
│                      │ (Viewers)        │                      │
│                      │                  │                      │
│                      │ - check_raw.py   │                      │
│                      │ - check_quality.py│                     │
│                      │ - verify.py      │                      │
│                      └──────────────────┘                      │
│                                  │                              │
│                                  ▼                              │
│                      ┌──────────────────┐                      │
│                      │ 驗證資料庫      │                      │
│                      │ (verified.json)  │                      │
│                      │                  │                      │
│                      │ - 通過驗證       │                      │
│                      │ - 品質評分       │                      │
│                      │ - 來源標記       │                      │
│                      │ - 驗證記錄       │                      │
│                      └──────────────────┘                      │
│                                  │                              │
│                                  ▼                              │
│                      ┌──────────────────┐                      │
│                      │ 完成資料庫      │                      │
│                      │ (venues.json)    │                      │
│                      │                  │                      │
│                      │ - 最終資料       │                      │
│                      │ - 可發布使用     │                      │
│                      │ - 高品質保證     │                      │
│                      └──────────────────┘                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 資料庫設計

### 1. 來源資料庫 (sources.json)

**用途**: 場地來源清單，爬蟲系統的輸入

**結構**:
```json
{
  "version": "1.0",
  "lastUpdated": "2026-03-26T00:00:00",
  "regions": [
    {
      "id": "TW-TPE",
      "name": "台北市",
      "nameEn": "Taipei City",
      "country": "台灣",
      "countryCode": "TW"
    },
    {
      "id": "TW-TNN",
      "name": "台南市",
      "nameEn": "Tainan City",
      "country": "台灣",
      "countryCode": "TW"
    }
  ],
  "venueTypes": [
    {
      "id": "conference_center",
      "name": "會議中心",
      "nameEn": "Conference Center",
      "priority": 1
    },
    {
      "id": "hotel",
      "name": "飯店場地",
      "nameEn": "Hotel Venue",
      "priority": 2
    },
    {
      "id": "wedding",
      "name": "婚宴場地",
      "nameEn": "Wedding Venue",
      "priority": 3
    },
    {
      "id": "exhibition",
      "name": "展演場地",
      "nameEn": "Exhibition Venue",
      "priority": 4
    },
    {
      "id": "sports",
      "name": "運動場地",
      "nameEn": "Sports Venue",
      "priority": 5
    }
  ],
  "sources": [
    {
      "id": 1001,
      "name": "集思台大會議中心",
      "nameEn": "NTUCC",
      "regionId": "TW-TPE",
      "venueTypeId": "conference_center",
      "url": "https://www.meeting.com.tw/ntu/",
      "webTech": "wordpress",
      "priority": 1,
      "status": "active",
      "notes": "重要場地，需要完整爬取",
      "lastChecked": "2026-03-25T10:30:00",
      "lastScraped": "2026-03-25T10:30:00",
      "scrapeVersion": "V4_PDF",
      "scrapeResult": "success"
    },
    {
      "id": 1002,
      "name": "台北國際會議中心",
      "nameEn": "TICC",
      "regionId": "TW-TPE",
      "venueTypeId": "conference_center",
      "url": "https://www.ticc.com.tw/",
      "webTech": "wordpress",
      "priority": 1,
      "status": "active",
      "notes": "WordPress 網站，需要專用爬蟲",
      "lastChecked": "2026-03-26T00:00:00",
      "lastScraped": null,
      "scrapeResult": null
    }
  ],
  "webTechTypes": [
    {
      "id": "static",
      "name": "Static HTML",
      "recommendedScraper": "requests + BeautifulSoup"
    },
    {
      "id": "wordpress",
      "name": "WordPress",
      "recommendedScraper": "scraper_wordpress_ticc.py"
    },
    {
      "id": "javascript",
      "name": "JavaScript Heavy",
      "recommendedScraper": "Playwright/Selenium"
    },
    {
      "id": "react",
      "name": "React SPA",
      "recommendedScraper": "Playwright"
    },
    {
      "id": "unknown",
      "name": "Unknown",
      "recommendedScraper": "deep_scraper_v2.py (auto-detect)"
    }
  ]
}
```

**欄位說明**:
- `id`: 唯一識別碼
- `regionId`: 地區 ID (對應 regions)
- `venueTypeId`: 場地類型 ID (對應 venueTypes)
- `webTech`: 網頁技術類型
- `priority`: 優先級 (1=最高, 5=最低)
- `status`: 狀態 (active, inactive, removed)
- `lastChecked`: 最後檢查時間
- `lastScraped`: 最後爬取時間
- `scrapeVersion`: 爬蟲版本
- `scrapeResult`: 爬取結果

### 2. 初步資料庫 (raw.json)

**用途**: 爬蟲原始輸出，未經驗證

**結構**:
```json
{
  "version": "1.0",
  "generatedAt": "2026-03-26T10:30:00",
  "generator": "deep_scraper_v2.py",
  "sources": {
    "sourceId": 1001,
    "sourceUrl": "https://www.meeting.com.tw/ntu/"
  },
  "data": [
    {
      "sourceId": 1001,
      "scrapedAt": "2026-03-26T10:30:00",
      "scraper": "deep_scraper_v2.py",
      "success": true,
      "data": {
        "name": "集思台大會議中心",
        "url": "https://www.meeting.com.tw/ntu/",
        "address": "台北市羅斯福路四段85號B1",
        "phone": "+886-2-3366-4504",
        "email": "ntu.service@meeting.com.tw",
        "rooms": [
          {
            "name": "國際會議廳",
            "capacity": 400,
            "area": 253.6,
            "source": "html"
          }
        ],
        "transportation": {},
        "images": [],
        "raw": {
          "html": "...",
          "pages": ["..."]
        }
      },
      "errors": [],
      "warnings": ["部分頁面無法存取"]
    }
  ],
  "summary": {
    "total": 1,
    "success": 1,
    "failed": 0,
    "withWarnings": 1
  }
}
```

### 3. 驗證資料庫 (verified.json)

**用途**: 通過驗證的資料

**結構**:
```json
{
  "version": "1.0",
  "verifiedAt": "2026-03-26T11:00:00",
  "verifier": "check_data_quality.py",
  "data": [
    {
      "id": 1128,
      "sourceId": 1001,
      "name": "集思台大會議中心",
      "qualityScore": 85,
      "completeness": {
        "basicInfo": true,
        "rooms": true,
        "capacity": true,
        "area": true,
        "price": true,
        "transportation": true,
        "images": false
      },
      "verification": {
        "passed": true,
        "checks": [
          "has_required_fields",
          "capacity_valid",
          "area_valid",
          "phone_valid",
          "email_valid"
        ],
        "issues": [],
        "warnings": ["missing_images"]
      },
      "data": {
        "name": "集思台大會議中心",
        "rooms": [...]
      }
    }
  ],
  "summary": {
    "total": 1,
    "passed": 1,
    "failed": 0,
    "averageQuality": 85
  }
}
```

### 4. 完成資料庫 (venues.json)

**用途**: 最終發布的資料

**結構**: 維持現有結構，新增 metadata 標記

```json
{
  "id": 1128,
  "name": "集思台大會議中心",
  "venueType": "會議中心",
  "sourceId": 1001,
  "qualityScore": 85,
  "lastVerified": "2026-03-26T11:00:00",
  "metadata": {
    "source": "sources.json",
    "sourceId": 1001,
    "scrapedAt": "2026-03-26T10:30:00",
    "scrapeVersion": "V4_PDF",
    "verifiedAt": "2026-03-26T11:00:00",
    "qualityScore": 85,
    "dataFlow": "sources → raw → verified → venues"
  }
}
```

---

## 🔄 資料流程

### 完整流程

``<arg_value>[來源資料庫]
    │
    │ sources.json
    │ (45 個來源)
    │
    ▼
[爬蟲系統]
    │
    ├─ 讀取 sources.json
    ├─ 過濾條件
    │   ├─ status == 'active'
    │   ├─ priority <= 3
    │   └─ 需要更新 (lastScraped > 7天)
    │
    ├─ 執行爬取
    │   ├─ 根據 webTech 選擇爬蟲
    │   ├─ 執行爬取
    │   └─ 處理 PDF
    │
    ▼
[初步資料庫]
    │
    │ raw.json
    │ (原始資料)
    │
    ▼
[檢視工具]
    │
    ├─ check_raw.py
    │   └─ 查看原始資料
    │
    ├─ check_quality.py
    │   └─ 品質檢查
    │
    └─ verify.py
        └─ 驗證資料
    │
    ▼
[驗證資料庫]
    │
    │ verified.json
    │ (驗證通過)
    │
    ▼
[最終整理]
    │
    ├─ 資料合併
    ├─ 去重
    └─ 格式統一
    │
    ▼
[完成資料庫]
    │
    │ venues.json
    │ (最終資料)
    │
    └─ 備份
```

---

## 🔧 系統工具架構

### 目錄結構

```
taiwan-venues-new/
├── 資料庫/
│   ├── sources.json           # 來源資料庫 ⭐ 新增
│   ├── raw.json              # 初步資料庫 ⭐ 新增
│   ├── verified.json         # 驗證資料庫 ⭐ 新增
│   └── venues.json           # 完成資料庫 (現有)
│
├── 爬蟲系統/
│   ├── scrapers/
│   │   ├── deep_scraper_v2.py
│   │   ├── full_site_scraper_v4.py
│   │   ├── parallel_venue_scraper.py
│   │   └── scraper_wordpress_ticc.py
│   │
│   └── pdf_parsers/
│       ├── pdf_downloader.py
│       ├── pdf_extractor.py
│       └── pdf_parser.py
│
├── 驗證工具/
│   ├── viewers/
│   │   ├── view_raw.py          # 查看原始資料
│   │   ├── view_verified.py     # 查看驗證資料
│   │   └── view_venues.py       # 查看完成資料
│   │
│   ├── checkers/
│   │   ├── check_quality.py     # 品質檢查
│   │   ├── check_completeness.py # 完整性檢查
│   │   └── check_accuracy.py    # 準確性檢查
│   │
│   └── verifiers/
│       ├── verify_basic.py      # 基本驗證
│       ├── verify_data.py       # 資料驗證
│       └── verify_format.py     # 格式驗證
│
├── 轉換工具/
│   ├── raw_to_verified.py       # raw → verified
│   ├── verified_to_venues.py    # verified → venues
│   └── rebuild_venues.py        # 重建 venues
│
├── 工具/
│   ├── source_manager.py        # 來源管理 ⭐ 新增
│   ├── web_tech_detector.py     # 技術檢測 ⭐ 新增
│   └── batch_processor.py       # 批次處理
│
├── 文檔/
│   ├── ARCHITECTURE.md           # 架構文檔 ⭐ 新增
│   ├── COMPLETE_WORKFLOW_GUIDE.md
│   ├── QUICK_REFERENCE_GUIDE.md
│   └── ...
│
└── 記憶體/
    └── memory/
```

---

## 🎯 使用流程

### 1. 管理來源資料

```bash
# 新增來源
python source_manager.py add --url https://example.com --name "場地名稱"

# 檢測網頁技術
python web_tech_detector.py --url https://example.com

# 更新來源狀態
python source_manager.py update --id 1001 --status "active"

# 列出來源
python source_manager.py list --priority 1

# 匯出來源
python source_manager.py export --format csv
```

### 2. 執行爬蟲

```bash
# 從來源資料庫爬取
python batch_processor.py --from sources --priority 1

# 爬取並保存到 raw.json
python batch_processor.py --output raw

# 爬取特定來源
python batch_processor.py --source-ids 1001,1002,1003
```

### 3. 驗證資料

```bash
# 查看原始資料
python viewers/view_raw.py --id 1001

# 品質檢查
python checkers/check_quality.py --input raw

# 驗證資料
python verifiers/verify_data.py --input raw --output verified

# 生成報告
python checkers/check_quality.py --report quality_report.md
```

### 4. 更新完成資料

```bash
# 從驗證資料更新
python converters/verified_to_venues.py

# 重建完成資料庫
python converters/rebuild_venues.py --from verified

# 查看差異
python converters/verified_to_venues.py --diff
```

---

## 📊 狀態追蹤

### 來源狀態

| 狀態 | 說明 | 處理方式 |
|------|------|----------|
| `active` | 活躍，定期更新 | 正常爬取 |
| `inactive` | 暫時不活躍 | 跳過爬取 |
| `removed` | 已下架 | 不處理 |
| `pending` | 待檢查 | 檢測後決定 |

### 爬取結果

| 結果 | 說明 | 處理方式 |
|------|------|----------|
| `success` | 成功 | 進入驗證 |
| `failed` | 失敗 | 記錄錯誤 |
| `partial` | 部分成功 | 標記警告 |
| `pending` | 待處理 | 重新排程 |

---

## 🎓 優勢

### 舊架構 vs 新架構

**舊架構**:
```
官網 → 爬蟲 → venues.json
```
- ❌ 來源管理混在爬蟲中
- ❌ 無法追蹤來源狀態
- ❌ 無法區分資料品質
- ❌ 難以重複執行

**新架構**:
```
來源資料庫 → 爬蟲 → 初步資料庫 → 驗證 → 驗證資料庫 → 完成資料庫
```
- ✅ 來源集中管理
- ✅ 狀態完整追蹤
- ✅ 品質分級管理
- ✅ 可重複執行任何階段
- ✅ 容易擴展到全球

---

## 🚀 實施計劃

### 階段 1: 建立來源資料庫

- [ ] 創建 sources.json 結構
- [ ] 匯入現有 45 個場地
- [ ] 建立地區分類
- [ ] 建立場地類型分類
- [ ] 實作 source_manager.py

### 階段 2: 重構爬蟲系統

- [ ] 修改爬蟲讀取 sources.json
- [ ] 實作 raw.json 輸出
- [ ] 實作批次處理器
- [ ] 實作網頁技術檢測

### 階段 3: 建立驗證系統

- [ ] 實作品質檢查工具
- [ ] 實作驗證工具
- [ ] 建立 verified.json
- [ ] 實作轉換工具

### 階段 4: 更新文檔

- [ ] 更新架構文檔
- [ ] 更新使用指南
- [ ] 更新 API 文檔

---

**設計完成**: 2026-03-26
**設計者**: le202
**狀態**: ⭐ 待實施
