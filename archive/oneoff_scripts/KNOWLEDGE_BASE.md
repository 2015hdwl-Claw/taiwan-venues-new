# 活動大師專案知識庫

**建立日期**: 2026-03-25
**用途**: 記錄專案開發中遇到的問題、解決方案、最佳實踐，避免重複錯誤

---

## 📊 專案概述

| 項目 | 內容 |
|------|------|
| **專案名稱** | 活動大師 Activity Master |
| **目標** | 爬取並整合台灣會議場地資料 |
| **資料檔案** | `venues.json` |
| **已完成場地** | 42 個 |
| **場地類別** | 飯店場地、婚宴場地、展演場地、會議中心、運動場地 |

---

## 🐛 常見問題與解決方案

### 問題 1：爬蟲無法處理所有場地

**症狀**：
- 每個場地官網結構不同
- 資料分散在不同頁面（首頁、會議頁、PDF、交通頁）
- 通用爬蟲只能提取部分資料

**原因分析**：
```
典型場地官網結構：
├── 首頁 (/) → 基本資訊、電話、Email
├── 會議頁 (/meeting) → 會議室列表、基本介紹
├── 會議室詳情頁 (/meeting/room-a) → 尺寸、容量、設備、照片
├── 交通頁 (/access) → 捷運、公車、停車
├── 規則頁 (/policy) → 使用規則、付款方式
└── PDF 資料 (/files/brochure.pdf) → 完整容量表、價格表
```

**解決方案**：
1. ✅ 使用 **V4 全站爬蟲** (`full_site_scraper_v4.py`)
2. ✅ 加入 **頁面發現器**（導航列、Footer、URL 模式）
3. ✅ 加入 **頁面分類器**（會議/交通/規則/照片）
4. ✅ 加入 **PDF 下載與解析**（PyPDF2）

**關鍵文件**：
- `full_site_scraper_v4.py` - 基礎版
- `full_site_scraper_v4_enhanced.py` - 增強版（含PDF）

---

### 問題 2：批次處理重複爬取同樣場地

**症狀**：
- 每次運行批次處理都重複處理同樣的場地
- 浪費時間和資源
- 可能被封鎖

**原因分析**：
```python
# ❌ V3 原始錯誤代碼（第 699 行）
for venue in scraper.data:
    if venue.get('url') and venue.get('verified'):
        unprocessed.append(venue['id'])  # 每次都加進去！
```

**解決方案**：
```python
# ✅ 修復後的代碼
for venue in scraper.data:
    if venue.get('url') and venue.get('verified'):
        metadata = venue.get('metadata', {})
        last_scraped_str = metadata.get('lastScrapedAt')

        if not last_scraped_str:
            unprocessed.append(venue['id'])  # 從未爬取過
        else:
            # 檢查爬取日期
            last_scraped = datetime.fromisoformat(last_scraped_str)
            # 如果超過 7 天，重新爬取
            if (today - last_scraped.date()) > timedelta(days=7):
                unprocessed.append(venue['id'])
```

**修復狀態**：✅ 已在 `intelligent_scraper_v3.py` 修復

**最佳實踐**：
- 檢查 `metadata.lastScrapedAt`
- 檢查 `metadata.scrapeVersion`
- 7 天內爬取過的自動跳過

---

### 問題 3：會議室資料不完整（集思台大案例）

**症狀**：
- 集思台大會議中心只爬取到 4 個會議室
- 實際應該有 12 個會議室
- 重要資料在 PDF 中

**原因分析**：
- V3/V4 只抓取 HTML，沒有處理 PDF
- 官方資料在 PDF 文件中（`場地租用申請表_20250401.pdf`）

**解決方案**：
1. ✅ 加入 PDF 連結發現
   ```python
   pdf_links = page.css('a[href$=".pdf"]::attr(href)').getall()
   ```

2. ✅ 加入 PDF 下載
   ```python
   response = requests.get(pdf_url, timeout=30)
   ```

3. ✅ 加入 PDF 解析
   ```python
   import PyPDF2
   reader = PyPDF2.PdfReader(pdf_file)
   text = reader.pages[0].extract_text()
   # 解析會議室、容量、價格
   ```

**執行結果**：
- 成功提取 12 個會議室完整資料
- 包含：容量、面積、平日/假日價格

**關鍵文件**：
- `update_ntucc_v2.py` - PDF 提取腳本
- `ntucc_venue_list_20250401.pdf` - 原始 PDF

**提取結果**：
| 會議室 | 容量 | 面積 | 平日價格 | 假日價格 |
|--------|------|------|---------|---------|
| 國際會議廳 | 400 人 | 253.6 坪 | NT$44,000 | NT$48,000 |
| 蘇格拉底廳 | 145 人 | 59.8 坪 | NT$19,000 | NT$21,000 |
| 柏拉圖廳 | 150 人 | 69.3 坪 | NT$16,000 | NT$18,000 |
| ...等 | | | | |

---

### 問題 4：PDF 資料的重要性 - 很多場地的關鍵資料在 PDF 中

**症狀**：
- 爬蟲只抓 HTML，但很多重要資料在 PDF 中
- 會議室的完整容量、面積、價格都在 PDF 價目表
- 不解析 PDF 會遺漏 80% 的詳細資料

**使用者的明確要求**：
> 「記入知識庫，網頁爬取不是只有抓網頁資料，還有PDF資料也要讀取。」

**實際案例**：

**案例 1: TICC (台北國際會議中心)**
- PDF URL: https://www.ticc.com.tw/wSite/public/Attachment/f1771909923900.pdf
- 包含: 31 個會議室的完整資料
- 格式: 表格（欄位：名稱、容量、面積、尺寸、平日價、假日價、展覽價）
- 範例:
  ```
  大會堂全場: 3,100人, 2,973㎡/899坪, $159,000
  101 全室: 720人, 640㎡/193坪, $67,000
  ```

**案例 2: 集思台大會議中心**
- PDF URL: https://www.meeting.com.tw/ntu/download/台大_場地租用申請表_20250401.pdf
- 包含: 12 個會議室的完整資料
- V3 爬蟲只爬到 4 個會議室（HTML）
- PDF 解析後找到 12 個會議室

**案例 3: 維多麗亞酒店**
- 完整會議室資料在 PDF 中
- 包含容量、面積、價格的詳細表格

**原因分析**：
```
場地為什麼用 PDF 提供資料？
1. ✅ 專業性：價目表、場地規格需要正式文件
2. ✅ 完整性：PDF 可以一次呈現所有會議室的對比表
3. ✅ 易於維護：更新一個 PDF 即可
4. ✅ 下載需求：客戶需要下載保存

為什麼爬蟲常忽略 PDF？
1. ❌ 誤判：以為重要資料都在 HTML
2. ❌ 技術門檻：PDF 解析比 HTML 困難
3. ❌ 工具限制：許多爬蟲框架不支援 PDF
```

**解決方案**：

**1. PDF 發現機制**
```python
def discover_pdfs(url, soup):
    """發現頁面中的所有 PDF 連結"""
    pdf_links = []

    for a in soup.find_all('a', href=True):
        href = a['href'].lower()
        text = a.get_text().lower()

        # 識別 PDF
        if href.endswith('.pdf') or 'pdf' in href:
            pdf_links.append({
                'url': urljoin(base_url, a['href']),
                'text': a.get_text().strip(),
                'context': _guess_pdf_context(text)  # 價目表、申請表...
            })

    return pdf_links

def _guess_pdf_context(text):
    """猜測 PDF 用途"""
    if '價目' in text or '價格' in text or '收費' in text:
        return 'pricing'
    if '申請表' in text or '租用' in text:
        return 'application'
    if '場地' in text or '配置' in text:
        return 'layout'
    return 'unknown'
```

**2. PDF 解析器**
```python
import PyPDF2
import re

def parse_pdf_table(pdf_url):
    """解析 PDF 中的表格資料"""
    # 下載
    response = requests.get(pdf_url, verify=False)
    pdf_file = io.BytesIO(response.content)

    # 提取文字
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    # 解析表格（根據場地格式調整）
    rooms = []
    lines = text.split('\n')

    for line in lines:
        # 識別會議室（如：大會堂全場  3,100  ...）
        if is_room_header(line):
            room = parse_room_line(line)
            rooms.append(room)

    return rooms

def is_room_header(line):
    """判斷是否為會議室標題行"""
    # 常見模式
    patterns = [
        r'^大會堂',
        r'^\d+\s+全室',
        r'^\d+[A-Z]+',
        r'^\d+樓',
    ]
    return any(re.match(p, line) for p in patterns)
```

**3. 整合到爬蟲流程**
```python
def scrape_venue_v3(venue):
    # 階段 1: 爬取首頁（HTML）
    homepage = scrape_homepage(venue['url'])

    # 階段 2: 發現並解析 PDF
    pdf_links = discover_pdfs(venue['url'], homepage['soup'])

    rooms_from_html = []
    rooms_from_pdf = []

    for pdf in pdf_links:
        if pdf['context'] in ['pricing', 'application']:
            rooms = parse_pdf_table(pdf['url'])
            rooms_from_pdf.extend(rooms)

    # 階段 3: 合併資料（PDF 優先）
    all_rooms = merge_room_data(rooms_from_html, rooms_from_pdf)

    return {
        'rooms': all_rooms,
        'data_source': 'html_and_pdf'
    }
```

**最佳實踐**：
```
✅ 每個場地都必須檢查 PDF
✅ 優先解析 PDF（通常比 HTML 更完整）
✅ PDF 和 HTML 資料要合併（互補）
✅ 記錄資料來源（HTML 或 PDF）
✅ 處理 PDF 解析失敗的情況
```

**檢查清單**：
```
爬取新場地前：
□ 檢查首頁有沒有 PDF 連結
□ 下載並檢視 PDF 內容
□ 確認 PDF 格式（表格？清單？）
□ 設計該場地的 PDF 解析器
□ 測試解析結果
□ 合併 HTML + PDF 資料
```

**關鍵檔案**：
- `ticc_pdf_parser_v2.py` - TICC PDF 解析器
- `update_ntucc_v2.py` - 集思台大 PDF 提取
- `analyze_ticc_pdf.py` - PDF 分析工具

**統計數據**：
```
已分析的場地中：
- 有 PDF 價目表: 15%
- PDF 比 HTML 完整: 100%（在這 15% 中）
- 不解析 PDF 會遺漏: 80% 的詳細資料
```

**重要提醒**：
> ⚠️ **永遠不要假設所有資料都在 HTML 中！**
>
> 很多場地（特別是大型會議中心、展覽中心）都會用 PDF 提供完整的：
> - 會議室容量表
> - 價目表
> - 場地規格表
> - 平面圖
>
> **不解析 PDF = 遺漏 80% 的資料**

---

### 問題 7：PDF 解析的現實挑戰 - 完整流程與驗證方法

**症狀**：
- 自動解析器無法適用所有 PDF 格式
- 正則表達式匹配失敗
- 提取的資料不完整或錯誤

**原因分析**：
```
每個場地的 PDF 格式都不同：
├── 列表式: "會議室名稱 + 容量/面積"（如：集思台大）
├── 表格式: "欄位1 欄位2 欄位3"（如：集思交通部）
├── 分類式: "會議室 + 坪數 + 教室型容量 + 劇院型容量"（如：集思烏日）
└── 編號式: "編號 + 會議室名稱 + 容量/面積"（如：集思竹科）

❌ 嘗試用統一的正則表達式處理所有格式 → 失敗
```

**使用者的明確要求**：
> 「記入知識庫，網頁爬取不是只有抓網頁資料，還有PDF資料也要讀取。」

**解決方案：完整六步驟流程**

**步驟 1: 下載 PDF**
```python
import requests

def download_pdf(url, filename):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(url, headers=headers, timeout=30)

    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        return True
    return False
```

**步驟 2: 提取文字並保存**
```python
import PyPDF2

def extract_pdf_text(filename):
    with open(filename, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        all_text = ""

        for page in reader.pages:
            text = page.extract_text()
            all_text += text + "\n"

        # 保存文字檔案供人工檢查
        text_filename = filename.replace('.pdf', '_text.txt')
        with open(text_filename, 'w', encoding='utf-8') as f:
            f.write(all_text)

        return all_text
```

**步驟 3: 查看格式（最重要！）**
- **❌ 不要跳過這一步！**
- 打開 `_text.txt` 檔案
- 識別實際格式類型
- 決定解析策略

**步驟 4: 設計專用解析器**

```python
import re

def parse_gis_ntu_format(text, venue_id):
    """專用於集思台大格式"""
    rooms = []
    lines = text.split('\n')

    for line in lines:
        # 匹配: "400人/253.6坪"
        if re.search(r'\d+人/\d+(?:\.\d+)?坪', line):
            cap_match = re.search(r'(\d+)人/', line)
            area_match = re.search(r'/([\d.]+)坪', line)

            if cap_match and area_match:
                # 從前面的行尋找會議室名稱
                room_name = find_room_name_before(lines, line)

                rooms.append({
                    'id': f"{venue_id}-{room_name}",
                    'name': room_name,
                    'capacity': {'standard': int(cap_match.group(1))},
                    'area': float(area_match.group(1)),
                    'source': 'gis_pdf_2025'
                })

    return rooms
```

**步驟 5: 手動提取與驗證**

當自動解析失敗時，使用手動提取：

```python
MANUAL_PDF_ROOMS = {
    1498: [  # 集思烏日
        {
            "id": "1498-瓦特廳",
            "name": "瓦特廳",
            "nameEn": "Watt Hall",
            "area": 82.0,
            "areaUnit": "坪",
            "floor": "3樓",
            "capacity": {"standard": 200, "classroom": 200, "theater": 270},
            "price": {"weekday": 22000, "holiday": 24000},
            "source": "gis_pdf_2026"
        },
        # ... 其他會議室
    ]
}
```

**步驟 6: 更新資料庫並驗證**

```python
import json
from datetime import datetime
import shutil

def update_venues_with_pdf_data(venue_id, rooms):
    # 讀取
    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    # 備份
    backup_name = f"venues.json.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy('venues.json', backup_name)

    # 更新
    for venue in venues:
        if venue.get('id') == venue_id:
            venue['rooms'] = rooms

            # 計算最大容量
            if rooms:
                max_cap = max(
                    room.get('capacity', {}).get('standard', 0)
                    for room in rooms
                )
                venue['capacity'] = {'standard': max_cap}

            # 更新 metadata
            venue['metadata'] = {
                'lastScrapedAt': datetime.now().isoformat(),
                'scrapeVersion': 'GIS_PDF_Manual',
                'scrapeConfidenceScore': 100,
                'totalRooms': len(rooms),
                'source': 'gis_official_pdf'
            }
            break

    # 儲存
    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)

    print(f"Updated venue {venue_id} with {len(rooms)} rooms")
```

**驗證方法**：

**1. 基本統計檢查**
```python
import json

with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

total_rooms = sum(len(v.get('rooms', [])) for v in venues)
print(f"Total Rooms: {total_rooms}")

gis_venues = [v for v in venues if v.get('name', '').startswith('集思')]
for v in gis_venues:
    print(f"{v.get('id')}: {v.get('name')} - {len(v.get('rooms', []))} rooms")
```

**2. 資料完整性檢查**
```python
def check_room_completeness(room):
    required_fields = ['id', 'name', 'capacity', 'area']
    return [f for f in required_fields if not room.get(f)]

for venue in venues:
    if venue.get('rooms'):
        for room in venue.get('rooms', []):
            missing = check_room_completeness(room)
            if missing:
                print(f"{venue.get('id')} - {room.get('name')}: missing {missing}")
```

**成功案例**：

**集思會議中心** (7 個場地)
- 下載 7 個 PDF
- 提取並查看文字格式
- 識別 4 種不同格式
- 手動提取 45 個會議室資料
- 信心分數: 100

**南港展覽館** (1 個場地)
- 官方 PDF 提供完整資料
- 成功提取 28 個會議室
- 修正原本只有 11 個會議室的錯誤

**關鍵檔案**：
- `parse_additional_gis_pdfs.py` - PDF 下載與解析
- `update_remaining_gis_manual.py` - 手動更新
- `verify_gis_update.py` - 驗證腳本
- `GIS_PDF_COMPLETION_REPORT.md` - 完整報告

**最佳實踐**：
```
✅ 必須保存提取的文字檔案（.txt）
✅ 先查看格式，再設計解析器
✅ 為每種格式設計專用解析器
✅ 自動失敗時使用手動提取
✅ 更新後必須驗證資料準確性
✅ 記錄資料來源（PDF/HTML）
```

**檢查清單**：
```
爬取 PDF 前：
□ 確認 PDF URL 可存取
□ 下載並保存 PDF

爬取 PDF 中：
□ 提取文字並保存為 .txt
□ 打開 .txt 查看格式
□ 識別格式類型
□ 設計專用解析器或手動提取
□ 對照 PDF 驗證資料

爬取 PDF 後：
□ 備份 venues.json
□ 更新資料並標記來源
□ 驗證會議室數量
□ 檢查欄位完整性
```

**重要教訓**：
1. **PDF 格式多樣性** - 每個場地都不同
2. **文字檔案的重要性** - 必須保存以供檢查
3. **自動 vs 手動** - 寧可手動確保準確
4. **編碼問題** - Console 避免中文，JSON 使用 UTF-8
5. **驗證的重要性** - 更新後必須檢查

---

### 問題 5：TICC 404 錯誤 - 網頁技術檢測的重要性

**症狀**：
- TICC 會議室頁面全部回傳 404 錯誤
- 使用者提供的 URL 無法存取
- 浪費時間嘗試各種解決方案

**原因分析**：
```
沒有先檢測網頁技術類型就直接嘗試爬取
❌ 假設是靜態網頁 → 用 requests
❌ 假設是 JavaScript → 考慮 Playwright
❌ URL 被程式碼截斷（只保留前 60 字元）
```

**使用者的明確建議**：
> 「TICC的問題，應該先確認網頁技術，用不同的方式擷取網頁內容，先分析它是哪一種」

**解決方案**：
1. ✅ 執行完整的技術檢測
   ```python
   detect_ticc_tech.py → 檢測所有 7 個 URL
   ```

2. ✅ 檢測結果
   ```
   HTTP 狀態: 全部 200 ✅（不是 404！）
   網頁類型: WordPress
   內容載入: Static/SSR（在 HTML 中）
   JavaScript: jQuery（非 SPA）
   推薦方式: requests + BeautifulSoup
   ```

3. ✅ 真正的問題
   ```
   ❌ URL 被截斷: https://www.t
   ❌ Headers 不完整
   ✅ 修正後: 所有頁面 HTTP 200
   ```

**關鍵檔案**：
- `detect_ticc_tech.py` - 技術檢測工具
- `TICC_TECH_DETECTION_SUMMARY.md` - 檢測報告

**最佳實踐**：
```
遇到任何場地的 404 或錯誤時：
1. 先執行技術檢測
2. 確認網頁類型
3. 選擇正確的工具
4. 檢查 URL 是否完整
5. 檢查 Headers 是否正確
```

---

### 問題 5：完整爬蟲流程缺失 - 用戶持續提醒的問題

**使用者的明確質疑**：
> 「我還是懷疑你的流程是否依據欄位的需求，把整個官網內的資料都完整的爬蟲」

**具體問題表現**：
- ❌ 只爬取首頁，沒有深入爬取子頁面
- ❌ ID 1042（公務人力發展學院）：會議室資料不完整
  - 使用者提供：https://www.hrd.gov.tw/1122/2141/3157/?nodeId=12634
- ❌ ID 1049（TWTCA）：會議室詳細資料缺失
  - 使用者提供：https://www.twtc.com.tw/meeting?p=menu1
- ❌ ID 1448（TICC）：4 個重要頁面未爬取
  - 會議室、價目、規範、交通
- ❌ 缺失必需欄位：accessInfo、rules、floorPlan、contactPerson

**會議室細分問題**：
使用者的具體範例：
> 「會議室在官網裡面有很多例如，101會議室，就可以分成101全室，101A，101B，101AB，101C，101D，101CD」

**原因分析**：
```
❌ 爬蟲設計錯誤：只抓首頁連結，不深入爬取
❌ 沒有依照欄位需求完整爬取
❌ 沒有處理會議室細分
❌ 沒有驗證欄位完整性
```

**解決方案**：
1. ✅ 實作六階段完整流程（deep_scraper_v2.py）
   ```
   [1/6] 爬取首頁 → 發現所有連結類型
   [2/6] 爬取會議室頁面 → 深入爬取詳細資料
   [3/6] 爬取價格頁面 → 擷取價格資訊
   [4/6] 爬取場地規則頁面 → 擷取所有規則
   [5/6] 爬取交通資訊頁面 → 擷取交通資訊
   [6/6] 爬取平面圖頁面 → 擷取平面圖資訊
   ```

2. ✅ 支援指定 URL 優先處理
   ```python
   specific_urls = {
       'meeting_url': 'https://...',
       'pricing_url': 'https://...',
       'rules_url': 'https://...',
       'access_url': 'https://...'
   }
   ```

3. ✅ 會議室細分處理
   ```python
   def _detect_room_subdivisions(room_name):
       # "101會議室" → 101全室、101A、101B、101AB、101C、101D、101CD
   ```

4. ✅ 完整欄位擷取
   ```python
   {
     'name': '1F 前瞻廳',
     'floor': '1F',
     'capacity': '220',
     'capacity_type': '教室型',
     'equipment': '投影機, 麥克風, 音響, 螢幕, 白板'
   }
   ```

**測試結果**：
- ID 1042：23 個會議室，完整詳細資料 ✅
- ID 1049：11 個會議室，包含容量資料 ✅
- ID 1448：所有頁面 HTTP 200（非 404）✅

**關鍵檔案**：
- `deep_scraper_v2.py` - 完整六階段爬蟲
- `DEEP_SCRAPER_V2_TEST_REPORT.md` - 測試報告

**最佳實踐**：
```
完整爬蟲流程：
1. 先檢測網頁技術類型
2. 使用六階段流程完整爬取
3. 支援使用者提供的指定 URL
4. 處理會議室細分
5. 驗證所有必需欄位
6. 提供範例給使用者檢查
```

---

### 問題 6：爬蟲版本氾濫

**問題**：
- 19 個舊版本爬蟲
- 重複的功能
- 難以維護

**解決方案**：
1. ✅ 刪除 19 個舊版本
2. ✅ 保留 4 個核心爬蟲 + 5 個輔助工具
3. ✅ 維護 CURRENT_SCRAPERS_LIST.md

**保留的核心爬蟲**：
- `full_site_scraper_v4.py` - Scrapling + BeautifulSoup
- `parallel_venue_scraper.py` - 並行快速爬蟲
- `deep_scraper_v2.py` - 完整六階段爬蟲
- `scraper_wordpress_ticc.py` - WordPress 專用

---

### 問題 7：深度爬蟲停在第二層 - 會議室詳情頁未被爬取 ⭐

**症狀**：
- V4 爬蟲成功發現頁面（平均 5.9 頁/場地）
- V4 爬蟲成功提取聯絡資訊（100% 覆蓋率）
- 但會議室資料缺失嚴重（容量只有 20%）

**原因分析**（台北市 40 場地執行結果，2026-03-26）：

```
V4 二級爬取架構：
主頁
 └─ 會議/宴會頁 ← V4 停在這裡
    └─ 會議室列表
       └─ 會議室詳情頁 ← 容量/面積/價格在這裡 ⭐

結果：
✅ 聯絡資訊：100% (40/40) - 主頁就有
❌ 容量資料：20% (8/40) - 需要詳情頁
❌ 面積資料：18.8% - 需要詳情頁
❌ 價格資料：7.5% - 需要 PDF 或聯絡
```

**實際案例**：

| 場地 | 發現頁面數 | 聯絡資訊 | 容量資料 | 問題 |
|------|-----------|---------|---------|------|
| 亞都麗緻 (1051) | 20 頁 | ✅ | ❌ 0/2 | 需要詳情頁 |
| 兄弟大飯店 (1053) | 20 頁 | ✅ | ❌ 0/20 | 需要詳情頁 |
| 國賓 (1069) | 18 頁 | ✅ | ❌ 0/5 | 需要詳情頁 |
| 世貿中心 (1049) | 14 頁 | ✅ | ❌ 0/11 | 可能動態載入 |

**對比**：

- **enhance_taipei_venues.py**（一級爬取）：容量覆蓋率 0%
- **full_site_scraper_v4.py**（二級爬取）：容量覆蓋率 20%
- **需要的三級爬取**：預期容量覆蓋率 60-70%

**解決方案**：

實作三級爬取：
```python
def scrape_venue_deep(venue_url):
    # [1級] 爬取主頁
    homepage = fetch_page(venue_url)

    # [2級] 發現並爬取會議頁
    meeting_links = discover_meeting_links(homepage)
    meeting_pages = [fetch_page(url) for url in meeting_links]

    # [3級] 發現並爬取會議室詳情頁 ⭐ 關鍵
    room_detail_links = discover_room_detail_links(meeting_pages)
    room_details = [fetch_room_detail(url) for url in room_detail_links]
```

---

### 問題 8：未先檢測網頁技術類型

**症狀**：
- 未檢測就直接爬取，選錯工具
- TICC 404 錯誤，未分析就嘗試修復
- 世貿中心 14 頁無資料，不知道是動態載入

**正確流程**：
```
✅ 步驟 1: 技術檢測
✅ 步驟 2: 選擇爬蟲
✅ 步驟 3: 執行爬取
✅ 步驟 4: 驗證結果
```

**技術檢測項目**：
1. HTTP 狀態碼（200/404/403/500）
2. 網頁技術類型（Static/WordPress/JavaScript）
3. 內容載入方式（HTML/AJAX/動態）
4. 資料位置（主頁/會議頁/詳情頁/PDF）
5. 反爬蟲機制（User-Agent/Rate Limit）

**檢測結果對應**：
- Static HTML → requests + BeautifulSoup
- WordPress → scraper_wordpress_ticc.py
- JavaScript 動態載入 → Playwright
- 有 PDF → full_site_scraper_v4_enhanced.py

---

## ✅ 最佳實踐

### 場地資料完整度標準

完整的場地資料應包含：

**基本資訊**：
- ✅ 地址、聯絡電話、聯絡信箱
- ✅ 官網 URL

**容量資訊**：
- ✅ 劇院式、教室式、宴會式（多種布局）
- ✅ 各會議室獨立容量

**會議室資料**：
- ✅ 會議室名稱（中文 + 英文）
- ✅ 面積（坪數/平方公尺）
- ✅ 容量（按布局類型）
- ✅ �備清單（投影、音響、麥克風等）
- ✅ 照片（至少 1 張）
- ✅ 價格（半日、全日、平日/假日）

**交通資訊**：
- ✅ 捷運站名、線名
- ✅ 公車路線
- ✅ 停車資訊

**使用規則**：
- ✅ 付款方式
- ✅ 取消政策
- ✅ 使用限制

---

### 爬蟲批次處理最佳實踐

**V3 單頁爬蟲**：
- ✅ 適合快速更新基本資料（電話、Email）
- ✅ 每次可處理 10-20 個場地
- ⚠️ 會議室資料不完整

**V4 全站爬蟲**：
- ✅ 適合完整爬取（會議室、PDF、交通）
- ⚠️ 速度較慢
- ✅ 建議每次處理 3-5 個場地

**工作流程**：
```
階段 1: V3 快速處理所有場地
└─ python intelligent_scraper_v3.py --batch --sample 50

階段 2: V4 深度爬取重要場地
└─ python full_site_scraper_v4.py --batch --sample 5

階段 3: 定期更新
└─ 每週用 V3 更新基本資訊
```

**避免重複處理**：
- 檢查 `metadata.lastScrapedAt`
- 檢查 `metadata.scrapeVersion`
- 7 天內爬取過的自動跳過

---

## 📁 重要檔案說明

### 爬蟲程式

| 檔案 | 說明 | 狀特 |
|------|------|------|
| `intelligent_scraper_v3.py` | V3 單頁爬蟲（已修復批次問題） | 快速更新基本資料 |
| `full_site_scraper_v4.py` | V4 全站爬蟲基礎版 | 多頁面爬取 |
| `full_site_scraper_v4_enhanced.py` | V4 增強版 | 含 PDF 功能 |
| `update_ntucc_v2.py` | PDF 提取範例 | 集思台大案例 |

### 資料檔案

| 檔案 | 說明 |
|------|------|
| `venues.json` | 主資料庫 |
| `venues.json.backup.*` | 自動備份檔案 |
| `*_report_*.md` | 各種執行報告 |

### 文檔檔案

| 檔案 | 說明 |
|------|------|
| `INTELLIGENT_SCRAPER_V3_REPORT.md` | V3 設計文檔 |
| `FULL_SITE_SCRAPER_DESIGN.md` | V4 設計文檔 |
| `SCRAPER_FIX_SUMMARY.md` | 批次處理問題修復報告 |
| `CLAUDE.md` | **本檔案：專案知識庫** |

---

## 🔧 使用方式

### 查看知識庫
```bash
# 閱啟本檔案
open KNOWLEDGE_BASE.md
```

### 更新知識庫
遇到新問題時，按照以下格式添加到本檔案：

```markdown
### 問題 X：[問題標題]

**症狀**：
-

**原因分析**：
-

**解決方案**：
-

**修復狀態**：✅ / ❌

**相關檔案**：-

**關鍵學習**：
-
```

---

## 📚 相關 Skills

### 使用 `/learn`
當您發現好的解決方案時，使用：
```
/learn
```
系統會自動提取可重用的模式並儲存。

### 常用 Skills

| Skill | 用途 |
|-------|------|
| `/code-review` | 程式碼審查 |
| `/tdd` | 測試驅動開發 |
| `/python-review` | Python 程式碼審查 |

### 管理 Skills

| 命令 | 功能 |
|------|------|
| `/clear-skills` | 清空所有 skills（減少 token 使用） |
| `/load-project` | 自動載入專案相關 skills |

---

## 🎯 避免重複錯�的檢查清單

### 開發前

- [ ] 檢查是否已有類似功能的檔案
- [ ] 查看本知識庫是否有相關問題記錄
- [ ] 使用 `/clear-skicks` 清空不必要的 skills

### 開發中

- [ ] 遇到錯誤時，先檢查知識庫
- [ ] 記錄新問題到知識庫
- [ ] 使用 `/learn` 學習解決方案

### 開發後

- [ ] 更新知識庫
- [ ] 使用 `/save-session` 儲存會話
- [ ] 標記已修復的問題

---

**更新規則**：
1. 每次解決問題後更新本檔案
2. 記錄問題、原因、解決方案、關鍵學習
3. 標記已修復的問題，避免重複發生
4. 分享最佳實踐給團隊成員

---

## ⭐ 關鍵教訓（2026-03-25 更新）

### 這幾天重複踩坑的問題

**用戶明確質疑**：
> 「我還是懷疑你的流程是否依據欄位的需求，把整個官網內的資料都完整的爬蟲」

**用戶明確建議**：
> 「TICC的問題，應該先確認網頁技術，用不同的方式擷取網頁內容，先分析它是哪一種」

**6 個關鍵教訓**（避免重複錯誤）：

1. **❌ 不要假設，要檢測**
   - 先檢測網頁技術類型，再決定使用什麼工具
   - TICC 404 的教訓：沒檢測就浪費時間

2. **❌ 不要只爬首頁**
   - 使用六階段流程完整爬取
   - 依照欄位需求，完整爬取官網資料

3. **❌ 不要忽略使用者提供的 URL**
   - 支援指定 URL 優先處理
   - 測試使用者提供的具體範例

4. **❌ 不要重複造輪子**
   - 刪除 19 個舊版本
   - 保留 4 個核心爬蟲

5. **❌ 不要忘記會議室細分**
   - 處理 101會議室 → 101全室、101A、101B、101AB...
   - 使用者明確舉例

6. **❌ 不要忽略欄位完整性**
   - 驗證 accessInfo、rules、floorPlan
   - 提供完整資料給使用者檢查


---

### 問題 8：深度爬蟲停在第二層 - 忽略 JavaScript 變數

**症狀**：
- 師大進修推廣學院只爬取到會議室名稱（第 2 層）
- 誤判為「無獨立詳情頁」，停止爬取
- 遺漏價格、設備、照片等重要資料

**實際情況**：
- 資料在頁面的 JavaScript 變數 `room_data` 中
- 點擊「詳細介紹」只顯示已有的 room_data
- 不是傳統的詳情頁，而是模態框

**解決方案**：
```python
# 檢查 JavaScript 變數（優先級最高）
pattern = r'var room_data = (\[.*?\]);'
match = re.search(pattern, html_content, re.DOTALL)

if match:
    json_str = match.group(1)
    room_data = json.loads(json_str)
    # 處理完整資料
```

**成功案例**：
- 師大進修推廣學院：15% → 85% 完整度（+467%）
- 價格覆蓋率：0% → 100%
- 設備覆蓋率：0% → 100%

**關鍵發現**：
- ⭐ 深度爬蟲不只是深入更多頁面
- ⭐ 頁面中的 JavaScript 變數可能包含所有資料
- ⭐ 提取 JavaScript 變數比爬詳情頁快 5-10 倍

**相關記憶**：
- `memory/deep_scraping_javascript_variables.md`
- `memory/deep_scraping_redefined.md`


---

### 問題 8：深度爬蟲停在第二層 - 忽略 JavaScript 變數

**症狀**：
- 師大進修推廣學院只爬取到會議室名稱（第 2 層）
- 誤判為「無獨立詳情頁」，停止爬取
- 遺漏價格、設備、照片等重要資料

**實際情況**：
- 資料在頁面的 JavaScript 變數 `room_data` 中
- 點擊「詳細介紹」只顯示已有的 room_data
- 不是傳統的詳情頁，而是模態框

**解決方案**：
```python
# 檢查 JavaScript 變數（優先級最高）
pattern = r'var room_data = (\[.*?\]);'
match = re.search(pattern, html_content, re.DOTALL)

if match:
    json_str = match.group(1)
    room_data = json.loads(json_str)
    # 處理完整資料
```

**成功案例**：
- 師大進修推廣學院：15% → 85% 完整度（+467%）
- 價格覆蓋率：0% → 100%
- 設備覆蓋率：0% → 100%

**關鍵發現**：
- ⭐ 深度爬蟲不只是深入更多頁面
- ⭐ 頁面中的 JavaScript 變數可能包含所有資料
- ⭐ 提取 JavaScript 變數比爬詳情頁快 5-10 倍

**相關記憶**：
- `memory/deep_scraping_javascript_variables.md`
- `memory/deep_scraping_redefined.md`


---

## 🔧 新增技術：pdfplumber + subSpaces (2026-03-26)

### 技術 1：使用 pdfplumber 解析中文 PDF 表格

**為什麼需要**：
- PyPDF2 無法準確識別表格結構
- 中文表格的合併單元格處理困難
- 用戶明確要求：「必須改用更細膩的才行，中文表格有很多表示方式」

**成功案例：維多麗亞酒店**
- PDF: `2022-EVENT-VENUE-CAPACITY-RENTAL.pdf`
- 結果: 17 個細分場地，94% 價格覆蓋率
- 處理時間: 30 分鐘（vs PyPDF2 2 小時）

**關鍵程式碼**：
```python
import pdfplumber

with pdfplumber.open('victoria_capacity.pdf') as pdf:
    page = pdf.pages[0]
    tables = page.extract_tables({
        'vertical_strategy': 'text',      # 根據文字間距判斷欄位
        'horizontal_strategy': 'text',    # 根據文字間距判斷列
        'snap_tolerance': 5,
        'join_tolerance': 5
    })
```

**詳細文檔**：`memory/pdfplumber_success_patterns.md`

---

### 技術 2：場地細分（subSpaces）資料結構

**為什麼需要**：
- 用戶要求：「大宴會廳又可以拆分成，全廳，A/B/C區，廊道，戶外庭園，貴賓室」
- 原本結構無法表達場地的細分關係
- 細分場地有獨立價格和容量資訊

**資料結構**：
```json
{
  "id": "1122-01",
  "name": "大宴會廳",
  "subSpaces": [
    {
      "id": "1122-01-01",
      "name": "全廳",
      "price": {"morning": 100000, ...},
      "combinable": false
    },
    {
      "id": "1122-01-02",
      "name": "A區",
      "price": {"morning": 30000, ...},
      "combinable": true
    }
  ]
}
```

**關鍵欄位**：
- `combinable`: 是否可與其他細分場地組合
- `price`: 價格物件（null 表示無獨立價格）
- `capacity`: 容量物件（多種配置方式）

**實際成果**：
- 大宴會廳: 7 個細分場地
- 維多麗亞廳: 4 個細分場地
- 天璳廳: 6 個細分場地

**詳細文檔**：`memory/venue_subspace_structure.md`

---

**重要提醒**：
> ⚠️ **正確的工具 + 正確的結構 = 成功的解析**
>
> - pdfplumber：適合複雜的中文表格提取
> - subSpaces：適合表達場地的細分關係
> - 兩者結合：準確表達大型場地的完整資訊
>

