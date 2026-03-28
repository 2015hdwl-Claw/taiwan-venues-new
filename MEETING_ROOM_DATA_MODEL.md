# 會議室資料模型與擷取程序

## 📋 完整會議室應包含的資料

### 必備欄位 (核心資料)

| 欄位 | 說明 | 範例 | 來源 |
|------|------|------|------|
| **id** | 會議室唯一識別碼 | "r001", "r002" | 系統生成 |
| **name** | 會議室名稱 | "萬豪廳", "2F會議室" | 官網 |
| **floor** | 樓層 | "2樓", "B1", "3F" | 官網 |
| **area** | 面積 | 200 | 官網 |
| **areaUnit** | 面積單位 | "坪", "平方公尺" | 官網 |
| **capacity** | 容量 | 500 | 官網 |
| **capacityType** | 容量類型 | "劇院式", "課桌式" | 官網 |
| **images** | 圖片 | {main, source} | 官網 |
| **equipment** | 設備清單 | "投影機、音響、麥克風" | 官網 |
| **priceHalfDay** | 半日價格 | 15000 | 官網 |
| **priceFullDay** | 全日價格 | 25000 | 官網 |
| **dimensions** | 尺寸資料 | {length, width, height} | 官網 |
| **minCapacity** | 最少人數 | 10 | 官網 |
| **description** | 會議室描述 | "適合大型演講..." | 官網 |

### 可選欄位 (補充資料)

| 欄位 | 說明 | 範例 |
|------|------|------|
| **capacityOptions** | 多種容量配置 | [{type: "劇院式", count: 500}, ...] |
| **features** | 特色功能 | "自然光"、"隔間" |
| **restrictions** | 使用限制 | "禁菸"、"不可攜帶外食" |
| **setupTime** | 佈置時間 | "2小時" |
| **catering** | 餐飲服務 | "提供咖啡茶點" |
| **availability** | 可用時間 | "週一至週五 09:00-22:00" |

---

## 🔍 擷取程序 - 從官網到欄位

### 步驟1: 找到會議室頁面

```python
# 1.1 抓取首頁
response = requests.get(venue_url)

# 1.2 尋找會議室相關連結
keywords = ['會議', 'meeting', '宴會', 'banquet', '場地', 'space', '會議室']
links = [a for a in soup.find_all('a')
         if any(kw in a.get_text().lower() for kw in keywords)]

# 1.3 優先選擇包含 "會議室" 或 "meeting room" 的連結
meeting_page_url = extract_best_meeting_link(links)
```

### 步驟2: 抓取會議室頁面

```python
# 2.1 抓取會議室頁面
response = requests.get(meeting_page_url)
soup = BeautifulSoup(response.text, 'html.parser')

# 2.2 識別會議室資訊的結構
# 常見結構類型:
# A. 表格 (table) - 每列一個會議室
# B. 卡片 (div.card) - 每個卡片一個會議室
# C. 列表 (ul/li) - 每個項目一個會議室
# D. 標題+內容 (h3 + p) - 標題是名稱，內容是詳細資訊
```

### 步驟3: 提取每個會議室的資料

#### 3.1 會議室名稱 (name)
```python
# 方法A: 從 h3, h4, strong 等標題提取
room_name = heading_element.get_text().strip()

# 方法B: 從卡片標題提取
room_name = card.find(class_='room-name').get_text().strip()

# 清理名稱
room_name = room_name.replace('會議室', '').replace(' Meeting Room', '').strip()
```

#### 3.2 樓層 (floor)
```python
# 從名稱推斷
if '2F' in room_name or '2樓' in room_name:
    floor = '2樓'
elif 'B1' in room_name:
    floor = 'B1'

# 或從頁面內容尋找
floor_element = soup.find(text=re.compile(r'樓層|Floor'))
if floor_element:
    floor = extract_floor_value(floor_element)
```

#### 3.3 面積 (area, areaUnit)
```python
# 尋找包含 "坪" 或 "平方公尺" 的文字
area_pattern = re.compile(r'(\d+)\s*(坪|平方米|㎡|m²)')

text_content = room_section.get_text()
area_match = area_pattern.search(text_content)

if area_match:
    area = int(area_match.group(1))
    areaUnit = '坪' if '坪' in area_match.group(2) else '平方公尺'
```

#### 3.4 容量 (capacity, capacityType)
```python
# 尋找 "容量"、"人"、"可容納" 等關鍵字
capacity_patterns = [
    r'容量[：:]\s*(\d+)\s*人',
    r'可容納\s*(\d+)\s*人',
    r'(\d+)\s*人',
    r'capacity[：:]\s*(\d+)',
]

for pattern in capacity_patterns:
    match = re.search(pattern, text_content)
    if match:
        capacity = int(match.group(1))
        break

# 容量類型
capacity_type = None
if '劇院式' in text_content or 'theater' in text_content.lower():
    capacity_type = '劇院式'
elif '課桌式' in text_content or 'classroom' in text_content.lower():
    capacity_type = '課桌式'
```

#### 3.5 尺寸 (dimensions)
```python
# 尋找長寬高資訊
dimension_pattern = re.compile(r'(\d+\.?\d*)\s*[米mM]\s*[x×]\s*(\d+\.?\d*)\s*[米mM]')

match = dimension_pattern.search(text_content)
if match:
    dimensions = {
        'length': float(match.group(1)),
        'width': float(match.group(2)),
        'unit': '公尺'
    }
```

#### 3.6 價格 (priceHalfDay, priceFullDay)
```python
# 尋找價格資訊
price_patterns = [
    r'半日[：:]\s*NT\$?\s*([\d,]+)',
    r'全日[：:]\s*NT\$?\s*([\d,]+)',
    r'half\s*day[：:]\s*NT\$?\s*([\d,]+)',
    r'full\s*day[：:]\s*NT\$?\s*([\d,]+)',
]

for pattern in price_patterns:
    match = re.search(pattern, text_content)
    if match:
        price = int(match.group(1).replace(',', ''))
        if '半日' in pattern or 'half' in pattern:
            priceHalfDay = price
        else:
            priceFullDay = price
```

#### 3.7 設備 (equipment)
```python
# 尋找設備清單
equipment_keywords = ['投影機', '音響', '麥克風', '投影', '螢幕',
                     'projector', 'sound', 'microphone', 'screen']

equipment_list = []
for keyword in equipment_keywords:
    if keyword in text_content:
        equipment_list.append(keyword)

equipment = ', '.join(equipment_list)
```

#### 3.8 圖片 (images)
```python
# 找會議室圖片
img_elements = room_section.find_all('img')

for img in img_elements:
    img_url = urljoin(base_url, img.get('src', ''))

    # 檢查是否為會議室圖片 (通過 alt 或 class 判斷)
    if 'room' in img.get('alt', '').lower() or 'meeting' in img.get('class', []):
        images = {
            'main': img_url,
            'source': base_url
        }
        break
```

#### 3.9 描述 (description)
```python
# 找會議室的描述文字
desc_elements = room_section.find_all('p')
desc_text = ' '.join([p.get_text().strip() for p in desc_elements])

# 清理格式
description = ' '.join(desc_text.split())[:200]  # 最多200字
```

### 步驟4: 組合資料

```python
room_data = {
    'id': f'r{venue_id}{room_index:03d}',  # 系統生成
    'name': room_name,                      # 從官網提取
    'floor': floor,                         # 從官網提取或推斷
    'area': area,                           # 從官網提取
    'areaUnit': areaUnit,                   # 從官網提取
    'capacity': capacity,                   # 從官網提取
    'capacityType': capacity_type,          # 從官網提取
    'dimensions': dimensions,               # 從官網提取 (可選)
    'priceHalfDay': priceHalfDay,           # 從官網提取 (可選)
    'priceFullDay': priceFullDay,           # 從官網提取 (可選)
    'equipment': equipment,                 # 從官網提取
    'images': images,                       # 從官網提取
    'description': description,             # 從官網提取 (可選)
    'source': meeting_page_url,             # 記錄來源
    'extractedAt': datetime.now().isoformat() # 記錄時間
}
```

### 步驟5: 驗證資料完整性

```python
def validate_room_data(room_data):
    """檢查必備欄位是否存在"""
    required_fields = ['id', 'name', 'capacity']
    missing_fields = [f for f in required_fields if not room_data.get(f)]

    if missing_fields:
        print(f'Warning: Missing fields {missing_fields} for room {room_data.get("name")}')

    return len(missing_fields) == 0
```

---

## 📊 完整流程範例：新場地擷取

### 輸入：新場地 URL
```
https://www.example-hotel.com.tw/
```

### 步驟1: 發現會議室頁面
```python
# 1. 抓首頁
# 2. 找到 "https://www.example-hotel.com.tw/meeting-rooms"
```

### 步驟2: 抓取會議室頁面
```python
# 抓取內容，識別結構為「卡片式」
```

### 步驟3: 提取會議室資料

#### 會議室1
```python
# 從官網抓到的原始資料:
"""
<div class="room-card">
  <h3>A廳</h3>
  <p>樓層：2樓</p>
  <p>面積：50坪</p>
  <p>容量：100人 (劇院式)</p>
  <p>設備：投影機、音響、麥克風</p>
  <p>價格：半日 NT$15,000 / 全日 NT$25,000</p>
  <img src="/images/room-a.jpg" />
</div>
"""

# 提取後的結構化資料:
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
    "main": "https://www.example-hotel.com.tw/images/room-a.jpg",
    "source": "https://www.example-hotel.com.tw/meeting-rooms"
  }
}
```

#### 會議室2
```python
# 從官網抓到的原始資料:
"""
<div class="room-card">
  <h3>B廳</h3>
  <p>容量：50人 (課桌式)</p>
  <img src="/images/room-b.jpg" />
</div>
"""

# 提取後的結構化資料:
{
  "id": "r1002",
  "name": "B廳",
  "floor": null,  # 官網未提供
  "area": null,   # 官網未提供
  "capacity": 50,
  "capacityType": "課桌式",
  "equipment": null,  # 官網未提供
  "priceHalfDay": null,  # 官網未提供
  "priceFullDay": null,  # 官網未提供
  "images": {
    "main": "https://www.example-hotel.com.tw/images/room-b.jpg",
    "source": "https://www.example-hotel.com.tw/meeting-rooms"
  }
}
```

### 步驟4: 儲存到 venues.json

```json
{
  "id": 1001,
  "name": "範例酒店",
  "url": "https://www.example-hotel.com.tw/",
  "rooms": [
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
        "main": "https://www.example-hotel.com.tw/images/room-a.jpg",
        "source": "https://www.example-hotel.com.tw/meeting-rooms"
      }
    },
    {
      "id": "r1002",
      "name": "B廳",
      "capacity": 50,
      "capacityType": "課桌式",
      "images": {
        "main": "https://www.example-hotel.com.tw/images/room-b.jpg",
        "source": "https://www.example-hotel.com.tw/meeting-rooms"
      }
    }
  ],
  "metadata": {
    "lastScrapedAt": "2026-03-25T14:00:00",
    "scrapeVersion": "Complete-Room-Extractor",
    "roomSource": "https://www.example-hotel.com.tw/meeting-rooms",
    "roomExtractedAt": "2026-03-25T14:00:00",
    "roomsCount": 2
  }
}
```

### 步驟5: 驗證

**檢查項目**:
- [ ] 官網有2個會議室 → 活動大師有2個會議室 ✓
- [ ] A廳容量100人 → 活動大師顯示100人 ✓
- [ ] B廳容量50人 → 活動大師顯示50人 ✓
- [ ] 價格正確 → 活動大師與官網一致 ✓

**原則**: 官網有什麼，活動大師有什麼；官網沒有的，活動大師不填（null）

---

## 🎯 關鍵原則

### 1. 完整性原則
> **官網有什麼，活動大師就要有什麼**

- ✅ 官網列出5個會議室 → 活動大師要有5個
- ✅ 官網標示容量100人 → 活動大師要顯示100人
- ❌ 不要只抓3個會議室（少2個）
- ❌ 不要捏造不存在的設備

### 2. 正確性原則
> **資料必須與官網一致**

- ✅ 官網說「劇院式100人」 → 活動大師填 capacity: 100, capacityType: "劇院式"
- ❌ 不要推斷或猜測
- ❌ 不要用其他場地的資料填補

### 3. 來源可追蹤原則
> **每筆資料都要記錄來源**

```json
{
  "rooms": [...],
  "metadata": {
    "roomSource": "https://www.example.com/meeting-rooms",
    "roomExtractedAt": "2026-03-25T14:00:00",
    "scrapeConfidence": "high"  // high/medium/low
  }
}
```

### 4. 容錯原則
> **官網沒有的資料，填 null，不要猜**

```python
# 好的做法
{
  "floor": null,       # 官網沒提供
  "area": null,        # 官網沒提供
  "capacity": 100      # 官網有提供
}

# 不好的做法
{
  "floor": "2樓",      # 推斷的（不準確）
  "area": 50,          # 猜測的（不準確）
  "capacity": 100
}
```

---

**文件版本**: v1.0
**建立日期**: 2026-03-25
**適用於**: 所有新場地的會議室資料擷取
