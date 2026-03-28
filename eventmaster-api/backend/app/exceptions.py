"""
自定義異常類
"""

from typing import Optional, Any
from fastapi import HTTPException, status


class EventMasterException(Exception):
    """EventMaster 基礎異常"""
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        details: Optional[Any] = None
    ):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(message)


class VenueNotFoundException(EventMasterException):
    """場地不存在"""
    def __init__(self, venue_id: int):
        super().__init__(
            message=f"Venue {venue_id} not found",
            code="VENUE_NOT_FOUND",
            details={"venue_id": venue_id}
        )


class ValidationException(EventMasterException):
    """驗證錯誤"""
    def __init__(self, message: str, field: str, value: Any):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details={"field": field, "value": str(value)}
        )


class AuthenticationException(EventMasterException):
    """認證錯誤"""
    def __init__(self, message: str = "Invalid API key"):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR"
        )


class RateLimitException(EventMasterException):
    """速率限制"""
    def __init__(self, limit: int):
        super().__init__(
            message=f"Rate limit exceeded. Maximum {limit} requests per month",
            code="RATE_LIMIT_EXCEEDED",
            details={"limit": limit}
        )


class DatabaseException(EventMasterException):
    """資料庫錯誤"""
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(
            message=message,
            code="DATABASE_ERROR"
        )


# FastAPI 異常處理器
def register_exception_handlers(app):
    """註冊全局異常處理器"""

    @app.exception_handler(EventMasterException)
    async def eventmaster_exception_handler(request, exc: EventMasterException):
        """處理 EventMaster 自定義異常"""
        return {
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc: HTTPException):
        """處理 FastAPI HTTPException"""
        return {
            "success": False,
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail,
                "status_code": exc.status_code
            }
        }

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc: Exception):
        """處理所有未捕獲的異常"""
        import logging
        logging.error(f"Unhandled exception: {exc}", exc_info=True)
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": str(exc) if exc else None
            }
        }
