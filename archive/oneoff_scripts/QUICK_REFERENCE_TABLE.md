# 快速對照表

## 📊 網頁技術 vs 擷取方式

| 網頁類型 | 比例 | 工具 | 範例 | 時間 |
|---------|------|------|------|------|
| **靜態/SSR** | 80% | requests + BeautifulSoup | WordPress, 傳統官網 | 0.5-2秒 |
| **有API** | 5% | 直接調用API | 現代Web應用 | 1-3秒 |
| **JS渲染** | 15% | Playwright | React/Vue/Angular | 3-10秒 |

### 判斷方法
```
右鍵 > 檢視網頁原始碼
├─ 看到內容 → 靜態/SSR → 用 requests
├─ 看不到內容 → JS渲染 → 用 Playwright
└─ Network有XHR → 有API → 直接調用API
```

---

## 📋 完整資料模型

### 場地級別（Venue Level）

| 類別 | 欄位 | 擷取頁面 | 擷取方法 |
|------|------|----------|----------|
| **基本** | id, name, venueType, city, address, url | 首頁 | 標題、meta |
| **聯絡** | contactPhone, **phoneExtension**, contactEmail, **contactPerson**, **contactPersonTitle** | 聯絡我們 | 正則 `分機(\d+)` |
| **交通** | **accessInfo.mrt**, **accessInfo.bus**, **accessInfo.parking**, **accessInfo.car** | 交通資訊 | 關鍵字「捷運」 |
| **規則** | **rules.catering**, **rules.smoking**, **rules.decoration**, **rules.deposit**, **rules.cancellation** | 租借須知 | 關鍵字「餐飲」 |
| **平面圖** | **floorPlan.url**, **floorPlan.description**, **floorPlan.floors** | 場地導覽 | `<img>` 標籤 |
| **圖片** | images.main, images.gallery, images.source | 相簿 | `<img>` 標籤 |

### 會議室級別（Room Level）

| 類別 | 欄位 | 擷取頁面 | 擷取方法 |
|------|------|----------|----------|
| **基本** | id, name, floor, area, areaUnit, capacity, capacityType | 會議室頁面 | 表格/卡片解析 |
| **設備** | equipment, priceHalfDay, priceFullDay | 會議室頁面 | 關鍵字「投影機」 |
| **圖片** | images.main, images.source | 會議室頁面 | `<img>` 標籤 |

**粗體** = 新增的遺漏欄位

---

## 🔄 完整流程

```
1. 判斷網頁類型（0.5秒）
   ├─ 靜態 → requests
   ├─ API → 直接調用
   └─ JS → Playwright

2. 基本資料（1-3秒）
   └─ 首頁 → name, phone, email

3. 聯絡資訊（1-3秒）
   └─ 聯絡我們 → person, extension

4. 交通資訊（1-3秒）
   └─ 交通資訊 → mrt, bus, parking

5. 場地規則（1-3秒）
   └─ 租借須知 → catering, smoking, deposit

6. 平面圖（1-3秒）
   └─ 場地導覽 → floorPlan

7. 會議室（2-5秒）
   └─ 會議室頁面 → rooms 陣列
```

**總耗時**: 5-20秒

---

## 🎯 關鍵原則

### 1. 完整性
官網有什麼 → 活動大師有什麼
```
官網5個會議室 → 活動大師5個 ✅
官網有交通資訊 → 活動大師有 accessInfo ✅
官網有平面圖 → 活動大師有 floorPlan ✅
```

### 2. 正確性
資料必須一致
```
官網「分機1234」→ phoneExtension: "1234" ✅
官網「捷運台北車站」→ accessInfo.mrt.station: "台北車站" ✅
```

### 3. 技術適配
```
80% → requests + BeautifulSoup（最快）
5% → API（最準）
15% → Playwright（最保險）
```

---

## 📖 文件索引

| 文件 | 內容 |
|------|------|
| **FINAL_ANSWER_SUMMARY.md** | 兩個問題的完整回答 |
| **COMPLETE_DATA_MODEL_WITH_ALL_FIELDS.md** | 完整資料模型 |
| **WEB_SCRAPING_STRATEGIES.md** | 網頁技術對策 |
| **UNIVERSAL_VENUE_EXTRACTOR.md** | 整合方案 |

---

**更新**: 2026-03-25
**版本**: v4.0（完整版）
