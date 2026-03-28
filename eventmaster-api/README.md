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

# 啟動 PostgreSQL 和 Redis（需自行安裝）

# 執行資料庫遷移
# TODO: alembic upgrade head

# 啟動開發伺服器
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API 文檔

啟動後訪問：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 測試 API

```bash
# 健康檢查
curl http://localhost:8000/health

# 取得場地列表
curl http://localhost:8000/api/v1/venues

# 取得場地詳情
curl http://localhost:8000/api/v1/venues/1086
```

## 開發工具

- **API 測試**: Postman, Insomnia, 或 /docs
- **資料庫管理**: pgAdmin (http://localhost:5050)
- **日誌**: `docker-compose logs -f backend`

## 專案結構

```
eventmaster-api/
├── backend/           # FastAPI 後端
│   ├── app/
│   │   ├── api/      # API 端點
│   │   ├── models/   # SQLAlchemy 模型
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── services/ # 業務邏輯
│   │   └── middleware/
│   ├── tests/
│   ├── main.py
│   └── requirements.txt
├── frontend/          # Next.js 前端（待開發）
├── docker-compose.yml
└── README.md
```

## 下一步

- [ ] 資料庫 Migration 腳本
- [ ] 第一個真實 API 端點（連接資料庫）
- [ ] API 認證機制
- [ ] 開發者門戶前端

---

**文檔所有者**: Jobs (CTO)
**建立日期**: 2026-04-01
