# EventMaster Admin Panel

Vue 3 + Vite + Element Plus 管理後台

## 快速開始

```bash
# 安裝依賴
npm install

# 開發模式
npm run dev

# 生產建置
npm run build
```

## 功能模組

- **儀表板** - 系統概況與統計
- **場地管理** - 場地資料 CRUD
- **問題追蹤** - 資料問題追蹤與 LLM 診斷
- **爬蟲任務** - 爬蟲任務管理
- **對話記錄** - AI 對話記錄查看
- **數據分析** - 使用分析與趨勢圖表

## 部署

### Vercel

```bash
vercel
```

### Docker

已在主專案的 `docker-compose.yml` 中整合

## 環境變數

```bash
VITE_API_BASE_URL=http://localhost:8000
```

## 專案結構

```
admin/
├── src/
│   ├── api/           # API 調用
│   ├── components/    # 共用組件
│   ├── layouts/       # 佈局組件
│   ├── router/        # 路由配置
│   ├── stores/        # Pinia 狀態管理
│   ├── styles/        # 樣式文件
│   ├── utils/         # 工具函數
│   ├── views/         # 頁面組件
│   ├── App.vue
│   └── main.js
├── index.html
├── package.json
└── vite.config.js
```

## 統一管理流程

### 資料爬取流程

```
本地執行爬蟲
    ↓
scraper/ 爬取官網
    ↓
提取會議室資料
    ↓
驗證資料完整性
    ↓
發現問題？
    ├─ 是 → 記錄到 problem_tracker
    │        ↓
    │    首次遇到？
    │        ├─ 是 → LLM 診斷 → 記錄結果
    │        └─ 否 → 跳過診斷
    │
    └─ 否 → 寫入 PostgreSQL
```

### 後台管理流程

```
管理員登入 (API Key)
    ↓
查看儀表板統計
    ↓
場地管理 / 問題追蹤 / 爬蟲任務
    ↓
調用 Admin API /api/v1/admin/*
    ↓
更新資料庫
    ↓
前台自動同步
```

## 爬蟲與診斷指令

### 完整掃描

```bash
# 掃描特定場地
cd tools
python pipeline.py scan --venue 1501

# 掃描所有場地
python pipeline.py scan
```

### 查看問題

```bash
# 查看所有問題
python pipeline.py problems

# 查看特定場地的問題
python pipeline.py problems --history 1501
```

### LLM 診斷

```bash
# 診斷特定問題
python tools/llm_diagnostic.py diagnose --venue 1501 --field pricing
```

## API Key 管理

### 創建 Admin API Key

```sql
INSERT INTO api_keys (key, name, is_active, created_at)
VALUES ('your-secure-api-key-here', 'Admin', true, NOW());
```

### 使用

1. 後台登入時輸入 API Key
2. API Key 存儲在 localStorage
3. 所有請求自動攜帶 `X-API-Key` header
