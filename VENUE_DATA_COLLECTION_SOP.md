# 活動大師場地資料收集標準作業程序 (SOP)

> **核心原則：正確的資料（源頭驗證）｜豐富的資料（會議室級別詳細）｜及時更新（定期驗證）**

---

## 📋 目錄

- [SOP 目的與範圍](#sop-目的與範圍)
- [核心原則](#核心原則)
- [資料收集流程圖](#資料收集流程圖)
- [第一章：新增場地](#第一章新增場地)
- [第二章：完整更新](#第二章完整更新)
- [第三章：基本更新](#第三章基本更新)
- [第四章：平面圖更新](#第四章平面圖更新)
- [第五章：資料類型標準](#第五章資料類型標準)
- [第六章：驗證機制](#第六章驗證機制)
- [第七章：錯誤處理](#第七章錯誤處理)
- [第八章：變更控制](#第八章變更控制)
- [第九章：常見問題排除](#第九章常見問題排除)
- [第十章：成功案例](#第十章成功案例)
- [檢查清單](#檢查清單)
- [附錄](#附錄)

---

## 🎯 SOP 目的與範圍

### 目的

統一「活動大師」平台場地資料的收集、驗證、更新流程，確保：

- ✅ **資料正確性**：從源頭驗證，避免髒資料進入系統
- ✅ **資料豐富度**：會議室級別的詳細資訊
- ✅ **資料及時性**：定期驗證、及時更新
- ✅ **流程可追溯**：每個步驟都有記錄、可驗證

### 適用範圍

- **場地類型**：
  - 飯店（hotel）
  - 會議中心（conference center）
  - 活動場地（event venue）
  - 咖啡廳（cafe）
  - 共享空間（coworking）
  - 其他類型

- **資料類型**：
  - 基本資訊（名稱、地址、聯絡方式）
  - 會議室資訊（名稱、尺寸、容量、設備）
  - 價格資訊（半日、全日、時段價）
  - 平面圖（PDF 或圖片）
  - 照片（場地、會議室）

- **更新類型**：
  - 新增場地（從零開始）
  - 完整更新（所有資料）
  - 基本更新（部分欄位）
  - 平面圖更新（單一項目）

---

## 💎 核心原則

### 原則 1：源頭驗證

**理念**：資料在源頭就應該正確，不是事後清理

❌ **錯誤做法**：先匯入資料 → 事後清理 → 修補錯誤  
✅ **正確做法**：匯入前完整驗證 → 確認正確 → 才允許進入系統

**優點**：
1. 避免髒資料從源頭杜絕錯誤
2. 節省時間不需要事後清理
3. 提高信任度用戶看到的是高品質資料
4. 降低維護成本減少後續修正工作

### 原則 2：會議室級別詳細

**理念**：每個會議室都要有完整資料，不要給藉口

**必備資料**：
- ✅ 官網真實照片
- ✅ 完整價格（morning/afternoon/evening）
- ✅ 完整尺寸（長x寬x高）
- ✅ 圓桌人數（roundtable_min/max）
- ✅ 柱子資訊
- ✅ 樓層
- ✅ 特色說明

**不接受的藉口**：
| 藉口 | 解決方案 |
|------|----------|
| "官網無法訪問" | 列出具體 URL，用戶可以手動提供 |
| "找不到照片" | 記錄嘗試過的頁面 URL |
| "官網是動態網頁" | 下載 PDF，PDF 一定有資料 |
| "沒有尺寸資訊" | PDF 一定有，認真讀 |

### 原則 3：定期驗證

**理念**：資料會過時，需要定期驗證

**驗證頻率**：
- **A 級場地**（熱門）：每 3 個月
- **B 級場地**（普通）：每 6 個月
- **C 級場地**（冷門）：每 12 個月

**驗證項目**：
- 官網是否仍可訪問
- 聯絡資訊是否正確
- 價格是否更新
- 照片是否有效

---

## 🔄 資料收集流程圖

### 整體流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    場地資料收集流程                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              v
        ┌────────────────────────────────────┐
        │  判斷：新增場地 or 更新場地？        │
        └───────────┬────────────┬───────────┘
                    │            │
         【新增】    │            │  【更新】
                    v            v
    ┌──────────────────┐    ┌──────────────────┐
    │ 第一章：新增場地  │    │ 判斷更新類型      │
    │ - 找官網         │    └──┬────┬────┬──────┘
    │ - 收集基本資訊   │       │    │    │
    │ - 收集會議室資料 │   【完整】│【基本】│【平面圖】
    │ - 驗證並匯入     │       v    v    v
    └──────────────────┘    ┌──┴┐ ┌─┴─┐ ┌┴───┐
                            │第2章│ │第3章│ │第4章│
                            └──┬─┘ └─┬─┘ └┬───┘
                               │     │    │
                               v     v    v
                          ┌────────────────────┐
                          │ 第五章：資料類型標準│
                          │ - 基本資訊標準      │
                          │ - 會議室資訊標準    │
                          │ - 價格資訊標準      │
                          │ - 平面圖標準        │
                          │ - 照片標準          │
                          └─────────┬──────────┘
                                    │
                                    v
                          ┌────────────────────┐
                          │ 第六章：驗證機制    │
                          │ - A/B/C 分級        │
                          │ - 品質評分          │
                          │ - 自動驗證腳本      │
                          └─────────┬──────────┘
                                    │
                                    v
                          ┌────────────────────┐
                          │ 第七章：錯誤處理    │
                          │ - 錯誤分類          │
                          │ - 處理流程          │
                          │ - 通知機制          │
                          └─────────┬──────────┘
                                    │
                                    v
                          ┌────────────────────┐
                          │ 第八章：變更控制    │
                          │ - 資料更新 vs UI    │
                          │ - Commit 規範       │
                          └─────────┬──────────┘
                                    │
                                    v
                          ┌────────────────────┐
                          │ 部署與驗證          │
                          │ - Git commit        │
                          │ - Vercel deploy     │
                          │ - 線上測試          │
                          └────────────────────┘
```

---

## 第一章：新增場地

> **適用場景**：從零開始建立一個新場地的完整資料

### 1.1 找官網

#### Step 1：搜尋官網

```bash
# Google 搜尋
https://www.google.com/search?q=場地名稱+官網

# 確認是官方網站
- 檢查域名是否為官方
- 檢查是否有聯絡資訊
- 檢查是否有會議室資訊
```

#### Step 2：識別頁面類型

**重要**：官網通常有多個頁面，要找對頁面！

| 頁面類型 | URL 特徵 | 用途 |
|---------|---------|------|
| 官網首頁 | `/` | 基本資訊（地址、營業時間） |
| 會議&宴會頁面 | `meeting`, `banquet`, `會議`, `宴會` | **聯絡資訊、報價** |
| 會議室介紹頁面 | `venue`, `space`, `場地` | 會議室詳細資訊、照片 |
| 場地 PDF | `.pdf` | 完整場地資訊、平面圖 |

**驗證規則**：
```python
def verify_meeting_page(url):
    """驗證是否為會議&宴會頁面"""
    
    # 1. 檢查 URL 關鍵字
    meeting_keywords = ['meeting', 'banquet', 'conference', 'event', '會議', '宴會']
    if not any(kw in url.lower() for kw in meeting_keywords):
        return False, "URL 不是會議&宴會頁面"
    
    # 2. 訪問頁面，檢查內容
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 3. 檢查是否包含會議室資訊
    meeting_terms = ['會議', '宴會', '場地', '廳', 'Ballroom', 'Meeting']
    page_text = soup.get_text()
    if not any(term in page_text for term in meeting_terms):
        return False, "頁面不包含會議室資訊"
    
    return True, "這是會議&宴會頁面"
```

#### Step 3：下載 PDF（如果有）

```bash
# 尋找場地 PDF
curl -s "官網會議頁面" | grep -o 'https://[^"]*\.pdf'

# 下載 PDF
curl -o venue_rooms.pdf "PDF URL"
```

**PDF 通常包含**：
- 會議室名稱
- 坪數/平方公尺
- 長x寬x高
- 容納人數（theater/classroom/roundtable）
- 價格（morning/afternoon/evening）
- 平面圖

### 1.2 收集基本資訊

#### 必填欄位（Level 1）

| 欄位 | 說明 | 驗證規則 | 來源頁面 |
|------|------|----------|---------|
| `name` | 場地名稱 | 非空，長度 2-50 字 | 官網首頁 |
| `venueType` | 場地類型 | 必須在預設清單內 | 判斷 |
| `city` | 縣市 | 必須符合台灣縣市格式 | 地址 |
| `address` | 完整地址 | 包含縣市、區、路名、號 | 官網首頁 |
| `contactPhone` | 聯絡電話 | 符合台灣電話格式 | **會議&宴會頁面** |
| `url` | 官網 URL | 有效 URL，可訪問 | 搜尋結果 |

#### 建議填寫（Level 2）

| 欄位 | 說明 | 驗證規則 | 來源頁面 |
|------|------|----------|---------|
| `contactPerson` | 聯絡人 | 非空 | 會議&宴會頁面 |
| `contactEmail` | Email | 符合 Email 格式，**會議專用** | **會議&宴會頁面** |
| `meetingUrl` | 會議頁面 URL | 有效 URL | 會議&宴會頁面 |
| `priceHalfDay` | 半日價格 | 數字，範圍 1000-100000 | PDF 或頁面 |
| `priceFullDay` | 全日價格 | 數字，範圍 1000-200000 | PDF 或頁面 |
| `maxCapacityTheater` | 劇院式容納 | 數字，範圍 10-10000 | PDF 或頁面 |
| `maxCapacityClassroom` | 教室式容納 | 數字，範圍 10-5000 | PDF 或頁面 |

#### 選填欄位（Level 3）

| 欄位 | 說明 | 驗證規則 |
|------|------|----------|
| `equipment` | 設備清單 | 非空字串 |
| `availableTimeWeekday` | 平日可用時段 | 時間格式 HH:MM-HH:MM |
| `availableTimeWeekend` | 假日可用時段 | 時間格式 HH:MM-HH:MM |
| `description` | 場地描述 | 非空字串 |
| `features` | 特色標籤 | 陣列 |

### 1.3 收集會議室資料

#### 會議室必填欄位

| 欄位 | 說明 | 驗證規則 |
|------|------|----------|
| `id` | 會議室 ID | 唯一，格式：場地ID-序號 |
| `name` | 會議室名稱 | 非空 |
| `capacity` | 容納人數 | 物件，包含多種配置 |
| `images.main` | 主照片 | 有效 URL，來自官網 |

#### 會議室建議欄位

| 欄位 | 說明 | 驗證規則 |
|------|------|----------|
| `area` | 坪數 | 數字 |
| `length` | 長度（公尺） | 數字 |
| `width` | 寬度（公尺） | 數字 |
| `height` | 高度（公尺） | 數字 |
| `floor` | 樓層 | 字串或數字 |
| `pillar` | 是否有柱子 | 布林值 |
| `shape` | 形狀 | 長方形、正方形、不規則 |
| `price` | 價格 | 物件，包含時段價格 |

#### 會議室資料結構

```json
{
  "id": "1103-1",
  "name": "春廳",
  "area": 50,
  "length": 10,
  "width": 5,
  "height": 3,
  "floor": "5樓",
  "pillar": false,
  "shape": "長方形",
  "capacity": {
    "theater": 60,
    "classroom": 40,
    "roundtable_min": 4,
    "roundtable_max": 6
  },
  "price": {
    "morning": 15000,
    "afternoon": 15000,
    "evening": 20000
  },
  "images": {
    "main": "https://www.example.com/files/room-a.jpg",
    "gallery": [
      "https://www.example.com/files/room-a-2.jpg"
    ],
    "source": "https://www.example.com/rooms#room-a"
  },
  "equipment": ["投影機", "音響", "麥克風"],
  "description": "採光良好，適合中型會議"
}
```

### 1.4 驗證並匯入

#### Step 1：必填欄位檢查

```bash
# 使用驗證腳本
python3 validate_venue_data.py --check-required <venue_data.json>
```

#### Step 2：格式驗證

```bash
python3 validate_venue_data.py --check-format <venue_data.json>
```

#### Step 3：官網驗證

```bash
python3 validate_venue_data.py --verify-website <venue_data.json>
```

#### Step 4：品質評分

```bash
python3 validate_venue_data.py --quality-score <venue_data.json>
```

#### Step 5：匯入或錯誤處理

**評分為 A 或 B**：
```bash
python3 validate_venue_data.py --import <venue_data.json>
```

**評分為 C**：
```bash
python3 validate_venue_data.py --report-issues <venue_data.json>
```

---

## 第二章：完整更新

> **適用場景**：對一個場地進行全面性的資料更新（通常是飯店）

### 2.1 找官網會議頁面

**不要只看首頁！要找：**
1. 會議&宴會頁面（通常在首頁選單）
2. 會議室照片頁面
3. 場地 PDF 下載連結

**範例（萬豪）**：
- 會議資訊頁：`/websev?cat=page&id=39`
- 會議室照片頁：`/websev?cat=page&subcat=17`
- 場租表 PDF：`/files/page_176778676814ut99b82.pdf`

### 2.2 下載 PDF

```bash
# 下載場租表或場地介紹 PDF
curl -o venue_rooms.pdf "https://www.官網.com/files/xxx.pdf"
```

### 2.3 讀取 PDF 內容

```bash
# 用 PDF skill 讀取
python3 /usr/lib/node_modules/openclaw/skills/pdf-extract/pdf_extract.py "venue_rooms.pdf"
```

**PDF 會包含**：
- 會議室名稱
- 坪數/平方公尺
- 長x寬x高
- 容納人數（theater/classroom/roundtable）
- 價格（morning/afternoon/evening）

### 2.4 提取官網照片

**方法 1：web_fetch**
```bash
curl -s "會議室照片頁面 URL" | grep -o 'https://.*\.jpg'
```

**方法 2：手動記錄**
```
會議室名稱 -> 照片 URL
萬豪廳 -> https://www.xxx.com/files/xxx_l.jpg
```

### 2.5 更新 venues.json

```python
import json

with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 找到飯店
hotel = [v for v in data if v.get('id') == 飯店ID][0]

# 更新每個會議室
for room in hotel['rooms']:
    # 從 PDF 資料更新
    room.update({
        'area': 坪數,
        'length': 長,
        'width': 寬,
        'height': 高,
        'capacity': {
            'theater': 劇院式,
            'classroom': 課桌式,
            'roundtable_min': 圓桌最小,
            'roundtable_max': 圓桌最大
        },
        'price': {
            'morning': 上午價格,
            'afternoon': 下午價格,
            'evening': 晚間價格
        },
        'images': [官網照片URL],
        'photo': 官網照片URL,
        'pillar': 是否有柱子,
        'floor': 樓層,
        'shape': 形狀,
        'description': 特色說明
    })

with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

### 2.6 驗證完整性

```bash
# 檢查每個會議室都有完整資料
python3 -c "
import json
with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

hotel = [v for v in data if v.get('id') == 飯店ID][0]

for room in hotel['rooms']:
    missing = []
    if not room.get('images'): missing.append('照片')
    if not room.get('price'): missing.append('價格')
    if not room.get('length'): missing.append('尺寸')
    if 'roundtable' not in room.get('capacity', {}): missing.append('圓桌')
    
    if missing:
        print(f'{room.get(\"name\")}: 缺少 {missing}')
"
```

### 2.7 同步部署

```bash
git add venues.json
git commit -m "完整更新：飯店名稱（依據官網 PDF）"
git push origin main
vercel --prod --yes
```

---

## 第三章：基本更新

> **適用場景**：更新場地的部分欄位（地址、電話、價格等）

### 3.1 識別需要更新的場地

```bash
# 搜尋特定場地
cd /root/.openclaw/workspace/taiwan-venues-new
grep -n "場地名稱" venues.json
```

### 3.2 從官網收集資料

參考「第一章：1.2 收集基本資訊」

### 3.3 更新 venues.json

```python
import json

# 讀取資料
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# 找到目標場地
venue = next((v for v in venues if v['id'] == 目標ID), None)

# 更新欄位
venue['name'] = '新名稱'
venue['address'] = '新地址'
# ... 更多更新

# 寫回檔案
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)
```

### 3.4 驗證更新

```bash
# 檢查 JSON 格式
python3 -m json.tool venues.json > /dev/null && echo "✅ JSON 格式正確"

# 本地測試
python3 -m http.server 8080
# 開啟瀏覽器訪問 http://localhost:8080
```

### 3.5 提交變更

```bash
git add venues.json
git commit -m "更新: 場地名稱 - 更新內容描述"
git push origin main
```

### 3.6 部署驗證

Vercel 會自動部署，約 1-2 分鐘後：
- 訪問線上網站
- 檢查更新是否正確顯示
- 測試所有相關功能

---

## 第四章：平面圖更新

> **核心原則：一個平面圖，勝過千言萬語**

### 4.1 平面圖來源

#### 來源 1：官網 PDF（最推薦）

**優點**：
- 官方正式資料
- 通常包含所有會議室配置
- 可直接連結（節省空間）

**常見位置**：
- 會議&宴會頁面
- 場地下載專區
- 場租表 PDF

**範例**：
```
台北萬豪酒店：
https://www.taipeimarriott.com.tw/files/page_157062443710javl802.pdf
```

#### 來源 2：官網圖片

**優點**：
- 載入速度快
- 適合行動裝置瀏覽

**缺點**：
- 可能解析度較低
- 需確認版權

**範例**：
```
寒舍艾麗酒店：
https://www.humblehousehotels.com/files/page_1409758643v0w2d3.jpg
```

#### 來源 3：場地直接提供

**情況**：
- 官網沒有平面圖
- 官網平面圖過時
- 場地提供更新版本

**處理方式**：
1. 請場地提供 PDF 或高解析度圖片
2. 上傳到 GitHub repo 的 `floorplans/` 資料夾
3. 使用 GitHub raw URL

**範例**：
```
台北寒舍艾美酒店：
https://raw.githubusercontent.com/2015hdwl-Claw/taiwan-venues-new/main/floorplans/lemeridien_floorplan.pdf
```

### 4.2 儲存位置與優先順序

#### 資料結構

```json
{
  "id": 1103,
  "name": "台北萬豪酒店",
  "floorPlan": "https://www.taipeimarriott.com.tw/files/xxx.pdf",
  "rooms": [
    {
      "id": "1103-1",
      "name": "春廳",
      "floorPlan": null,
      "layoutImage": null
    }
  ]
}
```

#### 儲存位置選擇

**場地層級（推薦）**：
- 使用時機：平面圖包含多個會議室配置
- 欄位：`venue.floorPlan`
- 優點：一次設定，所有會議室共用

**會議室層級（特殊情況）**：
- 使用時機：只有單一會議室的特殊配置圖
- 欄位：`room.floorPlan` 或 `room.layoutImage`

**前端顯示優先順序**：
```javascript
const floorPlanUrl = 
    currentVenue?.floorPlan ||    // 1. 場地的 floorPlan
    room.floorPlan ||              // 2. 會議室的 floorPlan
    room.layoutImage;              // 3. 會議室的 layoutImage
```

### 4.3 更新流程

#### Step 1：確認平面圖來源

```bash
# 1. 訪問官網會議頁面
curl -I "https://www.飯店官網.com/meeting"

# 2. 找到平面圖連結（PDF 或圖片）
# 通常在：
# - 會議&宴會 > 場地介紹
# - 下載專區
# - 場租表 PDF
```

#### Step 2：驗證 URL 可訪問性

```bash
# 檢查 URL 是否有效
curl -I "平面圖 URL"

# 預期回應：
# HTTP/2 200
# Content-Type: application/pdf  (PDF)
# Content-Type: image/jpeg       (圖片)
```

**成功標準**：
- ✅ HTTP 狀態碼 200
- ✅ Content-Type 正確
- ✅ 檔案大小 > 0

#### Step 3：更新 venues.json

```python
import json

# 讀取資料
with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 找到場地
venue_id = 1103  # 替換為實際 ID
for venue in data:
    if venue['id'] == venue_id:
        venue['floorPlan'] = 'https://平面圖URL'
        break

# 寫回檔案
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

#### Step 4：本地測試

```bash
# 1. 啟動本地伺服器
python3 -m http.server 8080

# 2. 開啟瀏覽器測試
# http://localhost:8080/room.html?venueId=1103&roomId=1103-1

# 3. 確認平面圖正確顯示
```

#### Step 5：提交變更

```bash
git add venues.json
git commit -m "feat(floorplan): 新增台北萬豪酒店平面圖"
git push origin main
```

#### Step 6：部署驗證

```bash
# 部署到 Vercel
vercel --prod --yes

# 等待 1-2 分鐘後，測試線上版本
# https://taiwan-venues-new.vercel.app/room.html?venueId=1103&roomId=1103-1
```

---

## 第五章：資料類型標準

### 5.1 基本資訊標準

#### 場地名稱 (name)

**格式**：完整正式名稱

**範例**：
- ✅ 台北萬豪酒店
- ✅ 台北寒舍艾美酒店
- ❌ 萬豪（不完整）
- ❌ 台北萬豪（不完整）

#### 地址 (address)

**格式**：縣市 + 區 + 路名 + 號

**範例**：
- ✅ 台北市信義區松高路18號
- ✅ 台北市中山區中山北路二段96號
- ❌ 台北市信義區（不完整）
- ❌ 松高路18號（缺少縣市區）

#### 聯絡電話 (contactPhone)

**格式**：區碼-電話-分機

**範例**：
- ✅ 02-8502-3899
- ✅ 02-8502-3899#123
- ✅ (02)8502-3899
- ❌ 請洽各分店（非標準格式）

**重要**：必須是**會議專線**，不是飯店總機

#### Email (contactEmail)

**格式**：標準 Email 格式

**範例**：
- ✅ catering@taipeimarriott.com.tw
- ✅ events@hotel.com
- ❌ events.taipei@marriott.com（通用信箱，非會議專用）

**重要**：必須是**會議專用信箱**

### 5.2 會議室資訊標準

#### 容納人數 (capacity)

**完整結構**：
```json
{
  "capacity": {
    "theater": 60,           // 劇院式
    "classroom": 40,         // 教室式
    "roundtable_min": 4,     // 圓桌（最小桌數）
    "roundtable_max": 6      // 圓桌（最大桌數）
  }
}
```

**注意**：
- `roundtable_min` 和 `roundtable_max` 是桌數，不是人數
- 每桌通常 10 人

#### 尺寸資訊

**完整結構**：
```json
{
  "area": 50,      // 坪數
  "length": 10,    // 長度（公尺）
  "width": 5,      // 寬度（公尺）
  "height": 3      // 高度（公尺）
}
```

**換算**：1 坪 ≈ 3.3058 平方公尺

### 5.3 價格資訊標準

#### 價格結構

**場地層級**：
```json
{
  "priceHalfDay": 15000,  // 半日價格
  "priceFullDay": 25000   // 全日價格
}
```

**會議室層級**（更詳細）：
```json
{
  "price": {
    "morning": 15000,     // 上午場（09:00-12:00）
    "afternoon": 15000,   // 下午場（13:00-17:00）
    "evening": 20000      // 晚間場（18:00-22:00）
  }
}
```

**注意**：
- 價格為整數，不含逗號
- 單位為新台幣

### 5.4 平面圖標準

#### 檔案格式

**支援格式**：
- ✅ PDF（推薦）
- ✅ JPG
- ✅ PNG
- ✅ WebP

**建議**：
- PDF 優先（通常是向量圖，可放大）
- 圖片解析度寬度 >= 800px

#### 儲存位置

**優先順序**：
1. 場地 `floorPlan`（90% 情況）
2. 會議室 `floorPlan`（特殊情況）
3. 會議室 `layoutImage`（很少使用）

### 5.5 照片標準

#### 照片來源規則

1. **首選**：官網的會議室照片
2. **次選**：場地提供的官方照片
3. **避免**：使用通用庫存照片（除非完全沒有官方照片）

#### 照片資料結構

**場地主照片**：
```json
{
  "images": {
    "main": "https://www.example.com/files/main-photo.jpg",
    "gallery": [
      "https://www.example.com/files/gallery-1.jpg",
      "https://www.example.com/files/gallery-2.jpg"
    ],
    "floorPlan": "https://www.example.com/files/floor-plan.jpg",
    "source": "https://www.example.com/venue-page",
    "verified": true,
    "verifiedAt": "2026-03-16T10:00:00.000Z",
    "lastUpdated": "2026-03-16"
  }
}
```

**會議室照片**：
```json
{
  "rooms": [
    {
      "id": "r001",
      "name": "宴會廳A",
      "images": {
        "main": "https://www.example.com/files/room-a.jpg",
        "gallery": [
          "https://www.example.com/files/room-a-2.jpg"
        ],
        "source": "https://www.example.com/rooms#room-a"
      }
    }
  ]
}
```

#### 照片品質要求

- 解析度：寬度 >= 800px
- 檔案大小：100KB - 5MB
- 格式：JPG、PNG、WebP
- 來源：必須記錄 `source` URL

---

## 第六章：驗證機制

### 6.1 品質評分標準

#### A 級：優質資料（90-100 分）

**條件**：
- ✅ 所有必填欄位完整
- ✅ 格式驗證全部通過
- ✅ 官網驗證成功
- ✅ 有主照片和所有會議室照片
- ✅ 價格、容納人數等數值合理

**處理**：可直接匯入

#### B 級：良好資料（70-89 分）

**條件**：
- ✅ 所有必填欄位完整
- ✅ 格式驗證通過
- ⚠️ 官網驗證部分成功
- ⚠️ 部分會議室缺少照片
- ⚠️ 部分選填欄位空白

**處理**：可匯入，需後續補充

#### C 級：待補充資料（<70 分）

**條件**：
- ❌ 缺少必填欄位
- ❌ 格式驗證失敗
- ❌ 官網無法驗證
- ❌ 缺少照片
- ❌ 資訊明顯錯誤

**處理**：不建議匯入，需補充資料

### 6.2 評分計算公式

```python
def calculate_quality_score(venue):
    """計算品質評分"""
    
    score = 0
    max_score = 100
    
    # 1. 必填欄位 (40分)
    required_fields = ['name', 'venueType', 'city', 'address', 'contactPhone', 'url']
    filled_required = sum(1 for f in required_fields if venue.get(f))
    score += (filled_required / len(required_fields)) * 40
    
    # 2. 格式驗證 (20分)
    if validate_phone_format(venue.get('contactPhone', '')):
        score += 10
    if validate_url_format(venue.get('url', '')):
        score += 10
    
    # 3. 官網驗證 (15分)
    if venue.get('verified'):
        score += 15
    
    # 4. 照片完整度 (15分)
    if venue.get('images', {}).get('main'):
        score += 5
    rooms_with_photos = sum(1 for r in venue.get('rooms', []) if r.get('images', {}).get('main'))
    total_rooms = len(venue.get('rooms', []))
    if total_rooms > 0:
        score += (rooms_with_photos / total_rooms) * 10
    
    # 5. 選填欄位 (10分)
    optional_fields = ['priceHalfDay', 'priceFullDay', 'equipment']
    filled_optional = sum(1 for f in optional_fields if venue.get(f))
    score += (filled_optional / len(optional_fields)) * 10
    
    return round(score, 1)
```

### 6.3 自動驗證腳本

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

class VenueDataValidator:
    """場地資料驗證器"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
    
    def validate(self, venue_data):
        """完整驗證流程"""
        
        # 重置記錄
        self.errors = []
        self.warnings = []
        self.info = []
        
        # 1. 必填欄位檢查
        self.check_required_fields(venue_data)
        
        # 2. 格式驗證
        self.check_formats(venue_data)
        
        # 3. 官網驗證
        if venue_data.get('url'):
            self.verify_website(venue_data)
        
        # 4. 照片驗證
        self.check_images(venue_data)
        
        # 5. 計算品質評分
        score = self.calculate_quality_score(venue_data)
        
        # 6. 決定處理方式
        result = {
            'venue': venue_data,
            'errors': self.errors,
            'warnings': self.warnings,
            'info': self.info,
            'qualityScore': score,
            'qualityGrade': self.get_grade(score),
            'canImport': len(self.errors) == 0,
            'status': self.get_status()
        }
        
        return result
    
    def check_required_fields(self, venue):
        """檢查必填欄位"""
        
        required = ['name', 'venueType', 'city', 'address', 'contactPhone', 'url']
        
        for field in required:
            if not venue.get(field):
                self.errors.append(f"缺少必填欄位: {field}")
    
    def check_formats(self, venue):
        """檢查格式"""
        
        # 電話格式
        phone = venue.get('contactPhone', '')
        if phone and not re.match(r'^[\d\-\(\)\s#]+$', phone):
            self.warnings.append(f"電話格式非標準: {phone}")
        
        # URL 格式
        url = venue.get('url', '')
        if url and not url.startswith(('http://', 'https://')):
            self.errors.append(f"URL 格式錯誤: {url}")
        
        # 價格範圍
        if venue.get('priceHalfDay'):
            if not (1000 <= venue['priceHalfDay'] <= 100000):
                self.warnings.append(f"半日價格異常: {venue['priceHalfDay']}")
    
    def verify_website(self, venue):
        """驗證官網"""
        
        try:
            response = requests.get(venue['url'], timeout=10)
            if response.status_code != 200:
                self.warnings.append(f"官網無法訪問: HTTP {response.status_code}")
                return
            
            # 檢查標題是否包含場地名稱
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('title')
            if title and venue['name'] not in title.text:
                self.info.append("場地名稱與官網標題不完全吻合")
            
        except Exception as e:
            self.warnings.append(f"官網連線失敗: {str(e)}")
    
    def check_images(self, venue):
        """檢查照片"""
        
        # 主照片
        if not venue.get('images', {}).get('main'):
            self.warnings.append("缺少場地主照片")
        
        # 會議室照片
        for room in venue.get('rooms', []):
            if not room.get('images', {}).get('main'):
                self.warnings.append(f"會議室 '{room.get('name')}' 缺少照片")
    
    def calculate_quality_score(self, venue):
        """計算品質評分"""
        
        score = 0
        
        # 必填欄位 (40分)
        required = ['name', 'venueType', 'city', 'address', 'contactPhone', 'url']
        filled = sum(1 for f in required if venue.get(f))
        score += (filled / len(required)) * 40
        
        # 格式正確 (20分)
        if len(self.errors) == 0:
            score += 20
        elif len(self.errors) <= 2:
            score += 10
        
        # 官網可訪問 (15分)
        if venue.get('url', '').startswith('http'):
            score += 15
        
        # 照片完整 (15分)
        if venue.get('images', {}).get('main'):
            score += 5
        rooms = venue.get('rooms', [])
        if rooms:
            rooms_with_photos = sum(1 for r in rooms if r.get('images', {}).get('main'))
            score += (rooms_with_photos / len(rooms)) * 10
        
        # 選填欄位 (10分)
        optional = ['priceHalfDay', 'priceFullDay', 'equipment']
        filled_opt = sum(1 for f in optional if venue.get(f))
        score += (filled_opt / len(optional)) * 10
        
        return round(score, 1)
    
    def get_grade(self, score):
        """根據評分取得等級"""
        
        if score >= 90:
            return 'A'
        elif score >= 70:
            return 'B'
        else:
            return 'C'
    
    def get_status(self):
        """決定狀態"""
        
        if len(self.errors) > 0:
            return 'CRITICAL_ERROR'
        elif len(self.warnings) > 0:
            return 'WARNING'
        else:
            return 'OK'
```

---

## 第七章：錯誤處理

### 7.1 錯誤分類

#### 1. 致命錯誤（Critical）

**定義**：無法匯入，必須修正

**範例**：
- 缺少場地名稱
- 缺少地址
- 缺少聯絡電話
- 官網 URL 完全無效

**處理**：
```python
{
  "status": "CRITICAL_ERROR",
  "canImport": False,
  "errors": [
    "缺少必填欄位: name",
    "缺少必填欄位: address"
  ],
  "action": "請補充完整後重新提交"
}
```

#### 2. 警告錯誤（Warning）

**定義**：可以匯入，但品質較低

**範例**：
- 電話格式非標準
- 部分會議室缺照片
- 官網驗證失敗但 URL 有效

**處理**：
```python
{
  "status": "WARNING",
  "canImport": True,
  "warnings": [
    "電話格式非標準: '請洽各分店'",
    "會議室 '包場空間' 使用非官網照片"
  ],
  "qualityGrade": "B",
  "action": "建議補充以提升品質"
}
```

#### 3. 資訊提示（Info）

**定義**：可選優化建議

**範例**：
- 缺少選填欄位
- 照片可使用更高品質版本

**處理**：
```python
{
  "status": "INFO",
  "canImport": True,
  "suggestions": [
    "建議補充設備清單",
    "建議補充半日/全日價格"
  ],
  "qualityGrade": "A",
  "action": "可選優化"
}
```

### 7.2 錯誤處理流程

```python
def handle_validation_result(result):
    """根據驗證結果決定處理方式"""
    
    if result['status'] == 'CRITICAL_ERROR':
        # 1. 記錄錯誤
        log_error(result)
        
        # 2. 發送通知
        send_notification(
            to='data-team@example.com',
            subject=f"資料驗證失敗: {result['venue_name']}",
            body=format_errors(result['errors'])
        )
        
        # 3. 標記為待處理
        save_to_pending_queue(result)
        
        return False
    
    elif result['status'] == 'WARNING':
        # 1. 允許匯入
        import_to_database(result['venue'])
        
        # 2. 標記為需補充
        mark_for_improvement(result['venue']['id'], result['warnings'])
        
        # 3. 記錄品質評分
        update_quality_score(result['venue']['id'], result['qualityGrade'])
        
        return True
    
    else:  # INFO
        # 直接匯入
        import_to_database(result['venue'])
        return True
```

---

## 第八章：變更控制

### 8.1 規則

#### 1. 資料更新（Data Update）

**定義**：只修改 `venues.json` 的內容

**允許的修改**：
- 場地基本資訊（地址、電話、價格）
- 會議室資料（名稱、尺寸、容量、設備）
- 照片 URL（images 陣列）
- 平面圖 URL（floorPlan）
- 驗證狀態（verified, needsUpdate）

**禁止的修改**：
- ❌ 修改任何 `.html` 檔案
- ❌ 修改任何 `.js` 檔案
- ❌ 修改任何 `.css` 檔案
- ❌ 修改頁面呈現邏輯

**Commit 格式**：
```
data: 更新 XXX 場地資料

- 修正地址：XXX
- 更新會議室照片
- 調整價格資訊
```

#### 2. UI 修改（UI Update）

**定義**：修改頁面呈現方式、功能、樣式

**允許的修改**：
- HTML 結構調整
- JavaScript 功能變更
- CSS 樣式更新
- 頁面布局改動

**注意**：
- ⚠️ UI 修改必須明確說明「修改 UI」
- ⚠️ 不要順便改資料

**Commit 格式**：
```
ui: 新增/修改 XXX 功能

- 新增平面圖嵌入顯示
- 調整會議室卡片布局
```

### 8.2 任務分類

| 任務描述 | 正確分類 |
|---------|---------|
| 「檢查 26 個會議室資料」 | ✅ 資料更新 |
| 「更新場地照片」 | ✅ 資料更新 |
| 「修正地址錯誤」 | ✅ 資料更新 |
| 「改善會議室顯示方式」 | ✅ UI 修改 |
| 「新增平面圖功能」 | ✅ UI 修改 |
| 「調整頁面排版」 | ✅ UI 修改 |

### 8.3 檢查清單

在 commit 之前，確認：

- [ ] 這次任務是「資料更新」還是「UI 修改」？
- [ ] 如果是資料更新，只有 `venues.json` 被修改？
- [ ] 如果是 UI 修改，沒有順便改資料？
- [ ] commit message 正確反映了修改類型？

---

## 第九章：常見問題排除

### Q1: 官網 PDF 無法訪問

**症狀**：
```bash
curl -I "https://官網/floorplan.pdf"
# HTTP/2 403 Forbidden
```

**解決方案**：
```bash
# 方案 1：手動下載後上傳到 GitHub
curl -L -o floorplan.pdf "PDF URL"
# 上傳到 floorplans/ 資料夾
git add floorplan.pdf
git commit -m "feat: 新增 XX 飯店平面圖（手動下載）"
git push

# 使用 GitHub raw URL
floorPlan: "https://raw.githubusercontent.com/2015hdwl-Claw/taiwan-venues-new/main/floorplans/xxx.pdf"

# 方案 2：聯繫場地索取 PDF
# 方案 3：截圖官網平面圖並上傳
```

### Q2: PDF 在行動裝置無法顯示

**解決方案**：
```bash
# 方案 1：提供 PDF 下載連結
# （前端需修改顯示邏輯）

# 方案 2：將 PDF 轉為圖片
pdftoppm -png -r 150 floorplan.pdf floorplan
# 上傳 floorplan-1.png

# 方案 3：同時提供 PDF 和圖片
{
  "floorPlan": "floorplan.pdf",
  "floorPlanImage": "floorplan.png"
}
```

### Q3: 官網沒有會議室照片怎麼辦？

**解決方案**：
1. 先確認是否有場地整體照片
2. 如果是分廳，可以使用主廳照片
3. 如果完全沒有，使用通用庫存照片並加註

### Q4: 照片 URL 是相對路徑怎麼辦？

**解決方案**：
```
相對路徑: /files/room.jpg
完整 URL: https://www.example.com/files/room.jpg
```

### Q5: 如何確認照片是否來自官網？

**解決方案**：
1. 檢查 URL domain 是否為官網域名
2. 記錄 `source` 欄位為照片來源頁面
3. 在 `note` 中註明照片類型（官方/庫存）

### Q6: 不確定使用哪個層級的平面圖？

**判斷準則**：

```
是否包含多個會議室？
├─ 是 → 使用場地層級（venue.floorPlan）
└─ 否 → 是否為單一會議室的特殊配置？
         ├─ 是 → 使用會議室層級（room.floorPlan）
         └─ 否 → 使用場地層級（venue.floorPlan）
```

**經驗法則**：
- 90% 的情況使用場地層級
- 只有在平面圖確實只包含單一會議室時，才使用會議室層級

### Q7: 如果真的卡住怎麼辦？

列出：
1. 嘗試了哪些官網 URL（具體連結）
2. 嘗試了哪些 PDF URL（具體連結）
3. 具體卡在哪裡（哪個步驟、哪個欄位）

**不要只說「無法訪問」，要列出 URL！**

---

## 第十章：成功案例

### 案例 1：台北萬豪酒店（完整更新）

**場地資訊**：
- ID：1103
- 會議室數量：26 間
- 樓層：5 樓

**更新過程**：

1. **找到官網會議頁面**
   ```
   https://www.taipeimarriott.com.tw/websev?cat=page&id=39
   ```

2. **定位平面圖 PDF**
   ```
   https://www.taipeimarriott.com.tw/files/page_157062443710javl802.pdf
   ```

3. **下載並讀取 PDF**
   ```bash
   curl -o marriott_rooms.pdf "PDF URL"
   python3 pdf_extract.py "marriott_rooms.pdf"
   ```

4. **提取會議室照片**
   - 從會議室介紹頁面（subcat=17）
   - 每個會議室都有專屬照片

5. **更新 venues.json**
   - 26 個會議室
   - 每個都有官網照片
   - 每個都有完整價格
   - 每個都有尺寸（長x寬x高）
   - 每個都有圓桌人數

6. **驗證與部署**
   ```bash
   git commit -m "完整更新：台北萬豪酒店（依據官網 PDF）"
   git push origin main
   vercel --prod --yes
   ```

**成果**：
- ✅ 所有 26 個會議室都有完整資料
- ✅ 用戶可清楚看到 5 樓的整體配置
- ✅ PDF 可放大查看細節

**執行時間**：約 10 分鐘

### 案例 2：台北寒舍艾美酒店（GitHub 託管）

**場地資訊**：
- ID：1097
- 會議室數量：14 間

**問題**：官網 PDF 無法直接連結（403 Forbidden）

**解決方案**：

1. **手動下載 PDF**
   ```bash
   curl -L -o lemeridien_floorplan.pdf "官網 PDF URL"
   ```

2. **上傳到 GitHub**
   ```bash
   mkdir -p floorplans
   mv lemeridien_floorplan.pdf floorplans/
   git add floorplans/lemeridien_floorplan.pdf
   git commit -m "feat: 新增艾美酒店平面圖檔案"
   git push
   ```

3. **使用 GitHub raw URL**
   ```json
   {
     "id": 1097,
     "name": "台北寒舍艾美酒店",
     "floorPlan": "https://raw.githubusercontent.com/2015hdwl-Claw/taiwan-venues-new/main/floorplans/lemeridien_floorplan.pdf"
   }
   ```

**成果**：
- ✅ 繞過官網的防爬蟲機制
- ✅ URL 穩定可靠（GitHub 保證可用）
- ✅ 未來更新方便（直接替換檔案）

**執行時間**：約 10 分鐘

### 案例 3：台北艾麗酒店（官網圖片）

**場地資訊**：
- ID：1098
- 會議室數量：7 間

**特點**：官網提供的是圖片格式

**更新過程**：

1. **找到平面圖圖片**
   ```
   https://www.humblehousehotels.com/files/page_1409758643v0w2d3.jpg
   ```

2. **驗證圖片**
   ```bash
   curl -I "圖片 URL"
   # HTTP/2 200
   # Content-Type: image/jpeg
   ```

3. **直接使用官網 URL**
   ```json
   {
     "id": 1098,
     "name": "台北艾麗酒店",
     "floorPlan": "https://www.humblehousehotels.com/files/page_1409758643v0w2d3.jpg"
   }
   ```

**成果**：
- ✅ 圖片載入速度快
- ✅ 行動裝置友善
- ⚠️ 解析度略低（但可接受）

**執行時間**：約 3 分鐘

---

## ✅ 檢查清單

### 新增場地檢查清單

- [ ] **官網驗證**
  - [ ] 找到官網首頁
  - [ ] 找到會議&宴會頁面
  - [ ] 找到會議室介紹頁面
  - [ ] 下載場地 PDF（如果有）

- [ ] **基本資訊**
  - [ ] 場地名稱完整
  - [ ] 地址完整（縣市+區+路名+號）
  - [ ] 聯絡電話（會議專線）
  - [ ] Email（會議專用）
  - [ ] 官網 URL

- [ ] **會議室資料**
  - [ ] 每個會議室都有 ID
  - [ ] 每個會議室都有名稱
  - [ ] 每個會議室都有照片
  - [ ] 每個會議室都有容納人數
  - [ ] 每個會議室都有尺寸（如可取得）

- [ ] **驗證**
  - [ ] 必填欄位完整
  - [ ] 格式驗證通過
  - [ ] 官網可訪問
  - [ ] 品質評分 >= 70

### 完整更新檢查清單

- [ ] **PDF 取得**
  - [ ] 下載場地 PDF
  - [ ] 讀取 PDF 內容
  - [ ] 提取所有會議室資料

- [ ] **照片更新**
  - [ ] 每個會議室都有官網照片
  - [ ] 照片 URL 可訪問
  - [ ] 記錄照片來源

- [ ] **資料更新**
  - [ ] 更新尺寸（長x寬x高）
  - [ ] 更新容納人數
  - [ ] 更新價格（morning/afternoon/evening）
  - [ ] 更新圓桌人數

- [ ] **驗證**
  - [ ] 每個會議室都有完整資料
  - [ ] 沒有遺漏欄位

### 基本更新檢查清單

- [ ] **資料收集**
  - [ ] 從官網取得最新資訊
  - [ ] 確認資料來源正確

- [ ] **更新執行**
  - [ ] 修改 venues.json
  - [ ] JSON 格式正確

- [ ] **驗證**
  - [ ] 本地測試
  - [ ] 線上驗證

### 平面圖更新檢查清單

- [ ] **來源確認**
  - [ ] 找到官網平面圖 URL
  - [ ] 或下載 PDF 並上傳 GitHub

- [ ] **URL 驗證**
  - [ ] HTTP 狀態碼 200
  - [ ] Content-Type 正確
  - [ ] 檔案大小 > 1KB

- [ ] **更新與測試**
  - [ ] 更新 venues.json
  - [ ] 本地測試
  - [ ] 線上驗證

---

## 📚 附錄

### A. Commit 格式規範

#### 資料更新

```
data: 更新 XXX 場地資料

- 修正地址：XXX
- 更新會議室照片
- 調整價格資訊
```

#### UI 修改

```
ui: 新增/修改 XXX 功能

- 新增平面圖嵌入顯示
- 調整會議室卡片布局
```

#### 平面圖更新

```
feat(floorplan): 新增台北萬豪酒店平面圖

- 來源：官網 PDF
- URL：https://www.taipeimarriott.com.tw/files/xxx.pdf
- 包含：5樓所有會議室配置

驗證：✅ URL 可訪問，檔案大小 2.3MB
```

### B. 驗證指令速查

```bash
# JSON 格式驗證
python3 -m json.tool venues.json > /dev/null && echo "✅ JSON 格式正確"

# URL 可訪問性檢查
curl -I "平面圖 URL"

# 官網驗證
python3 validate_venue_data.py --verify-website <venue_data.json>

# 品質評分
python3 validate_venue_data.py --quality-score <venue_data.json>
```

### C. 常用工具

- **PDF 讀取**：`python3 /usr/lib/node_modules/openclaw/skills/pdf-extract/pdf_extract.py`
- **本地伺服器**：`python3 -m http.server 8080`
- **部署**：`vercel --prod --yes`
- **Git**：`git add venues.json && git commit -m "描述" && git push origin main`

### D. 相關文件

- [DATA_EXTRACTION_SOP.md](./DATA_EXTRACTION_SOP.md) - 資料擷取標準作業程序
- [CHANGE_CONTROL_SOP.md](./CHANGE_CONTROL_SOP.md) - 變更控制
- [VENUE_COMPLETE_UPDATE_SOP.md](./VENUE_COMPLETE_UPDATE_SOP.md) - 完整更新
- [VENUE_UPDATE_SOP.md](./VENUE_UPDATE_SOP.md) - 基本更新
- [VENUE_PLAN_UPDATE_SOP.md](./VENUE_PLAN_UPDATE_SOP.md) - 平面圖更新
- [SOP_IMPROVEMENT_REPORT.md](./SOP_IMPROVEMENT_REPORT.md) - 改進報告

---

## 📝 更新記錄

| 日期 | 版本 | 更新內容 | 更新人 |
|------|------|----------|--------|
| 2026-03-21 | 1.0 | 建立完整的場地資料收集 SOP | Jobs |

---

**維護者**: Jobs (Global CTO)  
**最後更新**: 2026-03-21

---

_建立時間：2026-03-21（整合所有現有 SOP）_
