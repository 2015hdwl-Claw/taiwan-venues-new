@echo off
echo 🚀 EventMaster API 快速啟動腳本
echo ================================

REM 進入後端目錄
cd backend

REM 檢查 .env 是否存在
if not exist .env (
    echo ⚠️  .env 不存在，從 .env.example 複製...
    copy .env.example .env
    echo ✅ .env 已建立
)

REM 回到專案根目錄
cd ..

REM 啟動 Docker Compose
echo.
echo 📦 啟動 Docker 服務...
docker-compose up -d db redis

REM 等待資料庫啟動
echo.
echo ⏳ 等待資料庫啟動（5秒）...
timeout /t 5 /nobreak

REM 初始化資料庫
echo.
echo 🔧 初始化資料庫...
cd backend
python -c "from app.database import init_db; init_db()"

REM 匯入資料
echo.
echo 📊 匯入場地資料...
python scripts\import_venues.py

REM 啟動 API
echo.
echo 🎉 啟動 FastAPI...
echo API 文檔: http://localhost:8000/docs
echo.
uvicorn main:app --reload --host 0.0.0.0 --port 8000
