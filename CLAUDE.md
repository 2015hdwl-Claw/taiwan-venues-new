# 活動大師 Activity Master - 專案配置

**專案目標**: 爬取並整合台灣會議場地資料，提供完整的場地資訊平台

---

## ⚠️ 強制性規則（絕對不可違反）

### 三階段爬蟲流程 - 必須按順序執行

**每次爬取任何場地，必須按順序執行三階段，不可跳過任何階段**：

```
階段1：技術檢測 → 階段2：深度爬蟲 → 階段3：驗證寫入
```

#### 階段1：技術檢測（必須先執行，不可跳過）
```python
# 1.1 HTTP 狀態碼檢測
response = requests.get(url, timeout=15)
print(f"HTTP 狀態: {response.status_code}")

# 1.2 Content-Type 檢測
content_type = response.headers.get('Content-Type')
print(f"Content-Type: {content_type}")

# 1.3 網頁載入方式檢測（JS 框架）
soup = BeautifulSoup(response.text, 'html.parser')
scripts = soup.find_all('script')
# 檢查是否有 react, vue, angular, jquery

# 1.4 資料位置檢測
# 檢查 JSON-LD, 內嵌 JSON, HTML 結構

# 1.5 反爬蟲機制檢測
# 檢查 Cookies, Cloudflare, Rate Limiting

# 輸出：技術檢測報告（告訴你能不能爬、怎麼爬）
```

#### 階段2：深度爬蟲（基於階段1結果制定策略）
```python
# 根據階段1的結果決定策略：
# - 靜態HTML → 直接解析
# - 動態JS → 使用Selenium
# - Cloudflare → 手動處理或繞過
# - PDF優先 → 先下載PDF

# 2.1 第一級：主頁分析
# 尋找會議/宴會相關連結

# 2.2 第二級：會議室頁面發現
# 從主頁連結中找到會議室頁面

# 2.3 第三級：頁面內容提取
# 提取完整會議室資料（30欄位）

# 輸出：所有連結、PDF、會議室資訊
```

#### 階段3：驗證寫入（基於階段2結果驗證完整性）
```python
# 3.1 驗證提取的資料完整性
# 檢查 30 欄位標準

# 3.2 檢查資料品質
# 驗證容量、面積、價格的合理性

# 3.3 寫入 venues.json
# 建立備份 → 更新資料

# 3.4 生成驗證報告
# 確認資料完整度

# 輸出：更新後的 venues.json
```

### 禁止的事項

❌ **絕對不可跳過階段1直接寫爬蟲腳本**
- 錯誤：寫腳本訪問URL → 遇到404 → 放棄
- 正確：階段1技術檢測 → 分析結果 → 制定策略 → 執行

❌ **絕對不可遇到問題就放棄**
- 錯誤：遇到404/Cloudflare → 跳過這個場地
- 正確：回到階段1結果 → 分析失敗原因 → 調整策略 → 重試

❌ **絕對不可假設"應該可以"而不測試**
- 錯誤：假設URL正確 → 直接爬取 → 失敗
- 正確：先測試每個連結 → 確認可用 → 再深度爬取

### 強制檢查清單

每次寫爬蟲腳本前，必須問自己：

**寫腳本前**：
- [ ] 我是否已經完成階段1技術檢測？
- [ ] 我是否已經分析階段1的結果？
- [ ] 我是否知道這個網站能不能爬？
- [ ] 我是否知道需要什麼特殊處理？

**寫腳本時**：
- [ ] 我的腳本是否基於階段1的結果？
- [ ] 我的腳本是否處理了階段1發現的問題？
- [ ] 我的腳本是否測試了每個連結？

**遇到問題時**：
- [ ] 我是否回到階段1結果找原因？
- [ ] 我是否調整策略而不是放棄？
- [ ] 我是否記錄問題和對策？

### 記憶體參考

詳細規則請參考：[memory/three_stage_mandatory.md](memory/three_stage_mandatory.md)

---

## 專案背景

這是一個網頁爬蟲專案，用於自動化收集台灣各類會議場地的詳細資訊。

**核心挑戰**:
- 每個場地官網結構不同
- 關鍵資料分散在不同頁面（會議頁、交通頁、PDF文件）
- 需要處動態網頁和靜態HTML
- 資料品質驗證與去重

**資料庫**: `venues.json` - 目前包含 42 個已驗證場地

---

## 專案結構

### 主要爬蟲程式

| 檔案 | 版本 | 用途 | 速度 | 完整度 |
|------|------|------|------|--------|
| `intelligent_scraper_v3.py` | V3 | 單頁爬蟲 + 品質驗證 | ⚡ 快 | 🟡 基本 |
| `full_site_scraper_v4.py` | V4 | 全站爬蟲（多頁面發現） | 🐢 慢 | 🟢 完整 |
| `full_site_scraper_v4_enhanced.py` | V4+ | V4 + PDF 提取 | 🐢 慢 | 🟢 最完整 |

### 使用時機

**V3 單頁爬蟲** (intelligent_scraper_v3.py):
```bash
# 快速更新基本資料（電話、Email）
python intelligent_scraper_v3.py --batch --sample 10
```
- ✅ 適合: 更新聯絡資訊、快速處理大量場地
- ⚠️ 限制: 會議室資料不完整

**V4 全站爬蟲** (full_site_scraper_v4.py):
```bash
# 深度爬取完整資料（會議室、交通、照片）
python full_site_scraper_v4.py --batch --sample 3
```
- ✅ 適合: 重要場地、需要完整會議室資料
- ⚠️ 注意: 速度較慢，建議每次 3-5 個場地

**V4 Enhanced** (full_site_scraper_v4_enhanced.py):
```bash
# 包含 PDF 提取（適合官網有 PDF 價格表的場地）
python full_site_scraper_v4_enhanced.py --batch --sample 2
```
- ✅ 適合: 官網有 PDF 檔案的場地
- ⚠️ 注意: 最慢但最完整

---

## 關鍵技術實作

### 1. 批次處理機制

**避免重複爬取** - 檢查 `metadata.lastScrapedAt`:

```python
# ✅ 正確做法
metadata = venue.get('metadata', {})
last_scraped_str = metadata.get('lastScrapedAt')

if not last_scraped_str:
    unprocessed.append(venue['id'])  # 從未爬取
else:
    last_scraped = datetime.fromisoformat(last_scraped_str)
    if (today - last_scraped.date()) > timedelta(days=7):
        unprocessed.append(venue['id'])  # 超過 7 天
```

**❌ 錯誤做法** (已在 V3 修復):
```python
# 錯誤：每次都處理所有場地
for venue in scraper.data:
    if venue.get('url') and venue.get('verified'):
        unprocessed.append(venue['id'])  # 不要這樣做！
```

### 2. 資料品質驗證

**DataQualityValidator 類別** (intelligent_scraper_v3.py):

```python
# 電話驗證 (台灣格式)
is_valid, score, issues = DataQualityValidator.validate_phone(phone)
# 格式: +886-2-1234-5678 或 02-1234-5678

# Email 驗證 (含垃圾過濾)
is_valid, score, issues = DataQualityValidator.validate_email(email)
# 過濾: no-reply, @noreply, @spam

# 會議室驗證
is_valid, score, issues = DataQualityValidator.validate_rooms(rooms)
# 檢查: 容量 (5-5000)、面積、名稱
```

### 3. 頁面發現與分類

**V4 PageDiscoverer**:
```python
discoverer = PageDiscoverer()
all_pages = discoverer.discover_all(base_url, max_pages=30)

# 發現來源:
# 1. 導航列連結 (nav, menu)
# 2. Footer 連結
# 3. URL 模式猜測 (/meeting, /access, /contact)
```

**V4 PageClassifier**:
```python
classifier = PageClassifier()

page_type = classifier.classify(page, url)
# 回傳: 'meeting' | 'access' | 'contact' | 'policy' | 'gallery' | 'other'
```

### 4. PDF 提取

**PDFDiscoverer + PDFExtractor** (V4 Enhanced):

```python
# 發現 PDF
pdf_links = pdf_discoverer.discover_pdfs(base_url, page)

# 提取資料
for pdf_url in pdf_links:
    rooms = pdf_extractor.extract_rooms_from_pdf(pdf_url)
    # 解析: 會議室名稱、容量、面積、價格
```

**重要案例**: 集思台大會議中心 (ID: 1128)
- 只有 4 個會議室在 HTML
- 實際有 12 個會議室在 PDF
- PDF 來源: `https://www.meeting.com.tw/ntu/download/台大_場地租用申請表_20250401.pdf`

---

## venues.json 資料結構

```json
{
  "id": 1128,
  "name": "集思台大會議中心(NTUCC)",
  "venueType": "會議中心",
  "url": "https://www.meeting.com.tw/ntu/",
  "address": "台北市羅斯福路四段85號B1",
  "contact": {
    "phone": "+886-2-3366-4504",
    "email": "ntu.service@meeting.com.tw"
  },
  "capacity": {
    "theater": 400,
    "classroom": 150
  },
  "rooms": [
    {
      "id": "1128-01",
      "name": "國際會議廳",
      "nameEn": "International Conference Hall",
      "capacity": {"theater": 400},
      "area": 253.6,
      "areaUnit": "坪",
      "price": {"weekday": 44000, "holiday": 48000},
      "source": "pdf_20250401"
    }
  ],
  "traffic": {
    "mrt": "公館站",
    "bus": ["1", "207", "643"],
    "parking": "倍思地下停車場"
  },
  "verified": true,
  "metadata": {
    "lastScrapedAt": "2026-03-25T10:30:00",
    "scrapeVersion": "V4_PDF",
    "scrapeConfidenceScore": 85,
    "totalRooms": 12
  }
}
```

**關鍵欄位說明**:
- `verified`: true 表示已人工驗證過
- `metadata.lastScrapedAt`: 最後爬取時間
- `metadata.scrapeVersion`: V3 | V4 | V4_PDF
- `metadata.scrapeConfidenceScore`: 0-100 品質分數

---

## 場地分類

目前 5 大類別:

| 類別 | 說明 | 代表場地 |
|------|------|----------|
| 飯店場地 | 國際觀光飯店會議設施 | 寒舍艾麗、君悅、W飯店 |
| 婚宴場地 | 專業婚宴會館 | 龍邦、典華、薇閣 |
| 展演場地 | 大型展演空間 | 松山文创、集思台大 |
| 會議中心 | 純會議用途 | 台大醫院國際會議中心 |
| 運動場地 | 體育館、球場附設會議室 | 台北體育館 |

---

## 開發工作流程

### 1. 新增場地
```bash
# 方法 1: 手動新增到 venues.json
# 方法 2: 使用爬蟲自動發現
python intelligent_scraper_v3.py --url https://example.com
```

### 2. 爬取場地資料
```bash
# 快速更新 (V3)
python intelligent_scraper_v3.py --batch --sample 10

# 完整爬取 (V4)
python full_site_scraper_v4.py --batch --sample 3

# 含 PDF (V4+)
python full_site_scraper_v4_enhanced.py --batch --sample 2
```

### 3. 驗證資料品質
```bash
# 檢查特定場地
python check_venue_details.py --id 1128

# 生成報告
python generate_report.py --type quality
```

### 4. 手動修正
```bash
# 修正單一場地
python update_specific_venues.py --id 1128

# 從 PDF 更新
python update_ntucc_v2.py  # 集思台大範例
```

---

## 已知問題與解決方案

### 問題 1: 批次處理重複爬取
- **症狀**: 每次運行都爬取相同場地
- **原因**: 未檢查 `metadata.lastScrapedAt`
- **狀態**: ✅ 已在 V3 修復 (line 694-716)
- **檔案**: `intelligent_scraper_v3.py`

### 問題 2: 會議室資料不完整
- **症狀**: 只爬到部分會議室（如集思台大只有 4 個）
- **原因**: 關鍵資料在 PDF 中，非 HTML
- **解決**: 使用 V4 Enhanced 或手動 PDF 提取
- **案例**: `update_ntucc_v2.py` 成功提取 12 個會議室

### 問題 3: API Rate Limiting (429)
- **症狀**: `Usage limit reached for 5 hour`
- **解決**:
  - 使用 `/clear-skills` 減少 token
  - 等待 reset 時間
  - 縮短 prompt，避免大量分析

---

## 重要檔案

### 爬蟲核心
- `intelligent_scraper_v3.py` - V3 單頁爬蟲
- `full_site_scraper_v4.py` - V4 全站爬蟲
- `full_site_scraper_v4_enhanced.py` - V4 + PDF

### 資料檔案
- `venues.json` - 主資料庫
- `venues.json.backup.*` - 自動備份

### 文檔
- `KNOWLEDGE_BASE.md` - 專案知識庫（問題與解決方案）
- `CLAUDE.md` - 本檔案（Claude 專案配置）

### 範例腳本
- `update_ntucc_v2.py` - PDF 提取範例
- `check_venue_details.py` - 場地資料檢視

---

## 開發規範

### Python 程式碼風格
- 遵循 PEP 8
- 使用 UTF-8 編碼
- 函數加上類型提示 (Type Hints)
- 錯誤處理要完整 (try-except)

### Git 提交訊息格式
```
<type>: <description>

<optional body>
```

Type: feat, fix, refactor, docs, test, chore, perf, ci

範例:
```
feat: 加入 PDF 提取功能到 V4 爬蟲

- 使用 PyPDF2 解析 PDF 文件
- 自動發現並提取會議室資料
- 支援容量、面積、價格解析
```

---

## Claude 使用建議

### 當我需要:
1. **分析場地資料** → 直接讀取 `venues.json`
2. **修復爬蟲 bug** → 檢查對應版本的 `.py` 檔案
3. **理解專案問題** → 查閱 `KNOWLEDGE_BASE.md`
4. **快速批次處理** → 使用 V3
5. **完整深度爬取** → 使用 V4 或 V4+

### 避免的事項:
- ❌ 不要修改未備份的 `venues.json`（先備份再修改）
- ❌ 不要同時執行多個批次爬蟲（可能被封鎖）
- ❌ 不要忽略資料品質驗證警告
- ❌ 不要用 V4 處理超過 5 個場地（太慢）

---

## 專案知識庫

詳細的問題追蹤與解決方案請參考: [KNOWLEDGE_BASE.md](KNOWLEDGE_BASE.md)

**重點摘要**:
- ✅ V3 批次問題已修復
- ✅ V4 支援全站爬取
- ✅ PDF 提取已驗證（集思台大 12 會議室）
- ✅ 資料品質驗證機制完備

---

**最後更新**: 2026-03-25
**維護者**: le202
**Claude Code 版本**: Sonnet 4.6
