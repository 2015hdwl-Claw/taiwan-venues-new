---
name: venue_subspace_structure
description: 場地細分（subSpaces）資料結構設計與實作經驗
type: feedback
---

# 場地細分（subSpaces）資料結構設計

**專案**: 維多麗亞酒店場地細分
**日期**: 2026-03-26
**觸發**: 用戶要求「大宴會廳又可以拆分成，全廳，A/B/C區，廊道，戶外庭園，貴賓室」

---

## 為什麼需要 subSpaces 結構？

### 問題：原本的 rooms 結構無法表達場地細分

**原本的資料結構**：
```json
{
  "id": "1122-01",
  "name": "大宴會廳",
  "capacity": {"theater": 500},
  "price": {"morning": 100000}
}
```

**問題**：
- ❌ 無法表達大宴會廳包含 A/B/C 區
- ❌ 無法區分全廳租金和分區租金
- ❌ 無法記錄哪些區域可以組合使用
- ❌ 丟失了細分場地的獨立價格和容量資訊

### 用戶需求

> "維多麗雅酒店的會議室，大宴會廳又可以拆分成，全廳，A/B/C區，廊道，戶外庭園，貴賓室。這樣的拆解才對。"

**關鍵洞察**：
1. **大宴會廳不是單一場地**，而是多個可租用空間的集合
2. **細分場地有獨立價格**：全廳 NT$100,000，A區 NT$30,000
3. **細分場地可以組合**：A + B + C = 全廳
4. **某些空間無獨立價格**：如廊道包含在全廳租金中

---

## 解決方案：subSpaces 結構

### 資料結構設計

```json
{
  "id": "1122-01",
  "name": "大宴會廳",
  "nameEn": "Grand Ballroom",
  "floor": "1F",
  "totalAreaPing": 156,
  "totalAreaSqm": 516,
  "subSpaces": [
    {
      "id": "1122-01-01",
      "name": "全廳",
      "nameEn": "Full Ballroom",
      "areaPing": 156,
      "areaSqm": 516,
      "dimensions": {"length": 29, "width": 18, "height": 8},
      "price": {
        "morning": 100000,
        "afternoon": 100000,
        "evening": 300000,
        "fullDay": 360000,
        "overtime": 35000,
        "overnight": 100000
      },
      "capacity": {
        "theater": 450,
        "banquet": 300,
        "cocktail": 300,
        "classroom": 270
      },
      "combinable": false,
      "source": "PDF 2022: 會議宴席容納場租表"
    },
    {
      "id": "1122-01-02",
      "name": "A區",
      "nameEn": "Area A",
      "areaPing": 37,
      "areaSqm": 123,
      "price": {...},
      "capacity": {...},
      "combinable": true,
      "source": "PDF 2022"
    }
  ]
}
```

### 欄位說明

#### 主場地層級

| 欄位 | 類型 | 說明 | 範例 |
|------|------|------|------|
| `id` | string | 場地唯一識別碼 | "1122-01" |
| `name` | string | 中文名稱 | "大宴會廳" |
| `nameEn` | string | 英文名稱 | "Grand Ballroom" |
| `floor` | string | 樓層 | "1F" |
| `totalAreaPing` | number | 總面積（坪） | 156 |
| `totalAreaSqm` | number | 總面積（平方公尺） | 516 |
| `subSpaces` | array | 細分場地陣列 | [...] |

#### 細分場地層級（subSpaces）

| 欄位 | 類型 | 說明 | 範例 |
|------|------|------|------|
| `id` | string | 細分場地 ID（格式：`主場地ID-序號`） | "1122-01-01" |
| `name` | string | 中文名稱 | "全廳" |
| `nameEn` | string | 英文名稱 | "Full Ballroom" |
| `areaPing` | number | 面積（坪） | 156 |
| `areaSqm` | number | 面積（平方公尺） | 516 |
| `dimensions` | object | 尺寸（長寬高，單位：公尺） | `{"length": 29, "width": 18, "height": 8}` |
| `price` | object/null | 價格物件（如無獨立價格則為 null） | 見下表 |
| `capacity` | object | 容量物件 | 見下表 |
| `combinable` | boolean | 是否可與其他細分場地組合 | true/false |
| `note` | string|null | 備註說明 | "包含在全廳租金中" |
| `source` | string | 資料來源 | "PDF 2022" |

#### 價格物件（price）

| 欄位 | 類型 | 說明 | 範例 |
|------|------|------|------|
| `morning` | number | 上午時段（08:30-12:00 或 13:30-16:30） | 100000 |
| `afternoon` | number | 下午時段 | 100000 |
| `evening` | number | 晚上時段（18:00-22:00） | 300000 |
| `fullDay` | number | 全天時段（08:30-22:00） | 360000 |
| `overtime` | number | 超時計費（每小時） | 35000 |
| `overnight` | number | 夜間佈置（23:00-07:00） | 100000 |

#### 容量物件（capacity）

| 欄位 | 類型 | 說明 | 範例 |
|------|------|------|------|
| `theater` | number | 劇院式 | 450 |
| `banquet` | number | 圓桌（宴會） | 300 |
| `cocktail` | number | 雞尾酒 | 300 |
| `classroom` | number | 教室式 | 270 |
| `uShape` | number | U型 | 30 |

---

## 實作案例：維多麗亞酒店

### 場地結構

**1F 大宴會廳** - 7 個細分場地：
1. **全廳** (156坪, NT$100,000/時段) -不可組合
2. **A區** (37坪, NT$30,000/時段) -可組合
3. **B區** (44坪, NT$30,000/時段) -可組合
4. **C區** (74坪, NT$60,000/時段) -可組合
5. **廊道** (47坪, 無獨立價格) -不可組合
6. **維多麗亞戶外庭園** (123坪, NT$60,000/時段) -不可組合
7. **貴賓室** (3坪, NT$10,000/時段) -不可組合

**3F 維多麗亞廳** - 4 個細分場地：
1. 全廳 (171坪)
2. A區 (50坪)
3. B區 (44坪)
4. C區 (77坪)

**3F 天璳廳** - 6 個細分場地：
1. 全廳 (52坪)
2. N1/Noble Ballroom 1 (17坪)
3. N2/Noble Ballroom 2 (17坪)
4. N3/Noble Ballroom 3 (17坪)
5. 戶外花園 (67坪)
6. 戶外泳池 (67坪)

### 關鍵設計決策

#### 1. combinable 欄位的意義

**combinable = true**：表示該細分場地可以與其他細分場地同時租用並組合
- 例如：A區 + B區 可以組合成更大的會議空間
- 例如：N1 + N2 + N3 可以同時租用

**combinable = false**：表示該細分場地獨立存在，無法組合
- 例如：全廳（已經包含所有區域）
- 例如：廊道（附屬空間，無法單獨租用）
- 例如：戶外庭園（獨立空間，但與室內場地分開）

#### 2. 價格為 null 的處理

**price = null** 表示該細分場地無獨立價格
- 廊道：包含在全廳租金中
- 貴賓室：可能需要另外詢問

**實作建議**：
```python
# 建立價格物件時
if price_str == '-':
    price = None  # 無獨立價格
else:
    price = {
        'morning': clean_price(price_str),
        ...
    }
```

#### 3. ID 命名規則

**格式**：`{場地ID}-{細分序號}`

**範例**：
- 大宴會廳全廳：`1122-01-01`
- 大宴會廳A區：`1122-01-02`
- 維多麗亞廳全廳：`1122-02-01`
- 天璳廳N1：`1122-03-02`

**優點**：
- ID 唯一且易於追溯
- 可以快速識別所屬主場地
- 方便排序和查詢

---

## 如何判斷是否需要 subSpaces？

### 需要建立 subSpaces 的情況

1. **PDF 中有明確的分區價格**
   - 例如：全廳 NT$100,000，A區 NT$30,000
   - 表示可以分開租用

2. **場地名稱包含「區」、「廳」等字詞**
   - 例如：「A區」、「B區」、「N1廳」
   - 通常表示有細分場地

3. **容量資料有不同配置**
   - 例如：全廳 450人，A區 100人，B區 100人
   - 表示可以分開使用

4. **平面圖顯示可移動隔間**
   - 例如：PDF 中有隔間示意圖
   - 表示可以彈性組合

### 不需要建立 subSpaces 的情況

1. **單一會議室**
   - 例如：第一會議室、第二會議室
   - 直接作為獨立 room 即可

2. **無細分資料**
   - PDF 中只有總面積和總價格
   - 沒有分區資訊

3. **不可分割的空間**
   - 例如：小型會議室（< 50 坪）
   - 無隔間設計

---

## 如何從 PDF 提取 subSpaces？

### 步驟 1: 使用 pdfplumber 提取表格

```python
import pdfplumber

with pdfplumber.open('venue.pdf') as pdf:
    page = pdf.pages[0]
    tables = page.extract_tables({
        'vertical_strategy': 'text',
        'horizontal_strategy': 'text'
    })
```

### 步驟 2: 分析表格結構

**關鍵欄位**：
- 樓層：識別主場地
- 廳名：識別細分場地
- 坪/平方：面積資訊
- 價格欄位：判斷是否有獨立價格

### 步驟 3: 建立階層關係

```python
def build_subspaces_hierarchy(table):
    """從表格建立階層關係"""
    venues = []
    current_venue = None

    for row in table:
        floor = row[0]  # 樓層
        name = row[1]   # 廳名

        if floor and name:
            # 新主場地
            current_venue = {
                'floor': floor,
                'name': name,
                'subSpaces': []
            }
            venues.append(current_venue)
        elif name and not floor:
            # 細分場地
            subspace = parse_subspace(row)
            current_venue['subSpaces'].append(subspace)

    return venues
```

### 步驟 4: 解析細分場地

```python
def parse_subspace(row):
    """解析細分場地資料"""
    return {
        'name': row[1],
        'areaPing': float(row[2]) if row[2] else None,
        'areaSqm': float(row[3]) if row[3] else None,
        'price': parse_price(row[7]),
        'capacity': parse_capacity(row[12:17]),
        'combinable': determine_combinable(row)
    }
```

---

## Metadata 更新

### 必須記錄的資訊

```json
{
  "metadata": {
    "lastScrapedAt": "2026-03-26T12:01:55",
    "scrapeVersion": "pdfplumber_v1_subspaces",
    "pdfParser": "pdfplumber",
    "pdfUrl": "https://...pdf",
    "priceSource": "官方 PDF: 會議宴席容納場租表",
    "hasSubSpaces": true,
    "totalRooms": 3,
    "totalSubSpaces": 17,
    "subSpacesDetail": "大宴會廳(7)、維多麗亞廳(4)、天璳廳(6)",
    "priceCoverage": "94%"
  }
}
```

### 關鍵欄位說明

- **hasSubSpaces**: 是否使用 subSpaces 結構（bool）
- **totalRooms**: 主場地數量（int）
- **totalSubSpaces**: 細分場地總數（int）
- **subSpacesDetail**: 細分場地摘要（string）
- **priceCoverage**: 價格覆蓋率（string）

---

## 查詢與使用

### 查詢所有細分場地

```python
import json

with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

victoria = next(v for v in venues if v['id'] == 1122)

for room in victoria['rooms']:
    print(f"{room['name']} - {len(room['subSpaces'])} 個細分場地")
    for subspace in room['subSpaces']:
        print(f"  - {subspace['name']}: NT${subspace['price']['morning']:,}")
```

### 查詢特定細分場地

```python
# 查詢大宴會廳的 A 區
grand_ballroom = next(r for r in victoria['rooms'] if r['id'] == '1122-01')
area_a = next(s for s in grand_ballroom['subSpaces'] if s['id'] == '1122-01-02')

print(f"A區價格: NT${area_a['price']['morning']:,}")
# A區價格: NT$30,000
```

### 統計價格覆蓋率

```python
total_subspaces = sum(len(r.get('subSpaces', [])) for r in victoria['rooms'])
with_price = sum(
    1 for r in victoria['rooms']
    for s in r.get('subSpaces', [])
    if s.get('price')
)

coverage = (with_price / total_subspaces * 100) if total_subspaces else 0
print(f"價格覆蓋率: {coverage:.1f}% ({with_price}/{total_subspaces})")
```

---

## 總結

### ✅ subSpaces 結構優勢

1. **準確表達場地細分**：支援全廳、分區、附屬空間
2. **保留完整價格資訊**：每個細分場地都有獨立價格
3. **支援場地組合**：combinable 欄位標記可組合性
4. **靈活的資料結構**：可以適應不同場地的需求

### 🎯 使用時機

- ✅ **大型宴會廳**：有 A/B/C 區分區
- ✅ **會議中心**：有多個小型會議室
- ✅ **多功能場地**：可以組合或分割使用
- ❌ **小型會議室**：< 50 坪，無隔間設計

### 📝 最佳實踐

1. **使用 pdfplumber 解析 PDF**：準確提取表格資料
2. **建立階層關係**：主場地 → 細分場地
3. **記錄 combinable**：標記哪些細分場地可以組合
4. **更新 metadata**：記錄 subSpaces 相關資訊
5. **驗證資料準確性**：特別是用戶確認的價格

---

**最後更新**: 2026-03-26
**資料結構**: subSpaces
**成效**: 維多麗亞酒店 17 個細分場地，94% 價格覆蓋
