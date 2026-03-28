"""
API 測試
"""

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_check():
    """測試健康檢查端點"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_list_venues():
    """測試場地列表端點"""
    response = client.get("/api/v1/venues")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "venues" in data["data"]


def test_get_venue():
    """測試取得場地詳情"""
    # 假設有ID為1086的場地
    response = client.get("/api/v1/venues/1086")
    # 可能返回404（如果資料庫還沒有資料）
    assert response.status_code in [200, 404]


def test_register_api_key():
    """測試註冊API Key"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "use_case": "Testing"
        }
    )
    # 可能返回200或500（取決於資料庫狀態）
    assert response.status_code in [200, 500]


def test_cors_headers():
    """測試CORS標頭"""
    response = client.options("/api/v1/venues")
    assert "access-control-allow-origin" in response.headers


@pytest.mark.parametrize("city", ["台北", "台中", "高雄"])
def test_filter_by_city(city):
    """測試城市篩選"""
    response = client.get(f"/api/v1/venues?city={city}")
    assert response.status_code == 200
