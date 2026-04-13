"""
EventMaster API - 主應用程式
AI時代的活動場地智能接口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全域變量
app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用生命週期管理"""
    # 啟動時執行
    logger.info("🚀 EventMaster API 啟動中...")

    # 註冊異常處理器
    from app.exceptions import register_exception_handlers
    register_exception_handlers(app)

    app_state["startup"] = True

    yield

    # 關閉時執行
    logger.info("👋 EventMaster API 關閉中...")
    app_state["startup"] = False

# 創建 FastAPI 應用
app = FastAPI(
    title="EventMaster API",
    description="AI時代的活動場地智能接口",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生產環境應限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 健康檢查端點
@app.get("/health")
async def health_check():
    """健康檢查"""
    return {
        "status": "healthy",
        "service": "EventMaster API",
        "version": "1.0.0"
    }

# 根路徑
@app.get("/")
async def root():
    """API 根路徑"""
    return {
        "message": "EventMaster API",
        "description": "AI時代的活動場地智能接口",
        "version": "1.0.0",
        "docs": "/docs"
    }

# 匯入路由
from app.api import venues, auth, availability, search, admin
app.include_router(venues.router, prefix="/api/v1/venues", tags=["venues"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(availability.router, prefix="/api/v1/availability", tags=["availability"])
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
