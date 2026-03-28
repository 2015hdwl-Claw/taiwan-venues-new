# 完整會議室擷取流程示範

## 📋 定義：完整的會議室資料

### 必備欄位（核心資料）

```json
{
  "id": "r1001",              // 系統生成，格式: r{場地ID}{序號}
  "name": "A廳",               // 會議室名稱
  "floor": "2樓",              // 樓層
  "area": 50,                  // 面積數值
  "areaUnit": "坪",            // 面積單位
  "capacity": 100,             // 容量（人數）
  "capacityType": "劇院式",    // 容量類型
  "equipment": "投影機、音響、麥克風",  // 設備
  "priceHalfDay": 15000,       // 半日價格
  "priceFullDay": 25000,       // 全日價格
  "images": {                  // 圖片
    "main": "https://...",
    "source": "https://..."
  },
  "description": "...",        // 描述
  "source": "https://...",     // 資料來源URL
  "extractedAt": "2026-03-25T14:00:00"  // 擷取時間
}
```

---

## 🔍 擷取程序：5個步驟

### 步驟1：新增場地

```bash
python venue_discovery_tool.py
```

**輸入範例**：
```json
{
  "name": "台北君悅酒店",
  "url": "https://www.grandhyatttaipei.com/",
  "address": "台北市信義區松壽路2號"
}
```

**結果**：
- 場地新增到 venues.json
- 分配 ID: 1001
- 初始狀態: rooms = []

### 步驟2：執行完整會議室擷取

```bash
python complete_room_extractor.py
```

**程式會自動**：

1. **抓取首頁** → 找到會議室連結
   ```
   https://www.grandhyatttaipei.com/
   ↓
   找到: /meeting-rooms
   ```

2. **抓取會議室頁面** → 識別結構
   ```
   https://www.grandhyatttaipei.com/meeting-rooms
   ↓
   識別為「表格結構」
   找到 5 個會議室區塊
   ```

3. **提取每個會議室的資料**

   **會議室1: 宴會廳**
   ```
   官網原始資料:
   =============
   <div class="room">
     <h3>宴會廳</h3>
     <p>樓層：B1</p>
     <p>面積：200坪</p>
     <p>容量：500人 (劇院式)</p>
     <p>設備：投影機、音響、麥克風</p>
     <p>價格：半日 NT$50,000 / 全日 NT$80,000</p>
     <img src="room-banquet.jpg" />
   </div>

   提取後的結構化資料:
   ===================
   {
     "id": "r1001001",
     "name": "宴會廳",
     "floor": "B1",
     "area": 200,
     "areaUnit": "坪",
     "capacity": 500,
     "capacityType": "劇院式",
     "equipment": "投影機、音響、麥克風",
     "priceHalfDay": 50000,
     "priceFullDay": 80000,
     "images": {
       "main": "https://www.grandhyatttaipei.com/room-banquet.jpg",
       "source": "https://www.grandhyatttaipei.com/meeting-rooms"
     },
     "source": "https://www.grandhyatttaipei.com/meeting-rooms",
     "extractedAt": "2026-03-25T14:00:00"
   }
   ```

   **會議室2: 會議室A**
   ```
   官網原始資料:
   =============
   <div class="room">
     <h3>會議室A</h3>
     <p>容量：30人 (課桌式)</p>
   </div>

   提取後的結構化資料:
   ===================
   {
     "id": "r1001002",
     "name": "會議室A",
     "floor": null,         // 官網未提供
     "area": null,          // 官網未提供
     "capacity": 30,
     "capacityType": "課桌式",
     "equipment": null,     // 官網未提供
     "priceHalfDay": null,  // 官網未提供
     "priceFullDay": null,  // 官網未提供
     "images": null,        // 官網未提供
     "source": "https://www.grandhyatttaipei.com/meeting-rooms",
     "extractedAt": "2026-03-25T14:00:00"
   }
   ```

4. **驗證資料完整性**
   ```
   ✅ 宴會廳: 有 name, capacity, floor, area
   ⚠️  會議室A: 有 name, capacity，缺少 floor, area
   ```

5. **儲存到 venues.json**

### 步驟3：更新 venues.json

```json
{
  "id": 1001,
  "name": "台北君悅酒店",
  "url": "https://www.grandhyatttaipei.com/",
  "rooms": [
    {
      "id": "r1001001",
      "name": "宴會廳",
      "floor": "B1",
      "area": 200,
      "areaUnit": "坪",
      "capacity": 500,
      "capacityType": "劇院式",
      "equipment": "投影機、音響、麥克風",
      "priceHalfDay": 50000,
      "priceFullDay": 80000,
      "images": {
        "main": "https://www.grandhyatttaipei.com/room-banquet.jpg",
        "source": "https://www.grandhyatttaipei.com/meeting-rooms"
      }
    },
    {
      "id": "r1001002",
      "name": "會議室A",
      "capacity": 30,
      "capacityType": "課桌式"
    }
  ],
  "metadata": {
    "roomSource": "https://www.grandhyatttaipei.com/meeting-rooms",
    "roomExtractedAt": "2026-03-25T14:00:00",
    "roomsCount": 2,
    "scrapeConfidence": "high"
  }
}
```

---

## ✅ 驗證步驟

### 檢查清單

- [ ] **完整性**: 官網有5個會議室 → 活動大師有5個
- [ ] **正確性**:
  - [ ] 宴會廳容量500人 ✓
  - [ ] 會議室A容量30人 ✓
  - [ ] 價格正確 ✓
- [ ] **不遺漏**: 每個會議室都有 name
- [ ] **不捏造**: 官網沒有的資料填 null，不猜測

### 比對範例

| 項目 | 官網 | 活動大師 | 結果 |
|------|------|----------|------|
| 會議室數量 | 5 | 5 | ✅ |
| 宴會廳容量 | 500人 | 500人 | ✅ |
| 會議室A樓層 | 無資訊 | null | ✅ |
| 設備 | 投影機、音響 | 投影機、音響、麥克風 | ❌ (多了) |

---

## 🎯 關鍵原則

### 1. 官網有什麼，活動大師有什麼

```
官網列出 5 個會議室
  ↓
活動大師必須有 5 個 rooms
  ↓
不可只有 4 個（少1個）
不可有 6 個（多1個）
```

### 2. 官網沒有的，填 null

```python
# 好的例子
{
  "floor": null,      # 官網沒提到樓層
  "area": null,       # 官網沒提到面積
  "capacity": 100     # 官網有提到容量
}

# 不好的例子
{
  "floor": "2樓",     # 推測的（錯誤！）
  "area": 50,         # 估算的（錯誤！）
  "capacity": 100
}
```

### 3. 資料來源可追蹤

```json
{
  "rooms": [...],
  "metadata": {
    "roomSource": "https://www.example.com/meeting-rooms",
    "roomExtractedAt": "2026-03-25T14:00:00",
    "scrapeVersion": "Complete-Room-Extractor-v1",
    "scrapeConfidence": "high"  // high/medium/low
  }
}
```

---

## 📊 欄位對應表

| 官網常見格式 | 擷取方法 | venues.json 欄位 |
|-------------|---------|-----------------|
| **A廳** | h3 標題 | name: "A廳" |
| **樓層：2樓** | 正則匹配 `(\d+樓|B\d)` | floor: "2樓" |
| **面積：50坪** | 正則匹配 `(\d+)\s*(坪|㎡)` | area: 50, areaUnit: "坪" |
| **容量：100人** | 正則匹配 `(\d+)\s*人` | capacity: 100 |
| **劇院式** | 關鍵字匹配 | capacityType: "劇院式" |
| **半日 NT$15,000** | 正則匹配 `半日.*NT\$?([\d,]+)` | priceHalfDay: 15000 |
| **全日 NT$25,000** | 正則匹配 `全日.*NT\$?([\d,]+)` | priceFullDay: 25000 |
| **投影機、音響** | 關鍵字列表 | equipment: "投影機、音響" |
| **&lt;img src="..."&gt;** | img 標籤 | images: {main: "...", source: "..."} |

---

## 🛠️ 可用工具

### 1. venue_discovery_tool.py
**用途**: 新增場地
```bash
python venue_discovery_tool.py
```

### 2. complete_room_extractor.py
**用途**: 完整擷取會議室資料
```bash
python complete_room_extractor.py
```

### 3. check_rooms_data.py
**用途**: 檢查會議室資料完整性
```bash
python check_rooms_data.py
```

---

## 📝 完整範例：新場地從頭到尾

### 輸入：新場地
```
名稱: 台北文創會議中心
URL: https://www.tcccl.org.tw/
```

### 執行流程

```bash
# 1. 新增場地
python venue_discovery_tool.py
# 輸入名稱和URL
# 結果: 場地 ID 1002 新增到 venues.json

# 2. 擷取會議室
python complete_room_extractor.py
# 自動處理 ID 1002
# 結果: 發現 3 個會議室

# 3. 檢查結果
python check_rooms_data.py
# 結果:
# - 場地 1002: 3 個會議室
# - 會議室1: 大會議室 (200人)
# - 會議室2: 小會議室 (30人)
# - 會議室3: VIP室 (10人)
```

### 最終結果

```json
{
  "id": 1002,
  "name": "台北文創會議中心",
  "url": "https://www.tcccl.org.tw/",
  "rooms": [
    {
      "id": "r1002001",
      "name": "大會議室",
      "capacity": 200,
      "capacityType": "劇院式",
      "floor": "3樓",
      "area": 100,
      "areaUnit": "坪",
      "equipment": "投影機、音響、麥克風",
      "priceHalfDay": 30000,
      "priceFullDay": 50000,
      "source": "https://www.tcccl.org.tw/meeting-rooms"
    },
    {
      "id": "r1002002",
      "name": "小會議室",
      "capacity": 30,
      "capacityType": "課桌式"
    },
    {
      "id": "r1002003",
      "name": "VIP室",
      "capacity": 10,
      "capacityType": "董事會"
    }
  ],
  "metadata": {
    "roomSource": "https://www.tcccl.org.tw/meeting-rooms",
    "roomExtractedAt": "2026-03-25T14:30:00",
    "roomsCount": 3
  }
}
```

---

**文件版本**: v1.0
**建立日期**: 2026-03-25
**適用於**: 所有新場地的會議室資料擷取
