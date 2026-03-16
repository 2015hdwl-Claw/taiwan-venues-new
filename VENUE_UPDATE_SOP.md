# 場地資料更新標準作業程序 (SOP)

## 📋 目錄
- [更新流程](#更新流程)
- [照片規範](#照片規範)
- [資料驗證](#資料驗證)
- [常見問題](#常見問題)

---

## 🔄 更新流程

### 1. 識別需要更新的場地

```bash
# 搜尋特定場地
cd /root/.openclaw/workspace/taiwan-venues-new
grep -n "場地名稱" venues.json
```

### 2. 從官網收集資料

- **必填欄位**：
  - 場地名稱 (name)
  - 地址 (address)
  - 聯絡電話 (contactPhone)
  - 官網 URL (url)
  
- **選填欄位**：
  - 聯絡人 (contactPerson)
  - Email (contactEmail)
  - 價格 (priceHalfDay, priceFullDay)
  - 容納人數 (maxCapacityTheater, maxCapacityClassroom)
  - 可用時段 (availableTimeWeekday, availableTimeWeekend)
  - 設備清單 (equipment)

### 3. 更新 venues.json

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

### 4. 驗證更新

```bash
# 檢查 JSON 格式
python3 -m json.tool venues.json > /dev/null && echo "✅ JSON 格式正確"

# 本地測試
python3 -m http.server 8080
# 開啟瀏覽器訪問 http://localhost:8080
```

### 5. 提交變更

```bash
git add venues.json
git commit -m "更新: 場地名稱 - 更新內容描述"
git push origin main
```

### 6. 部署驗證

Vercel 會自動部署，約 1-2 分鐘後：
- 訪問線上網站
- 檢查更新是否正確顯示
- 測試所有相關功能

---

## 📸 照片規範

### ⚠️ 重要原則

**每個會議室必須有專屬照片！**

### 照片來源規則

1. **首選**：官網的會議室照片
2. **次選**：場地提供的官方照片
3. **避免**：使用通用庫存照片（除非完全沒有官方照片）

### 如何找到正確的照片 URL

#### 方法一：檢查網頁原始碼

```bash
# 下載官網 HTML
curl -s "https://www.example.com/venue-page" > venue.html

# 搜尋圖片 URL
grep -oP 'files/[^"]+\.(jpg|jpeg|png|webp)' venue.html
grep -oP 'https://[^"]+\.(jpg|jpeg|png|webp)' venue.html
```

#### 方法二：使用瀏覽器開發者工具

1. 開啟官網頁面
2. 按 F12 開啟開發者工具
3. 切換到 "Network" 標籤
4. 篩選 "Img" 類型
5. 重新整理頁面
6. 找到會議室照片的 URL

#### 方法三：檢查網頁元素

1. 在照片上右鍵 → "檢查元素"
2. 找到 `<img>` 標籤
3. 複製 `src` 屬性值

### 照片資料結構

#### 場地主照片

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
    "lastUpdated": "2026-03-16",
    "note": "照片驗證備註"
  }
}
```

#### 會議室照片（每個 room 必須有）

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
        "source": "https://www.example.com/rooms#room-a",
        "note": "照片說明（選填）"
      }
    }
  ]
}
```

### 特殊情況處理

#### 情況一：分廳沒有獨立照片

如果多個會議室是同一個大空間的分隔（如宴會廳分廳），可以使用相同的主照片：

```json
{
  "id": "r002",
  "name": "宴會廳A廳",
  "images": {
    "main": "https://www.example.com/files/banquet-hall.jpg",
    "note": "分廳使用宴會廳主圖",
    "source": "https://www.example.com/banquet"
  }
}
```

#### 情況二：找不到任何照片

如果官網完全沒有照片，使用 fallback：

```json
{
  "id": "r003",
  "name": "會議室B",
  "images": {
    "main": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=800",
    "note": "官網無照片，使用庫存照片",
    "source": "https://www.example.com/meeting-rooms"
  }
}
```

### 照片更新檢查清單

- [ ] 確認每個 room 都有 `images.main`
- [ ] 確認照片 URL 來自官網
- [ ] 測試照片 URL 可正常訪問
- [ ] 記錄照片來源頁面 (`source`)
- [ ] 如有特殊情況，加入 `note` 說明
- [ ] 更新 `lastUpdated` 日期

---

## ✅ 資料驗證

### 驗證清單

#### 基本資訊
- [ ] 場地名稱正確
- [ ] 地址完整（縣市 + 區 + 路名 + 號）
- [ ] 聯絡電話格式正確（02-XXXX-XXXX）
- [ ] 官網 URL 可訪問

#### 會議室資料
- [ ] 每個 room 都有唯一 ID
- [ ] 每個 room 都有照片
- [ ] 面積、容納人數等數值合理
- [ ] 價格資訊正確

#### 照片資料
- [ ] 主照片 URL 有效
- [ ] 照片來源已記錄
- [ ] 照片解析度足夠（建議寬度 >= 800px）

### 自動驗證腳本

```python
import json
import requests

def validate_venue(venue_id):
    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)
    
    venue = next((v for v in venues if v['id'] == venue_id), None)
    
    if not venue:
        print(f"❌ 找不到場地 ID: {venue_id}")
        return False
    
    errors = []
    
    # 檢查基本資訊
    if not venue.get('name'):
        errors.append("缺少場地名稱")
    if not venue.get('address'):
        errors.append("缺少地址")
    if not venue.get('contactPhone'):
        errors.append("缺少聯絡電話")
    
    # 檢查照片
    if not venue.get('images', {}).get('main'):
        errors.append("缺少場地主照片")
    
    # 檢查會議室照片
    for room in venue.get('rooms', []):
        if not room.get('images', {}).get('main'):
            errors.append(f"會議室 '{room['name']}' 缺少照片")
    
    # 測試照片 URL
    main_image = venue.get('images', {}).get('main')
    if main_image:
        try:
            response = requests.head(main_image, timeout=5)
            if response.status_code != 200:
                errors.append(f"主照片 URL 無效: {response.status_code}")
        except Exception as e:
            errors.append(f"無法訪問主照片: {str(e)}")
    
    if errors:
        print(f"❌ 驗證失敗 - {venue['name']}")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print(f"✅ 驗證通過 - {venue['name']}")
        return True

# 使用範例
validate_venue(1077)
```

---

## ❓ 常見問題

### Q1: 官網沒有會議室照片怎麼辦？

**A**: 
1. 先確認是否有場地整體照片
2. 如果是分廳，可以使用主廳照片
3. 如果完全沒有，使用通用庫存照片並加註

### Q2: 照片 URL 是相對路徑怎麼辦？

**A**: 轉換為完整 URL：
```
相對路徑: /files/room.jpg
完整 URL: https://www.example.com/files/room.jpg
```

### Q3: 如何批量更新多個場地的照片？

**A**: 使用 Python 腳本：

```python
import json

with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# 批量更新邏輯
for venue in venues:
    if not venue.get('images', {}).get('main'):
        # 加入預設照片或其他邏輯
        pass

with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)
```

### Q4: 更新後網站沒有變化？

**A**: 
1. 清除瀏覽器快取（Ctrl + Shift + R）
2. 等待 1-2 分鐘讓 Vercel 完成部署
3. 檢查 Git 是否成功 push
4. 查看 Vercel 部署日誌

### Q5: 如何確認照片是否來自官網？

**A**: 
1. 檢查 URL domain 是否為官網域名
2. 記錄 `source` 欄位為照片來源頁面
3. 在 `note` 中註明照片類型（官方/庫存）

---

## 📝 更新記錄

| 日期 | 場地 | 更新內容 | 更新人 |
|------|------|----------|--------|
| 2026-03-16 | 台北艾麗酒店 (ID: 1077) | 為所有會議室加入專屬照片 | Jobs |

---

## 🔗 相關資源

- [Vercel 部署文檔](https://vercel.com/docs)
- [JSON 格式驗證](https://jsonlint.com/)
- [圖片優化指南](https://web.dev/fast/#optimize-your-images)

---

**最後更新**: 2026-03-16  
**維護者**: Jobs (Global CTO)
