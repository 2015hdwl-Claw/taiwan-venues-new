# 三個場地爬蟲流程與資料擷取網址

## 1. 台北萬豪酒店 (Marriott Taipei)

**ID**: 1103
**官網**: https://www.taipeimarriott.com.tw/

### 爬蟲流程

#### 階段1：技術檢測
```python
import requests
from bs4 import BeautifulSoup

url = "https://www.taipeimarriott.com.tw/"

# 1. HTTP 狀態碼
response = requests.get(url)
# 預期：200 OK

# 2. Content-Type
print(response.headers.get('Content-Type'))
# 預期：text/html (靜態網頁)

# 3. 網頁類型檢測
soup = BeautifulSoup(response.text, 'html.parser')
scripts = soup.find_all('script')
# 檢查是否有 React/Vue/Angular
# 預期：靜態 HTML + jQuery
```

#### 階段2：深度爬蟲（三級）

**第一級：主頁**
```
URL: https://www.taipeimarriott.com.tw/

尋找連結：
- 會議室/MICE
- 場地租借
- 宴會/會議
```

**第二級：會議室頁面**
```
URL: https://www.taipeimarriott.com.tw/dining/meetings-events/banquet

尋找資料：
1. 會議室名稱列表
2. 會議室詳細連結
3. PDF 連結（場租表、價格表）
```

**第三級：PDF 解析**
```
PDF 連結範例：
- /assets/files/banquet-rate-sheet.pdf
- /assets/files/meeting-room-rates.pdf

使用 pdfplumber 解析：
import pdfplumber

with pdfplumber.open(pdf_path) as pdf:
    tables = page.extract_tables({
        'vertical_strategy': 'text',
        'horizontal_strategy': 'text'
    })
    # 提取：會議室名稱、坪數、容量、價格
```

#### 階段3：資料整合
```python
# 完整 30 欄位結構
room = {
    'id': '1103-01',
    'name': 'Spring 春',
    'nameEn': 'Spring',
    'floor': '3F',  # 需要提取
    'areaPing': 48,  # 從 PDF 提取
    'areaSqm': 158.7,  # ping × 3.3058
    'dimensions': {'length': 15.2, 'width': 10.4, 'height': 3.5},
    'capacity': {
        'theater': 120,
        'banquet': 8,
        'classroom': 60,
        'uShape': None,
        'cocktail': None,
        'roundTable': None
    },
    'price': {
        'weekday': 15000,
        'holiday': 18000,
        'morning': None,
        'afternoon': None,
        'evening': None,
        'fullDay': None,
        'hourly': None
    },
    'equipment': None,
    'source': 'marriott_official_pdf'
}
```

### 資料擷取網址

| 層級 | URL | 資料 |
|------|-----|------|
| 主頁 | https://www.taipeimarriott.com.tw/ | 導航連結 |
| 會議頁 | https://www.taipeimarriott.com.tw/dining/meetings-events | 會議室列表 |
| 價格表 | /assets/files/banquet-rate-sheet.pdf | 完整價格、容量、坪數 |

### 缺漏項目
- 3 個會議室缺少面積（需要從 PDF 提取）
- 2 個會議室缺少容量（需要從 PDF 或詳細頁面提取）

---

## 2. NUZONE 展演空間

**ID**: 1034
**官網**: https://www.nuzone.com.tw/

### 爬蟲流程

#### 階段1：技術檢測
```python
url = "https://www.nuzone.com.tw/"

# 1. 檢測網頁類型
# 預期：Wix 託管（靜態 HTML）

# 2. 檢測資料位置
# Wix 網站通常使用：
# - JSON-LD 結構化資料
# - 靜態 HTML 內嵌資料
```

#### 階段2：深度爬蟲

**第一級：主頁**
```python
# 尋找會議室/展演空間資訊
url = "https://www.nuzone.com.tw/"

soup = BeautifulSoup(response.text, 'html.parser')

# 尋找關鍵字
keywords = ['展演空間', '會議室', '場地租借', '價格']

# Wix 特定選擇器
# data-section 或 section 標籤
```

**第二級：關於我們/場地介紹頁面**
```
可能的 URL：
- /about
- /venue
- /space
- /facility
```

**第三級：聯絡頁面**
```
URL: /contact

尋找：
1. 電話/Email
2. 租金資訊
3. 場地說明
```

#### 階段3：資料整合
```python
# NUZONE 資料結構（簡化版）
room = {
    'id': '1034-01',
    'name': '2F展演空間',
    'floor': '2F',
    'area': 200,  # 坪（需詢問或從平面圖推測）
    'areaUnit': '坪',
    'capacity': 500,  # 劇院式
    'priceHalfDay': 15000,  # 已有
    'priceFullDay': 25000,  # 已有
    'equipment': '專業音響、投影設備、燈光',  # 已有
    'images': [...],  # 已有
    'contact': {
        'phone': '需要詢問',
        'email': '需要詢問'
    }
}
```

### 資料擷取網址

| 層級 | URL | 資料 |
|------|-----|------|
| 主頁 | https://www.nuzone.com.tw/ | 場地概況 |
| 關於頁 | https://www.nuzone.com.tw/about | 場地說明 |
| 聯絡頁 | https://www.nuzone.com.tw/contact | 聯絡資訊 |

### 缺漏項目
- 3 個會議室缺少面積（坪數已存在，需轉換為 ㎡）
- 3 個會議室缺少價格（可能不公開或需詢問）

### 特殊處理
```python
# 坪數轉換為 ㎡
area_ping = room.get('area', 0)
area_sqm = round(area_ping * 3.3058, 1)

room['areaPing'] = area_ping
room['areaSqm'] = area_sqm
room['areaUnit'] = '㎡'
```

---

## 3. 台北怡亨酒店 (Hotel Éclat Taipei)

**ID**: 1082
**官網**: https://www.eclathotels.com/zt/taipei

### 爬蟲流程

#### 階段1：技術檢測
```python
url = "https://www.eclathotels.com/zt/taipei"

# 1. 檢測網頁類型
# 預期：多語言網站 (zh-tw, en)

# 2. 檢測是否有會議室頁面
# 通常在：
# - /meetings
# - /events
# - /banquet
```

#### 階段2：深度爬蟲

**第一級：主頁**
```python
# 尋找會議室連結
soup.select('a[href*="meet"]')
soup.select('a[href*="event"]')
soup.select('a[href*="mice"]')
```

**第二級：會議室頁面**
```
可能的 URL：
- /meetings
- /events
- /zh-tw/meetings
- /banquet

尋找：
1. 會議室名稱（只有 1 個）
2. 容量資訊
3. 面積資訊
4. 價格資訊（通常不公開）
```

**第三級：PDF 或圖片**
```
尋找：
- 場地圖片（可能包含尺寸）
- PDF 宣傳冊
- 聯絡資訊（直接詢問）
```

#### 階段3：資料整合
```python
# 怡亨只有 1 個會議室
room = {
    'id': '1082-01',
    'name': '會議室',
    'nameEn': 'Meeting Room',  # 需提取
    'floor': '?,  # 需提取
    'area': None,  # 可能不公開
    'areaUnit': '㎡',
    'capacity': None,  # 需提取
    'price': {
        'note': '需詢問'  # 高級飯店通常不公開價格
    },
    'equipment': '需要詢問',
    'contact': {
        'phone': '需要提取',
        'email': '需要提取'
    }
}
```

### 資料擷取網址

| 層級 | URL | 資料 |
|------|-----|------|
| 主頁 | https://www.eclathotels.com/zt/taipei | 導航 |
| 會議頁 | https://www.eclathotels.com/zt/taipei/meetings | 會議室資訊 |
| 聯絡頁 | https://www.eclathotels.com/zt/taipei/contact | 聯絡方式 |

### 缺漏項目
- 1 個會議室缺少面積（可能不公開）
- 1 個會議室缺少容量（需要提取）

### 特殊處理
```python
# 高級飯店通常不公開價格
if not room.get('price'):
    room['price'] = {
        'note': '需詢問飯店',
        'contact': True
    }

# 面積可能不公開，需要標記
if not room.get('areaSqm') and not room.get('areaPing'):
    room['areaNote'] = '未公開，需實地測量或詢問'
```

---

## 執行建議

### 優先順序
1. **台北萬豪**（高優先級）：23 會議室，有 PDF 可提取
2. **NUZONE**（中優先級）：3 會議室，坪數需轉換
3. **台北怡亨**（低優先級）：1 會議室，高級飯店資料可能不公開

### 自動化腳本範例
```python
# 自動爬取萬豪
python scrape_marriott.py --url https://www.taipeimarriott.com.tw/ --extract-pdf

# 處理 NUZONE
python scrape_nuzone.py --convert-ping-to-sqm

# 處理怡亨
python scrape_eclat.py --ask-for-missing
```

### 驗證清單
- [ ] 檢查 HTTP 狀態碼 = 200
- [ ] 確認網頁類型（靜態/動態）
- [ ] 尋找 PDF 連結
- [ ] 提取所有會議室名稱
- [ ] 提取面積（坪 → ㎡）
- [ ] 提取容量（6 種類型）
- [ ] 提取價格（或標記「需詢問」）
- [ ] 驗證完整度（30 欄位標準）

---

**最後更新**: 2026-03-26
**優先級**: 高 - 台北萬豪 > NUZONE > 台北怡亨
