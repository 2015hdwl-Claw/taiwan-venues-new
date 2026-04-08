# 完整場地資料模型（補充版）

## 📋 場地級別資料（Venue Level）

### 必備欄位

| 欄位 | 說明 | 範例 | 來源 |
|------|------|------|------|
| **id** | 場地唯一ID | 1001 | 系統生成 |
| **name** | 場地名稱 | "台北君悅酒店" | 官網 |
| **url** | 官網URL | "https://..." | 使用者輸入 |
| **venueType** | 場地類型 | "飯店場地", "展演場地" | 官網 |
| **city** | 城市 | "台北市" | 官網 |
| **address** | 地址 | "台北市信義區..." | 官網 |

### 聯絡資訊（重要）

| 欄位 | 說明 | 範例 | 擷取方法 |
|------|------|------|----------|
| **contactPhone** | 總機電話 | "02-1234-5678" | 正則: `0\d-\d{4}-\d{4}` |
| **phoneExtension** | 分機號碼 | "分機 1234" 或 "#1234" | 正則: `分機\s*(\d+)|#(\d+)` |
| **contactEmail** | Email | "info@example.com" | 正則: `[\w.-]+@[\w.-]+\.\w+` |
| **contactPerson** | 聯絡人 | "張先生（會議部）" | 從「聯絡我們」頁面提取 |
| **contactPersonTitle** | 聯絡人職稱 | "會議部經理" | 伴隨聯絡人資訊 |

### 交通資訊（重要）

| 欄位 | 說明 | 範例 | 擷取方法 |
|------|------|------|----------|
| **accessInfo** | 交通資訊物件 | {mrt, bus, parking, car} | 從「交通資訊」或「位置」頁面 |
| **accessInfo.mrt** | 捷運資訊 | {station, line, exit} | 關鍵字: "捷運", "MRT" |
| **accessInfo.mrt.station** | 捷運站名 | "台北車站" | 提取站名 |
| **accessInfo.mrt.line** | 捷運路線 | "藍線", "紅線" | 提取路線 |
| **accessInfo.mrt.exit** | 出口 | "1號出口" | 提取出口 |
| **accessInfo.bus** | 公車資訊 | ["1", "257", "捷運接駁"] | 關鍵字: "公車" |
| **accessInfo.parking** | 停車資訊 | "有，停車費200/小時" | 關鍵字: "停車" |
| **accessInfo.car** | 開車資訊 | "國道1號...交流道" | 關鍵字: "開車", "國道" |

### 場地規則（重要）

| 欄位 | 說明 | 範例 | 擷取方法 |
|------|------|------|----------|
| **rules** | 租借規則物件 | {catering, smoking, decoration, ...} | 從「租借須知」或「場地規則」頁面 |
| **rules.catering** | 餐飲規定 | "僅限指定餐飲" | 關鍵字: "餐飲", "食物" |
| **rules.smoking** | 吸煙規定 | "全館禁菸" | 關鍵字: "吸菸", "禁菸" |
| **rules.decoration** | 佈置規定 | "不可使用釘子" | 關鍵字: "佈置", "裝潢" |
| **rules.noise** | 噪音規定 | "晚上10點後不可大聲" | 關鍵字: "噪音", "音量" |
| **rules.cleanup** | 清理規定 | "需自行清理" | 關鍵字: "清理", "复原" |
| **rules.deposit** | 押金規定 | "需繳押金10,000元" | 關鍵字: "押金", "保證金" |
| **rules.cancellation** | 取消政策 | "取消需7天前通知" | 關鍵字: "取消", "退費" |
| **rules.terms** | 完整條款文字 | "租借條款：..." | 提取完整段落 |

### 場地平面圖（重要）

| 欄位 | 說明 | 範例 | 擷取方法 |
|------|------|------|----------|
| **floorPlan** | 平面圖物件 | {url, description, floors} | 從「場地導覽」或「平面圖」頁面 |
| **floorPlan.url** | 平面圖URL | "https://.../floorplan.jpg" | 找 `<img>` 或 SVG |
| **floorPlan.description** | 平面圖說明 | "1F: 大廳, 2F: 會議室" | 從圖說或 alt 文字 |
| **floorPlan.floors** | 各樓層資訊 | [{floor, rooms, area}] | 從平面圖文字提取 |
| **floorPlan.hasFloorPlan** | 是否有平面圖 | true | 檢查是否找到平面圖 |

### 圖片與媒體

| 欄位 | 說明 | 範例 | 擷取方法 |
|------|------|------|----------|
| **images** | 場地圖片物件 | {main, gallery, source} | 從各頁面提取 |
| **images.main** | 主圖 | "https://.../main.jpg" | 首頁主要圖片 |
| **images.gallery** | 圖片清單 | ["url1", "url2", ...] | 所有相關圖片 |
| **images.source** | 圖片來源頁面 | "https://.../gallery" | 記錄來源 |

### 營業資訊

| 欄位 | 說明 | 範例 | 擷取方法 |
|------|------|------|----------|
| **availableTimeWeekday** | 平日可用時間 | "09:00-22:00" | 從「營業時間」提取 |
| **availableTimeWeekend** | 假日可用時間 | "09:00-18:00" | 從「營業時間」提取 |
| **priceHalfDay** | 半日價格（場地級） | 15000 | 從「價格」頁面 |
| **priceFullDay** | 全日價格（場地級） | 25000 | 從「價格」頁面 |
| **maxCapacityTheater** | 最大容量（劇院式） | 500 | 從「容量」頁面 |
| **maxCapacityClassroom** | 最大容量（課桌式） | 300 | 從「容量」頁面 |

---

## 📋 會議室級別資料（Room Level）

### 必備欄位

| 欄位 | 說明 | 範例 |
|------|------|------|
| **id** | 會議室ID | "r1001" |
| **name** | 會議室名稱 | "A廳" |
| **floor** | 樓層 | "2樓" |
| **area** | 面積 | 50 |
| **areaUnit** | 面積單位 | "坪" |
| **capacity** | 容量 | 100 |
| **capacityType** | 容量類型 | "劇院式" |
| **equipment** | 設備 | "投影機、音響" |
| **priceHalfDay** | 半日價格 | 15000 |
| **priceFullDay** | 全日價格 | 25000 |
| **images** | 圖片 | {main, source} |

### 進階欄位

| 欄位 | 說明 | 範例 |
|------|------|------|
| **dimensions** | 尺寸 | {length: 10, width: 8, height: 3} |
| **minCapacity** | 最少人數 | 10 |
| **capacityOptions** | 多種容量配置 | [{type: "劇院式", count: 100}, ...] |
| **features** | 特色功能 | "自然光", "隔間" |
| **restrictions** | 使用限制 | "禁菸", "不可攜帶外食" |
| **setupTime** | 佈置時間 | "2小時" |
| **catering** | 餐飲服務 | "提供咖啡茶點" |
| **availability** | 可用時間 | "週一至週五 09:00-22:00" |
| **description** | 描述 | "適合大型演講..." |

---

## 🔄 完整擷取程序（更新版）

### 階段1：場地基本資料（Venue Level）

```
步驟1：抓取首頁
  ├─ 提取：name, city, address, venueType
  ├─ 提取聯絡資訊：contactPhone, phoneExtension, contactEmail
  └─ 提取主圖：images.main

步驟2：抓取「聯絡我們」頁面
  ├─ 提取：contactPerson, contactPersonTitle
  ├─ 提取：contactPhone（更完整）
  ├─ 提取：contactEmail（更完整）
  └─ 提取：contactPhone, phoneExtension

步驟3：抓取「交通資訊」或「位置」頁面
  ├─ 提取：accessInfo.mrt（捷運站、路線、出口）
  ├─ 提取：accessInfo.bus（公車路線）
  ├─ 提取：accessInfo.parking（停車資訊）
  └─ 提取：accessInfo.car（開車資訊）

步驟4：抓取「租借須知」或「場地規則」頁面
  ├─ 提取：rules.catering（餐飲規定）
  ├─ 提取：rules.smoking（吸菸規定）
  ├─ 提取：rules.decoration（佈置規定）
  ├─ 提取：rules.noise（噪音規定）
  ├─ 提取：rules.cleanup（清理規定）
  ├─ 提取：rules.deposit（押金規定）
  ├─ 提取：rules.cancellation（取消政策）
  └─ 提取：rules.terms（完整條款）

步驟5：抓取「場地平面圖」或「場地導覽」頁面
  ├─ 提取：floorPlan.url（平面圖URL）
  ├─ 提取：floorPlan.description（平面圖說明）
  ├─ 提取：floorPlan.floors（各樓層資訊）
  └─ 設定：floorPlan.hasFloorPlan

步驟6：抓取「場地照片」或「相簿」頁面
  ├─ 提取：images.gallery（圖片清單）
  └─ 記錄：images.source
```

### 階段2：會議室資料（Room Level）

```
步驟7：抓取「會議室」或「場地租借」頁面
  ├─ 識別會議室結構（表格/卡片/列表）
  └─ 對每個會議室：
      ├─ 提取：name, floor, area, capacity
      ├─ 提取：capacityType, equipment
      ├─ 提取：priceHalfDay, priceFullDay
      ├─ 提取：dimensions, minCapacity
      ├─ 提取：images
      └─ 提取：description
```

---

## 🔍 擷取方法對照表

### 聯絡資訊

| 官網格式 | 擷取方法 | venues.json 欄位 |
|---------|---------|-----------------|
| `電話：02-1234-5678` | 正則 `0\d-\d{4}-\d{4}` | contactPhone: "02-1234-5678" |
| `電話：02-1234-5678 分機 1234` | 正則 `分機\s*(\d+)` | phoneExtension: "1234" |
| `電話：02-1234-5678 #1234` | 正則 `#(\d+)` | phoneExtension: "1234" |
| `Email：info@example.com` | 正則 `[\w.-]+@[\w.-]+\.\w+` | contactEmail: "info@example.com" |
| `聯絡人：張先生` | 從「聯絡資訊」段落提取 | contactPerson: "張先生" |
| `會議部 李經理` | 伴隨標題提取 | contactPerson: "李經理", contactPersonTitle: "會議部經理" |

### 交通資訊

| 官網格式 | 擷取方法 | venues.json 欄位 |
|---------|---------|-----------------|
| `捷運：台北車站` | 關鍵字「捷運」+站名 | accessInfo.mrt.station: "台北車站" |
| `捷運藍線台北車站` | 關鍵字「捷運」+路線 | accessInfo.mrt.line: "藍線" |
| `1號出口` | 關鍵字「出口」 | accessInfo.mrt.exit: "1號出口" |
| `公車：1, 257, 捷運接駁` | 關鍵字「公車」+數字 | accessInfo.bus: ["1", "257", "捷運接駁"] |
| `停車：有，200/小時` | 關鍵字「停車」 | accessInfo.parking: "有，200/小時" |
| `國道1號台北交流道` | 關鍵字「國道」 | accessInfo.car: "國道1號台北交流道" |

### 場地規則

| 官網格式 | 擷取方法 | venues.json 欄位 |
|---------|---------|-----------------|
| `僅限指定餐飲` | 關鍵字「餐飲」 | rules.catering: "僅限指定餐飲" |
| `全館禁菸` | 關鍵字「禁菸」 | rules.smoking: "全館禁菸" |
| `不可使用釘子` | 關鍵字「佈置」 | rules.decoration: "不可使用釘子" |
| `晚上10點後不可大聲` | 關鍵字「噪音」 | rules.noise: "晚上10點後不可大聲" |
| `需自行清理` | 關鍵字「清理」 | rules.cleanup: "需自行清理" |
| `押金10,000元` | 關鍵字「押金」 | rules.deposit: "10,000元" |
| `取消需7天前通知` | 關鍵字「取消」 | rules.cancellation: "需7天前通知" |

### 場地平面圖

| 官網格式 | 擷取方法 | venues.json 欄位 |
|---------|---------|-----------------|
| `<img src="floorplan.jpg">` | 找 `<img>` + alt文字包含「平面圖」 | floorPlan.url: "https://.../floorplan.jpg" |
| `平面圖：1F大廳、2F會議室` | 從圖說或 alt 提取 | floorPlan.description: "1F大廳、2F會議室" |
| `<svg class="floor-plan">` | 找 `<svg>` 或 `.floor-plan` class | floorPlan.url: "https://.../floor.svg" |
| `2F: A廳(50坪)、B廳(30坪)` | 從平面圖文字提取 | floorPlan.floors: [{floor: "2F", rooms: [...]}, ...] |

---

## 📊 完整資料結構範例

```json
{
  "id": 1001,
  "name": "台北君悅酒店",
  "venueType": "飯店場地",
  "city": "台北市",
  "address": "台北市信義區松壽路2號",
  "url": "https://www.grandhyatttaipei.com/",

  "contactPhone": "02-1234-5678",
  "phoneExtension": "1234",
  "contactEmail": "meeting@grandhyatt.com",
  "contactPerson": "張先生",
  "contactPersonTitle": "會議部經理",

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

  "floorPlan": {
    "url": "https://www.example.com/floorplan.jpg",
    "description": "1F: 大廳, 2F: 會議室A/B/C",
    "floors": [
      {
        "floor": "1F",
        "rooms": ["大廳"],
        "area": 100
      },
      {
        "floor": "2F",
        "rooms": ["會議室A", "會議室B", "會議室C"],
        "area": 200
      }
    ],
    "hasFloorPlan": true
  },

  "images": {
    "main": "https://www.example.com/main.jpg",
    "gallery": [
      "https://www.example.com/photo1.jpg",
      "https://www.example.com/photo2.jpg"
    ],
    "source": "https://www.example.com/gallery"
  },

  "availableTimeWeekday": "09:00-22:00",
  "availableTimeWeekend": "09:00-18:00",
  "priceHalfDay": 15000,
  "priceFullDay": 25000,
  "maxCapacityTheater": 500,
  "maxCapacityClassroom": 300,

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
        "main": "https://www.example.com/banquet.jpg",
        "source": "https://www.example.com/meeting-rooms"
      }
    }
  ],

  "metadata": {
    "roomSource": "https://www.example.com/meeting-rooms",
    "contactSource": "https://www.example.com/contact",
    "accessSource": "https://www.example.com/access",
    "rulesSource": "https://www.example.com/rules",
    "floorPlanSource": "https://www.example.com/floorplan",
    "extractedAt": "2026-03-25T14:00:00",
    "scrapeVersion": "Complete-Venue-Extractor-v1",
    "pagesScraped": ["首頁", "聯絡我們", "交通資訊", "租借須知", "場地平面圖", "會議室"]
  }
}
```

---

**文件版本**: v2.0
**建立日期**: 2026-03-25
**更新**: 補充場地級別的所有欄位
