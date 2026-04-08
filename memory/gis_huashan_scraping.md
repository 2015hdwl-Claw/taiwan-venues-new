---
name: gis_huashan_scraping_patterns
description: 集思(GIS)系列場地與華山1914的爬蟲模式、資料修正經驗、前端格式相容性要求
type: feedback
---

## 集思(GIS)系列場地 — meeting.com.tw 共用結構

所有集思場地（MOTC、NTUT、NTU、HSP、Wenxin、Xinwuri 等）使用相同的網站架構。

### 網站結構
- 首頁：`https://www.meeting.com.tw/{venue}/`
- 場地介紹頁（含完整會議室表格）：`https://www.meeting.com.tw/{venue}/floor-introduction.html` 或 `.php`
- 每個場地的圖片路徑：`https://www.meeting.com.tw/{venue}/images/lease/{room-slug}-slider-{N}.jpg`
- 平面圖：`https://www.meeting.com.tw/{venue}/images/floor-{venue}.png`
- 所有場地時段一致：AM 08:00-12:00, PM 13:00-17:00, Evening 18:00-21:30
- 清潔費：租金 10%

### 已知場地 slug 對照
| slug | ID | 名稱 | 狀態 |
|------|-----|------|------|
| motc | 1494 | 集思交通部 | OK |
| ntut | 1495 | 集思北科大 | OK |
| ntu | 1128 | 集思台大 | OK |
| hsp | 1496 | 集思竹科 | OK |
| xinwuri | 1498 | 集思新烏日 | 待驗證 |
| wenxin | ? | 集思文心 | 404 |
| ntc | 1497 | 集思台中文心 | 404 |
| cyc | ? | 集思新北 | 404 |
| yms | ? | 集思陽明交大 | 404 |

### 圖片命名規則（非固定）
- MOTC：`thehall-slider-01.jpg`, `forum-slider-01.jpg`, `thegallery-slider-01.jpg`, `chambers-slider-01.jpg`
- NTUT：`lecture-hall-slider-1.jpg`, `room201-slider-1.jpg` 等
- NTU：`forum-slider-1.jpg`, `socrates-slider-01.jpg` 等
- **必須從實際頁面提取圖片 URL，不可假設命名規則**

---

## 華山1914 API

### 資料來源
- 場地列表：`https://www.huashan1914.com/w/huashan1914/AppPlaceList`（靜態 HTML 頁面，含完整場地資料）
- 場地詳情：`https://www.huashan1914.com/w/huashan1914/AppPlaceInfo?pid={PID}`
- 圖片基礎 URL：`https://media.huashan1914.com/WebUPD/huashan1914/AppPlace/`

### 關鍵 PID 對照
- PID 16 = 西1館（最大，800人，205坪，$126,000/日）
- PID 22 = 華山劇場（戶外，1200人，450坪，$126,000/日）
- PID 10 = 中4A紅酒作業場（350人，120坪，$100,000/日）
- PID 35 = 西5-2館（錯誤頁面，無資料）

### 聯絡資訊
- 電話：(02) 2358-1914
- 租借時間：週一至週五 09:30-18:00

---

## 前端資料格式相容性（必須遵守）

### equipment 欄位
- **必須是 array**，不可是 string
- venue.js line 234-235: `room.equipment.slice(0, 3).join('、')` — string 會 crash
- 正確：`["投影設備", "音響系統", "無線麥克風"]`
- 錯誤：`"投影設備、音響系統、無線麥克風"`

### pricing 欄位
- room.js `renderPricing()` 讀取 `pricing.morning || pricing.afternoon || pricing.halfDay`
- 必須包含 `pricing.halfDay` 或 `pricing.fullDay`
- 格式：`{"halfDay": 9000, "fullDay": 18000}`

### images 欄位
- 主圖：`images.main`（venue.js 使用）
- 相簿：`images.gallery`（array of URLs）
- 前端 `onerror` 處理：`this.style.display='none'` — 圖片失效會隱藏

---

## 重複場地處理

### ID 1100 vs ID 1124（台北花園大酒店）
- 同一家飯店、同地址、同官網
- ID 1100 保留（有 14 間完整會議室，品質分數 100）
- ID 1124 已設 `active: false`

### 判斷重複標準
- 相同官網 URL
- 相同地址
- 相同聯絡電話
- 保留資料較完整的 venue，另一個設 `active: false`

---

## 2026-03-31 大修正摘要

### 修正的場地
1. **ID 1494 (MOTC)**: 4 間錯誤會議室 → 正確的集會堂/國際會議廳/201/202；地址、電話、圖片全部修正
2. **ID 1495 (NTUT)**: 新增感恩廳（最大房間）；9 間房間價格全部修正（差距 2-4 倍）
3. **ID 1496 (HSP)**: 地址修正（光復路 → 工業東二路）
4. **ID 1124**: 設為 inactive
5. **ID 1125 (華山)**: 23 間場地價格全部修正（$5K-$10K → $20K-$126K）；電話修正；新增金八廣場、樹前草地
6. **全局**: 29 個 venue 的 equipment string → array 轉換

### 根本原因
- 自動爬蟲（`python -m scraper --test`）的 PDF 提取器會把表格標題當會議室名稱
- 部分場地價格被錯誤提取（可能混淆了價格欄位）
- 圖片 URL 使用相對路徑而非完整 URL

### 預防措施
- 爬蟲後必須對比官網實際資料
- 價格提取後做合理性檢查（例如 46 坪房間 $3,000 明顯過低）
- 會議室名稱必須在官網可見，不應出現在 PDF 表格標題行

---

**Why**: 避免未來爬蟲和資料修正時重複踩坑，特別是 GIS 系列場地的共用結構和前端格式相容性問題。

**How to apply**:
- 爬取任何集思場地時，參考此記憶的共用結構和 slug 對照
- 寫入 venues.json 前確認 equipment 是 array、pricing 有 halfDay/fullDay
- 修正資料後驗證前端 venue.html 和 room.html 能正確渲染
