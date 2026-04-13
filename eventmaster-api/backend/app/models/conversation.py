"""
資料庫模型 - AI 對話記錄
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.venue import Base


class Conversation(Base):
    """AI 對話記錄"""
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)  # 前端 session
    user_query = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    venues_recommended = Column(JSON)  # 推薦的場地 ID
    feedback = Column(Integer)  # 使用者評分 1-5
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    user_fingerprint = Column(String(100))  # 匿名識別

    def to_dict(self):
        return {
            'id': self.id,
            'sessionId': self.session_id,
            'userQuery': self.user_query,
            'aiResponse': self.ai_response,
            'venuesRecommended': self.venues_recommended,
            'feedback': self.feedback,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'userFingerprint': self.user_fingerprint,
        }
