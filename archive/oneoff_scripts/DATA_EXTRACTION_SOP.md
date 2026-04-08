# 資料擷取標準作業程序 (SOP)

> **核心原則：資料在源頭就應該正確，不是事後清理**

---

## 📋 目錄

- [核心理念](#核心理念)
- [資料擷取流程](#資料擷取流程)
- [必填欄位檢查](#必填欄位檢查)
- [自動官網驗證機制](#自動官網驗證機制)
- [品質評分標準](#品質評分標準)
- [錯誤處理流程](#錯誤處理流程)
- [範例程式碼](#範例程式碼)
- [檢查清單](#檢查清單)

---

## 🎯 核心理念

### 為什麼要源頭驗證？

❌ **錯誤做法**：先匯入資料 → 事後清理 → 修補錯誤
✅ **正確做法**：匯入前完整驗證 → 確認正確 → 才允許進入系統

**優點**：
1. **避免髒資料**：從源頭杜絕錯誤
2. **節省時間**：不需要事後清理
3. **提高信任度**：用戶看到的是高品質資料
4. **降低維護成本**：減少後續修正工作

---

## 🔄 資料擷取流程

### 流程圖

```
┌─────────────┐
│ 收集來源資料 │
└──────┬──────┘
       │
       v
┌─────────────────┐
│ 必填欄位檢查    │
│ - name          │
│ - address       │
│ - contactPhone  │
│ - url           │
└──────┬──────────┘
       │
       v
┌─────────────────┐
│ 格式驗證        │
│ - 電話格式      │
│ - URL 格式      │
│ - 價格範圍      │
└──────┬──────────┘
       │
       v
┌─────────────────┐
│ 官網驗證        │
│ - 訪問官網      │
│ - 比對資訊      │
│ - 提取照片      │
└──────┬──────────┘
       │
       v
┌─────────────────┐
│ 品質評分        │
│ - A級：完整     │
│ - B級：部分缺   │
│ - C級：需補充   │
└──────┬──────────┘
       │
       v
┌─────────────────┐
│ 驗證通過？      │
└──┬───────────┬──┘
   │ YES       │ NO
   v           v
┌────────┐  ┌──────────┐
│匯入系統│  │錯誤處理  │
└────────┘  └──────────┘
```

### 步驟 1：收集來源資料

**來源**：
- 官方網站（最可靠）
- 場地提供者直接提供
- 公開資料庫
- 實地訪問

**格式**：
```json
{
  "name": "場地名稱",
  "venueType": "類型",
  "city": "縣市",
  "address": "完整地址",
  "contactPerson": "聯絡人",
  "contactPhone": "電話",
  "contactEmail": "Email",
  "url": "官網",
  "priceHalfDay": 6000,
  "priceFullDay": 10000,
  "maxCapacityTheater": 40,
  "maxCapacityClassroom": 25,
  "availableTimeWeekday": "09:00-18:00",
  "availableTimeWeekend": "10:00-17:00",
  "equipment": "投影機、音響",
  "images": {
    "main": "主照片 URL",
    "gallery": ["照片1", "照片2"]
  },
  "rooms": [
    {
      "name": "會議室名稱",
      "capacity": 30,
      "area": "20坪",
      "price": "5,000",
      "images": {
        "main": "會議室照片 URL"
      }
    }
  ]
}
```

### 步驟 2：必填欄位檢查

使用驗證腳本自動檢查：

```bash
python3 validate_venue_data.py --check-required <venue_data.json>
```

### 步驟 3：格式驗證

```bash
python3 validate_venue_data.py --check-format <venue_data.json>
```

### 步驟 4：官網驗證

```bash
python3 validate_venue_data.py --verify-website <venue_data.json>
```

### 步驟 5：品質評分

```bash
python3 validate_venue_data.py --quality-score <venue_data.json>
```

### 步驟 6：匯入或錯誤處理

**評分為 A 或 B**：
```bash
python3 validate_venue_data.py --import <venue_data.json>
```

**評分為 C**：
```bash
python3 validate_venue_data.py --report-issues <venue_data.json>
```

---

## ✅ 必填欄位檢查

### Level 1：基本資訊（必填）

| 欄位 | 說明 | 驗證規則 |
|------|------|----------|
| `name` | 場地名稱 | 非空，長度 2-50 字 |
| `venueType` | 場地類型 | 必須在預設清單內 |
| `city` | 縣市 | 必須符合台灣縣市格式 |
| `address` | 完整地址 | 包含縣市、區、路名、號 |
| `contactPhone` | 聯絡電話 | 符合台灣電話格式 |
| `url` | 官網 URL | 有效 URL，可訪問 |

### Level 2：營運資訊（建議填寫）

| 欄位 | 說明 | 驗證規則 |
|------|------|----------|
| `contactPerson` | 聯絡人 | 非空 |
| `contactEmail` | Email | 符合 Email 格式 |
| `priceHalfDay` | 半日價格 | 數字，範圍 1000-100000 |
| `priceFullDay` | 全日價格 | 數字，範圍 1000-200000 |
| `maxCapacityTheater` | 劇院式容納 | 數字，範圍 10-10000 |
| `maxCapacityClassroom` | 教室式容納 | 數字，範圍 10-5000 |

### Level 3：設備與照片（選填但重要）

| 欄位 | 說明 | 驗證規則 |
|------|------|----------|
| `equipment` | 設備清單 | 非空字串 |
| `images.main` | 主照片 | 有效 URL，可訪問 |
| `rooms[].images.main` | 會議室照片 | 有效 URL，可訪問 |

### 驗證範例

```python
# Level 1 驗證
required_fields = ['name', 'venueType', 'city', 'address', 'contactPhone', 'url']

for field in required_fields:
    if not venue.get(field):
        errors.append(f"缺少必填欄位: {field}")
```

---

## 🌐 自動官網驗證機制

### 驗證項目

1. **官網可訪問性**
   - URL 是否有效
   - 網站是否可連線
   - 回應時間是否合理

2. **資訊比對**
   - 場地名稱是否一致
   - 地址是否吻合
   - 電話是否正確

3. **照片提取**
   - 自動提取主照片
   - 提取會議室照片
   - 記錄照片來源

### 驗證流程

```python
def verify_from_website(venue_data):
    """從官網驗證資料"""
    
    # 1. 訪問官網
    try:
        response = requests.get(venue_data['url'], timeout=10)
        if response.status_code != 200:
            return False, "官網無法訪問"
    except Exception as e:
        return False, f"官網連線失敗: {str(e)}"
    
    # 2. 提取資訊
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 3. 比對場地名稱
    title = soup.find('title')
    if title and venue_data['name'] not in title.text:
        warnings.append("場地名稱與官網標題不符")
    
    # 4. 提取照片
    images = extract_images(soup, venue_data['url'])
    
    return True, images
```

### 照片驗證規則

```python
def validate_image_url(url, source_url):
    """驗證照片 URL"""
    
    # 1. 檢查 URL 格式
    if not url.startswith(('http://', 'https://')):
        # 嘗試轉換相對路徑
        url = urljoin(source_url, url)
    
    # 2. 檢查是否可訪問
    try:
        response = requests.head(url, timeout=5)
        if response.status_code != 200:
            return False, "照片 URL 無效"
    except:
        return False, "無法訪問照片"
    
    # 3. 檢查檔案類型
    if not any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
        return False, "非支援的圖片格式"
    
    return True, url
```

---

## 📊 品質評分標準

### A 級：優質資料（可直接匯入）

**條件**：
- ✅ 所有必填欄位完整
- ✅ 格式驗證全部通過
- ✅ 官網驗證成功
- ✅ 有主照片和所有會議室照片
- ✅ 價格、容納人數等數值合理

**評分**：90-100 分

**範例**：
```json
{
  "name": "台北艾麗酒店",
  "venueType": "飯店",
  "city": "台北市",
  "address": "台北市信義區松高路18號",
  "contactPhone": "02-6614-8000",
  "url": "https://www.citadines.com/",
  "images": {
    "main": "https://example.com/main.jpg",
    "source": "https://www.citadines.com/gallery"
  },
  "rooms": [
    {
      "name": "宴會廳",
      "images": {
        "main": "https://example.com/room.jpg"
      }
    }
  ],
  "qualityScore": 95,
  "qualityGrade": "A"
}
```

### B 級：良好資料（可匯入，需後續補充）

**條件**：
- ✅ 所有必填欄位完整
- ✅ 格式驗證通過
- ⚠️ 官網驗證部分成功
- ⚠️ 部分會議室缺少照片
- ⚠️ 部分選填欄位空白

**評分**：70-89 分

**範例**：
```json
{
  "name": "CAMA咖啡",
  "contactPhone": "請洽各分店",  // ⚠️ 非標準格式
  "images": {
    "main": "https://example.com/main.jpg"
  },
  "rooms": [
    {
      "name": "包場空間",
      "images": {
        "main": "https://images.unsplash.com/..."  // ⚠️ 非官網照片
      }
    }
  ],
  "qualityScore": 75,
  "qualityGrade": "B"
}
```

### C 級：待補充資料（不建議匯入）

**條件**：
- ❌ 缺少必填欄位
- ❌ 格式驗證失敗
- ❌ 官網無法驗證
- ❌ 缺少照片
- ❌ 資訊明顯錯誤

**評分**：<70 分

**處理方式**：
1. 列出所有問題
2. 發送給資料提供者補充
3. 標記為「待驗證」
4. 不進入正式資料庫

**範例**：
```json
{
  "name": "測試場地",
  "address": "台北市",  // ❌ 地址不完整
  "contactPhone": "",  // ❌ 電話空白
  "url": "invalid-url",  // ❌ URL 格式錯誤
  "qualityScore": 45,
  "qualityGrade": "C",
  "issues": [
    "地址不完整（缺少區、路名、號）",
    "聯絡電話為空",
    "官網 URL 格式錯誤"
  ]
}
```

### 評分計算公式

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

---

## ⚠️ 錯誤處理流程

### 錯誤分類

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

### 錯誤處理腳本

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

## 💻 範例程式碼

### 完整驗證流程

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


# 使用範例
if __name__ == '__main__':
    # 讀取場地資料
    with open('venue_data.json', 'r', encoding='utf-8') as f:
        venue = json.load(f)
    
    # 驗證
    validator = VenueDataValidator()
    result = validator.validate(venue)
    
    # 輸出結果
    print(f"品質評分: {result['qualityScore']} ({result['qualityGrade']})")
    print(f"可匯入: {result['canImport']}")
    print(f"狀態: {result['status']}")
    
    if result['errors']:
        print("\n❌ 錯誤:")
        for error in result['errors']:
            print(f"  - {error}")
    
    if result['warnings']:
        print("\n⚠️  警告:")
        for warning in result['warnings']:
            print(f"  - {warning}")
```

---

## ✅ 檢查清單

### 資料匯入前檢查

- [ ] **必填欄位完整**
  - [ ] 場地名稱
  - [ ] 場地類型
  - [ ] 縣市
  - [ ] 完整地址
  - [ ] 聯絡電話
  - [ ] 官網 URL

- [ ] **格式驗證通過**
  - [ ] 電話格式正確
  - [ ] URL 格式正確
  - [ ] 價格範圍合理
  - [ ] 容納人數合理

- [ ] **官網驗證成功**
  - [ ] URL 可訪問
  - [ ] 場地資訊吻合
  - [ ] 提取到照片

- [ ] **照片完整**
  - [ ] 場地主照片存在
  - [ ] 所有會議室都有照片
  - [ ] 照片 URL 可訪問

- [ ] **品質評分達標**
  - [ ] 評分 >= 70 分
  - [ ] 等級為 A 或 B
  - [ ] 無致命錯誤

### 匯入後驗證

- [ ] **系統內檢查**
  - [ ] JSON 格式正確
  - [ ] 欄位完整顯示
  - [ ] 照片正常載入
  - [ ] 連結可點擊

- [ ] **功能測試**
  - [ ] 搜尋功能正常
  - [ ] 篩選功能正常
  - [ ] 詳細頁面正常

---

## 📝 更新記錄

| 日期 | 版本 | 更新內容 | 更新人 |
|------|------|----------|--------|
| 2026-03-17 | 1.0 | 建立完整的資料擷取 SOP | Jobs |

---

**維護者**: Jobs (Global CTO)  
**最後更新**: 2026-03-17
