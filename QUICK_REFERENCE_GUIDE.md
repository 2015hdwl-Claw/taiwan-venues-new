# 活動大師 - 快速參考指南

**更新日期**: 2026-03-26

---

## 🚀 快速開始

### 最常用的指令

```bash
# 檢查資料庫狀態
python check_db_status.py

# 檢視特定場地
python check_venue_details.py --id 1128

# 批次爬取場地 (快速)
python parallel_venue_scraper.py --batch --sample 10

# 完整爬取單一場地
python deep_scraper_v2.py --url https://example.com --batch

# 檢查資料品質
python check_data_quality.py
```

---

## 📊 資料庫概覽

### venues.json 結構

```
45 個場地
├─ 43 個有會議室資料 (95.6%)
└─ 2 個待處理

399 個會議室總計

場地類型:
  會議中心: 23 個
  婚宴場地: 11 個
  飯店場地: 10 個
  運動場地: 4 個
  展演場地: 3 個
```

### 資料欄位說明

**必備欄位**:
- `id`: 場地唯一識別碼
- `name`: 場地名稱
- `venueType`: 場地類型
- `url`: 官網連結
- `rooms`: 會議室列表

**重要欄位**:
- `address`: 地址
- `phone`: 電話
- `email`: Email
- `capacity`: 最大容量
- `transportation`: 交通資訊

**元數據**:
- `metadata.lastScrapedAt`: 最後爬取時間
- `metadata.scrapeVersion`: 爬蟲版本
- `metadata.source`: 資料來源

---

## 🔧 工具選擇指南

### 我想要...

| 需求 | 使用工具 | 指令 |
|------|----------|------|
| 爬取新場地 (完整) | deep_scraper_v2.py | `python deep_scraper_v2.py --url <URL> --batch` |
| 爬取新場地 (快速) | full_site_scraper_v4.py | `python full_site_scraper_v4.py --batch --sample 3` |
| 批次更新多個場地 | parallel_venue_scraper.py | `python parallel_venue_scraper.py --batch --sample 10` |
| 檢視場地詳情 | check_venue_details.py | `python check_venue_details.py --id <ID>` |
| 檢查資料品質 | check_data_quality.py | `python check_data_quality.py` |
| 處理 PDF 資料 | 見 PDF_SCRAPING_SOP.md | - |
| 更新特定場地 | update_specific_venues.py | `python update_specific_venues.py --id <ID>` |

---

## 📋 工作流程清單

### 新增場地

- [ ] 1. 收集官網 URL
- [ ] 2. 檢測網頁技術類型
- [ ] 3. 執行爬蟲
- [ ] 4. 驗證資料完整性
- [ ] 5. 修正問題
- [ ] 6. 更新資料庫

### 批次更新

- [ ] 1. 檢查待更新場地
- [ ] 2. 執行批次爬蟲
- [ ] 3. 驗證更新結果
- [ ] 4. 生成報告

### PDF 處理

- [ ] 1. 下載 PDF
- [ ] 2. 提取文字
- [ ] 3. 查看格式
- [ ] 4. 設計解析器
- [ ] 5. 提取資料
- [ ] 6. 驗證準確性
- [ ] 7. 更新資料庫

---

## 🎯 爬蟲選擇決策樹

```
需要處理場地？
│
├─ 新場地
│   │
│   ├─ 重要場地 (需要完整資料)
│   │   └─▶ deep_scraper_v2.py
│   │       - 六階段完整爬取
│   │       - 會議室細分處理
│   │       - 支援指定 URL
│   │
│   └─ 一般場地
│       └─▶ full_site_scraper_v4.py
│           - 全站自動爬取
│           - PDF 處理
│           - 多頁面發現
│
└─ 現有場地更新
    │
    ├─ 少量場地 (<5)
    │   └─▶ deep_scraper_v2.py --batch --sample 5
    │
    └─ 大量場地 (>5)
        └─▶ parallel_venue_scraper.py --batch --sample 10
            - 並行處理
            - 快速更新
            - 自動跳過已更新
```

---

## 📁 檔案快速查找

### 我想找到...

| 需求 | 檔案 |
|------|------|
| 主資料庫 | `venues.json` |
| 最新備份 | `venues.json.backup.*` (最新時間戳) |
| 完整爬蟲 | `deep_scraper_v2.py` |
| 快速爬蟲 | `parallel_venue_scraper.py` |
| 檢查工具 | `check_*.py` |
| 知識庫 | `KNOWLEDGE_BASE.md` |
| PDF SOP | `PDF_SCRAPING_SOP.md` |
| 專案配置 | `CLAUDE.md` |
| 問題排查 | `KNOWLEDGE_BASE.md` → 相關問題 |

---

## ⚠️ 常見問題快速解決

### 問題: 爬蟲失敗

**症狀**: HTTP 404, 連線失敗

**解決**:
1. 檢查網站是否可連線: `curl -I <URL>`
2. 檢測網頁技術類型
3. 選擇正確的爬蟲
4. 參考: `KNOWLEDGE_BASE.md` → 問題 5

### 問題: 資料不完整

**症狀**: 會議室資料缺失

**解決**:
1. 檢查是否有 PDF: `PDF_SCRAPING_SOP.md`
2. 使用完整爬蟲: `deep_scraper_v2.py`
3. 手動更新: `update_specific_venues.py`

### 問題: 批次處理重複

**症狀**: 每次都爬取相同場地

**解決**:
1. 檢查 `metadata.lastScrapedAt`
2. 確認爬蟲版本正確
3. 參考: `KNOWLEDGE_BASE.md` → 問題 2

### 問題: PDF 解析失敗

**症狀**: 無法提取 PDF 資料

**解決**:
1. 遵循六步驟流程: `PDF_SCRAPING_SOP.md`
2. 查看提取的文字檔案
3. 設計專用解析器或手動提取

---

## 🔍 資料檢查清單

### 爬取後檢查

- [ ] 資料完整性 (必備欄位都有)
- [ ] 資料準確性 (容量、面積合理)
- [ ] 資料一致性 (無衝突)
- [ ] 資料來源標記

### 更新前檢查

- [ ] 已建立備份
- [ ] 確認更新範圍
- [ ] 測試影響評估

### 更新後檢查

- [ ] 驗證更新結果
- [ ] 檢查資料品質
- [ ] 生成報告

---

## 📞 尋求協助

### 查看資訊

1. **知識庫**: `KNOWLEDGE_BASE.md`
2. **記憶體**: `memory/` 目錄
3. **SOP**: `PDF_SCRAPING_SOP.md`
4. **完整文檔**: `COMPLETE_WORKFLOW_GUIDE.md`

### 常用指令

```bash
# 查看場地詳情
python check_venue_details.py --id <ID>

# 檢查資料品質
python check_data_quality.py

# 查看資料庫狀態
python check_db_status.py

# 查看爬蟲進度
python check_progress.py
```

---

## 📊 狀態速查

### 資料庫狀態

```bash
python check_db_status.py
```

輸出:
```
Total venues: 45
Venues with rooms: 43 (95.6%)
Total rooms: 399
```

### 待處理場地

```bash
python check_progress.py
```

顯示需要爬取或更新的場地

### 特定場地

```bash
python check_venue_details.py --id 1128
```

顯示完整場地資訊

---

**快速參考版本**: v1.0
**完整文檔**: COMPLETE_WORKFLOW_GUIDE.md
**最後更新**: 2026-03-26
