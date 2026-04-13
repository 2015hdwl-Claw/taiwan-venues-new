"""
資料庫連接配置
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from app.models.venue import Base
# 導入所有模型以確保表格被註冊
from app.models.problem import Problem
from app.models.scrape_task import ScrapeTask
from app.models.conversation import Conversation
from app.models.query_log import QueryLog
from app.models.api_key import APIKey
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 支援 SQLite 開發環境
USE_SQLITE = os.getenv("USE_SQLITE", "false").lower() == "true"

if USE_SQLITE:
    DATABASE_URL = "sqlite:///./eventmaster.db"
else:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://eventmaster:eventpass@localhost:5432/eventmaster")

# 同步引擎（用於 migration 和腳本）
if USE_SQLITE:
    sync_engine = create_engine(
        DATABASE_URL,
        echo=True if os.getenv("DEBUG") == "true" else False,
        connect_args={"check_same_thread": False}  # SQLite 需要此設定
    )
else:
    sync_engine = create_engine(
        DATABASE_URL,
        echo=True if os.getenv("DEBUG") == "true" else False,
        pool_pre_ping=True
    )

# 同步 Session
SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)

# 異步引擎（用於 API）
if USE_SQLITE:
    # SQLite 使用 aiosqlite
    ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
else:
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True if os.getenv("DEBUG") == "true" else False
)

# 異步 Session
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


def get_db() -> Session:
    """取得資料庫 session（依賴注入）"""
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncSession:
    """取得異步資料庫 session"""
    async with AsyncSessionLocal() as session:
        yield session


def init_db():
    """初始化資料庫（建立所有表格）"""
    Base.metadata.create_all(bind=sync_engine)
    print("✅ 資料庫表格已建立")
