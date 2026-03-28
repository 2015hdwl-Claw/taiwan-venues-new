"""
API認證與授權
"""

import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from app.exceptions import AuthenticationException

# API Key Header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class APIKeyManager:
    """API Key 管理器"""

    @staticmethod
    def generate_api_key() -> tuple[str, str]:
        """
        生成 API Key

        Returns:
            (api_key, key_prefix) - 完整的key和前綴
        """
        # 生成隨機 key
        random_bytes = secrets.token_bytes(16)
        api_key = f"em_{random_bytes.hex()}"

        # 生成前綴（用於快速查找）
        key_prefix = api_key[:10]

        # 生成 hash（用於存儲）
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        return api_key, key_prefix, key_hash

    @staticmethod
    def verify_api_key(api_key: str, stored_hash: str) -> bool:
        """
        驗證 API Key

        Args:
            api_key: 用戶提供的 API Key
            stored_hash: 資料庫中存儲的 hash

        Returns:
            是否有效
        """
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        return secrets.compare_digest(key_hash, stored_hash)


class APIKeyAuth:
    """API Key 認證依賴"""

    def __init__(self, db: Session):
        self.db = db

    async def __call__(self, api_key: str = Depends(api_key_header)) -> dict:
        """
        驗證 API Key 並返回用戶資訊

        Args:
            api_key: 從 header 中提取的 API Key

        Returns:
            API Key 資訊

        Raises:
            AuthenticationException: 認證失敗
        """
        if not api_key:
            raise AuthenticationException("Missing API key")

        # 檢查是否以 em_ 開頭
        if not api_key.startswith("em_"):
            raise AuthenticationException("Invalid API key format")

        # 查詢資料庫（使用前綴快速查找）
        from app.models.api_key import APIKey
        key_prefix = api_key[:10]

        key_record = self.db.query(APIKey).filter(
            APIKey.key_prefix == key_prefix
        ).first()

        if not key_record:
            raise AuthenticationException("API key not found")

        # 驗證 key
        if not APIKeyManager.verify_api_key(api_key, key_record.key_hash):
            raise AuthenticationException("Invalid API key")

        # 檢查是否啟用
        if not key_record.is_active:
            raise AuthenticationException("API key is inactive")

        # 檢查是否過期
        if key_record.expires_at and key_record.expires_at < datetime.utcnow():
            raise AuthenticationException("API key has expired")

        # 更新最後使用時間
        key_record.last_used_at = datetime.utcnow()
        self.db.commit()

        return {
            "id": key_record.id,
            "user_name": key_record.user_name,
            "email": key_record.email,
            "permissions": key_record.permissions or [],
            "rate_limit": key_record.rate_limit
        }


def get_current_user(db: Session = Depends(get_db)):
    """
    取得當前用戶的依賴（用於路由中）

    用法:
        @router.get("/protected")
        async def protected_endpoint(user: dict = Depends(get_current_user)):
            return {"user": user}
    """
    return APIKeyAuth(db)


def require_permission(permission: str):
    """
    檢查權限的裝飾器工廠

    用法:
        @router.get("/admin")
        @require_permission("admin")
        async def admin_endpoint():
            return {"message": "Admin only"}
    """
    def decorator(func):
        async def wrapper(*args, user: dict = Depends(get_current_user), **kwargs):
            if permission not in user.get("permissions", []):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{permission}' required"
                )
            return await func(*args, user=user, **kwargs)
        return wrapper
    return decorator


# 測試用的 API Key（開發環境）
DEV_API_KEY = "em_dev_test_key_12345678901234567890"
DEV_API_KEY_HASH = hashlib.sha256(DEV_API_KEY.encode()).hexdigest()
