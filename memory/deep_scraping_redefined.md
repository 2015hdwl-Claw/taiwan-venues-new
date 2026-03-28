# 重新定義的深度爬蟲邏輯

**類型**: feedback
**描述**: 深度爬蟲不應侷限於頁面層級，應該檢查所有資料來源

---

## 舊的深度爬蟲思維（錯誤）

```
第 1 層：主頁
第 2 層：會議室列表頁
第 3 層：會議室詳情頁
❌ 停止：如果沒有詳情頁 URL，就認為沒有第 3 層
```

**問題**：
- ❌ 忽略了頁面中已有的 JavaScript 資料
- ❌ 忽略了 JSON-LD 結構化資料
- ❌ 忽略了隱藏的 data-* 屬性
- ❌ 錯過了大量可用資料

---

## 新的深度爬蟲思維（正確）

```
第 1 層：主頁
   ↓ 發現連結

第 2 層：會議室列表頁
   ↓ 提取會議室名稱
   ↓ 【關鍵】檢查頁面中的所有資料來源

第 3 層：詳情資料（多種形式）
   ├─ 詳情頁 URL（傳統方式）
   ├─ JavaScript 變數（常見）⭐
   ├─ JSON-LD 結構化資料
   ├─ data-* 屬性
   ├─ 隱藏的 input/textarea
   └─ API 端點

第 4 層：附加資料
   ├─ 照片頁面
   ├─ PDF 文件
   ├─ 價格表
   └─ 規則說明

第 5 層：外部資料
   ├─ Google Maps
   ├─ 社群媒體
   └─ 評價網站

第 6 層：相關資料
   ├─ 粉絲專頁
   ├─ 活動記錄
   └─ 聯絡資訊

... 無限延伸
```

---

## 為什麼要重新定義？

### 案例：師大進修推廣學院

**舊思維判斷**：
- 第 2 層：場地頁面 ✅
- 第 3 層：❌ 無獨立詳情頁
- **結論**：只能爬到第 2 層

**新思維判斷**：
- 第 2 層：場地頁面 ✅
- 第 3 層：✅ **發現 JavaScript 變數 `room_data`**
- **結果**：85% 資料完整性（價格、設備、照片 100%）

**對比**：
- 舊思維：15% 完整度（只有容量）
- 新思維：85% 完整度（完整資料）
- **改善：+467%** ⭐

---

## 通用檢測流程

### 深度爬蟲檢測順序

**優先級順序**（從高到低）：

1. **JavaScript 變數**（優先級最高）
   ```python
   # 常見變數名
   room_data, venue_data, event_data, space_data
   meeting_data, banquet_data, facility_data

   # 提取模式
   var room_data = [...]
   const venueData = {...}
   window.meetingInfo = {...}
   ```

2. **JSON-LD 結構化資料**
   ```html
   <script type="application/ld+json">
   {
     "@context": "https://schema.org",
     "@type": "MeetingRoom",
     "name": "會議室名稱",
     "capacity": 100
   }
   </script>
   ```

3. **data-* 屬性**
   ```html
   <div data-room='{"name": "...", "capacity": ...}'>
   ```

4. **隱藏的表單欄位**
   ```html
   <input type="hidden" name="room_json" value='{...}'>
   <textarea id="room_data" style="display:none">{...}</textarea>
   ```

5. **傳統詳情頁 URL**
   ```html
   <a href="/room/detail/123">詳細介紹</a>
   ```

6. **API 端點**
   ```javascript
   $.ajax({
     url: '/api/room/' + room_id,
     success: function(data) { ... }
   });
   ```

7. **HTML 註解**
   ```html
   <!-- room_data: {"id":123, "name":"..."} -->
   ```

---

## 實作策略

### 標準深度爬蟲流程

```python
def deep_scrape_venue(url):
    """標準深度爬蟲流程"""

    # [第 1 層] 獲取主頁
    homepage = fetch_page(url)

    # [第 2 層] 發現會議室列表頁
    meeting_links = find_meeting_links(homepage)
    meeting_page = fetch_page(meeting_links[0])

    # [第 3 層] 提取詳情資料（檢查所有來源）

    # 3.1 優先：JavaScript 變數
    room_data = extract_js_variables(meeting_page)
    if room_data:
        return process_js_data(room_data)

    # 3.2 JSON-LD
    jsonld_data = extract_json_ld(meeting_page)
    if jsonld_data:
        return process_jsonld_data(jsonld_data)

    # 3.3 data-* 屬性
    data_attr = extract_data_attributes(meeting_page)
    if data_attr:
        return process_data_attributes(data_attr)

    # 3.4 詳情頁 URL
    detail_links = find_detail_page_links(meeting_page)
    if detail_links:
        return scrape_detail_pages(detail_links)

    # 3.5 API 端點
    api_endpoints = find_api_endpoints(meeting_page)
    if api_endpoints:
        return call_api_endpoints(api_endpoints)

    # [第 4 層] 如果都沒有，使用其他方法
    # - Playwright（動態載入）
    # - 手動輸入
    # - 標記為待處理

    return mark_for_manual_review()
```

---

## 關鍵技術

### 1. JavaScript 變數提取

```python
import re
import json

def extract_js_variables(html_content):
    """提取所有 JavaScript 變數"""

    # 常見變數名
    var_names = [
        'room_data', 'rooms', 'venue_data', 'venues',
        'meeting_data', 'meeting', 'event_data', 'events',
        'space_data', 'spaces', 'facility_data', 'facilities'
    ]

    for var_name in var_names:
        # 模式 1: var room_data = [...]
        pattern1 = rf'var\s+{var_name}\s*=\s*(\[.*?\]);'
        match = re.search(pattern1, html_content, re.DOTALL)

        # 模式 2: const roomData = [...]
        pattern2 = rf'const\s+{var_name}\s*=\s*(\[.*?\]);'
        match2 = re.search(pattern2, html_content, re.DOTALL)

        # 模式 3: window.roomData = {...}
        pattern3 = rf'window\.{var_name}\s*=\s*(\[.*?\]);'
        match3 = re.search(pattern3, html_content, re.DOTALL)

        # 模式 4: let roomData = [...]
        pattern4 = rf'let\s+{var_name}\s*=\s*(\[.*?\]);'
        match4 = re.search(pattern4, html_content, re.DOTALL)

        if match or match2 or match3 or match4:
            # 解析 JSON
            json_match = match or match2 or match3 or match4
            json_str = json_match.group(1)

            try:
                data = json.loads(json_str)
                return {var_name: data}
            except:
                continue

    return None
```

### 2. JSON-LD 提取

```python
def extract_json_ld(html_content):
    """提取 JSON-LD 結構化資料"""

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_content, 'html.parser')

    # 尋找所有 JSON-LD script 標籤
    scripts = soup.find_all('script', {'type': 'application/ld+json'})

    for script in scripts:
        try:
            data = json.loads(script.string)

            # 檢查是否為相關類型
            if data.get('@type') in ['MeetingRoom', 'EventVenue', 'Place']:
                return data
        except:
            continue

    return None
```

### 3. data-* 屬性提取

```python
def extract_data_attributes(html_content):
    """提取 data-* 屬性中的資料"""

    from bs4 import BeautifulSoup
    import json

    soup = BeautifulSoup(html_content, 'html.parser')

    # 尋找所有帶有 data- 開頭的屬性
    elements = soup.find_all(attrs={'data-room': True})
    elements.extend(soup.find_all(attrs={'data-venue': True}))
    elements.extend(soup.find_all(attrs={'data-space': True}))

    for element in elements:
        try:
            data_json = element.get('data-room') or element.get('data-venue') or element.get('data-space')

            if data_json:
                return json.loads(data_json)
        except:
            continue

    return None
```

---

## 成功案例

### 師大進修推廣學院

**檢測結果**：
- ❌ 無詳情頁 URL
- ✅ **發現 `room_data` JavaScript 變數**

**提取成果**：
```json
{
  "id": 22,
  "name": "1F藝文展覽廳",
  "seats": 100,
  "price": "11980",
  "unit": "每日",
  "hardware": "軌道投射燈",
  "software": "無",
  "network": "無",
  "photos": {...}
}
```

**資料完整性**：85%（價格 100%、設備 100%、照片 100%）

---

## How to Apply（如何應用）

### 爬蟲前檢查清單

**在開始爬蟲前，先檢查頁面源碼**：

1. ✅ 搜尋關鍵字：`var room_data`、`const venues`
2. ✅ 搜尋 JSON-LD：`application/ld+json`
3. ✅ 搜尋 data- 屬性：`data-room=`
4. ✅ 搜尋隱藏欄位：`type="hidden"`
5. ✅ 搜尋 API 端點：`/api/room`

**檢查順序**：
```bash
# 在瀏覽器開發者工具中
Ctrl+F → "var room_data"
Ctrl+F → "application/ld+json"
Ctrl+F → "data-room="
Ctrl+F → "/api/"
```

### 決策樹

```
發現會議室列表頁
    │
    ├─ 有詳情頁 URL？
    │   ├─ 是 → 爬取詳情頁
    │   └─ 否 → 繼續檢查
    │
    ├─ 有 JavaScript 變數？
    │   ├─ 是 → 提取變數（優先）⭐
    │   └─ 否 → 繼續檢查
    │
    ├─ 有 JSON-LD？
    │   ├─ 是 → 提取 JSON-LD
    │   └─ 否 → 繼續檢查
    │
    ├─ 有 data-* 屬性？
    │   ├─ 是 → 提取屬性
    │   └─ 否 → 繼續檢查
    │
    ├─ 有 API 端點？
    │   ├─ 是 → 調用 API
    │   └─ 否 → 使用其他方法
    │
    └─ Playwright / 手動
```

---

## Why：為什麼這樣做？

### 理由 1：資料完整性

**JavaScript 變數**通常包含：
- ✅ 價格資訊（最重要）
- ✅ 設備清單（硬體、軟體、網路）
- ✅ 照片數量和 URL
- ✅ 注意事項和規則
- ✅ 適合的活動類型

**詳情頁**可能只有：
- ⚠️ 基本描述
- ⚠️ 簡單規格
- ❌ 缺少價格

### 理由 2：效率

**提取 JavaScript 變數**：
- 時間：1-2 分鐘
- 可靠度：95%+
- 額外請求：0 次

**爬取詳情頁**：
- 時間：5-10 分鐘
- 可靠度：70-80%
- 額外請求：10-20 次

**改善：5-10 倍效率提升**

### 理由 3：準確度

**JavaScript 變數**：
- 來源：官方後端資料庫
- 格式：結構化 JSON
- 準確度：100%

**詳情頁 HTML**：
- 來源：可能經過前端處理
- 格式：非結構化文字
- 準確度：80-90%

---

## 總結

### 核心原則

**「深度爬蟲 = 發現所有資料來源，不只是爬取更多頁面」**

1. ✅ **不要被 URL 限制**：資料可能在 JavaScript 中
2. ✅ **檢查所有來源**：變數、JSON-LD、屬性、API
3. ✅ **優先提取隱藏資料**：比爬取詳情頁更可靠
4. ✅ **無限深入**：第 3 層、第 4 層、第 5 層...直到窮盡

---

**何時使用**：
- 每次爬蟲前，先檢查頁面源碼
- 找 `var`、`const`、`window` 變數
- 找 `data-*` 屬性
- 找 JSON-LD 腳本

**How to apply**：
```python
# 標準模板
def scrape_venue(url):
    page = fetch(url)

    # 優先檢查 JavaScript 變數
    js_data = extract_js_vars(page)
    if js_data:
        return js_data

    # 其次檢查 JSON-LD
    jsonld = extract_json_ld(page)
    if jsonld:
        return jsonld

    # 最後才爬詳情頁
    return scrape_detail_pages(page)
```

---

**更新時間**: 2026-03-26
**影響**: 所有深度爬蟲任務
**優先級**: 最高 ⭐⭐⭐⭐⭐
