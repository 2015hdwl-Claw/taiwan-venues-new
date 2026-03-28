# 全站智能爬蟲設計方案

**日期**: 2026-03-25
**版本**: V4.0 設計

---

## 🎯 核心洞察

### 問題分析

活動大師需要的資料分散在官網的**不同頁面**：

```
典型飯店官網結構：
├── 首頁 (/)
│   └── 基本資訊、電話、Email
├── 會議/宴會頁面 (/meeting, /banquet, /events)
│   ├── 會議室列表
│   ├── 會議室詳細頁面
│   ├── 容量表格
│   └── 價格資訊
├── 各會議室詳細頁 (/meeting/ballroom, /meeting/room-a)
│   ├── 尺寸（長寬高）
│   ├── 面積（坪/平方公尺）
│   ├── 容量（劇院式、教室式...）
│   ├── 照片
│   └── 設備清單
├── 交通資訊頁 (/access, /location, /traffic)
│   ├── 捷運/公車資訊
│   ├── 停車資訊
│   └── 地圖
├── 使用規則頁 (/terms, /policy, /rules)
│   ├── 付款方式
│   ├── 取消政策
│   └── 使用限制
└── 聯絡我們頁 (/contact)
    ├── 電話
    ├── Email
    └── 表單
```

### 當前爬蟲的問題

| 問題 | 說明 | 影響 |
|------|------|------|
| **單頁爬取** | 只爬取首頁 | 遺漏 80% 的資料 |
| **淺層提取** | 只提取文字和連結 | 沒有進入會議室詳細頁 |
| **無結構理解** | 不認識頁面類型 | 不知道哪個頁面有什麼資料 |
| **無智能導航** | 不會自動點擊相關連結 | 錯過重要頁面 |

---

## 🚀 解決方案：全站智能爬蟲 V4

### 核心概念

```
1. 發現階段：探索官網結構，找到所有相關頁面
2. 分類階段：識別每個頁面的類型（會議、交通、規則...）
3. 提取階段：從不同類型頁面提取特定資料
4. 整合階段：合併所有資料到統一格式
```

### 架構設計

```python
class FullSiteScraper:
    """全站智能爬蟲"""

    def scrape_full_site(self, url):
        # 1. 發現所有頁面
        pages = self.discover_pages(url)

        # 2. 分類頁面
        classified = {
            'meeting': [],      # 會議/宴會頁面
            'rooms': [],        # 會議室詳細頁
            'access': [],       # 交通頁面
            'contact': [],      # 聯絡頁面
            'policy': [],       # 規則頁面
            'gallery': [],      # 照片頁面
        }

        for page in pages:
            page_type = self.classify_page(page)
            classified[page_type].append(page)

        # 3. 提取資料
        data = {}
        data['basic'] = self.extract_basic_info(classified['contact'])
        data['rooms'] = self.extract_rooms(classified['meeting'] + classified['rooms'])
        data['access'] = self.extract_access_info(classified['access'])
        data['policy'] = self.extract_policy(classified['policy'])
        data['photos'] = self.extract_photos(classified['gallery'])

        # 4. 整合資料
        return self.merge_data(data)
```

---

## 📋 頁面發現策略

### 策略 1：導航列分析

```python
def discover_from_nav(self, page):
    """從導航列發現重要頁面"""

    # 常見導航關鍵字
    nav_keywords = {
        'meeting': ['會議', '宴會', '會議室', 'Meeting', 'Banquet', 'Events', 'MICE'],
        'access': ['交通', '位置', '交通資訊', 'Access', 'Location', 'Traffic', 'Map'],
        'contact': ['聯絡', '聯絡我們', 'Contact', 'Contact Us'],
        'policy': ['規則', '政策', '注意事項', 'Policy', 'Terms', 'Rules'],
        'gallery': ['照片', '圖片', '媒體', 'Gallery', 'Photos', 'Images'],
    }

    nav_links = page.css('nav a::attr(href)').getall()

    discovered = []
    for link in nav_links:
        text = page.css(f'a[href="{link}"]::text').get()
        for page_type, keywords in nav_keywords.items():
            if any(kw in text for kw in keywords):
                discovered.append({
                    'url': self._absolute_url(link, page),
                    'type': page_type,
                    'source': 'navigation'
                })

    return discovered
```

### 策略 2：Footer 連結

```python
def discover_from_footer(self, page):
    """從 Footer 發現頁面"""

    footer_links = page.css('footer a::attr(href)').getall()

    # Footer 通常有：交通、聯絡、法律資訊
    discovered = []
    for link in footer_links:
        url = self._absolute_url(link, page)
        if self._is_relevant_link(url):
            discovered.append({
                'url': url,
                'type': 'unknown',
                'source': 'footer'
            })

    return discovered
```

### 策略 3：URL 模式識別

```python
def discover_by_url_pattern(self, base_url):
    """根據 URL 模式猜測頁面"""

    common_patterns = [
        '/meeting',
        '/meetings',
        '/banquet',
        '/banquets',
        '/events',
        '/mice',
        '/conference',
        '/access',
        '/location',
        '/traffic',
        '/contact',
        '/contact-us',
        '/policy',
        '/terms',
        '/gallery',
        '/photos',
    ]

    discovered = []
    for pattern in common_patterns:
        url = base_url.rstrip('/') + pattern
        if self._url_exists(url):
            discovered.append({
                'url': url,
                'type': 'guessed',
                'source': 'url_pattern'
            })

    return discovered
```

---

## 🏷️ 頁面分類器

```python
class PageClassifier:
    """頁面類型分類器"""

    def classify(self, url, html_content):
        """分類頁面類型"""

        # 特徵提取
        features = {
            'url_keywords': self._extract_url_keywords(url),
            'title': self._get_title(html_content),
            'headings': self._get_headings(html_content),
            'content_keywords': self._extract_content_keywords(html_content),
            'has_table': self._has_capacity_table(html_content),
            'has_images': self._has_many_images(html_content),
        }

        # 規則分類
        if self._is_meeting_page(features):
            return 'meeting'
        elif self._is_room_detail_page(features):
            return 'room_detail'
        elif self._is_access_page(features):
            return 'access'
        elif self._is_contact_page(features):
            return 'contact'
        elif self._is_policy_page(features):
            return 'policy'
        elif self._is_gallery_page(features):
            return 'gallery'
        else:
            return 'other'

    def _is_meeting_page(self, features):
        """判斷是否為會議/宴會頁面"""

        # URL 關鍵字
        url_kws = ['meeting', 'banquet', 'event', 'mice']

        # 內容關鍵字
        content_kws = ['會議室', '宴會廳', '容量', '坪數', '會議']

        # 檢查
        has_url_kw = any(kw in features['url_keywords'] for kw in url_kws)
        has_content_kw = any(kw in features['content_keywords'] for kw in content_kws)

        return has_url_kw or has_content_kw

    def _is_room_detail_page(self, features):
        """判斷是否為會議室詳細頁"""

        # 通常有：尺寸、容量、設備清單、照片

        has_dimensions = any(kw in features['content_keywords']
                            for kw in ['長', '寬', '高', '坪', '平方公尺', 'm'])

        has_capacity = any(kw in features['content_keywords']
                          for kw in ['人', '容量', '席'])

        has_facilities = any(kw in features['content_keywords']
                            for kw in ['投影', '音響', '麥克風', '設備'])

        return has_dimensions and (has_capacity or has_facilities)
```

---

## 📥 資料提取器

### 會議室提取器

```python
class RoomExtractor:
    """會議室資料提取器"""

    def extract_from_meeting_page(self, page):
        """從會議頁面提取會議室列表"""

        rooms = []

        # 策略 1: 從表格提取
        tables = page.css('table')
        for table in tables:
            rooms.extend(self._extract_from_table(table))

        # 策略 2: 從卡片提取
        cards = page.css('.room-card, .meeting-room, .banquet-room')
        for card in cards:
            room = self._extract_from_card(card)
            if room:
                rooms.append(room)

        # 策略 3: 從列表提取
        items = page.css('.room-list-item, .meeting-item')
        for item in items:
            room = self._extract_from_list_item(item)
            if room:
                rooms.append(room)

        return rooms

    def _extract_from_table(self, table):
        """從表格提取會議室"""

        rooms = []

        # 識別容量表格
        headers = table.css('th::text').getall()

        if not self._is_capacity_table(headers):
            return []

        # 解析每一行
        rows = table.css('tr')[1:]  # 跳過標題行
        for row in rows:
            cells = row.css('td')

            room = {
                'name': cells[0].css('::text').get(),
                'floor': self._extract_floor(cells[0].css('::text').get()),
                'area': self._extract_area(cells[1].css('::text').get()),
                'height': self._extract_height(cells[1].css('::text').get()),
                'capacity': {
                    'theater': self._parse_number(cells[2].css('::text').get()),
                    'classroom': self._parse_number(cells[3].css('::text').get()),
                    'banquet': self._parse_number(cells[4].css('::text').get()),
                }
            }

            rooms.append(room)

        return rooms

    def extract_from_room_detail_page(self, page):
        """從會議室詳細頁提取完整資料"""

        room = {}

        # 名稱（通常在 h1）
        room['name'] = page.css('h1::text').get()

        # 尺寸資訊（可能在文字描述中）
        text = ' '.join(page.css('::text').getall())

        # 提取：長 x 寬 x 高
        dimensions = re.search(r'(\d+(?:\.\d+)?)\s*[×x]\s*(\d+(?:\.\d+)?)\s*[×x]\s*(\d+(?:\.\d+)?)\s*[公尺米m]', text)
        if dimensions:
            room['length'] = float(dimensions.group(1))
            room['width'] = float(dimensions.group(2))
            room['height'] = float(dimensions.group(3))

        # 面積
        area = re.search(r'(\d+(?:\.\d+)?)\s*[坪平方公尺㎡㎡sqm]', text)
        if area:
            room['area'] = float(area.group(1))

        # 容量（多種布局）
        capacity_patterns = {
            'theater': r'劇院[式式]\s*[:：]?\s*(\d+)',
            'classroom': r'教室[式式]\s*[:：]?\s*(\d+)',
            'banquet': r'宴會[式式]\s*[:：]?\s*(\d+)',
            'ushape': r'[uU][型型]\s*[:：]?\s*(\d+)',
            'roundtable': r'圓桌\s*[:：]?\s*(\d+)',
        }

        room['capacity'] = {}
        for layout, pattern in capacity_patterns.items():
            match = re.search(pattern, text)
            if match:
                room['capacity'][layout] = int(match.group(1))

        # 設備清單
        facilities = self._extract_facilities(page)
        room['facilities'] = facilities

        # 照片
        images = self._extract_room_images(page)
        room['images'] = images

        # 價格（如果有）
        price_info = self._extract_price(page)
        if price_info:
            room['price'] = price_info

        return room
```

### 交通資訊提取器

```python
class AccessExtractor:
    """交通資訊提取器"""

    def extract(self, page):
        """提取交通資訊"""

        access = {}

        # 捷運資訊
        mrt = self._extract_mrt_info(page)
        if mrt:
            access['mrt'] = mrt

        # 公車資訊
        bus = self._extract_bus_info(page)
        if bus:
            access['bus'] = bus

        # 停車資訊
        parking = self._extract_parking_info(page)
        if parking:
            access['parking'] = parking

        # 地址
        address = self._extract_address(page)
        if address:
            access['address'] = address

        return access

    def _extract_mrt_info(self, page):
        """提取捷運資訊"""

        # 關鍵字：捷運、MRT、站
        text = ' '.join(page.css('::text').getall())

        mrt_patterns = [
            r'捷運.*?([^\s]{2,4}站)',
            r'([^\s]{2,4}站).*?捷運',
            r'MRT.*?([^\s]{2,4}Station)',
        ]

        for pattern in mrt_patterns:
            match = re.search(pattern, text)
            if match:
                return {
                    'station': match.group(1),
                    'walking_time': self._extract_walking_time(text),
                    'exit': self._extract_exit_info(text),
                }

        return None
```

### 使用規則提取器

```python
class PolicyExtractor:
    """使用規則提取器"""

    def extract(self, page):
        """提取使用規則"""

        policy = {}

        # 付款方式
        payment = self._extract_payment_methods(page)
        if payment:
            policy['payment'] = payment

        # 取消政策
        cancellation = self._extract_cancellation_policy(page)
        if cancellation:
            policy['cancellation'] = cancellation

        # 使用限制
        restrictions = self._extract_restrictions(page)
        if restrictions:
            policy['restrictions'] = restrictions

        # 包含項目
        inclusions = self._extract_inclusions(page)
        if inclusions:
            policy['inclusions'] = inclusions

        return policy
```

---

## 🔄 完整工作流程

```python
def scrape_venue_full_site(self, venue_url):
    """完整爬取場地官網"""

    print(f"\n{'='*80}")
    print(f"🔍 開始全站爬取: {venue_url}")
    print(f"{'='*80}\n")

    # 1. 發現階段
    print("📡 階段 1: 發現所有頁面")
    pages = self.discover_all_pages(venue_url)
    print(f"   ✅ 發現 {len(pages)} 個頁面")

    # 2. 分類階段
    print("\n🏷️  階段 2: 分類頁面")
    classified = self.classify_pages(pages)
    for page_type, type_pages in classified.items():
        print(f"   {page_type}: {len(type_pages)} 個頁面")

    # 3. 提取階段
    print("\n📥 階段 3: 提取資料")
    data = {}

    # 基本資訊
    print("   📋 提取基本資訊...")
    data['basic'] = self.extract_basic_info(classified.get('contact', []))

    # 會議室資料
    print("   🚪 提取會議室資料...")
    meeting_pages = classified.get('meeting', []) + classified.get('room_detail', [])
    data['rooms'] = self.extract_rooms_from_pages(meeting_pages)
    print(f"      找到 {len(data['rooms'])} 個會議室")

    # 交通資訊
    print("   🚗 提取交通資訊...")
    data['access'] = self.extract_access(classified.get('access', []))

    # 使用規則
    print("   📜 提取使用規則...")
    data['policy'] = self.extract_policy(classified.get('policy', []))

    # 照片
    print("   🖼️  提取照片...")
    data['photos'] = self.extract_photos(classified.get('gallery', []))

    # 4. 整合階段
    print("\n🔗 階段 4: 整合資料")
    final_data = self.merge_and_validate(data)

    print(f"\n{'='*80}")
    print(f"✅ 爬取完成")
    print(f"   會議室: {len(final_data.get('rooms', []))} 個")
    print(f"   交通資訊: {'✅' if final_data.get('access') else '❌'}")
    print(f"   使用規則: {'✅' if final_data.get('policy') else '❌'}")
    print(f"   照片: {len(final_data.get('photos', []))} 張")
    print(f"{'='*80}\n")

    return final_data
```

---

## 📊 資料格式標準

### 活動大師欄位對應

```json
{
  "id": 1043,
  "name": "台北六福萬怡酒店",
  "url": "https://www.courtyardtaipei.com.tw",

  // 基本資訊
  "address": "台北市南港區忠孝東路七段359號",
  "contactPhone": "02-6615-6565",
  "contactEmail": "service@courtyardtaipei.com",

  // 容量資訊
  "maxCapacityTheater": 250,
  "maxCapacityClassroom": 150,
  "maxCapacityBanquet": 120,

  // 會議室詳細資料
  "rooms": [
    {
      "id": "1043-01",
      "name": "超新星宴會廳",
      "nameEn": "Supernova Ballroom",
      "floor": "7F",

      // 尺寸資訊
      "dimensions": "19.1M x 14.7M x 3M",
      "length": 19.1,
      "width": 14.7,
      "height": 3.0,
      "area": 281,
      "areaUnit": "平方公尺",

      // 容量（多種布局）
      "capacity": {
        "theater": 250,
        "classroom": 150,
        "ushape": 100,
        "roundtable": 120,
        "reception": 180
      },

      // 設備
      "facilities": [
        "投影設備",
        "音響系統",
        "麥克風",
        "舞台",
        "LED燈光"
      ],

      // 照片
      "images": [
        "https://example.com/room1.jpg",
        "https://example.com/room2.jpg"
      ],

      // 價格
      "price": {
        "halfDay": 35000,
        "fullDay": 60000,
        "currency": "TWD"
      }
    }
  ],

  // 交通資訊
  "access": {
    "mrt": {
      "station": "南港展覽館站",
      "line": "板南線、文湖線",
      "exit": "2號出口",
      "walkingTime": "5分鐘"
    },
    "bus": [
      "212", "212直", "270", "518"
    ],
    "parking": {
      "available": true,
      "spaces": 200,
      "fee": "計次收費"
    }
  },

  // 使用規則
  "policy": {
    "payment": ["現金", "信用卡", "轉帳"],
    "cancellation": "活動前14天通知取消",
    "restrictions": [
      "禁止攜帶外食",
      "禁煙"
    ],
    "inclusions": [
      "基本音響設備",
      "麥克風2支",
      "投影設備"
    ]
  },

  // 照片庫
  "photos": [
    {
      "url": "https://example.com/photo1.jpg",
      "type": "exterior",
      "description": "外觀"
    },
    {
      "url": "https://example.com/photo2.jpg",
      "type": "interior",
      "description": "大宴會廳"
    }
  ]
}
```

---

## 🎯 實作優先級

### Phase 1：核心功能（本週）

1. ✅ 頁面發現器
   - 導航列分析
   - URL 模式猜測

2. ✅ 頁面分類器
   - 會議頁面識別
   - 會議室詳細頁識別

3. ✅ 會議室提取器
   - 表格解析
   - 卡片解析

### Phase 2：進階功能（下週）

4. ⏳ 交通資訊提取器
5. ⏳ 使用規則提取器
6. ⏳ 照片提取器

### Phase 3：優化（本月）

7. ⏳ 智能重試機制
8. ⏳ 資料驗證與補全
9. ⏳ 報告生成

---

## 💡 預期效果

### 資料完整度提升

| 項目 | V3 單頁爬取 | V4 全站爬取 | 提升 |
|------|-------------|-------------|------|
| 會議室名稱 | 50% | 95% | +90% |
| 會議室尺寸 | 5% | 80% | +1500% |
| 會議室容量 | 0% | 85% | +∞ |
| 會議室設備 | 0% | 75% | +∞ |
| 交通資訊 | 0% | 70% | +∞ |
| 使用規則 | 0% | 60% | +∞ |
| 會議室照片 | 10% | 80% | +700% |

### 自動化率提升

- **V3**: 26.7% 高信心（但資料不完整）
- **V4**: 預計 60% 高信心且資料完整

---

**這個設計是否符合您的需求？我可以開始實作 V4 全站智能爬蟲。**
