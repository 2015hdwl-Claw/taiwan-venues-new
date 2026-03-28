# 回答你的三個問題

## 問題1：完整的會議空間（會議室）應該包含哪些資料？

### 答案：

#### 必備欄位（一定要有）

| 欄位 | 說明 | 範例 | 重要程度 |
|------|------|------|----------|
| **id** | 唯一識別碼 | "r1001" | ⭐⭐⭐ 系統生成 |
| **name** | 會議室名稱 | "A廳", "2F會議室" | ⭐⭐⭐ 一定要有 |
| **capacity** | 容量（人數） | 100 | ⭐⭐⭐ 一定要有 |
| **floor** | 樓層 | "2樓", "B1" | ⭐⭐ 重要 |
| **area** | 面積 | 50 | ⭐⭐ 重要 |
| **areaUnit** | 面積單位 | "坪", "平方公尺" | ⭐⭐ 重要 |
| **capacityType** | 容量類型 | "劇院式", "課桌式" | ⭐⭐ 重要 |
| **equipment** | 設備 | "投影機、音響" | ⭐⭐ 重要 |
| **priceHalfDay** | 半日價格 | 15000 | ⭐ 有最好 |
| **priceFullDay** | 全日價格 | 25000 | ⭐ 有最好 |
| **images** | 圖片 | {main, source} | ⭐ 有最好 |

**最小要求**：
- ✅ name（會議室名稱）
- ✅ capacity（容量）
- ⭐️ floor, area, equipment, price（盡量有）

#### 完整範例

```json
{
  "id": "r1001",
  "name": "宴會廳",
  "floor": "2樓",
  "area": 200,
  "areaUnit": "坪",
  "capacity": 500,
  "capacityType": "劇院式",
  "equipment": "投影機、音響、麥克風、投影幕",
  "priceHalfDay": 50000,
  "priceFullDay": 80000,
  "images": {
    "main": "https://www.example.com/banquet-hall.jpg",
    "source": "https://www.example.com/meeting-rooms"
  },
  "description": "適合大型會議、研討會、發表會",
  "source": "https://www.example.com/meeting-rooms",
  "extractedAt": "2026-03-25T14:00:00"
}
```

---

## 問題2：這些資料取得的程序為何？

### 答案：5步驟程序

### 步驟1：找到會議室頁面
```python
# 1.1 抓取場地首頁
response = requests.get('https://www.example-hotel.com/')

# 1.2 尋找會議室相關連結
keywords = ['會議', 'meeting', '宴會', 'banquet', '會議室', 'meeting-room']
連結篩選 → 找到: /meeting-rooms
```

**程式**：`complete_room_extractor.py` 的 `_find_meeting_page()` 方法

### 步驟2：抓取會議室頁面
```python
response = requests.get('https://www.example-hotel.com/meeting-rooms')
soup = BeautifulSoup(response.text, 'html.parser')
```

**程式**：`complete_room_extractor.py` 的 `extract_venue_rooms()` 方法

### 步驟3：識別會議室結構
```python
# 嘗試4種結構:
# A. 表格 (table)
# B. 卡片 (div.card)
# C. 列表 (ul/li)
# D. 標題+內容 (h3 + p)

找到: 表格結構，5個會議室
```

**程式**：`complete_room_extractor.py` 的 `_identify_room_structure()` 方法

### 步驟4：提取每個會議室的資料

對每個會議室執行以下提取：

#### 4.1 提取名稱 (name)
```python
# 從標題提取
<h3>A廳</h3>  →  name = "A廳"
```

#### 4.2 提取樓層 (floor)
```python
# 正則匹配
"樓層：2樓"  →  floor = "2樓"
```

#### 4.3 提取面積 (area, areaUnit)
```python
# 正則匹配
"面積：50坪"  →  area = 50, areaUnit = "坪"
```

#### 4.4 提取容量 (capacity)
```python
# 正則匹配
"容量：100人"  →  capacity = 100
```

#### 4.5 提取容量類型 (capacityType)
```python
# 關鍵字匹配
"劇院式100人"  →  capacityType = "劇院式"
```

#### 4.6 提取設備 (equipment)
```python
# 關鍵字列表
"設備：投影機、音響、麥克風"
  →  equipment = "投影機、音響、麥克風"
```

#### 4.7 提取價格 (priceHalfDay, priceFullDay)
```python
# 正則匹配
"半日 NT$15,000"  →  priceHalfDay = 15000
"全日 NT$25,000"  →  priceFullDay = 25000
```

#### 4.8 提取圖片 (images)
```python
# 找 img 標籤
<img src="room-a.jpg" />
  →  images = {main: "https://.../room-a.jpg", source: "..."}
```

**程式**：`complete_room_extractor.py` 的 `_extract_single_room()` 及其子方法

### 步驟5：驗證資料
```python
# 檢查必備欄位
required_fields = ['id', 'name', 'capacity']
missing = [f for f in required_fields if not room_data.get(f)]

if missing:
    print(f'警告: 缺少 {missing}')
```

**程式**：`complete_room_extractor.py` 的 `_validate_room()` 方法

---

## 問題3：新場地如何從官網抓資料，處理後回到欄位？

### 答案：完整流程對應

### 輸入：新場地 URL
```
https://www.example-hotel.com/
```

### 流程：官網 → 欄位

#### 會議室1：從官網到欄位

```
官網HTML:
============================================================
<div class="room">
  <h3>宴會廳</h3>
  <p>樓層：2樓</p>
  <p>面積：200坪</p>
  <p>容量：500人 (劇院式)</p>
  <p>設備：投影機、音響、麥克風</p>
  <p>價格：半日 NT$50,000 / 全日 NT$80,000</p>
  <img src="images/banquet.jpg" />
</div>
============================================================

↓ 程式提取 ↓

{
  "id": "r1001001",           ← 系統生成
  "name": "宴會廳",            ← 從 <h3> 提取
  "floor": "2樓",             ← 從 "樓層：2樓" 提取
  "area": 200,                ← 從 "200坪" 提取數值
  "areaUnit": "坪",           ← 從 "200坪" 提取單位
  "capacity": 500,            ← 從 "500人" 提取
  "capacityType": "劇院式",   ← 從 "(劇院式)" 提取
  "equipment": "投影機、音響、麥克風",  ← 從 "設備：..." 提取
  "priceHalfDay": 50000,      ← 從 "半日 NT$50,000" 提取
  "priceFullDay": 80000,      ← 從 "全日 NT$80,000" 提取
  "images": {                 ← 從 <img> 提取
    "main": "https://www.example-hotel.com/images/banquet.jpg",
    "source": "https://www.example-hotel.com/meeting-rooms"
  }
}

============================================================
```

#### 會議室2：官網資料較少

```
官網HTML:
============================================================
<div class="room">
  <h3>會議室A</h3>
  <p>容量：30人</p>
</div>
============================================================

↓ 程式提取 ↓

{
  "id": "r1001002",
  "name": "會議室A",           ← 從 <h3> 提取
  "floor": null,               ← 官網沒提供 → null
  "area": null,                ← 官網沒提供 → null
  "areaUnit": null,            ← 官網沒提供 → null
  "capacity": 30,              ← 從 "30人" 提取
  "capacityType": null,        ← 官網沒提供 → null
  "equipment": null,           ← 官網沒提供 → null
  "priceHalfDay": null,        ← 官網沒提供 → null
  "priceFullDay": null,        ← 官網沒提供 → null
  "images": null               ← 官網沒提供 → null
}

============================================================
關鍵：官網沒有的，填 null，不推測、不捏造
```

### 最終：儲存到 venues.json

```json
{
  "id": 1001,
  "name": "範例酒店",
  "url": "https://www.example-hotel.com/",
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
      "images": {
        "main": "https://www.example-hotel.com/images/banquet.jpg",
        "source": "https://www.example-hotel.com/meeting-rooms"
      }
    },
    {
      "id": "r1001002",
      "name": "會議室A",
      "capacity": 30
    }
  ],
  "metadata": {
    "roomSource": "https://www.example-hotel.com/meeting-rooms",
    "roomExtractedAt": "2026-03-25T14:00:00",
    "roomsCount": 2,
    "scrapeConfidence": "high"
  }
}
```

---

## 🎯 關鍵原則

### 1. 完整性
官網有5個會議室 → 活動大師必須有5個
```
✅ 正確: 官網5個 → 活動大師5個
❌ 錯誤: 官網5個 → 活動大師4個（少1個）
❌ 錯誤: 官網5個 → 活動大師6個（多1個）
```

### 2. 正確性
官網的資料必須一致
```
✅ 正確: 官網說「500人」→ 活動大師填 500
❌ 錯誤: 官網說「500人」→ 活動大師填 450（推測）
```

### 3. 不缺不漏
官網有的欄位要有，沒有的填 null
```
官網: {name, capacity, floor}
✅ 正確: {name, capacity, floor}
❌ 錯誤: {name, capacity}（少了 floor）
❌ 錯誤: {name, capacity, floor, area}（多了 area）
```

---

## 🛠️ 可用工具

### 1. venue_discovery_tool.py
```bash
python venue_discovery_tool.py
```
**功能**: 新增場地到 venues.json

### 2. complete_room_extractor.py
```bash
python complete_room_extractor.py
```
**功能**: 完整擷取會議室資料（5步驟）

### 3. check_rooms_data.py
```bash
python check_rooms_data.py
```
**功能**: 檢查資料完整性

---

## 📊 欄位提取對應表

| 官網HTML | 提取方法 | venues.json 欄位 | 程式方法 |
|---------|---------|-----------------|----------|
| `<h3>A廳</h3>` | 提取標題文字 | name: "A廳" | `_extract_name()` |
| `樓層：2樓` | 正則 `(\d+樓|B\d)` | floor: "2樓" | `_extract_floor()` |
| `面積：50坪` | 正則 `(\d+)\s*(坪|㎡)` | area: 50, areaUnit: "坪" | `_extract_area()` |
| `容量：100人` | 正則 `(\d+)\s*人` | capacity: 100 | `_extract_capacity()` |
| `劇院式` | 關鍵字匹配 | capacityType: "劇院式" | `_extract_capacity_type()` |
| `半日 NT$15,000` | 正則 `半日.*NT\$?([\d,]+)` | priceHalfDay: 15000 | `_extract_price()` |
| `<img src="..." />` | img 標籤 | images: {...} | `_extract_images()` |

---

**總結**：
1. **完整會議室資料** = 11個欄位（id, name, floor, area, areaUnit, capacity, capacityType, equipment, priceHalfDay, priceFullDay, images）
2. **取得程序** = 5步驟（找會議室頁面 → 抓取 → 識別結構 → 提取資料 → 驗證）
3. **官網到欄位** = 程式自動提取，官網有什麼就提取什麼，沒有的填 null

**文件版本**: v1.0
**建立日期**: 2026-03-25
