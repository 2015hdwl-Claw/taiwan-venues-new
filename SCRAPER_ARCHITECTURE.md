# 活動大師爬蟲架構文檔

## 📊 當前狀態 (2026-03-25)

### 資料庫狀態
- **總場地數**: 50
- **活躍場地**: 43
- **已爬取**: 43 (100%)
- **總發現頁面**: 319
- **平均頁面/場地**: 7.4

### 使用版本
- **V4**: 14 個場地
- **V4-Practical**: 29 個場地

---

## 🛠️ 爬蟲程式架構

### 主要爬蟲 (2個活躍版本)

#### 1. **V4 全站爬蟲** (`full_site_scraper_v4.py`)
**用途**: �準全站爬取
**成功率**: ~70%
**使用場地**: 14個

**特點**:
- 使用 Scrapling Fetcher
- 智能頁面發現（導航、Footer、URL pattern）
- 頁面分類（meeting, access, contact, policy, gallery）
- 結構化資料提取

**流程**:
```
1. 讀取 venues.json
2. 選擇場地ID
3. 發現頁面:
   - 抓取首頁
   - 解析導航列 (<nav>)
   - 解析 Footer (<footer>)
   - URL 模式猜測
4. 分類頁面
5. 提取資料:
   - 基本資訊（電話、Email）
   - 會議室資訊
   - 交通資訊
6. 更新 venues.json
7. 儲存結果
```

**限制**:
- 只能識別標準 `<nav>` 和 `<footer>` 標籤
- URL重定向問題
- 對特殊網站結構效果差

---

#### 2. **V4-Practical 實用爬蟲** (`fix_all_zero_page_venues.py`)
**用途**: 修復無頁面場地
**成功率**: 93.5%
**使用場地**: 29個

**特點**:
- 使用 requests + BeautifulSoup
- 找所有連結（不限於 nav/footer）
- 多種關鍵字匹配
- 忽略SSL錯誤

**流程**:
```
1. 讀取 venues.json
2. 找出無頁面場地 (pagesDiscovered = 0)
3. 對每個場地:
   a. 抓取首頁
   b. 提取所有 <a> 連結
   c. 用關鍵字過濾會議相關連結
   d. 提取電話、Email、捷運資訊
   e. 更新 metadata
4. 儲存 venues.json
5. 生成報告
```

**優勢**:
- ✅ 簡單直接
- ✅ 高成功率（93.5%）
- ✅ 快速
- ✅ 容易維護

---

### 輔助工具 (10個)

#### 報告生成
- `generate_v4_final_report.py` - 生成V4統計報告
- `check_v4_progress.py` - 檢查爬取進度
- `check_pages_discovered.py` - 統計頁面發現數

#### 維護工具
- `fix_v4_metadata.py` - 修復metadata
- `fix_all_pages_discovered.py` - 修正頁面數統計
- `process_v4_remaining.py` - 批次處理剩餘場地

#### 測試工具
- `practical_scraper.py` - 測試實用爬蟲
- `test_real_scraping.py` - 測試多種爬蟲方法
- `test_citizenm_v4_issue.py` - Debug工具

---

## 📋 資料結構

### venues.json 格式
```json
{
  "id": 1001,
  "name": "場地名稱",
  "status": "active",  // 或 "discontinued"
  "url": "https://example.com",
  "contactPhone": "02-1234-5678",
  "contactEmail": "info@example.com",
  "address": "台北市...",
  "accessInfo": {
    "mrt": {
      "station": "台北車站",
      "line": "藍線"
    },
    "bus": ["1", "2", "3"],
    "parking": "有"
  },
  "rooms": [
    {
      "id": "1001-01",
      "name": "會議室A",
      "capacity": 100,
      "source": "web_scraping"
    }
  ],
  "metadata": {
    "lastScrapedAt": "2026-03-25T...",
    "scrapeVersion": "V4-Practical",
    "pagesDiscovered": 21,
    "fullSiteScraped": true
  }
}
```

---

## 🔄 標準執行流程

### 新場地爬取
```bash
# 1. 單個場地測試
python full_site_scraper_v4.py --test 1001

# 2. 批次處理（5個一批）
python full_site_scraper_v4.py --batch --sample 5

# 3. 修復無頁面場地
python fix_all_zero_page_venues.py
```

### 進度檢查
```bash
# 檢查V4進度
python check_v4_progress.py

# 統計頁面發現
python check_pages_discovered.py

# 生成完整報告
python generate_v4_final_report.py
```

---

## 📊 結果呈現

### 1. JSON 資料庫 (venues.json)
- **結構化資料**
- 可直接用於API、資料庫
- 包含完整metadata

### 2. 統計報告 (Markdown)
```markdown
# V4 全站爬蟲最終報告

## 執行摘要
- 總活躍場地數：43
- V4 已處理：43
- 涵蓋率：100.0%

## 明星場地
1. 台北體育館 - 32 頁面
2. 茹曦酒店 - 29 頁面
...
```

### 3. 控制台輸出
```
[1034] NUZONE展演空間
  OK: 0 -> 6 pages
  Meeting links: 5
  Phones: 10
  Emails: 10
```

---

## ⚙️ 執行參數

### V4 爬蟲參數
```bash
# 測試單個場地
python full_site_scraper_v4.py --test <場地ID>

# 批次處理
python full_site_scraper_v4.py --batch --sample 5
```

### 實用爬蟲參數
```bash
# 自動處理所有無頁面場地
python fix_all_zero_page_venues.py
```

---

## 🔍 比較與建議

### 選擇建議

| 需求 | 推薦工具 | 理由 |
|------|----------|------|
| **一般爬取** | V4-Practical | 成功率93.5%，簡單快速 |
| **已爬取場地** | V4 | 有詳細頁面分類 |
| **新場地** | V4-Practical | 先用簡單方法 |
| **複雜網站** | V4 → V4-Practical | 先V4失敗再用Practical |

### 執行順序
```
1. 新場地 → V4-Practical (一次成功)
2. 需要詳細分類 → V4
3. V4失敗 → V4-Practical修復
```

---

## 📁 檔案組織

### 核心檔案 (必須保留)
- `full_site_scraper_v4.py` - 主爬蟲
- `fix_all_zero_page_venues.py` - 實用爬蟲
- `venues.json` - 資料庫
- `check_v4_progress.py` - 進度檢查

### 報告檔案
- `V4_FINAL_REPORT_*.md` - 統計報告
- `practical_updater_results.json` - 更新結果

### 可清理檔案 (舊版本)
- `intelligent_scraper_v3.py` - V3舊版
- `hotel_scraper.py` - 舊版
- `smart_scraper.py` - 舊版
- ... (共18個舊版本)

---

## 🎯 最佳實踐

### 1. 爬取新場地
```bash
# 直接用實用爬蟲（一次成功）
python fix_all_zero_page_venues.py
```

### 2. 檢查進度
```bash
python check_v4_progress.py
```

### 3. 生成報告
```bash
python generate_v4_final_report.py
```

### 4. 備份管理
```python
# 執行前會自動備份
venues.json.backup.YYYYMMDD_HHMMSS
```

---

## 🚀 未來改進方向

### 短期
1. 整合 V4 和 V4-Practical 成單一工具
2. 清理18個舊版本檔案
3. 增加錯誤重試機制

### 中期
1. 增加 Playwright 支援（處理JS渲染）
2. 自動URL修正
3. 增量更新功能

### 長期
1. 建立爬蟲調度系統
2. 定期自動更新
3. 資料品質監控

---

**更新時間**: 2026-03-25
**當前版本**: V4 + V4-Practical
**維護者**: Claude Code
