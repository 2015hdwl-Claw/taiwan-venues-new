# Day 1 執行任務（2026-04-04）

## 前置：已完成

- [x] `ai_knowledge_base/schema.json` — AI 知識庫完整結構定義
- [x] `ai_knowledge_base/venues/1072.json` — 圓山大飯店完整範例
- [x] `CLAUDE.md` — 已加入 AI 知識庫架構說明
- [x] `PLAN_AI_KNOWLEDGE_BASE.md` — 7 天上市計畫

---

## 今天要完成

### Task 1: 撰寫 `tools/sync_to_ai.py`

**功能**：讀取 `venues.json`，為每個場地產生 `ai_knowledge_base/venues/{id}.json`

**轉換邏輯**：

```
venues.json 欄位              → ai_knowledge_base 欄位
─────────────────────────────────────────────────────
id, name, venueType, city...  → identity
(不存在)                       → summary (留空，Day 3 LLM 推斷填入)
risks                         → risks (直接複製)
rules (扁平字串)               → rules (轉為 [{rule: "...", exception: null, ...}])
pricingTips                   → pricingTips (直接複製)
transportation + accessInfo   → logistics
rooms[].limitations           → rooms[].limitations
rooms[].loadIn                → rooms[].loadIn
rooms[].ceilingHeight         → rooms[].ceilingHeight
rooms[].equipment (名稱[])    → rooms[].equipment ([{name: "...", spec: null, ...}])
rooms[].capacity              → rooms[].capacity
rooms[].area                  → rooms[].area
rooms[].pricing               → rooms[].pricing
(不存在)                       → ragChunks[] (留空，Day 3 生成)
(不存在)                       → inquiries (留空結構 {pending:[], sent:[]})
(不存在)                       → seasonal (留空，Day 2-3 填入)
```

**CLI 介面**：
```bash
python tools/sync_to_ai.py                  # 同步全部場地
python tools/sync_to_ai.py --venue 1072     # 只同步指定場地
python tools/sync_to_ai.py --dry-run        # 只顯示將產生的檔案，不寫入
```

**重要規則**：
- 單向同步：venues.json → AI 知識庫，**永遠不回寫**
- 不覆蓋已有且 confidence=confirmed 的知識（保留人工填入的資料）
- 新欄位（summary, seasonal, logistics, ragChunks）若 venues.json 無對應資料，填 null 或空陣列
- 每次同步寫入 sync_log（時間、場地數、新增/更新/跳過）

### Task 2: 執行首次同步

```bash
python tools/sync_to_ai.py
```

預期產出：58 個檔案在 `ai_knowledge_base/venues/`

### Task 3: 驗證

- 確認 `ai_knowledge_base/venues/1072.json` 與手動建立的一致
- 抽查 3 個無知識的場地，確認結構正確、空欄位合理
- 確認 sync_log 記錄正確

---

## 參考檔案

| 檔案 | 用途 |
|------|------|
| `ai_knowledge_base/schema.json` | Schema 定義 |
| `ai_knowledge_base/venues/1072.json` | 完整範例 |
| `venues.json` | 資料來源 |
| `CLAUDE.md` 第 5 節 | AI 知識庫架構說明 |
| `PLAN_AI_KNOWLEDGE_BASE.md` | 完整 7 天計畫 |

## 知識缺口分析（1072 為例）

### 已有（可直接同步）
- identity, risks, pricingTips, rules（扁平版）
- rooms: 13間全有 capacity, area, ceilingHeight, equipment, limitations

### 要爬蟲（本地有 PDF）
- `regent_meeting_package.pdf` → rules 結構化、equipment 規格、定價
- `regent_floorplan_8~13.pdf`（6份）→ layout、合併可能性
- 官網圖片頁 → rooms[].images（12/13 間缺圖）

### 要寫 email（官網找不到）
- 收件：cc@grand-hotel.org（宴會部）
- 缺：每間 loadIn 細節、equipment 外接規定、定價、淡季折扣、停車位數、遊覽車停靠
- 3 情境提問：200人研討會、500人尾牙、1000人國際會議
