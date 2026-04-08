# 活動大師 AI 知識庫 — 1 週上市計畫

**目標上線日**: 2026-04-11（六）
**啟動日**: 2026-04-04（六）

---

## 現狀盤點

| 項目 | 數值 |
|------|------|
| 場地總數 | 58（啟用 48） |
| 會議室總數 | ~370 |
| 有 risks 的場地 | 7 |
| 有 pricingTips 的場地 | 7 |
| 有 rules 的場地 | 9 |
| 有 limitations 的會議室 | 38 |
| 有 loadIn 的會議室 | 2 |
| 前端技術 | 純 HTML/JS 靜態站 |
| 部署 | Vercel |
| 後端 | 無（eventmaster-api/ 未啟用） |

---

## 週計畫（7 天）

### Day 1（4/4 六）：Schema + 資料架構

**目標**：定義 AI 知識庫 Schema，建立資料分離機制

- [ ] 1.1 定義 `ai_knowledge_base/schema.json`（AI 專用結構化 schema）
  - venue 層：risks, pricingTips, rules, seasonal, logistics
  - room 層：limitations, loadIn, suitableEventTypes, equipment(spec+externalAllowed), ceilingHeight, breakoutRooms
  - 每筆知識帶 source, verifiedAt, expiresAt, confidence
- [ ] 1.2 建立 `ai_knowledge_base/venues/` 目錄結構（每場地一個 JSON）
- [ ] 1.3 撰寫 `tools/sync_to_ai.py`（venues.json → AI 知識庫格式，單向同步）
- [ ] 1.4 從現有 9 個有知識的場地，執行首次同步驗證

**交付物**：`ai_knowledge_base/` 完整目錄 + sync 腳本

### Day 2（4/5 日）：爬蟲擴充 + 活動情境模板

**目標**：讓爬蟲能提取深層知識，定義活動情境

- [ ] 2.1 擴充 `scraper/extractors.py`
  - 新增 `KnowledgeExtractor` class
  - 從 PDF 的「注意事項」「租借辦法」「收費標準」提取 rules/limitations
  - 從官網的「場地須知」「FAQ」提取 hidden rules
  - 提取 equipment specs（不只有名稱，還有規格）
- [ ] 2.2 新增 `scraper/knowledge_config.py`
  - 活動情境定義：研討會、發表會、尾牙、家庭日、說明會、培訓
  - 每情境的通用問題模板（15-20 題）
  - 問題 → schema 欄位對照表
- [ ] 2.3 新增 `tools/inquiry_generator.py`
  - 輸入：場地 ID + 活動情境
  - 輸出：email 範本（含已知情識、待確認問題）
  - 自動排除已有資料的問題

**交付物**：擴充後的爬蟲 + 活動情境模板 + 詢問信生成器

### Day 3（4/6 一）：知識採集執行

**目標**：最大化知識庫覆蓋率

- [ ] 3.1 對現有 PDF 文件執行深度提取
  - `jhsi_hcph_docs/` 的 5 份 PDF（竹科租借辦法、管理規則、餐飲規則）
  - `jhsi_wuri_docs/` 的 5 份 PDF（新烏日租借辦法、管理規則）
  - `mayfull_pkg1.pdf`, `mayfull_pkg2.pdf`
  - `regent_meeting_package.pdf`
- [ ] 3.2 用 LLM 逐一爬取其餘場地官網的「場地須知」「FAQ」頁面
  - 優先處理 41 個缺知識的場地
  - 至少完成 20 個場地的基礎 rules 提取
- [ ] 3.3 批次產出詢問信（針對爬不到的資訊）
  - 6 情境 × 高優先場地 = ~30 封信
  - 存至 `communication/outgoing/`

**交付物**：知識庫覆蓋率從 9 → 29+ 場地

### Day 4（4/7 二）：RAG Pipeline

**目標**：建置 AI 助理後端

- [ ] 4.1 選擇並設定 LLM API
  - 使用 Claude API（Anthropic SDK）或 OpenAI API
  - API key 存於 Vercel environment variables
- [ ] 4.2 新增 `api/assistant.js`（Vercel Serverless Function）
  - POST endpoint：接收用戶問題
  - RAG 流程：embed query → 搜尋相關知識 → 組裝 context → 呼叫 LLM → 回傳
- [ ] 4.3 新增 `tools/generate_embeddings.py`
  - 將 `ai_knowledge_base/venues/*.json` 轉為 chunks
  - 使用 OpenAI embeddings API 生成向量
  - 輸出 `ai_knowledge_base/embeddings.json`
- [ ] 4.4 System Prompt 設計
  - 角色：活動大師 AI 場地顧問
  - 規則：只基於知識庫回答，不知道就誠實說
  - 不知到時：產生詢問信草稿
  - 引用來源：每個回答附上資料出處
  - 語言：繁體中文

**交付物**：`api/assistant.js` 可用（本地測試通過）

### Day 5（4/8 三）：AI 助理前端

**目標**：Chat Widget + 首頁改版

- [ ] 5.1 新增 `chat.js` + `chat.css`（浮動 Chat Widget）
  - 右下角對話泡泡
  - 訊息氣泡 UI（用戶 + AI）
  - 載入動畫
  - 「產生詢問信」按鈕
  - 來源引用摺疊區塊
- [ ] 5.2 修改 `index.html`
  - 標題改為：「活動大師 — 活動企劃的場地知識庫」
  - 副標：「官網沒寫的場地限制、潛規則、踩坑經驗，都在這裡」
  - 首頁新增「知識亮點」區塊（展示 3-5 條精選知識）
  - 移除企業表單、反饋表單等空殼功能
  - 引入 chat.js
- [ ] 5.3 修改 `venue.html` / `room.html`
  - 場地頁面：知識區塊優先顯示（risks → rules → pricingTips）
  - 會議室頁面：limitations + loadIn 突出顯示
  - 每頁加入「問 AI」按鈕，自動帶入場地 context

**交付物**：前端改版完成（本地可預覽）

### Day 6（4/9 四）：整合測試

**目標**：端到端測試 + 修 bug

- [ ] 6.1 API 測試
  - 基本問答（有知識的場地）
  - 複雜查詢（跨場地比較）
  - 未知問題處理（「不知道」+ 詢問信）
  - 幻覺測試（確認不會編造資訊）
- [ ] 6.2 前端測試
  - Chat widget 互動
  - 知識亮點展示
  - 各頁面 RWD
  - 載入效能
- [ ] 6.3 知識品質審查
  - 抽查 10 筆知識的準確性
  - 確認 source/verifiedAt 正確
  - 確認無過時資訊
- [ ] 6.4 安全性檢查
  - API key 不暴露
  - Rate limiting（防止濫用）
  - 輸入 sanitization

**交付物**：所有測試通過

### Day 7（4/10 五）：上線

**目標**：部署 + 監控

- [ ] 7.1 設定 Vercel environment variables（API key）
- [ ] 7.2 `vercel --prod --yes` 部署
- [ ] 7.3 線上煙霧測試
  - 首頁載入
  - AI 助理對話
  - 場地頁面知識顯示
- [ ] 7.4 設定監控
  - Vercel analytics
  - API error logging
  - 用戶提問日誌（供後續知識庫補充）
- [ ] 7.5 發送第一批詢問信（從 `communication/outgoing/`）

**交付物**：正式上線 🚀

---

## 技術決策

| 決策 | 選擇 | 理由 |
|------|------|------|
| LLM | Claude Haiku | 成本低（$0.25/MTok）、品質足夠 |
| Embedding | OpenAI text-embedding-3-small | 便宜、效果好 |
| 向量儲存 | JSON 檔案（`embeddings.json`） | 58 場地規模不需向量 DB |
| 後端 | Vercel Serverless Function | 與現有部署整合 |
| 前端 | 純 JS（維持現有架構） | 不引入新框架 |

---

## 風險與應對

| 風險 | 機率 | 應對 |
|------|------|------|
| LLM 幻覺 | 高 | 嚴格 RAG + system prompt 限制 + 來源引用 |
| API 成本超預期 | 低 | Haiku 極便宜 + rate limiting |
| 知識覆蓋率不足 | 中 | 首日上線 9 場地深度 + 20 場地基礎，持續補充 |
| Vercel serverless 限制 | 低 | 10s timeout 足夠、500MB 夠用 |
| 前端改版影響現有功能 | 中 | 改版只改首頁，詳情頁不動 |

---

## 成功指標（上線時）

- [ ] AI 助理可正確回答已知情識的問題（0 幻覺）
- [ ] 不知道的問題能誠實回答 + 產出詢問信
- [ ] 知識覆蓋 ≥ 20 場地（基礎 rules）
- [ ] 首頁定位清晰（知識庫，非搜尋引擎）
- [ ] 30+ 封詢問信已準備好可發送
