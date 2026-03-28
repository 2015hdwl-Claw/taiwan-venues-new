# API架構設計文檔

**用途**: Jobs (CTO) 設計EventMaster API架構
**建立日期**: 2026-04-01
**目標**: W1 Day 2-3完成

---

## 1. API設計原則

### 1.1 核心原則

**API-first, not UI-first**
- 設計目標是AI模型調用，不是人類瀏覽器
- 優化JSON格式，不考慮HTML渲染
- 回應包含AI需要的上下文資訊

**AI-Friendly Design**
- 符合OpenAI function calling標準
- 提供why_recommended欄位讓AI直接用於回應
- 包含hidden_knowledge讓AI提醒用戶注意事項

**Developer Experience (DX)**
- 簡潔直觀的端點設計
- 清晰的錯誤訊息
- 完整的API文檔與範例

### 1.2 RESTful設計原則

- 使用名詞，不是動詞：`/venues` not `/getVenues`
- 使用HTTP動詞：GET、POST、PUT、DELETE
- 版本控制：`/api/v1/`
- 統一錯誤格式

---

## 2. RESTful API端點設計

### 2.1 場地端點

#### GET /api/v1/venues
**描述**：查詢場地列表（支援篩選、分頁、排序）

**查詢參數**：
```json
{
  "city": "台北",           // 城市（可選）
  "capacity_min": 100,     // 最小容量（可選）
  "capacity_max": 500,     // 最大容量（可選）
  "layout": "theater",     // 配置方式：theater|banquet|classroom（可選）
  "amenities": "projector,sound_system",  // 設備（可選，逗號分隔）
  "price_min": 10000,      // 最低價格（可選）
  "price_max": 50000,      // 最高價格（可選）
  "page": 1,              // 頁碼（預設1）
  "limit": 20,            // 每頁數量（預設20，最大100）
  "sort": "capacity_desc"  // 排序：capacity_asc|capacity_desc|price_asc|price_desc（可選）
}
```

**回應範例**：
```json
{
  "success": true,
  "data": {
    "venues": [
      {
        "id": 1086,
        "name": "台北晶華酒店 Regent Taipei",
        "type": "hotel",
        "city": "台北",
        "address": "台北市中山區南京東路三段133號",
        "contact": {
          "phone": "02-2523-8000",
          "email": "banquet@regenttaipei.com"
        },
        "location": {
          "lat": 25.0517,
          "lng": 121.5404
        },
        "summary": {
          "total_rooms": 12,
          "max_capacity": 1200,
          "price_range": "25,000 - 150,000 TWD/day"
        },
        "suitability_score": 0.95,  // 0-1，AI用於排序
        "why_recommended": "適合大型會議與宴會，位於市中心交通便利"  // AI可直接用於回應
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 52,
      "total_pages": 3
    }
  },
  "meta": {
    "request_id": "uuid",
    "timestamp": "2026-04-01T10:00:00Z"
  }
}
```

#### GET /api/v1/venues/{id}
**描述**：取得單一場地詳情

**路徑參數**：
- `id`: 場地ID（整數）

**回應範例**：
```json
{
  "success": true,
  "data": {
    "venue": {
      "id": 1086,
      "name": "台北晶華酒店 Regent Taipei",
      "type": "hotel",
      "city": "台北",
      "address": "台北市中山區南京東路三段133號",
      "contact": {
        "phone": "02-2523-8000",
        "email": "banquet@regenttaipei.com"
      },
      "url": "https://www.regenttaipei.com",
      "description": "台北晶華酒店坐落於繁華的南京東路上...",
      "location": {
        "lat": 25.0517,
        "lng": 121.5404,
        "nearby_mrt": ["南京復興站", "松江南京站"]
      },
      "amenities": {
        "parking": true,
        "wifi": true,
        "projector": true,
        "sound_system": true,
        "catering": "in_house",
        "accessibility": true
      },
      "meeting_rooms": [
        {
          "id": 1,
          "name": "晶華會",
          "dimensions": {
            "length": 20,
            "width": 16.5,
            "height": 3.5,
            "area": 330,
            "floor": 3
          },
          "capacity": {
            "theater": 360,
            "banquet": 280,
            "classroom": 160,
            "reception": 400
          },
          "amenities": ["projector", "sound_system", "wifi", "air_con"],
          "images": {
            "main": "https://cdn.eventmaster.tw/venues/1086/room1.jpg",
            "gallery": ["..."]
          },
          "price": {
            "half_day": 25000,
            "full_day": 45000,
            "currency": "TWD"
          }
        }
      ],
      "hidden_knowledge": {  // AI無法從官網取得的資訊
        "booking_tips": [
          "週末有婚宴需提早3個月預訂",
          "結帳時提及'企業會議'可獲免費升級"
        ],
        "common_pitfalls": [
          "場地高度限制3.5公尺，大型舞台裝置無法進入",
          "週末不得外叫餐飲（飯店內部餐飲獨家合約）"
        ],
        "pro_tips": [
          "訂9:00-17:00時段比8:00-16:00便宜20%",
          "一樓會議室吵雜，建議選三樓以上"
        ],
        "vendor_relationships": {
          "preferred_av": "視通科技（有長期合作折扣）",
          "parking": "地下停車場，會議室可享3小時免費"
        }
      }
    }
  }
}
```

#### GET /api/v1/venues/{id}/rooms
**描述**：取得場地的所有會議室

#### GET /api/v1/venues/{id}/availability
**描述**：取得場地即時可用性

**查詢參數**：
```json
{
  "start_date": "2026-04-15",  // 開始日期（YYYY-MM-DD）
  "end_date": "2026-04-20",    // 結束日期（可選）
  "room_id": 1                 // 會議室ID（可選）
}
```

**回應範例**：
```json
{
  "success": true,
  "data": {
    "availability": [
      {
        "date": "2026-04-15",
        "rooms": [
          {
            "room_id": 1,
            "room_name": "晶華會",
            "morning": "available",
            "afternoon": "booked",
            "full_day": "not_available",
            "price": {
              "half_day": 25000,
              "full_day": 45000,
              "currency": "TWD",
              "discount": "early_bird_20_off"
            }
          }
        ]
      }
    ]
  }
}
```

#### POST /api/v1/venues/search
**描述**：智能搜尋（AI主動理解用戶需求）

**請求範例**：
```json
{
  "query": "我要辦一個像TED的活動",
  "requirements": {
    "style": "ted_talk",        // 活動類型
    "audience_size": 500,        // 預期人數
    "date_range": {
      "start": "2026-05-01",
      "end": "2026-05-31"
    },
    "budget_range": {
      "min": 50000,
      "max": 150000
    },
    "must_have": ["stage", "projector", "sound_system"],
    "city": "台北"
  }
}
```

**回應範例**：
```json
{
  "success": true,
  "data": {
    "venues": [
      {
        "venue": { /* 完整場地資料 */ },
        "match_score": 0.95,
        "match_reasons": [
          "舞台高度適合TED風格",
          "包含專業視聽設備",
          "價格在預算範圍內"
        ],
        "warnings": [
          "週末需提早3個月預訂"
        ]
      }
    ]
  }
}
```

### 2.2 認證端點

#### POST /api/v1/auth/register
**描述**：註冊API key

#### POST /api/v1/auth/verify
**描述**：驗證API key

---

## 3. GraphQL Schema設計

### 3.1 Type定義

```graphql
type Venue {
  id: ID!
  name: String!
  type: VenueType!
  city: String!
  address: String!
  contact: ContactInfo
  location: Location
  meetingRooms: [MeetingRoom!]!
  hiddenKnowledge: HiddenKnowledge
  suitabilityScore(query: VenueQuery): Float
  whyRecommended(query: VenueQuery): String
}

type MeetingRoom {
  id: ID!
  name: String!
  dimensions: Dimensions
  capacity: Capacity
  amenities: [String!]!
  images: Images
  price: Pricing
}

type HiddenKnowledge {
  bookingTips: [String!]!
  commonPitfalls: [String!]!
  proTips: [String!]!
  vendorRelationships: VendorRelationships
}

type Query {
  venues(
    city: String
    capacityMin: Int
    capacityMax: Int
    layout: Layout
    amenities: [String!]
    page: Int
    limit: Int
  ): VenueConnection!

  venue(id: ID!): Venue

  search(query: String!, requirements: SearchRequirements): VenueSearchResult!
}
```

### 3.2 Query範例

```graphql
query GetVenuesInTaipei {
  venues(
    city: "台北"
    capacityMin: 300
    layout: THEATER
    limit: 10
 ) {
    venues {
      id
      name
      meetingRooms {
        name
        capacity {
          theater
          banquet
        }
      }
      hiddenKnowledge {
        bookingTips
        proTips
      }
    }
  }
}
```

---

## 4. 錯誤處理

### 4.1 統一錯誤格式

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": [
      {
        "field": "capacity_min",
        "message": "Must be greater than 0"
      }
    ]
  },
  "meta": {
    "request_id": "uuid",
    "timestamp": "2026-04-01T10:00:00Z"
  }
}
```

### 4.2 HTTP狀態碼

| 狀態碼 | 含義 | 使用情境 |
|--------|------|----------|
| 200 | OK | 請求成功 |
| 400 | Bad Request | 參數錯誤 |
| 401 | Unauthorized | API key無效 |
| 403 | Forbidden | 無權限 |
| 404 | Not Found | 資源不存在 |
| 429 | Too Many Requests | 超過速率限制 |
| 500 | Internal Server Error | 伺服器錯誤 |

---

## 5. API認證機制

### 5.1 API Key

**生成方式**：
- 使用UUID v4
- 前綴：`em_`（EventMaster）
- 總長度：36字符

**範例**：`em_01234567-89ab-cdef-0123-456789abcdef`

**傳遞方式**：
```
Header: X-API-Key: em_01234567-89ab-cdef-0123-456789abcdef
```

### 5.2 速率限制

| 方案 | 限制 | 適用對象 |
|------|------|----------|
| 免費 | 1000次/月 | 早期測試者 |
| 標準 | 10,000次/月 | 付費開發者 |
| 企業 | 無限制 | 企業客戶 |

---

## 6. 快取策略

### 6.1 Redis快取

**場地列表**：快取1小時
```python
cache_key = f"venues:list:{hash(query_params)}"
cache_ttl = 3600  # 1 hour
```

**場地詳情**：快取24小時
```python
cache_key = f"venue:{venue_id}"
cache_ttl = 86400  # 24 hours
```

**即時可用性**：不快取（或快取5分鐘）
```python
cache_key = f"availability:{venue_id}:{date}"
cache_ttl = 300  # 5 minutes
```

### 6.2 CDN快取

**靜態資源**：場地照片、文檔
- CDN: Cloudflare或CloudFront
- TTL: 7天

---

## 7. 監控與日誌

### 7.1 API監控指標

- 回應時間（p50, p95, p99）
- 請求成功率
- 錯誤率
- API調用量

### 7.2 日誌格式

```json
{
  "timestamp": "2026-04-01T10:00:00Z",
  "level": "info",
  "request_id": "uuid",
  "method": "GET",
  "path": "/api/v1/venues",
  "status_code": 200,
  "response_time_ms": 45,
  "user_agent": "OpenAI/1.0",
  "api_key": "em_***"  // 隱藏部分
}
```

---

## 8. 安全性

### 8.1 安全措施

- [ ] API key驗證
- [ ] 速率限制
- [ ] CORS設定
- [ ] SQL注入防護
- [ ] XSS防護
- [ ] HTTPS only
- [ ] 輸入驗證

### 8.2 API Key權限

| 權限 | 說明 |
|------|------|
| `read:venues` | 讀取場地資料 |
| `read:availability` | 讀取可用性 |
| `write:bookings` | 建立預訂（未來功能） |

---

**文檔所有者**: Jobs (CTO)
**建立日期**: 2026-04-01
**完成期限**: W1 Day 3 (2026-04-03)
**審核者**: Jane (CEO)
**下次更新**: W1 Day 4（技術棧決策後）
