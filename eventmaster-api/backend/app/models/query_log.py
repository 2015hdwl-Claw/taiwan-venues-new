"""
資料庫模型 - 查詢記錄
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from app.models.venue import Base


class QueryLog(Base):
    """查詢記錄"""
    __tablename__ = 'query_logs'

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    endpoint = Column(String(100), nullable=False)
    params = Column(JSON)
    response_count = Column(Integer, default=0)
    execution_time_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'sessionId': self.session_id,
            'endpoint': self.endpoint,
            'params': self.params,
            'responseCount': self.response_count,
            'executionTimeMs': self.execution_time_ms,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }
