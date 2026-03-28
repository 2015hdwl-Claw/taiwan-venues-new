"""
API Key 資料模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.venue import Base


class APIKey(Base):
    """API 金鑰"""
    __tablename__ = 'api_keys'

    id = Column(Integer, primary_key=True, index=True)
    key_hash = Column(String(255), unique=True, nullable=False, index=True)
    key_prefix = Column(String(10), nullable=False, index=True)

    user_name = Column(String(255))
    email = Column(String(255))

    # 權限（JSONB）
    permissions = Column(JSON)  # ["read:venues", "read:availability"]

    # 限制
    rate_limit = Column(Integer, default=1000)  # 每月請求數

    # 狀態
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    last_used_at = Column(DateTime)

    # 關聯
    usage_logs = relationship("UsageLog", back_populates="api_key")


class UsageLog(Base):
    """使用記錄"""
    __tablename__ = 'usage_logs'

    id = Column(Integer, primary_key=True, index=True)
    api_key_id = Column(Integer, ForeignKey('api_keys.id'))

    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)  # GET, POST, etc.
    status_code = Column(Integer, nullable=False)

    response_time_ms = Column(Integer)

    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(String(512))

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # 關聯
    api_key = relationship("APIKey", back_populates="usage_logs")
