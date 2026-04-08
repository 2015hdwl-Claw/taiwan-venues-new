# 記憶體索引

本專案相關的重要記憶體，避免重複踩坑。

## 記憶體清單

### [deep_scraping_javascript_variables](deep_scraping_javascript_variables.md)
**類型**: feedback
**描述**: 從頁面的 JavaScript 變數中提取完整資料 - 師大進修推廣學院成功案例

**重點內容**：
- ✅ 師大進修推廣學院從 JavaScript 變數 `room_data` 提取完整資料
- ✅ 資料完整性從 15% 提升到 85%（+467%）
- ✅ 價格、設備、照片覆蓋率從 0% 提升到 100%
- ✅ 提取方法：`var room_data = (\[.*?\]);` 正則表達式
- ✅ 常見變數名：room_data, venue_data, event_data, space_data

**何時使用**：
- 遇到有「詳細介紹」按鈕但無獨立詳情頁的場地
- 檢查頁面源碼中的 JavaScript 變數
- 學校、政府機構、活動場地預約系統

---

### [deep_scraping_redefined](deep_scraping_redefined.md)
**類型**: feedback
**描述**: 重新定義深度爬蟲邏輯 - 不應侷限於頁面層級

**重點內容**：
- ✅ 舊思維：第 1 層→第 2 層→第 3 層（詳情頁）
- ✅ 新思維：第 3 層包含詳情頁、JavaScript 變數、JSON-LD、data-* 屬性、API
- ✅ 優先級：JavaScript 變數 > JSON-LD > data-* 屬性 > 詳情頁 > API
- ✅ 效率：提取 JavaScript 變數比爬詳情頁快 5-10 倍
- ✅ 準確度：JavaScript 變數來自官方後端，準確度 100%

**何時使用**：
- 所有深度爬蟲任務的標準流程
- 爬蟲前檢查頁面是否有隱藏資料
- 設計爬蟲策略時的優先級參考

---

### [three_stage_scraping_workflow](three_stage_scraping_workflow.md)
**類型**: feedback
**描述**: 三階段標準爬蟲流程 - 技術檢測、深度爬取、驗證寫入

**重點內容**：
- ✅ 階段 1：技術檢測（HTTP狀態、網頁類型、載入方式、資料位置、反爬蟲）
- ✅ 階段 2：深度爬蟲（三級爬取：主頁→會議頁→詳情頁）
- ✅ 階段 3：驗證寫入（立即驗證、檢查清單、使用工具）
- ✅ 關鍵數據：台北市40場地執行結果（聯絡100% vs 容量20%）

**何時使用**：
- 任何新場地爬取前（必須先技術檢測）
- 遇到爬蟲成功率低時（檢查是否深度不足）
- 設計新爬蟲流程時（遵循三階段標準）

---

### [venue_scraping_process_lessons](venue_scraping_process_lessons.md)
**類型**: feedback
**描述**: 場地資料擷取流程關鍵教訓

**重點內容**：
- ✅ 必須先檢測網頁技術類型再爬取
- ✅ 完整六階段爬蟲流程（首頁→會議室→價格→規則→交通→平面圖）
- ✅ 會議室細分處理（101會議室 → 101全室、101A、101B等）
- ✅ 避免版本氾濫（刪除19個舊版本）
- ✅ 欄位完整性檢查清單
- ✅ 測試驅動開發流程

**何時使用**：
- 開始新場地爬取前
- 遇到 404 或爬取錯誤時
- 設計新的爬蟲流程時

---

### [pdf_parsing_lessons](pdf_parsing_lessons.md)
**類型**: feedback
**描述**: PDF 爬蟲解析流程與驗證方法的實務教訓

**重點內容**：
- ✅ 完整六步驟流程（下載 → 提取 → 查看格式 → 設計解析器 → 手動提取 → 更新）
- ✅ PDF 格式多樣性（列表/表格/分類/編號）
- ✅ 自動 vs 手動提取的選擇標準
- ✅ Windows 編碼問題處理
- ✅ 四種驗證方法（統計/特定場地/詳細檢查/完整性）
- ✅ 成功案例（集思 7 場地 45 會議室、南港 28 會議室）

**何時使用**：
- 需要解析 PDF 資料時
- 自動解析失敗時
- 設計新的爬蟲流程時
- 驗證資料準確性時

---

---

### [gis_huashan_scraping](gis_huashan_scraping.md)
**類型**: feedback
**描述**: 集思(GIS)系列 meeting.com.tw 共用結構、華山 API、前端格式相容性、2026-03-31 大修正經驗

**重點內容**：
- ✅ 所有集思場地共用相同網站架構（floor-introduction 頁面）
- ✅ meeting.com.tw 圖片路徑模式（需從實際頁面提取，不可假設命名）
- ✅ 華山1914 API: `AppPlaceList` 頁面含完整場地資料（23個場地）
- ✅ equipment 必須是 array（string 會導致 venue.js crash）
- ✅ pricing 需要 halfDay/fullDay 格式（room.js 相容）
- ✅ 2026-03-31 修正：6個場地資料修正、重複場地處理、29個 equipment 轉換
- ✅ 自動爬蟲 PDF 提取器會產生垃圾資料（表格標題當會議室名稱）

**何時使用**：
- 爬取任何集思系列場地時
- 寫入 venues.json 前的格式檢查
- 修正場地資料時的參考經驗

---

## 使用說明

### 新增記憶體
1. 在 `memory/` 目錄下創建新檔案
2. 使用標準 frontmatter 格式
3. 更新本索引檔案

### 記憶體類型
- **user**: 使用者相關資訊
- **feedback**: 回饋和教訓（避免重複錯誤）
- **project**: 專案特定資訊
- **reference**: 外部系統參考

### 查詢記憶體
在需要時參考相關記憶體，避免重複錯誤。

---

**最後更新**：2026-03-31
**總記憶體數**：6 個
**最新新增**：gis_huashan_scraping（集思系列+華山API+前端格式+大修正經驗）
