# 完整場地擷取器 - 整合版

## 🎯 兩個問題的答案

### 問題1：不同網頁技術的擷取方式

**答案**：需要使用不同的工具和策略

| 網頁類型 | 比例 | 工具 | 速度 |
|---------|------|------|------|
| **靜態/SSR** | 80% | requests + BeautifulSoup | ⚡⚡⚡ 最快 |
| **CSR（JS渲染）** | 15% | Playwright | ⚡ 慢 |
| **可調用API** | 5% | 直接調用API | ⚡⚡ 快 |

**建議流程**：
```
1. 先試 requests + BeautifulSoup（80%成功）
   ↓ 失敗
2. 再試 API 逆向（最快最準）
   ↓ 失敗
3. 最後用 Playwright（保險）
```

### 問題2：遺漏的欄位

**答案**：補充完整，共分兩層

#### 場地級別（Venue Level）
- ✅ 聯絡資訊：電話、分機、Email、聯絡人
- ✅ 交通資訊：捷運、公車、停車、開車
- ✅ 場地規則：餐飲、禁菸、佈置、噪音、押金、取消
- ✅ 場地平面圖：URL、說明、各樓層資訊
- ✅ 圖片：主圖、相簿

#### 會議室級別（Room Level）
- ✅ 基本：name, floor, area, capacity, equipment, price
- ✅ 進階：dimensions, capacityOptions, features, restrictions

---

## 📊 完整資料模型

```json
{
  "id": 1001,

  // === 基本資料 ===
  "name": "台北君悅酒店",
  "venueType": "飯店場地",
  "city": "台北市",
  "address": "台北市信義區松壽路2號",
  "url": "https://www.grandhyatttaipei.com/",

  // === 聯絡資訊 ===
  "contactPhone": "02-1234-5678",
  "phoneExtension": "1234",
  "contactEmail": "meeting@grandhyatt.com",
  "contactPerson": "張先生",
  "contactPersonTitle": "會議部經理",

  // === 交通資訊 ===
  "accessInfo": {
    "mrt": {
      "station": "台北車站",
      "line": "藍線",
      "exit": "1號出口"
    },
    "bus": ["1", "257", "捷運接駁"],
    "parking": "有，200/小時",
    "car": "國道1號台北交流道"
  },

  // === 場地規則 ===
  "rules": {
    "catering": "僅限指定餐飲",
    "smoking": "全館禁菸",
    "decoration": "不可使用釘子",
    "noise": "晚上10點後不可大聲",
    "cleanup": "需自行清理",
    "deposit": "10,000元",
    "cancellation": "需7天前通知",
    "terms": "租借條款：..."
  },

  // === 場地平面圖 ===
  "floorPlan": {
    "url": "https://www.example.com/floorplan.jpg",
    "description": "1F: 大廳, 2F: 會議室A/B/C",
    "floors": [
      {"floor": "1F", "rooms": ["大廳"], "area": 100},
      {"floor": "2F", "rooms": ["A廳", "B廳", "C廳"], "area": 200}
    ],
    "hasFloorPlan": true
  },

  // === 圖片 ===
  "images": {
    "main": "https://www.example.com/main.jpg",
    "gallery": ["url1", "url2"],
    "source": "https://www.example.com/gallery"
  },

  // === 會議室 ===
  "rooms": [
    {
      "id": "r1001001",
      "name": "宴會廳",
      "floor": "2樓",
      "area": 200,
      "areaUnit": "坪",
      "capacity": 500,
      "capacityType": "劇院式",
      "equipment": "投影機、音響、麥克風",
      "priceHalfDay": 50000,
      "priceFullDay": 80000,
      "images": {"main": "...", "source": "..."}
    }
  ],

  // === Metadata ===
  "metadata": {
    "roomSource": "https://www.example.com/meeting-rooms",
    "contactSource": "https://www.example.com/contact",
    "accessSource": "https://www.example.com/access",
    "rulesSource": "https://www.example.com/rules",
    "floorPlanSource": "https://www.example.com/floorplan",
    "extractedAt": "2026-03-25T14:00:00",
    "scrapeVersion": "Universal-Venue-Extractor-v1",
    "scrapeMethod": "static|api|playwright"
  }
}
```

---

## 🔄 完整擷取程序（6階段）

### 階段1：判斷網頁類型

```python
def detect_page_type(url):
    """自動判斷網頁類型"""

    # 測試1：檢查原始碼
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    if has_meeting_rooms_in_html(soup):
        return 'static'  # 靜態/SSR

    # 測試2：檢查 API
    if has_api_endpoint(url):
        return 'api'  # 可調用 API

    # 測試3：需要 Playwright
    return 'dynamic'  # CSR
```

### 階段2：基本資料（首頁）

```python
# 根據類型選擇工具
if page_type == 'static':
    soup = get_static_html(url)
elif page_type == 'api':
    data = call_api(url)
elif page_type == 'dynamic':
    soup = get_dynamic_html(url)  # 用 Playwright

# 提取基本資料
venue_data = {
    'name': extract_name(soup),
    'venueType': extract_venue_type(soup),
    'city': extract_city(soup),
    'address': extract_address(soup),
    'contactPhone': extract_phone(soup),
    'contactEmail': extract_email(soup)
}
```

### 階段3：聯絡資訊（聯絡我們頁面）

```python
contact_url = find_contact_page(url)
soup = scrape(contact_url)

contact_data = {
    'contactPerson': extract_contact_person(soup),
    'contactPersonTitle': extract_title(soup),
    'contactPhone': extract_phone_detailed(soup),
    'phoneExtension': extract_extension(soup),  # 分機
    'contactEmail': extract_email_detailed(soup)
}
```

### 階段4：交通資訊（交通/位置頁面）

```python
access_url = find_access_page(url)
soup = scrape(access_url)

access_data = {
    'accessInfo': {
        'mrt': {
            'station': extract_mrt_station(soup),
            'line': extract_mrt_line(soup),
            'exit': extract_mrt_exit(soup)
        },
        'bus': extract_bus_routes(soup),
        'parking': extract_parking_info(soup),
        'car': extract_driving_info(soup)
    }
}
```

### 階段5：場地規則（租借須知頁面）

```python
rules_url = find_rules_page(url)
soup = scrape(rules_url)

rules_data = {
    'rules': {
        'catering': extract_catering_rules(soup),
        'smoking': extract_smoking_rules(soup),
        'decoration': extract_decoration_rules(soup),
        'noise': extract_noise_rules(soup),
        'cleanup': extract_cleanup_rules(soup),
        'deposit': extract_deposit_rules(soup),
        'cancellation': extract_cancellation_rules(soup),
        'terms': extract_full_terms(soup)
    }
}
```

### 階段6：場地平面圖（導覽/平面圖頁面）

```python
floor_plan_url = find_floor_plan_page(url)
soup = scrape(floor_plan_url)

floor_plan_data = {
    'floorPlan': {
        'url': extract_floor_plan_image(soup),
        'description': extract_floor_plan_description(soup),
        'floors': extract_floor_info(soup),
        'hasFloorPlan': True
    }
}
```

### 階段7：會議室資料（會議室頁面）

```python
meeting_rooms_url = find_meeting_rooms_page(url)
soup = scrape(meeting_rooms_url)

rooms = extract_all_rooms(soup)

rooms_data = {
    'rooms': [
        {
            'id': generate_room_id(venue_id, i),
            'name': room['name'],
            'floor': room['floor'],
            'area': room['area'],
            'areaUnit': room['areaUnit'],
            'capacity': room['capacity'],
            'capacityType': room['capacityType'],
            'equipment': room['equipment'],
            'priceHalfDay': room['priceHalfDay'],
            'priceFullDay': room['priceFullDay'],
            'images': room['images']
        }
        for room, i in zip(rooms, range(1, len(rooms)+1))
    ]
}
```

---

## 🛠️ 使用工具

### 完整場地擷取器

```bash
# 自動判斷並擷取完整資料
python universal_venue_extractor.py --url "https://www.example.com"
```

**功能**：
- ✅ 自動判斷網頁類型（靜態/API/動態）
- ✅ 擷取所有場地級別資料（聯絡、交通、規則、平面圖）
- ✅ 擷取所有會議室資料
- ✅ 驗證資料完整性
- ✅ 記錄資料來源

### 進度檢查

```bash
# 檢查哪些欄位已填、哪些缺失
python check_venue_completeness.py --venue-id 1001
```

---

## 📖 完整文件

1. **[COMPLETE_DATA_MODEL_WITH_ALL_FIELDS.md](COMPLETE_DATA_MODEL_WITH_ALL_FIELDS.md)**
   - 完整資料模型定義
   - 包含所有遺漏的欄位

2. **[WEB_SCRAPING_STRATEGIES.md](WEB_SCRAPING_STRATEGIES.md)**
   - 不同網頁技術的擷取策略
   - 靜態、SSR、CSR、API 的處理方式

3. **[ANSWER_TO_YOUR_QUESTIONS.md](ANSWER_TO_YOUR_QUESTIONS.md)**
   - 回答3個核心問題
   - 包含完整範例

---

## ✅ 關鍵原則（不變）

### 1. 完整性
官網有什麼，活動大師有什麼
```
✅ 官網5個會議室 → 活動大師5個
✅ 官網有交通資訊 → 活動大師有 accessInfo
✅ 官網有平面圖 → 活動大師有 floorPlan
```

### 2. 正確性
資料必須與官網一致
```
✅ 官網說「02-1234-5678 分機1234」→ 活動大師填 contactPhone + phoneExtension
✅ 官網說「捷運台北車站」→ 活動大師填 accessInfo.mrt.station
```

### 3. 技術適配性
根據網頁技術選擇工具
```
靜態/SSR → requests + BeautifulSoup（80%）
有 API → 直接調用 API（5%）
CSR → Playwright（15%）
```

---

**更新日期**: 2026-03-25
**版本**: v2.0（補充完整欄位 + 技術策略）
