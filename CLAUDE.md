# 活動大師 Activity Master — 專案配置

**部署網址**: https://taiwan-venues-new-indol.vercel.app/
**資料庫**: `venues.json`（57 場地、48 啟用、370 會議室）
**最後更新**: 2026-04-04

---

## 1. 架構

### 前端：純靜態網站（無框架）

```
index.html + app.js    → 場地列表頁（分頁、篩選、排序）
venue.html + venue.js  → 場地詳情頁（會議室列表、圖片、設備）
room.html  + room.js   → 會議室詳情頁（定價、平面圖、容量）
```

- 前端直接 `fetch('venues.json')`，無後端 API
- 三個 JS 檔案同步維護 `DATA_VERSION` 常數（目前 `20260401-v12`），每次資料更新必須遞增
- 部署：`vercel --prod --yes`

### 資料架構

| 檔案 | 用途 |
|------|------|
| `venues.json` | 主資料庫（所有場地） |
| `venues_taipei.json` | 台北場地子集（24 場地），由 `venues.json` 過濾產生 |

- `active: false` 的場地前端不顯示
- 修改 `venues.json` 後必須跑 `pipeline.py sync`

### 工具架構

```
tools/
├── pipeline.py          # CLI 入口（所有指令的唯一入口）
├── estimators.py        # 統一估算公式（area/price）
├── validators.py        # 格式驗證（equipment/pricing/schema）
├── sync.py              # 檔案同步（taipei/DATA_VERSION）
└── constants.py         # 費率表、係數、場地分類
```

### pipeline.py 指令

| 指令 | 用途 | 需要LLM？ |
|------|------|-----------|
| `audit` | 掃描缺值 | 否 |
| `estimate` | 用固定公式補 area | 否 |
| `sync` | venues → venues_taipei + DATA_VERSION | 否 |
| `validate` | 驗證格式相容性 | 否 |
| `deploy` | vercel --prod --yes | 否 |
| `fix <id>` | audit + estimate + validate + sync | 否 |
| `crawl <id>` | 爬官網提取精確數據 | **是** |
| `images <id>` | 下載圖片、判斷是否為會議室 | **是** |

---

## 2. 規則

### LLM 角色邊界

**LLM 負責（需要理解力）：** 爬官網、判斷圖片、PDF 解讀、新場地建檔

**LLM 不負責（固定規則，不可浪費 token）：** area/price 估算、檔案同步、版本更新、格式驗證、部署

### 定價規則（重要）

- **有官方明確場地租借費** → 寫入 `halfDay`/`fullDay`
- **官網只有「每人會議專案價」** → 不等於場地費，寫 `{"note": "價格需電話洽詢"}`
- **官網/PDF 無定價** → 寫 `{"note": "價格需電話洽詢"}`
- `estimators.py` 的 `estimate_pricing()` 保留供參考，但**不可直接寫入 venues.json**

### 前端格式相容性

- `equipment` 必須是 array（前端用 `.slice().join()`）
- `pricing` 必須有 `halfDay`/`fullDay` 或 `note`（不可三個都沒有）
- **venue 主圖用 `images: {"main": "url"}`**（巢狀物件），**不是 `image: "url"`（字串）**。前端讀 `venue.images?.main`
- room 主圖同理：`room.images.main` 或 `room.images[0]`
- `area` 使用單一數值（坪），不用 `areaSqm`/`areaPing`
- `areaUnit` 一律用 `"坪"`
- `source` 標記數據來源日期

### 容量比估算公式（唯一來源：`tools/estimators.py`）

- area: `max(theater×0.9, banquet×1.5, classroom×1.3, ushape×2.0) / 3.3058`，四捨五入到 0.5 坪

### 爬蟲策略

- 先找 PDF（最準確），再爬官網
- 同一網站試超過 2 次失敗 → 改用估算
- 爬蟲後必須人工對比官網資料，不可直接信任
- Room name matching 用 `repr()` 確認精確字元

### 會議室 JSON 結構

```json
{
  "id": "1128-01",
  "name": "國際會議廳",
  "capacity": { "theater": 400 },
  "area": 253.6,
  "areaUnit": "坪",
  "floor": "B1",
  "pricing": { "halfDay": 44000, "fullDay": 88000 },
  "equipment": ["投影設備", "音響"],
  "images": { "main": "https://...", "gallery": ["https://..."] },
  "ceilingHeight": 5.0,
  "limitations": ["天花板高度5m，超過4.5m的舞台設備需提前申請"],
  "loadIn": { "elevator": "有貨梯（限重1.5噸）", "vehicleAccess": false },
  "source": "官網活動場地頁_20260331"
}
```

### 場地分類

| 類別 | 代表場地 |
|------|----------|
| 飯店場地 | 寒舍艾麗、君悅、W飯店 |
| 婚宴場地 | 龍邦、典華、薇閣 |
| 展演場地 | 松山文創、華山1914 |
| 會議中心 | 集思台大、台大醫院國際會議中心 |

---

## 3. 禁止事項

- **禁止寫新的 `fix_*.py` 一次性腳本** — 全部走 `pipeline.py`
- **禁止在對話中重複寫估算公式** — 公式只在 `tools/estimators.py`
- **禁止手動同步 `venues_taipei.json`** — 用 `pipeline.py sync`
- **禁止手動改 `DATA_VERSION`** — 用 `pipeline.py sync`
- **禁止用公式估算金額寫入 pricing.halfDay/fullDay** — 爬不到就寫 `note: "價格需電話洽詢"`
- **禁止 `pipeline.py knowledge` 不帶 `--save` 就寫入 venues.json** — 預設只輸出 stdout，加 `--save` 才寫檔
- **禁止背景執行 `pipeline.py knowledge --save`** — 避免覆寫其他場地更新
- **優先使用 `search.py` 而非 WebSearch/WebReader** — 避免配額限制。Agent 任務中用 `python ~/.claude/scripts/search.py --url "URL"` 抓取網頁
- 不可直接信任自動爬蟲結果而不驗證
- 不可假設圖片 URL 命名規則（必須從頁面提取）
- 不可將 `equipment` 寫成 string
- 部署不用問使用者（`vercel --prod --yes`）

---

## 4. 已知技術問題

- **SSL EOF**: 典華 denwell.com.tw → `ssl.create_default_context(check_hostname=False)`
- **403 AJAX**: 六福萬怡 → 需要 CSRF token + cookies
- **JS 渲染空白**: 公務人力 Umumba → 需找 PDF
- **集思(GIS)系列**: 共用 meeting.com.tw，圖片路徑 `meeting.com.tw/{slug}/images/lease/{room-slug}-slider-{N}.jpg`
- **華山1914 API**: `https://www.huashan1914.com/w/huashan1914/AppPlaceList`

---

---

## 5. AI 知識庫架構（2026-04-04 新增）

### 定位

活動大師 = **活動企劃的場地知識庫**（非搜尋引擎、非比價平台）
目標族群：負責把活動辦好的人（活動企劃/公關公司/企業內部）— 同一價值鏈
差異化：官網沒寫的場地限制、潛規則、踩坑經驗 + AI 助理

### 雙層資料分離

```
前端資料層（不動）
├── venues.json           ← 前端直接消費
└── venues_taipei.json    ← 台北子集

AI 資料層（獨立，單向同步）
├── ai_knowledge_base/
│   ├── schema.json       ← AI 專用結構定義
│   └── venues/*.json     ← 每場地完整知識（58 個檔案）
└── tools/sync_to_ai.py   ← venues.json → AI 格式（唯讀，AI 不回寫）
```

### AI 知識庫 Schema（ai_knowledge_base/schema.json）

每個場地 `venues/{id}.json` 包含：
- `identity` — 基本識別（從 venues.json 同步）
- `summary` — RAG 用精簡描述 + strengths/weaknesses/suitableEventTypes
- `risks` — 預訂提前量、旺季、常見問題
- `rules` — 結構化規定（每條有 rule/exception/penalty/negotiable）
- `pricingTips` — 省錢技巧
- `seasonal` — 旺季/淡季/折扣（新增）
- `logistics` — 停車/交通/無障礙/遊覽車（新增）
- `rooms[]` — 會議室知識（suitableEventTypes, equipment 詳細規格, loadIn 擴充, breakoutRooms）
- `ragChunks[]` — 預切 RAG 檢索片段（每段有 id/category/text/metadata）
- `inquiries` — 詢問信紀錄（pending/sent）

### 每筆知識的 metadata

```json
{
  "source": "官網租借辦法_20260331",
  "verifiedAt": "2026-04-01",
  "expiresAt": "2026-10-01",
  "confidence": "confirmed | unverified | outdated"
}
```

### 琜官網知識採集：找這些頁面

| 目標頁面 | 對應欄位 |
|--------|--------|
| 「場地須知」「租借辦法」「收費標準」 | rules, pricingTips, risks.bookingLeadTime |
| 「注意事項」「FAQ」「常見問題」 | limitations, risks.commonIssues |
| 「設備清單」「場地規格」 | equipment 詳細規格, ceilingHeight |
| 「交通資訊」「停車」 | logistics（AI 層） |
| 旺季/檔期公告 | risks.peakSeasons |

### 7 天上市計畫

詳見 `PLAN_AI_KNOWLEDGE_BASE.md`

### 當前知識覆蓋率

- 有 risks: 7/58 場地
- 有 rules: 9/58
- rooms with limitations: 38/~370
- rooms with loadIn: 2/~370

### 完整範例

`ai_knowledge_base/venues/1072.json` — 圓山大飯店（已有資料/要爬/要問 的完整對照）

---

**維護者**: le202
