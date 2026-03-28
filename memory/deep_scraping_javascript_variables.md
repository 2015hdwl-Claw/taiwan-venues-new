# 深度爬蟲：JavaScript 變數提取

**類型**: feedback
**描述**: 從頁面的 JavaScript 變數中提取完整資料 - 師大進修推廣學院成功案例

---

## 問題背景

### 錯誤判斷

**最初判斷**：
- 師大進修推廣學院只有第 2 層資料（會議室列表）
- 點擊「詳細介紹」按鈕會彈出模態框
- **誤判為「無獨立詳情頁」**

**實際情況**：
- ✅ 詳細資料在頁面的 `room_data` JavaScript 變數中
- ✅ 點擊「詳細介紹」只是顯示已有的 `room_data` 資料
- ✅ 所有完整資料都已經在第 2 層的 HTML 中

---

## 解決方案

### 深度爬蟲第 3 層：JavaScript 變數提取

**資料結構**：
```javascript
var room_data = [
  {
    "id": 22,
    "enable": 1,
    "location": "圖書館校區 進修推廣學院",
    "priority": 2,
    "type": "活動場地",
    "name": "1F藝文展覽廳",
    "price": "11980",
    "unit": "每日",
    "counts": 1,
    "seats": 100,
    "activitys": "藝術相關藝文展覽及研習等活動",
    "hardware": "軌道投射燈",
    "software": "無",
    "network": "無",
    "notice": "<p><span style=\"font-size:20px\">藝文展覽廳長寬15*8公尺</span></p>",
    "url": "",
    "photos": {"2": "20220611145119.jpg", ...},
    "photo_counts": 4
  },
  // ... 更多會議室
];
```

**提取方法**：
```python
import re
import json

# 從 HTML 中提取 room_data 變數
pattern = r'var room_data = (\[.*?\]);'
match = re.search(pattern, html_content, re.DOTALL)

if match:
    json_str = match.group(1)
    room_data = json.loads(json_str)
    # 處理所有會議室的完整資料
```

---

## 成果對比

### 第 2 層 vs 第 3 層（JavaScript 變數）

| 指標 | 第 2 層爬蟲 | 第 3 層深度爬蟲 | 改善 |
|------|-----------|---------------|------|
| 容量覆蓋率 | 92.3% | **100%** | +7.7% |
| **價格覆蓋率** | 0% | **100%** ⭐ | **新增** |
| **設備覆蓋率** | 0% | **100%** ⭐ | **新增** |
| **照片覆蓋率** | 0% | **100%** ⭐ | **新增** |
| 面積覆蓋率 | 0% | 7.7% | 新增 |
| **資料完整性** | 15% | **85%** | **+467%** |

### 實際抓取的資料

**1F藝文展覽廳**（完整示例）：
- ✅ 容量：100 人
- ✅ **價格**：NT$11,980 / 每日 ⭐
- ✅ **面積**：120 平方公尺（15×8 公尺）
- ✅ **類型**：活動場地
- ✅ **地點**：圖書館校區 進修推廣學院
- ✅ **硬體設備**：軌道投射燈
- ✅ **軟體**：無
- ✅ **網路**：無
- ✅ **適合活動**：藝術相關藝文展覽及研習等活動
- ✅ **注意事項**：長寬 15*8 公尺
- ✅ **照片**：4 張

---

## 關鍵教訓

### 1. 不要侷限於「頁面層數」

**錯誤思維**：
- 第 1 層：主頁
- 第 2 層：會議室列表
- 第 3 層：詳情頁
- ❌ 誤判：如果沒有詳情頁 URL，就沒有第 3 層

**正確思維**：
- 第 1 層：主頁
- 第 2 層：會議室列表頁
- **第 3 層：詳情頁 / JavaScript 變數 / API / JSON-LD** ⭐
- 第 4 層：照片頁面 / PDF / 附加資料
- 第 5 層：外部資料（Google Maps、社群媒體）

### 2. 檢查頁面中的所有資料來源

**常見的隱藏資料位置**：
1. **JavaScript 變數**（最常見）
   - `var room_data = [...]`
   - `var venue_data = {...}`
   - `window.venueInfo = {...}`

2. **JSON-LD 結構化資料**
   - `<script type="application/ld+json">`

3. **data-* 屬性**
   - `<div data-room='{"..."}'>`

4. **隱藏的 `<input>` 或 `<textarea>`**
   - `<input type="hidden" name="room_data" value='{...}'>`

5. **HTML 註解中**
   - `<!-- room_data: {"..."} -->`

### 3. 點擊事件可能不會發送新請求

**判斷方法**：
```javascript
// 檢查點擊事件的處理方式
$(document).delegate('.btn-show-room-detail', 'click', function(event) {
    var index = $(this).attr("index");
    // 方式 A: 從 room_data 變數讀取（無需請求）
    room = room_data[i];
    // 方式 B: AJAX 請求
    $.ajax({ url: '/api/room/' + index });
});
```

**如果是方式 A**：資料已經在頁面中，直接提取即可
**如果是方式 B**：需要模擬 AJAX 請求

---

## 通用檢測流程

### 深度爬蟲檢測清單

```python
def check_data_sources(html_content):
    """檢查頁面中所有可能的資料來源"""

    sources = {
        'javascript_variables': False,
        'json_ld': False,
        'data_attributes': False,
        'hidden_inputs': False,
        'ajax_endpoints': False,
        'api_links': False
    }

    # 1. 檢查 JavaScript 變數
    if re.search(r'var\s+(room_data|venue_data|event_data)\s*=', html_content):
        sources['javascript_variables'] = True

    # 2. 檢查 JSON-LD
    if '<script type="application/ld+json">' in html_content:
        sources['json_ld'] = True

    # 3. 檢查 data-* 屬性
    if re.search(r'data-[a-z]+="{', html_content):
        sources['data_attributes'] = True

    # 4. 檢查隱藏的 input
    if '<input type="hidden"' in html_content:
        sources['hidden_inputs'] = True

    # 5. 檢查 AJAX 端點
    if re.search(r'\$\.ajax\(|\.get\(|\.post\(', html_content):
        sources['ajax_endpoints'] = True

    # 6. 檢查 API 連結
    if re.search(r'"/api/[a-z]+', html_content):
        sources['api_links'] = True

    return sources
```

---

## 實作範例

### 完整的深度爬蟲腳本

```python
import re
import json
import requests

def deep_scrape_with_js_variables(url):
    """深度爬蟲：包含 JavaScript 變數提取"""

    # [1] 獲取頁面 HTML
    response = requests.get(url)
    html_content = response.text

    # [2] 提取 JavaScript 變數
    room_data = extract_js_variable(html_content, 'room_data')

    if room_data:
        # 成功提取 JavaScript 變數
        return process_js_data(room_data)
    else:
        # [3] 嘗試其他方法
        # - AJAX 端點
        # - API 連結
        # - JSON-LD
        return try_other_methods(html_content)

def extract_js_variable(html_content, var_name):
    """提取指定的 JavaScript 變數"""

    # 模式 1: var room_data = [...]
    pattern1 = rf'var\s+{var_name}\s*=\s*(\[.*?\]);'
    match = re.search(pattern1, html_content, re.DOTALL)

    if match:
        json_str = match.group(1)
        return json.loads(json_str)

    # 模式 2: const roomData = [...]
    pattern2 = rf'const\s+{var_name}\s*=\s*(\[.*?\]);'
    match = re.search(pattern2, html_content, re.DOTALL)

    if match:
        json_str = match.group(1)
        return json.loads(json_str)

    # 模式 3: window.roomData = {...}
    pattern3 = rf'window\.{var_name}\s*=\s*(\[.*?\]);'
    match = re.search(pattern3, html_content, re.DOTALL)

    if match:
        json_str = match.group(1)
        return json.loads(json_str)

    return None

def process_js_data(room_data):
    """處理提取的 JavaScript 資料"""

    processed_rooms = []

    for room in room_data:
        processed_room = {
            'id': room.get('id'),
            'name': room.get('name'),
            'capacity': room.get('seats'),
            'price': room.get('price'),
            'price_unit': room.get('unit'),
            'equipment': {
                'hardware': room.get('hardware'),
                'software': room.get('software'),
                'network': room.get('network')
            },
            'location': room.get('location'),
            'type': room.get('type'),
            'description': room.get('activitys'),
            'notice': room.get('notice'),
            'photos': room.get('photos'),
            'photo_count': room.get('photo_counts'),
            'source': 'javascript_variable'
        }
        processed_rooms.append(processed_room)

    return processed_rooms
```

---

## 適用場景

### 這種方法適用於：

✅ **學校、政府機構網站**
- 通常使用 JavaScript 變數儲存資料
- 資料完整度高
- 例如：師大進修推廣學院、公務人力發展學院

✅ **活動場地預約系統**
- 場地資訊、價格表、設備清單
- 常用 `room_data`、`venue_data` 等變數名

✅ **會議室管理系統**
- 多個會議室的詳細資訊
- 包含容量、價格、設備、照片

### 不適用於：

❌ **純靜態 HTML 網站**
- 資料直接在 HTML 結構中
- 使用 BeautifulSoup 即可

❌ **SPA 單頁應用（React/Vue）**
- 資料透過 API 動態載入
- 需要使用 Playwright 或直接調用 API

---

## 成功指標

### 師大進修推廣學院 - 最終成果

| 指標 | 數據 |
|------|------|
| 會議室數 | 13 個 |
| 容量覆蓋率 | 100% |
| **價格覆蓋率** | **100%** ⭐ |
| **設備覆蓋率** | **100%** ⭐ |
| **照片覆蓋率** | **100%** ⭐ |
| 資料完整性 | 85% |
| 處理時間 | 5 分鐘 |
| 資料準確度 | 100%（官方資料） |

---

## 總結

### 核心原則

**「深度爬蟲不只是深入更多頁面，而是發現頁面中的隱藏資料」**

1. ✅ **不要侷限於 URL 層級**：資料可能在 JavaScript 變數中
2. ✅ **檢查所有資料來源**：`var`、`const`、`window`、JSON-LD
3. ✅ **分析點擊事件**：可能不會發送新請求
4. ✅ **優先提取隱藏資料**：比模擬點擊更可靠

### 最佳實踐

```python
# 標準深度爬蟲流程
def standard_deep_scrape(url):
    # 1. 獲取頁面
    html = get_page(url)

    # 2. 提取 JavaScript 變數
    js_data = extract_js_variables(html)

    if js_data:
        # 成功：資料已在頁面中
        return process_data(js_data)
    else:
        # 3. 嘗試爬取詳情頁
        detail_links = find_detail_links(html)

        if detail_links:
            # 成功：有詳情頁 URL
            return scrape_detail_pages(detail_links)
        else:
            # 4. 嘗試 API 或 AJAX
            api_data = try_api_endpoints(html)

            if api_data:
                return process_data(api_data)
            else:
                # 失敗：需要其他方法（Playwright、手動）
                return mark_for_manual_review()
```

---

**為什麼重要**：
- **師大進修推廣學院**從 15% 完整度提升到 **85%**（+467%）
- **價格資料**從 0% 提升到 **100%**
- **設備資料**從 0% 提升到 **100%**
- **照片資料**從 0% 提升到 **100%**

**下次遇到類似情況**：
1. 先檢查頁面源碼中的 JavaScript 變數
2. 常見變數名：`room_data`、`venue_data`、`event_data`、`space_data`
3. 使用正則表達式提取：`var\s+(\w+)\s*=\s*(\[.*?\]);`
4. 解析 JSON 並結構化

---

**更新時間**: 2026-03-26
**相關場地**: 師大進修推廣學院（ID: 1493）
**適用場景**: 學校、政府機構、活動場地預約系統
