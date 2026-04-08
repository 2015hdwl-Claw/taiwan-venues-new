# 活動大師網站設計規格書
## 三層架構設計 - 台北市場地

**版本**: 1.0  
**日期**: 2026-03-15  
**設計者**: Steve (CMO)  
**實作者**: Jobs (CTO)

---

## 📋 目錄

1. [專案概述](#專案概述)
2. [三層架構設計](#三層架構設計)
3. [頁面結構](#頁面結構)
4. [資料結構](#資料結構)
5. [UI 元件設計](#ui-元件設計)
6. [功能需求](#功能需求)
7. [實作優先順序](#實作優先順序)
8. [技術規格](#技術規格)

---

## 專案概述

### 目標
將現有單層場地列表升級為三層架構，提供更完整的場地和會議室資訊。

### 範圍
- **第一階段**: 僅實作台北市場地（135 個場地）
- **核心功能**: 三層架構 + 會議室資訊顯示
- **暫緩功能**: 比較功能、評價系統、即時時段查詢

### 目標用戶
- 企業活動策劃人員
- 會議室租借需求者
- 活動場地搜尋用戶

---

## 三層架構設計

### 架構概覽

```
第一層：場地搜尋列表
    ↓ 點擊場地卡片
第二層：場地詳情頁（含會議室列表）
    ↓ 點擊會議室卡片
第三層：會議室詳情頁
```

### 用戶旅程

```
用戶進入網站
    → 搜尋/篩選場地（第一層）
    → 瀏覽場地列表
    → 點擊感興趣的場地
    → 查看場地詳情 + 會議室列表（第二層）
    → 點擊特定會議室
    → 查看會議室完整資訊（第三層）
    → 聯絡場地或返回
```

---

## 頁面結構

### 第一層：場地搜尋列表頁（首頁）

**URL**: `/` 或 `/index.html`

#### 頁面布局

```
┌─────────────────────────────────────────┐
│  Logo   活動大師        [關於] [聯絡]   │ ← 頂部導航
├─────────────────────────────────────────┤
│  🏢 找場地，辦活動                       │ ← Hero 區塊
│  [    搜尋場地...    ] [搜尋]           │
├─────────────────────────────────────────┤
│  篩選條件：                              │
│  [地區 ▼] [類型 ▼] [人數 ▼] [預算 ▼]   │ ← 篩選器
├─────────────────────────────────────────┤
│  找到 135 個台北市場地    [網格|列表]   │ ← 結果統計
├─────────────────────────────────────────┤
│  ┌─────┐  ┌─────┐  ┌─────┐            │
│  │ 場地 │  │ 場地 │  │ 場地 │            │ ← 場地卡片
│  │ 卡片 │  │ 卡片 │  │ 卡片 │            │   (網格視圖)
│  └─────┘  └─────┘  └─────┘            │
│  ┌─────┐  ┌─────┐  ┌─────┐            │
│  │ 場地 │  │ 場地 │  │ 場地 │            │
│  └─────┘  └─────┘  └─────┘            │
├─────────────────────────────────────────┤
│  [1] [2] [3] ... [10]                   │ ← 分頁
└─────────────────────────────────────────┘
```

#### 場地卡片設計（網格視圖）

```
┌──────────────────────┐
│  [場地主圖]          │
│  ┌────────────────┐  │
│  │                │  │
│  │   場地照片     │  │
│  │                │  │
│  └────────────────┐  │
├──────────────────────┤
│  台北君悅酒店        │ ← 場地名稱
│  📍 信義區           │ ← 行政區
│  🏨 飯店             │ ← 類型
│  👥 50-500人         │ ← 容量範圍
│  💰 $15,000起        │ ← 價格區間
│  🚪 8間會議室        │ ← 會議室數量
│  ⭐ 4.5 (暫無)       │ ← 評分（暫緩）
│  [查看詳情 →]        │ ← CTA 按鈕
└──────────────────────┘
```

#### 場地卡片設計（列表視圖）

```
┌─────────────────────────────────────────────┐
│ [縮圖]  台北君悅酒店                          │
│         📍 信義區松壽路2號  🏨 飯店           │
│         👥 50-500人  💰 $15,000起             │
│         🚪 8間會議室  ⭐ 4.5                 │
│         [查看詳情 →]                          │
└─────────────────────────────────────────────┘
```

---

### 第二層：場地詳情頁

**URL**: `/venue.html?id={venueId}`

#### 頁面布局

```
┌─────────────────────────────────────────┐
│  [← 返回搜尋]   活動大師                 │ ← 頂部導航
├─────────────────────────────────────────┤
│  台北君悅酒店                            │ ← 場地名稱
│  📍 台北市信義區松壽路2號                │
│  🏨 飯店場地  ⭐ 4.5 (暫無)              │
├─────────────────────────────────────────┤
│  [場地主圖]                              │
│  ┌───────────────────────────────────┐  │
│  │                                   │  │
│  │       場地照片輪播                │  │
│  │                                   │  │
│  └───────────────────────────────────┘  │
│  [1] [2] [3] [4] [5]                    │ ← 圖片導航
├─────────────────────────────────────────┤
│  📋 場地資訊                             │ ← 基本資訊區
│  ├─ 容納人數：50-500人                   │
│  ├─ 價格區間：$15,000 - $80,000         │
│  ├─ 場地類型：飯店                       │
│  ├─ 可用時段：09:00-21:00               │
│  └─ 設備：投影、音響、燈光...           │
├─────────────────────────────────────────┤
│  🚪 會議室列表 (8間)                     │ ← 會議室列表
│  ┌─────────┐  ┌─────────┐             │
│  │ 會議室1 │  │ 會議室2 │             │
│  │ 50人    │  │ 100人   │             │
│  │ $15,000 │  │ $25,000 │             │
│  └─────────┘  └─────────┘             │
│  ┌─────────┐  ┌─────────┐             │
│  │ 會議室3 │  │ 會議室4 │             │
│  │ 200人   │  │ 500人   │             │
│  │ $40,000 │  │ $80,000 │             │
│  └─────────┘  └─────────┘             │
├─────────────────────────────────────────┤
│  📞 聯絡資訊                             │ ← 聯絡區
│  ├─ 聯絡人：場地租借部                   │
│  ├─ 電話：02-2720-1234                  │
│  ├─ Email：venue@hyatt.com             │
│  └─ [聯絡場地] [加入比較]               │
├─────────────────────────────────────────┤
│  📍 交通資訊                             │ ← 地圖區
│  [Google Maps 嵌入]                     │
├─────────────────────────────────────────┤
│  📝 注意事項                             │ ← 注意事項
│  - 需提前7天預約                         │
│  - 提供餐飲服務                          │
│  - 停車位充足                            │
└─────────────────────────────────────────┘
```

#### 會議室卡片設計

```
┌──────────────────────┐
│  [會議室照片]        │
│  ┌────────────────┐  │
│  │                │  │
│  │   會議室照片   │  │
│  │                │  │
│  └────────────────┘  │
├──────────────────────┤
│  君悅廳              │ ← 會議室名稱
│  👥 50-100人         │ ← 容納人數
│  📐 80坪             │ ← 坪數
│  💰 $15,000/天       │ ← 價格
│  🛠️ 投影、音響       │ ← 設備
│  [查看詳情 →]        │ ← CTA 按鈕
└──────────────────────┘
```

---

### 第三層：會議室詳情頁

**URL**: `/room.html?venueId={venueId}&roomId={roomId}`

#### 頁面布局

```
┌─────────────────────────────────────────┐
│  [← 返回場地]   台北君悅酒店             │ ← 頂部導航
├─────────────────────────────────────────┤
│  君悅廳                                  │ ← 會議室名稱
│  📍 台北君悅酒店 3F                      │
├─────────────────────────────────────────┤
│  [會議室主圖]                           │
│  ┌───────────────────────────────────┐  │
│  │                                   │  │
│  │       會議室照片輪播              │  │
│  │                                   │  │
│  └───────────────────────────────────┘  │
├─────────────────────────────────────────┤
│  📊 空間資訊                             │ ← 空間資訊
│  ├─ 坪數：80坪                           │
│  ├─ 挑高：3.5米                          │
│  ├─ 樓層：3樓                            │
│  └─ 窗戶：有自然採光                     │
├─────────────────────────────────────────┤
│  👥 容納人數                             │ ← 容納資訊
│  ├─ 劇院式：100人                        │
│  ├─ 課桌式：80人                         │
│  ├─ U型：50人                            │
│  └─ 圓桌式：60人                         │
├─────────────────────────────────────────┤
│  💰 價格方案                             │ ← 價格區
│  ├─ 半天（4小時）：$10,000              │
│  ├─ 全天（8小時）：$15,000              │
│  └─ 超時每小時：$2,000                  │
├─────────────────────────────────────────┤
│  🛠️ 設備清單                             │ ← 設備區
│  ✅ 投影設備  ✅ 音響系統                │
│  ✅ 無線麥克風  ✅ 白板                  │
│  ✅ WiFi  ✅ 空調                        │
│  ✅ 茶水服務  ✅ 停車位                  │
├─────────────────────────────────────────┤
│  ⏰ 可用時段                             │ ← 時段區
│  ├─ 平日：09:00-21:00                   │
│  └─ 假日：10:00-18:00                   │
├─────────────────────────────────────────┤
│  📝 注意事項                             │ ← 注意事項
│  - 需提前7天預約                         │
│  - 附免費茶水                            │
│  - 可代訂餐盒                            │
├─────────────────────────────────────────┤
│  [聯絡場地] [加入比較] [返回場地]       │ ← 行動區
└─────────────────────────────────────────┘
```

---

## 資料結構

### 擴充後的場地資料結構

```json
{
  "id": 1001,
  "name": "台北君悅酒店",
  "venueType": "飯店",
  "city": "台北市",
  "district": "信義區",
  "address": "台北市信義區松壽路2號",
  "verified": true,
  
  "images": {
    "main": "https://example.com/main.jpg",
    "gallery": [
      "https://example.com/1.jpg",
      "https://example.com/2.jpg"
    ],
    "floorPlan": "https://example.com/floor.jpg"
  },
  
  "contactPerson": "場地租借部",
  "contactPhone": "02-2720-1234",
  "contactEmail": "venue@hyatt.com",
  "url": "https://taipei.grandhyatt.com/",
  
  "availableTimeWeekday": "09:00-21:00",
  "availableTimeWeekend": "10:00-18:00",
  
  "equipment": "投影設備、音響系統、燈光控制",
  
  "capacityRange": {
    "min": 50,
    "max": 500
  },
  
  "priceRange": {
    "minHalfDay": 15000,
    "maxHalfDay": 30000,
    "minFullDay": 25000,
    "maxFullDay": 80000
  },
  
  "roomsCount": 8,
  
  "rooms": [
    {
      "id": "r001",
      "name": "君悅廳",
      "floor": "3F",
      "area": 80,
      "ceiling": 3.5,
      "hasWindow": true,
      
      "capacity": {
        "theater": 100,
        "classroom": 80,
        "ushape": 50,
        "roundtable": 60
      },
      
      "pricing": {
        "halfDay": 10000,
        "fullDay": 15000,
        "overtime": 2000
      },
      
      "images": {
        "main": "https://example.com/room1.jpg",
        "gallery": [
          "https://example.com/room1-1.jpg",
          "https://example.com/room1-2.jpg"
        ]
      },
      
      "equipment": [
        "投影設備",
        "音響系統",
        "無線麥克風",
        "白板",
        "WiFi",
        "空調",
        "茶水服務",
        "停車位"
      ],
      
      "availableTimeWeekday": "09:00-21:00",
      "availableTimeWeekend": "10:00-18:00",
      
      "notes": "需提前7天預約，附免費茶水，可代訂餐盒",
      
      "features": [
        "自然採光",
        "挑高空間",
        "獨立入口"
      ]
    }
  ],
  
  "location": {
    "lat": 25.0340,
    "lng": 121.5645
  },
  
  "parking": {
    "available": true,
    "count": 200,
    "fee": "免費3小時"
  },
  
  "catering": {
    "available": true,
    "options": ["茶點", "餐盒", "自助餐", "桌餐"]
  },
  
  "notes": "需提前7天預約，提供餐飲服務，停車位充足"
}
```

### 資料欄位說明

#### 必填欄位（現有）
- `id`: 場地唯一識別碼
- `name`: 場地名稱
- `venueType`: 場地類型
- `city`: 縣市
- `address`: 完整地址

#### 新增欄位（第二層需要）
- `district`: 行政區
- `capacityRange`: 容納人數範圍
- `priceRange`: 價格區間
- `roomsCount`: 會議室數量
- `rooms`: 會議室列表（第三層需要）
- `location`: 地理座標
- `parking`: 停車資訊
- `catering`: 餐飲服務

#### 會議室欄位（第三層需要）
- `id`: 會議室 ID
- `name`: 會議室名稱
- `floor`: 樓層
- `area`: 坪數
- `capacity`: 各種擺位的容納人數
- `pricing`: 價格方案
- `equipment`: 設備清單（陣列）
- `features`: 特色標籤

---

## UI 元件設計

### 1. 搜尋列元件

```html
<div class="search-bar">
  <input type="text" placeholder="搜尋場地名稱、地址...">
  <button class="search-btn">🔍 搜尋</button>
</div>
```

**樣式**:
- 寬度: 100%（手機）/ 600px（桌面）
- 高度: 48px
- 圓角: 24px
- 陰影: 0 2px 8px rgba(0,0,0,0.1)

### 2. 篩選器元件

```html
<div class="filters">
  <select class="filter-select">
    <option>所有地區</option>
    <option>信義區</option>
    <option>大安區</option>
    ...
  </select>
  
  <select class="filter-select">
    <option>所有類型</option>
    <option>飯店</option>
    <option>會議中心</option>
    ...
  </select>
  
  <select class="filter-select">
    <option>容納人數</option>
    <option>50人以下</option>
    <option>50-100人</option>
    ...
  </select>
  
  <select class="filter-select">
    <option>預算範圍</option>
    <option>$10,000以下</option>
    <option>$10,000-$30,000</option>
    ...
  </select>
</div>
```

**樣式**:
- 手機: 垂直排列
- 桌面: 水平排列
- 每個寬度: 150px

### 3. 場地卡片元件

```html
<div class="venue-card" data-id="1001">
  <div class="card-image">
    <img src="main.jpg" alt="場地名稱">
    <span class="badge">飯店</span>
  </div>
  
  <div class="card-content">
    <h3 class="venue-name">台北君悅酒店</h3>
    <p class="venue-location">📍 信義區</p>
    <p class="venue-type">🏨 飯店</p>
    <p class="venue-capacity">👥 50-500人</p>
    <p class="venue-price">💰 $15,000起</p>
    <p class="venue-rooms">🚪 8間會議室</p>
    
    <button class="btn-primary">查看詳情 →</button>
  </div>
</div>
```

**樣式**:
- 卡片寬度: 280px（網格）
- 圓角: 12px
- 陰影: 0 4px 12px rgba(0,0,0,0.1)
- Hover: 上移 4px + 陰影加深

### 4. 會議室卡片元件

```html
<div class="room-card" data-venue-id="1001" data-room-id="r001">
  <div class="card-image">
    <img src="room.jpg" alt="會議室名稱">
  </div>
  
  <div class="card-content">
    <h4 class="room-name">君悅廳</h4>
    <p class="room-capacity">👥 50-100人</p>
    <p class="room-area">📐 80坪</p>
    <p class="room-price">💰 $15,000/天</p>
    <p class="room-equipment">🛠️ 投影、音響</p>
    
    <button class="btn-secondary">查看詳情 →</button>
  </div>
</div>
```

### 5. 圖片輪播元件

```html
<div class="image-carousel">
  <div class="carousel-main">
    <img src="current.jpg" alt="當前圖片">
    <button class="carousel-prev">❮</button>
    <button class="carousel-next">❯</button>
  </div>
  
  <div class="carousel-dots">
    <span class="dot active"></span>
    <span class="dot"></span>
    <span class="dot"></span>
  </div>
</div>
```

### 6. 價格方案元件

```html
<div class="pricing-card">
  <h4>💰 價格方案</h4>
  
  <div class="price-item">
    <span class="label">半天（4小時）</span>
    <span class="price">$10,000</span>
  </div>
  
  <div class="price-item">
    <span class="label">全天（8小時）</span>
    <span class="price">$15,000</span>
  </div>
  
  <div class="price-item">
    <span class="label">超時每小時</span>
    <span class="price">$2,000</span>
  </div>
</div>
```

---

## 功能需求

### 第一層：場地搜尋列表頁

#### 核心功能
1. **搜尋功能**
   - 關鍵字搜尋（場地名稱、地址）
   - 即時搜尋（輸入時即時過濾）
   - 搜尋結果高亮

2. **篩選功能**
   - 地區篩選（行政區）
   - 類型篩選（飯店、會議中心等）
   - 人數篩選（區間選擇）
   - 預算篩選（區間選擇）
   - 組合篩選（多條件）
   - 篩選清除功能

3. **排序功能**
   - 預設排序（相關性）
   - 價格排序（低到高 / 高到低）
   - 容量排序（小到大 / 大到小）

4. **視圖切換**
   - 網格視圖（預設）
   - 列表視圖
   - 記住用戶偏好

5. **分頁功能**
   - 每頁顯示 12 筆
   - 頁碼導航
   - 上一頁 / 下一頁

#### 資料顯示
- 場地主圖
- 場地名稱
- 行政區
- 場地類型
- 容納人數範圍
- 價格區間
- 會議室數量

### 第二層：場地詳情頁

#### 核心功能
1. **基本資訊顯示**
   - 場地名稱、地址
   - 場地類型
   - 容納人數範圍
   - 價格區間
   - 可用時段
   - 設備清單

2. **圖片輪播**
   - 主圖 + 圖庫
   - 左右切換
   - 指示器點擊

3. **會議室列表**
   - 網格顯示（3列）
   - 每個會議室卡片
   - 點擊進入第三層

4. **聯絡資訊**
   - 聯絡人
   - 電話（可點擊撥打）
   - Email（可點擊發送）
   - 官網連結

5. **地圖顯示**
   - Google Maps 嵌入
   - 標記場地位置

6. **返回導航**
   - 返回搜尋列表
   - 保留之前的搜尋狀態

### 第三層：會議室詳情頁

#### 核心功能
1. **空間資訊**
   - 坪數、挑高、樓層
   - 窗戶 / 自然採光

2. **容納人數**
   - 四種擺位的人數
   - 劇院式、課桌式、U型、圓桌式

3. **價格方案**
   - 半天價格
   - 全天價格
   - 超時費用

4. **設備清單**
   - 圖標 + 文字
   - 分類顯示

5. **可用時段**
   - 平日時段
   - 假日時段

6. **注意事項**
   - 預約規定
   - 服務內容
   - 限制事項

7. **行動按鈕**
   - 聯絡場地
   - 加入比較（暫緩）
   - 返回場地

---

## 實作優先順序

### Phase 1: 基礎架構（第一週）
**目標**: 完成三層架構的基本框架

1. **資料準備**
   - [ ] 擴充 venues.json 結構
   - [ ] 添加會議室資料（至少 3 個場地的會議室）
   - [ ] 添加圖片 URL（先用佔位圖）

2. **頁面結構**
   - [ ] 建立 venue.html（第二層）
   - [ ] 建立 room.html（第三層）
   - [ ] 更新 index.html（第一層）

3. **導航邏輯**
   - [ ] 第一層 → 第二層（帶 venueId）
   - [ ] 第二層 → 第三層（帶 venueId + roomId）
   - [ ] 各層返回功能

### Phase 2: 第一層優化（第二週）
**目標**: 完善場地搜尋列表功能

1. **搜尋功能**
   - [ ] 關鍵字搜尋
   - [ ] 即時過濾

2. **篩選功能**
   - [ ] 地區篩選（台北市行政區）
   - [ ] 類型篩選
   - [ ] 人數篩選
   - [ ] 預算篩選

3. **視圖切換**
   - [ ] 網格 / 列表視圖
   - [ ] 記住偏好

4. **分頁功能**
   - [ ] 實作分頁邏輯
   - [ ] 頁碼導航

### Phase 3: 第二層詳情頁（第三週）
**目標**: 完善場地詳情頁

1. **基本資訊**
   - [ ] 場地資訊顯示
   - [ ] 聯絡資訊

2. **圖片輪播**
   - [ ] 實作輪播功能
   - [ ] 手機滑動支援

3. **會議室列表**
   - [ ] 網格顯示
   - [ ] 卡片設計

4. **地圖整合**
   - [ ] Google Maps 嵌入

### Phase 4: 第三層會議室頁（第四週）
**目標**: 完善會議室詳情頁

1. **空間資訊**
   - [ ] 坪數、挑高、樓層
   - [ ] 容納人數（四種擺位）

2. **價格方案**
   - [ ] 價格顯示
   - [ ] 方案卡片

3. **設備清單**
   - [ ] 圖標設計
   - [ ] 分類顯示

### Phase 5: 優化與測試（第五週）
**目標**: 完善細節與效能

1. **響應式設計**
   - [ ] 手機版優化
   - [ ] 平板版優化
   - [ ] 桌面版優化

2. **效能優化**
   - [ ] 圖片懶加載
   - [ ] 搜尋效能優化

3. **用戶體驗**
   - [ ] Loading 狀態
   - [ ] 錯誤處理
   - [ ] 空狀態設計

---

## 技術規格

### 前端技術
- **框架**: 純 HTML + CSS + JavaScript（無框架）
- **樣式**: CSS Variables + Flexbox + Grid
- **響應式**: Mobile-first，斷點 768px / 1024px

### 資料處理
- **資料來源**: venues.json（靜態檔案）
- **載入方式**: fetch API
- **快取**: Browser cache + LocalStorage（用戶偏好）

### URL 設計
```
第一層: / 或 /index.html
第二層: /venue.html?id=1001
第三層: /room.html?venueId=1001&roomId=r001
```

### SEO 考量
- 每頁有唯一的 title 和 meta description
- 結構化資料（Schema.org）
- 語義化 HTML 標籤

### 效能目標
- First Contentful Paint: < 1.5s
- Time to Interactive: < 3s
- Lighthouse Score: > 90

### 瀏覽器支援
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+
- Mobile Safari iOS 13+
- Chrome Android 80+

---

## 設計規範

### 色彩系統
```css
:root {
  /* 主色調 */
  --primary: #2563eb;
  --primary-dark: #1d4ed8;
  --primary-light: #3b82f6;
  
  /* 輔助色 */
  --secondary: #64748b;
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
  
  /* 灰階 */
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-300: #d1d5db;
  --gray-400: #9ca3af;
  --gray-500: #6b7280;
  --gray-600: #4b5563;
  --gray-700: #374151;
  --gray-800: #1f2937;
  --gray-900: #111827;
  
  /* 背景 */
  --bg-primary: #ffffff;
  --bg-secondary: #f9fafb;
  
  /* 文字 */
  --text-primary: #111827;
  --text-secondary: #6b7280;
}
```

### 字體系統
```css
:root {
  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  
  /* 字體大小 */
  --text-xs: 0.75rem;    /* 12px */
  --text-sm: 0.875rem;   /* 14px */
  --text-base: 1rem;     /* 16px */
  --text-lg: 1.125rem;   /* 18px */
  --text-xl: 1.25rem;    /* 20px */
  --text-2xl: 1.5rem;    /* 24px */
  --text-3xl: 1.875rem;  /* 30px */
  --text-4xl: 2.25rem;   /* 36px */
  
  /* 行高 */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;
}
```

### 間距系統
```css
:root {
  --spacing-1: 0.25rem;  /* 4px */
  --spacing-2: 0.5rem;   /* 8px */
  --spacing-3: 0.75rem;  /* 12px */
  --spacing-4: 1rem;     /* 16px */
  --spacing-5: 1.25rem;  /* 20px */
  --spacing-6: 1.5rem;   /* 24px */
  --spacing-8: 2rem;     /* 32px */
  --spacing-10: 2.5rem;  /* 40px */
  --spacing-12: 3rem;    /* 48px */
  --spacing-16: 4rem;    /* 64px */
}
```

### 圓角系統
```css
:root {
  --radius-sm: 0.25rem;  /* 4px */
  --radius-md: 0.375rem; /* 6px */
  --radius-lg: 0.5rem;   /* 8px */
  --radius-xl: 0.75rem;  /* 12px */
  --radius-2xl: 1rem;    /* 16px */
  --radius-full: 9999px;
}
```

### 陰影系統
```css
:root {
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}
```

---

## 給 Jobs 的實作指南

### 立即開始的任務

#### 1. 資料準備（最優先）
**目標**: 擴充 venues.json，添加會議室資料

**步驟**:
1. 選擇 3-5 個台北市場地作為範例
2. 根據上面的資料結構，添加 `rooms` 陣列
3. 每個場地至少添加 2-3 個會議室
4. 先用佔位圖（Unsplash 或 placeholder.com）

**驗證**:
- JSON 格式正確
- 資料結構符合規格
- 至少 3 個場地有完整的會議室資料

#### 2. 建立第二層頁面
**目標**: 建立 venue.html

**步驟**:
1. 複製 index.html 的基本結構
2. 讀取 URL 參數 `id`
3. 從 venues.json 載入對應場地資料
4. 顯示場地基本資訊
5. 顯示會議室列表（網格）
6. 實作返回按鈕

**驗證**:
- 能正確顯示場地資訊
- 能顯示會議室列表
- 點擊會議室卡片能跳轉（暫時用 console.log）

#### 3. 建立第三層頁面
**目標**: 建立 room.html

**步驟**:
1. 建立新檔案
2. 讀取 URL 參數 `venueId` 和 `roomId`
3. 從 venues.json 找到對應會議室
4. 顯示完整會議室資訊
5. 實作返回場地按鈕

**驗證**:
- 能正確顯示會議室資訊
- 能顯示四種擺位的人數
- 能顯示價格方案
- 能顯示設備清單

#### 4. 更新第一層
**目標**: 讓場地卡片能跳轉到第二層

**步驟**:
1. 更新場地卡片的點擊事件
2. 跳轉到 `venue.html?id={venueId}`
3. 更新場地卡片顯示會議室數量

**驗證**:
- 點擊場地卡片能跳轉
- 第二層能正確顯示

### 技術實作要點

#### URL 參數處理
```javascript
// 取得 URL 參數
function getUrlParams() {
  const params = new URLSearchParams(window.location.search);
  return {
    id: params.get('id'),
    venueId: params.get('venueId'),
    roomId: params.get('roomId')
  };
}
```

#### 資料載入
```javascript
// 載入場地資料
async function loadVenueData() {
  const response = await fetch('venues.json');
  const venues = await response.json();
  return venues;
}

// 根據 ID 找場地
function findVenueById(venues, id) {
  return venues.find(v => v.id === parseInt(id));
}

// 根據 ID 找會議室
function findRoomById(venue, roomId) {
  return venue.rooms.find(r => r.id === roomId);
}
```

#### 圖片輪播（簡易版）
```javascript
let currentImageIndex = 0;

function showImage(index) {
  const images = document.querySelectorAll('.carousel-image');
  images.forEach((img, i) => {
    img.style.display = i === index ? 'block' : 'none';
  });
  updateDots(index);
}

function nextImage() {
  currentImageIndex = (currentImageIndex + 1) % totalImages;
  showImage(currentImageIndex);
}

function prevImage() {
  currentImageIndex = (currentImageIndex - 1 + totalImages) % totalImages;
  showImage(currentImageIndex);
}
```

### 檔案結構（完成後）

```
taiwan-venues-new/
├── index.html          # 第一層：場地搜尋列表
├── venue.html          # 第二層：場地詳情頁
├── room.html           # 第三層：會議室詳情頁
├── style.css           # 共用樣式
├── app.js              # 第一層邏輯
├── venue.js            # 第二層邏輯
├── room.js             # 第三層邏輯
├── venues.json         # 場地資料（已擴充）
├── vercel.json
└── README.md
```

---

## 驗收標準

### Phase 1 完成標準
- [ ] 3 個場地有完整的會議室資料
- [ ] venue.html 能正確顯示場地資訊
- [ ] room.html 能正確顯示會議室資訊
- [ ] 三層之間的導航正常

### Phase 2 完成標準
- [ ] 搜尋功能正常
- [ ] 篩選功能正常
- [ ] 視圖切換正常
- [ ] 分頁功能正常

### Phase 3 完成標準
- [ ] 場地詳情頁完整
- [ ] 圖片輪播正常
- [ ] 會議室列表顯示正常
- [ ] 地圖顯示正常

### Phase 4 完成標準
- [ ] 會議室詳情頁完整
- [ ] 四種擺位人數顯示
- [ ] 價格方案顯示
- [ ] 設備清單顯示

### 最終驗收
- [ ] 所有 135 個台北市場地都有基本資訊
- [ ] 至少 20 個場地有完整的會議室資料
- [ ] 三層架構完整運作
- [ ] 響應式設計完成
- [ ] 效能符合目標
- [ ] 無重大 Bug

---

## 附錄

### A. 台北市行政區列表
```
松山區、信義區、大安區、中山區、中正區、
大同區、萬華區、文山區、南港區、內湖區、
士林區、北投區
```

### B. 場地類型列表
```
飯店、會議中心、展演場地、政府機關、
學校場地、咖啡廳、餐廳、戶外場地、
社區中心、教堂、其他
```

### C. 設備清單範例
```
投影設備、音響系統、無線麥克風、白板、
翻頁板、WiFi、空調、茶水服務、停車位、
舞台、燈光控制、直播設備、錄影設備、
桌椅、講台、投票系統、同步翻譯
```

### D. 參考資源
- [Google Maps Embed API](https://developers.google.com/maps/documentation/embed)
- [Unsplash 佔位圖](https://unsplash.com/)
- [CSS Grid Guide](https://css-tricks.com/snippets/css/complete-guide-grid/)
- [Flexbox Guide](https://css-tricks.com/snippets/css/a-guide-to-flexbox/)

---

## 版本歷程

| 版本 | 日期 | 修改者 | 說明 |
|------|------|--------|------|
| 1.0 | 2026-03-15 | Steve | 初版設計規格書 |

---

**下一步**: Jobs 請根據此規格書開始實作 Phase 1 的任務。如有任何疑問，隨時提出討論。
