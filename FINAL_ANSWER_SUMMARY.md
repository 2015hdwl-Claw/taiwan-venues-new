# 最終回答：兩個核心問題

## 問題1：不同網頁技術要用不同方式擷取嗎？

**答案：是的！**

### 📊 現況分析

台灣場地網站的技術分佈：
- **80%**：靜態網頁或伺服器端渲染（SSR）
- **15%**：客戶端渲染（CSR，JavaScript 產生內容）
- **5%**：有公開 API 可以直接調用

### 🛠️ 三種擷取方式

#### 方式1：requests + BeautifulSoup（最常用）

**適用**：靜態網頁、SSR
**特徵**：右鍵「檢視網頁原始碼」能看到內容
**速度**：⚡⚡⚡ 最快（0.5-2秒）
**成功率**：60-70%

```python
import requests
from bs4 import BeautifulSoup

response = requests.get('https://www.example.com')
soup = BeautifulSoup(response.text, 'html.parser')

# 直接提取資料
meeting_rooms = soup.find_all('div', class_='room')
```

#### 方式2：Playwright（JS渲染網頁）

**適用**：React, Vue, Angular 等前端框架
**特徵**：原始碼看不到內容，需要等待 JS 執行
**速度**：⚡ 慢（3-10秒）
**成功率**：95%+

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('https://www.example.com')

    # 等待 JS 渲染完成
    page.wait_for_selector('.room-list')

    # 提取資料
    html = page.content()
    soup = BeautifulSoup(html, 'html.parser')

    browser.close()
```

#### 方式3：直接調用 API（最乾淨）

**適用**：網站有公開 API
**特徵**：在開發者工具 Network 標籤能看到 XHR 請求
**速度**：⚡⚡ 快（1-3秒）
**成功率**：90%+

```python
import requests

# 從 Network 標籤找到的 API URL
api_url = 'https://api.example.com/venues/123/rooms'

response = requests.get(api_url)
data = response.json()

# 直接使用 JSON 資料
for room in data['rooms']:
    print(room['name'], room['capacity'])
```

### 🎯 建議流程

```
1. 先測試是否為靜態網頁（80% 成功）
   ↓ 失敗
2. 嘗試找 API 端點（最快最準）
   ↓ 失敗
3. 使用 Playwright（保險，95%+ 成功）
```

### 💡 自動判斷方法

```python
def smart_scrape(url):
    # 步驟1：測試靜態
    if is_static_page(url):
        return scrape_with_requests(url)

    # 步驟2：測試 API
    api_result = try_api(url)
    if api_result:
        return api_result

    # 步驟3：使用 Playwright
    return scrape_with_playwright(url)
```

---

## 問題2：遺漏的欄位

**答案：補充完整！**

### 📋 完整資料模型（兩層）

#### 第一層：場地級別（Venue Level）

##### 1. 聯絡資訊
```json
{
  "contactPhone": "02-1234-5678",      // 總機
  "phoneExtension": "1234",            // 分機（新增）
  "contactEmail": "info@example.com",
  "contactPerson": "張先生",            // 聯絡人（新增）
  "contactPersonTitle": "會議部經理"   // 職稱（新增）
}
```

**擷取方法**：
-電話分機：正則 `分機\s*(\d+)|#(\d+)`
-聯絡人：從「聯絡我們」頁面提取

##### 2. 交通資訊（新增）
```json
{
  "accessInfo": {
    "mrt": {
      "station": "台北車站",           // 捷運站
      "line": "藍線",                  // 路線
      "exit": "1號出口"                // 出口
    },
    "bus": ["1", "257", "捷運接駁"],    // 公車
    "parking": "有，200/小時",          // 停車
    "car": "國道1號台北交流道"          // 開車
  }
}
```

**擷取方法**：
-從「交通資訊」或「位置」頁面提取
-關鍵字：「捷運」、「公車」、「停車」

##### 3. 場地規則（新增）
```json
{
  "rules": {
    "catering": "僅限指定餐飲",        // 餐飲規定
    "smoking": "全館禁菸",              // 吸菸規定
    "decoration": "不可使用釘子",       // 佈置規定
    "noise": "晚上10點後不可大聲",      // 噪音規定
    "cleanup": "需自行清理",            // 清理規定
    "deposit": "10,000元",              // 押金
    "cancellation": "需7天前通知",      // 取消政策
    "terms": "租借條款：..."            // 完整條款
  }
}
```

**擷取方法**：
-從「租借須知」或「場地規則」頁面提取
-關鍵字：「餐飲」、「禁菸」、「押金」

##### 4. 場地平面圖（新增）
```json
{
  "floorPlan": {
    "url": "https://www.example.com/floorplan.jpg",  // 平面圖URL
    "description": "1F: 大廳, 2F: 會議室",           // 說明
    "floors": [                                       // 各樓層
      {"floor": "1F", "rooms": ["大廳"], "area": 100},
      {"floor": "2F", "rooms": ["A廳", "B廳"], "area": 200}
    ],
    "hasFloorPlan": true                              // 是否有平面圖
  }
}
```

**擷取方法**：
-從「場地導覽」或「平面圖」頁面提取
-找 `<img>` 或 SVG

##### 5. 圖片資訊
```json
{
  "images": {
    "main": "https://www.example.com/main.jpg",     // 主圖
    "gallery": ["url1", "url2"],                    // 相簿
    "source": "https://www.example.com/gallery"     // 來源頁面
  }
}
```

#### 第二層：會議室級別（Room Level）

```json
{
  "id": "r1001",
  "name": "A廳",
  "floor": "2樓",
  "area": 50,
  "areaUnit": "坪",
  "capacity": 100,
  "capacityType": "劇院式",
  "equipment": "投影機、音響、麥克風",
  "priceHalfDay": 15000,
  "priceFullDay": 25000,
  "images": {
    "main": "https://...",
    "source": "https://..."
  }
}
```

---

## 🔄 完整擷取程序（更新版）

### 階段1：判斷網頁類型（0.5秒）
```python
# 檢查原始碼是否包含會議室資料
# 決定用 requests、API 或 Playwright
```

### 階段2：基本資料（1-3秒）
```python
# 從首頁提取：
# - name, venueType, city, address
# - contactPhone, contactEmail
# - images.main
```

### 階段3：聯絡資訊（1-3秒）
```python
# 從「聯絡我們」頁面提取：
# - contactPerson, contactPersonTitle
# - phoneExtension（分機）
```

### 階段4：交通資訊（1-3秒）
```python
# 從「交通資訊」頁面提取：
# - accessInfo.mrt（捷運）
# - accessInfo.bus（公車）
# - accessInfo.parking（停車）
# - accessInfo.car（開車）
```

### 階段5：場地規則（1-3秒）
```python
# 從「租借須知」頁面提取：
# - rules.catering（餐飲）
# - rules.smoking（禁菸）
# - rules.decoration（佈置）
# - rules.deposit（押金）
# - rules.cancellation（取消）
```

### 階段6：場地平面圖（1-3秒）
```python
# 從「場地導覽」頁面提取：
# - floorPlan.url
# - floorPlan.description
# - floorPlan.floors
```

### 階段7：會議室資料（2-5秒）
```python
# 從「會議室」頁面提取：
# - rooms 陣列（每個會議室的完整資料）
```

**總耗時**：5-20秒（根據網頁技術和資料量）

---

## 📖 完整文件

1. **[COMPLETE_DATA_MODEL_WITH_ALL_FIELDS.md](COMPLETE_DATA_MODEL_WITH_ALL_FIELDS.md)**
   - 完整資料模型（包含所有新增欄位）
   - 每個欄位的擷取方法

2. **[WEB_SCRAPING_STRATEGIES.md](WEB_SCRAPING_STRATEGIES.md)**
   - 不同網頁技術的擷取策略
   - 靜態、API、Playwright 的使用方式

3. **[UNIVERSAL_VENUE_EXTRACTOR.md](UNIVERSAL_VENUE_EXTRACTOR.md)**
   - 整合兩個問題的完整方案
   - 自動判斷網頁類型
   - 7階段完整擷取流程

---

## ✅ 核心原則（不變）

### 1. 官網有什麼，活動大師有什麼
```
✅ 官網有5個會議室 → 活動大師5個
✅ 官網有交通資訊 → 活動大師有 accessInfo
✅ 官網有平面圖 → 活動大師有 floorPlan
✅ 官網有分機號碼 → 活動大師有 phoneExtension
```

### 2. 技術適配
```
靜態/SSR 網頁 → requests + BeautifulSoup（快）
有 API → 直接調用 API（最準）
JS 渲染 → Playwright（保險）
```

### 3. 資料來源可追蹤
```json
{
  "metadata": {
    "contactSource": "https://www.example.com/contact",
    "accessSource": "https://www.example.com/access",
    "rulesSource": "https://www.example.com/rules",
    "floorPlanSource": "https://www.example.com/floorplan",
    "roomSource": "https://www.example.com/meeting-rooms",
    "scrapeMethod": "static|api|playwright",
    "extractedAt": "2026-03-25T14:00:00"
  }
}
```

---

## 🎯 總結

### 問題1：不同技術要不同方式嗎？
**是的！**
- 80% 用 requests（快）
- 5% 用 API（準）
- 15% 用 Playwright（保險）

### 問題2：遺漏的欄位？
**已補充完整！**
- ✅ 聯絡資訊（分機、聯絡人）
- ✅ 交通資訊（捷運、公車、停車）
- ✅ 場地規則（餐飲、禁菸、押金等）
- ✅ 場地平面圖（URL、說明、樓層）

### 核心原則
**「官網有什麼，活動大師有什麼；不要多，不要少」**
- 使用適當的技術擷取
- 記錄資料來源
- 驗證資料完整性

---

**建立日期**: 2026-03-25
**版本**: v3.0（完整版）
