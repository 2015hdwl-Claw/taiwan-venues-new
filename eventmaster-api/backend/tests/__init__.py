"""
Pytest 配置
"""

import pytest
import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent))


@pytest.fixture
def db_session():
    """資料庫 session fixture"""
    from app.database import SyncSessionLocal
    db = SyncSessionLocal()
    yield db
    db.close()


@pytest.fixture
def test_client():
    """測試客戶端 fixture"""
    from fastapi.testclient import TestClient
    from main import app

    return TestClient(app)
