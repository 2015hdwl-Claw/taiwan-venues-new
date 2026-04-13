# EventMaster API - 開發環境啟動指南

## 快速啟動

### 1. 使用 Docker Compose（推薦）

```bash
# 進入專案目錄
cd eventmaster-api

# 啟動所有服務
docker-compose up -d

# 查看日誌
docker-compose logs -f backend

# 停止服務
docker-compose down
```

### 2. 本地開發（不使用 Docker）

**前置需求**：
- Python 3.11+
- PostgreSQL 15
- Redis 7

```bash
# 安裝依賴
cd backend
pip install -r requirements.txt

# 複製環境變數
cp .env.example .env

# 初始化資料庫
python scripts/init_db.py

# 啟動開發伺服器
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API 文檔

啟動後訪問：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Admin API 端點

### 儀表板
```
GET /api/v1/admin/dashboard
```
返回系統統計資料

### 問題管理
```
GET /api/v1/admin/problems?venue_id=1501&status=open
POST /api/v1/admin/problems/{id}/diagnose
PUT /api/v1/admin/problems/{id}/status?status=fixed
```

### 爬蟲任務
```
GET /api/v1/admin/scrape-tasks
POST /api/v1/admin/scrape-tasks
```

### 對話記錄
```
GET /api/v1/admin/conversations?session_id=xxx
```

### 使用分析
```
GET /api/v1/admin/analytics?days=30
```

## 測試 API

```bash
# 健康檢查
curl http://localhost:8000/health

# Admin 儀表板
curl http://localhost:8000/api/v1/admin/dashboard

# 問題列表
curl http://localhost:8000/api/v1/admin/problems

# 觸發 LLM 診斷
curl -X POST http://localhost:8000/api/v1/admin/problems/1/diagnose
```

## 專案結構

```
eventmaster-api/
├── backend/           # FastAPI 後端
│   ├── app/
│   │   ├── api/      # API 端點
│   │   │   ├── admin.py   # Admin API (Phase 2)
│   │   │   ├── venues.py
│   │   │   ├── auth.py
│   │   │   ├── availability.py
│   │   │   └── search.py
│   │   ├── models/   # SQLAlchemy 模型
│   │   │   ├── venue.py
│   │   │   ├── problem.py    # 問題追蹤 (新增)
│   │   │   ├── scrape_task.py  # 爬蟲任務 (新增)
│   │   │   ├── conversation.py # 對話記錄 (新增)
│   │   │   └── query_log.py     # 查詢記錄 (新增)
│   │   ├── schemas/
│   │   ├── services/
│   │   └── middleware/
│   ├── scripts/
│   │   └── init_db.py    # 資料庫初始化 (新增)
│   ├── tests/
│   ├── main.py
│   └── requirements.txt
├── frontend/          # Next.js 前端（待開發）
├── docker-compose.yml
└── README.md
```

## 資料庫模型

新增模型 (Phase 2):
- `Problem` - 問題追蹤
- `ScrapeTask` - 爬蟲任務記錄
- `Conversation` - AI 對話記錄
- `QueryLog` - 查詢記錄

## Python 工具整合

```bash
# 在 taiwan-venues-new/ 目錄下使用

# 問題追蹤
python tools/problem_tracker.py list
python tools/problem_tracker.py stats
python tools/problem_tracker.py history 1501

# LLM 診斷
python tools/llm_diagnostic.py diagnose --venue 1501 --field pricing
python tools/llm_diagnostic.py from-tracker --limit 5

# Pipeline 整合指令
python tools/pipeline.py scan --venue 1501
python tools/pipeline.py diagnose --venue 1501
python tools/pipeline.py problems --stats
python tools/pipeline.py problems --history 1501
```

## Phase 3: 後台管理界面

Vue 3 + Vite + Element Plus 管理後台已完成開發，包含以下功能：

### 功能模組

1. **儀表板 (Dashboard)** - 系統概況統計
2. **場地管理 (Venues)** - 場地資料 CRUD
3. **問題追蹤 (Problems)** - 資料問題追蹤與 LLM 診斷
4. **爬蟲任務 (Scrape Tasks)** - 爬蟲任務管理
5. **對話記錄 (Conversations)** - AI 對話記錄查看
6. **數據分析 (Analytics)** - 使用分析與趨勢圖表

### 本地開發

```bash
# 進入管理後台目錄
cd admin

# 安裝依賴
npm install

# 啟動開發伺服器 (http://localhost:3001)
npm run dev

# 生產建置
npm run build
```

### 部署

```bash
# 方式 1: Vercel 部署
cd admin
vercel

# 方式 2: Docker Compose (包含後台)
docker-compose up -d
```

### 後台訪問

- 本地開發: http://localhost:3001
- 需要 API Key 才能登入

---

## 統一管理流程

### 資料流

```
┌─────────────────────────────────────────────────────────────────────┐
│                        統一管理流程                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐    ┌──────────────────┐    ┌─────────────────┐   │
│  │  前台網站     │    │   API Gateway    │    │   後台管理界面   │   │
│  │  (Static)    │◄──►│   (FastAPI)      │◄──►│  (Vue Admin)    │   │
│  │              │    │                  │    │                 │   │
│  └──────────────┘    └──────────────────┘    └─────────────────┘   │
│         │                   │                        │              │
│         │                   ▼                        │              │
│         │        ┌──────────────────┐               │              │
│         │        │   PostgreSQL     │               │              │
│         │        │   (主資料庫)      │               │              │
│         │        └──────────────────┘               │              │
│         │                   ▲                        │              │
│         │                   │                        │              │
│         │           ┌───────┴────────┐              │              │
│         │           │                 │              │              │
│         │    ┌──────▼─────┐   ┌──────▼──────┐       │              │
│         │    │  爬蟲服務   │   │ LLM 診斷    │       │              │
│         │    │  Scraper   │   │ Diagnostic  │       │              │
│         │    └────────────┘   └─────────────┘       │              │
│         │                   │                        │              │
│         │    ┌──────────────▼──────────────────┐    │              │
│         │    │      問題追蹤系統                │    │              │
│         │    │   (Problem Tracker)            │    │              │
│         │    └────────────────────────────────┘    │              │
│         │                   │                        │              │
│         └───────────────────┼────────────────────────┘              │
│                             │                                       │
│                    ┌────────▼────────┐                             │
│                    │  venues.json    │                             │
│                    │  (來源資料)      │                             │
│                    └─────────────────┘                             │
└─────────────────────────────────────────────────────────────────────┘
```

### 工作流程

1. **資料爬取**
   - 後台新增爬蟲任務
   - 爬蟲服務執行並更新資料庫
   - 問題自動記錄到追蹤系統

2. **問題診斷**
   - 問題追蹤系統避免重複診斷
   - LLM 只在首次遇到問題時診斷
   - 診斷結果記錄並提供修復建議

3. **資料管理**
   - 前台網站從 API 獲取資料
   - 後台管理所有資料操作
   - 資料同步更新

---

**文檔所有者**: Jobs (CTO)
**建立日期**: 2026-04-01
**更新日期**: 2026-04-13 (Phase 3 完成)
