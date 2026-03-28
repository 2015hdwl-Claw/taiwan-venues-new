# EventMaster API - 快速啟動指南

## 🚀 一鍵啟動（推薦）

### Windows
```bash
setup_and_run.bat
```

### Linux/Mac
```bash
chmod +x setup_and_run.sh
./setup_and_run.sh
```

這個腳本會自動：
1. 啟動 PostgreSQL 和 Redis
2. 初始化資料庫表格
3. 從 venues.json 匯入 52 個場地
4. 啟動 FastAPI 伺服器

---

## 📖 手動啟動

### 1. 啟動 Docker 服務
```bash
docker-compose up -d db redis
```

### 2. 初始化資料庫
```bash
cd backend
python -c "from app.database import init_db; init_db()"
```

### 3. 匯入場地資料
```bash
python scripts/import_venues.py
```

### 4. 啟動 API
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## ✅ 測試 API

### 1. 健康檢查
```bash
curl http://localhost:8000/health
```

### 2. 取得場地列表
```bash
curl http://localhost:8000/api/v1/venues
```

### 3. 取得場地詳情
```bash
curl http://localhost:8000/api/v1/venues/1086
```

### 4. 城市篩選
```bash
curl "http://localhost:8000/api/v1/venues?city=台北"
```

### 5. 容量篩選
```bash
curl "http://localhost:8000/api/v1/venues?capacity_min=300"
```

---

## 📚 API 文檔

啟動後訪問：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

在 Swagger UI 中你可以：
- 查看所有 API 端點
- 測試 API 請求
- 查看請求/回應格式

---

## 🗄️ 資料庫管理

### 查看 PostgreSQL
```bash
# 連接到資料庫
docker exec -it eventmaster-api-db-1 psql -U eventmaster -d eventmaster

# 查詢場地
SELECT id, name, city FROM venues LIMIT 10;

# 查詢會議室
SELECT id, name, capacity_theater FROM meeting_rooms LIMIT 10;

# 退出
\q
```

### 使用 pgAdmin
訪問: http://localhost:5050
- Email: admin@eventmaster.tw
- Password: admin

---

## 🛑 停止服務

```bash
# 停止所有服務
docker-compose down

# 停止並刪除資料（注意：會刪除所有資料）
docker-compose down -v
```

---

## 🐛 常見問題

### 1. 找不到 venues.json
**問題**: `❌ 找不到 venues.json`

**解決**:
```bash
# 確認 venues.json 在上層目錄
ls ../../venues.json

# 或修改 scripts/import_venues.py 中的路徑
```

### 2. 資料庫連接失敗
**問題**: `connection refused`

**解決**:
```bash
# 確認 PostgreSQL 正在運行
docker ps | grep postgres

# 查看日誌
docker-compose logs db
```

### 3. 端口衝突
**問題**: `port 8000 is already in use`

**解決**:
```bash
# 修改端口
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

---

## 📊 已實作的端點

| 端點 | 方法 | 說明 | 狀態 |
|------|------|------|------|
| `/health` | GET | 健康檢查 | ✅ |
| `/api/v1/venues` | GET | 場地列表（支援篩選、分頁） | ✅ |
| `/api/v1/venues/{id}` | GET | 場地詳情 | ✅ |
| `/api/v1/venues/{id}/rooms` | GET | 會議室列表 | ✅ |

---

## 🎯 下一步

- [ ] 完成 availability 端點（即時可用性）
- [ ] 完成 search 端點（智能搜尋）
- [ ] 添加 API 認證（API Key）
- [ ] 開發者門戶前端

---

**準備好開始了嗎？執行 `setup_and_run.bat` 或 `./setup_and_run.sh`！**
