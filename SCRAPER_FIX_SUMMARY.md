# 爬蟲批次處理問題修復報告

**日期**: 2026-03-25
**問題**: V3 批次處理重複爬取同樣的場地
**狀態**: ✅ 已修復

---

## 🐛 問題描述

### V3 原始 BUG

**問題代碼**（第 699 行）：
```python
# ❌ 錯誤邏輯
for venue in scraper.data:
    if venue.get('url') and venue.get('verified'):
        unprocessed.append(venue['id'])  # 每次都加進去！
```

**問題**：
- 只檢查是否有 URL 和 verified
- **沒有檢查 `metadata.lastScrapedAt`**
- 每次運行都會重新處理所有已驗證的場地

**影響**：
- 浪費時間重複爬取
- 重複寫入 venues.json
- 可能被網站封鎖（過度爬取）

---

## ✅ 修復方案

### V3 修復（已套用）

**修復代碼**：
```python
# ✅ 正確邏輯
for venue in scraper.data:
    if venue.get('status') == 'discontinued':
        continue
    if venue.get('url') and venue.get('verified'):
        # 檢查是否已經爬取過
        metadata = venue.get('metadata', {})
        last_scraped_str = metadata.get('lastScrapedAt')

        if not last_scraped_str:
            # 從未爬取過
            unprocessed.append(venue['id'])
        else:
            # 檢查爬取時間
            last_scraped = datetime.fromisoformat(last_scraped_str)
            # 如果超過 7 天，重新爬取
            if (today - last_scraped.date()) > timedelta(days=7):
                unprocessed.append(venue['id'])
```

**修復內容**：
1. ✅ 檢查 `metadata.lastScrapedAt` 是否存在
2. ✅ 如果存在，檢查爬取日期
3. ✅ 超過 7 天才重新爬取
4. ✅ 7 天內爬取過的跳過

---

## 🚀 V4 全站爬蟲（新版本）

### V4 的改進邏輯

**代碼**：
```python
# ✅ V4 增強版邏輯
for venue in scraper.data:
    if venue.get('url') and venue.get('verified'):
        metadata = venue.get('metadata', {})
        last_scraped_str = metadata.get('lastScrapedAt')
        scrape_version = metadata.get('scrapeVersion')

        # V4 邏輯：檢查版本和時間
        if scrape_version == 'V4':
            # 如果是 V4 爬取的，檢查時間
            if last_scraped_str:
                last_scraped = datetime.fromisoformat(last_scraped_str)
                if (today - last_scraped.date()) <= timedelta(days=7):
                    continue  # 跳過最近爬取的
        # 不是 V4 或超過 7 天，需要處理
        unprocessed.append(venue['id'])
```

**V4 額外功能**：
- ✅ 追蹤爬蟲版本（`scrapeVersion`）
- ✅ 區分 V3 和 V4 的爬取結果
- ✅ 避免用不同版本重複爬取

---

## 📊 測試結果

### V3 修復後測試

```
✅ 修復後的邏輯測試:
   總場地數: 50
   已驗證場地: 42
   需要處理（未爬取或超過7天）: 0 個

✅ 所有場地都已爬取過（7天內）
```

### V4 測試

```
🔍 V4 批次處理邏輯測試:
======================================================================
總場地數: 50
已驗證場地: 42
需要處理: 35 個

前 10 個待處理場地:
ID     名稱                        版本       上次爬取
1034   NUZONE展演空間                None     2026-03-25
1042   公務人力發展學院                  None     2026-03-25
...
```

**說明**：
- 35 個場地的 `scrapeVersion` 是 None（因為還沒用 V4 爬取）
- 等用 V4 爬取後，會標記為 `V4`
- 下次運行時會跳過這些場地（7天內）

---

## 🎯 兩版本對比

| 特性 | V3（修復後） | V4（全站爬蟲） |
|------|--------------|---------------|
| 避免重複處理 | ✅ 7天內不重複 | ✅ 7天內不重複 |
| 爬取範圍 | 單頁（首頁） | **全站（多頁面）** |
| 頁面發現 | ❌ 無 | ✅ 導航+Footer+URL 模式 |
| 頁面分類 | ❌ 無 | ✅ 自動分類 |
| 版本追蹤 | ❌ 無 | ✅ `scrapeVersion: V4` |
| 會議室資料 | 僅名稱 | 名稱+容量+尺寸 |
| 交通資訊 | ❌ 無 | ✅ 捷運+公車+停車 |
| 使用規則 | ❌ 無 | ✅ 政策+限制 |

---

## 📖 使用建議

### 場景 1：快速更新基本資料

使用 **V3**（修復後）：
```bash
python intelligent_scraper_v3.py --batch --sample 20
```

**優點**：
- 速度快（只爬首頁）
- 適合更新電話、Email

**缺點**：
- 會議室資料不完整

---

### 場景 2：完整爬取所有資料

使用 **V4**（全站爬蟲）：
```bash
python full_site_scraper_v4.py --batch --sample 3
```

**優點**：
- 會議室完整資料
- 交通資訊
- 使用規則

**缺點**：
- 較慢（需爬多個頁面）
- 建議每次 3-5 個場地

---

### 場景 3：測試單個場地

```bash
# V3 測試
python intelligent_scraper_v3.py --test 1043

# V4 測試
python full_site_scraper_v4.py --test 1043
```

---

## 🔍 驗證邏輯

### 檢查場地狀態

```python
import json
from datetime import datetime, timedelta

with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

today = datetime.now().date()
for venue in venues:
    if venue.get('verified'):
        metadata = venue.get('metadata', {})
        last_scraped = metadata.get('lastScrapedAt')
        version = metadata.get('scrapeVersion', 'None')

        if last_scraped:
            days_ago = (today - datetime.fromisoformat(last_scraped).date()).days
            print(f"[{venue['id']}] {version} - {days_ago} 天前")
```

---

## ✅ 確認清單

- [x] **V3 BUG 已修復**
  - 檢查 `lastScrapedAt`
  - 7天內不重複

- [x] **V4 邏輯正確**
  - 檢查 `scrapeVersion`
  - 檢查 `lastScrapedAt`
  - 7天內不重複

- [x] **測試通過**
  - V3: 0 個需重複處理
  - V4: 正確識別待處理場地

- [x] **向後兼容**
  - V3 和 V4 可並存
  - 都不會重複處理

---

## 💡 結論

### 問題：V4 會不會也有同樣的問題？

**答：不會！** ✅

**原因**：
1. V4 的批次處理邏輯**從一開始就是正確的**
2. 使用 `scrapeVersion` 追蹤版本
3. 檢查 `lastScrapedAt` 日期
4. 7天內爬取過的自動跳過

### 建議工作流程

1. **先用 V3 快速處理**所有場地的基本資料
   ```bash
   python intelligent_scraper_v3.py --batch --sample 50
   ```

2. **再用 V4 深度爬取**重要場地（每次3-5個）
   ```bash
   python full_site_scraper_v4.py --batch --sample 5
   ```

3. **定期更新**（每週一次）
   - V3: 更新基本聯絡資訊
   - V4: 更新完整資料（選擇性）

---

## 📁 檔案清單

| 檔案 | 說明 | 狀態 |
|------|------|------|
| intelligent_scraper_v3.py | V3 單頁爬蟲（已修復） | ✅ 可用 |
| full_site_scraper_v4.py | V4 全站爬蟲 | ✅ 可用 |
| venues.json | 場地資料庫 | ✅ 已更新 |

---

**✅ 兩個版本都**不會**重複處理場地，可放心使用！**
