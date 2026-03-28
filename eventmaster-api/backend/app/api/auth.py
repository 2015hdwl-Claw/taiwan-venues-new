"""
認證 API 端點
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.database import SyncSessionLocal, get_db
from app.models.api_key import APIKey
from app.auth import APIKeyManager, get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# ===== Pydantic Schemas =====

class RegisterRequest(BaseModel):
    """註冊 API Key 請求"""
    name: str
    email: EmailStr
    use_case: str = Field(description="描述您的使用場景")


class RegisterResponse(BaseModel):
    """註冊 API Key 回應"""
    api_key: str
    message: str
    info: dict


class VerifyResponse(BaseModel):
    """驗證 API Key 回應"""
    valid: bool
    user_info: Optional[dict] = None


# ===== 端點實作 =====

@router.post("/register", response_model=dict)
async def register_api_key(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    註冊新的 API Key

    免費額度：前1000次調用/月
    """
    try:
        # 生成 API Key
        api_key, key_prefix, key_hash = APIKeyManager.generate_api_key()

        # 計算過期時間（1年後）
        expires_at = datetime.utcnow() + timedelta(days=365)

        # 建立資料庫記錄
        api_key_record = APIKey(
            key_hash=key_hash,
            key_prefix=key_prefix,
            user_name=request.name,
            email=request.email,
            permissions=["read:venues", "read:availability"],
            rate_limit=1000,  # 免費額度
            expires_at=expires_at
        )

        db.add(api_key_record)
        db.commit()
        db.refresh(api_key_record)

        logger.info(f"✅ New API key registered: {key_prefix} ({request.email})")

        return {
            "success": True,
            "data": {
                "api_key": api_key,
                "message": "API key created successfully",
                "info": {
                    "name": request.name,
                    "rate_limit": 1000,
                    "expires_at": expires_at.isoformat(),
                    "permissions": ["read:venues", "read:availability"]
                }
            }
        }

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Failed to register API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to create API key")


@router.post("/verify")
async def verify_api_key(
    api_key: str,
    db: Session = Depends(get_db)
):
    """
    驗證 API Key

    用於測試 API Key 是否有效
    """
    try:
        # 檢查格式
        if not api_key.startswith("em_"):
            return {
                "success": False,
                "error": {
                    "code": "INVALID_FORMAT",
                    "message": "API key must start with 'em_'"
                }
            }

        # 查詢資料庫
        key_prefix = api_key[:10]
        key_record = db.query(APIKey).filter(
            APIKey.key_prefix == key_prefix
        ).first()

        if not key_record:
            return {
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "API key not found"
                }
            }

        # 驗證
        if not APIKeyManager.verify_api_key(api_key, key_record.key_hash):
            return {
                "success": False,
                "error": {
                    "code": "INVALID",
                    "message": "API key is invalid"
                }
            }

        # 檢查狀態
        if not key_record.is_active:
            return {
                "success": False,
                "error": {
                    "code": "INACTIVE",
                    "message": "API key is inactive"
                }
            }

        # 檢查過期
        if key_record.expires_at and key_record.expires_at < datetime.utcnow():
            return {
                "success": False,
                "error": {
                    "code": "EXPIRED",
                    "message": f"API key expired on {key_record.expires_at.isoformat()}"
                }
            }

        return {
            "success": True,
            "data": {
                "valid": True,
                "user_info": {
                    "name": key_record.user_name,
                    "email": key_record.email,
                    "rate_limit": key_record.rate_limit,
                    "permissions": key_record.permissions,
                    "expires_at": key_record.expires_at.isoformat() if key_record.expires_at else None
                }
            }
        }

    except Exception as e:
        logger.error(f"❌ Failed to verify API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to verify API key")


@router.get("/me")
async def get_current_key_info(
    user: dict = Depends(get_current_user)
):
    """
    取得當前 API Key 資訊

    需要認證
    """
    return {
        "success": True,
        "data": {
            "user": user
        }
    }
