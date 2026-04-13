"""
資料庫模型 - 爬蟲任務記錄
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.venue import Base


class ScrapeTask(Base):
    """爬蟲任務記錄"""
    __tablename__ = 'scrape_tasks'

    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey('venues.id'), nullable=False, index=True)
    task_type = Column(String(50), nullable=False)  # full, incremental, verify
    status = Column(String(20), nullable=False, default='pending', index=True)  # pending, running, success, failed
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    rooms_found = Column(Integer, default=0)
    problems_found = Column(Integer, default=0)
    error_message = Column(Text)
    tech_report = Column(JSON)  # 技術偵測報告
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 關聯
    venue = relationship("Venue", back_populates="scrape_tasks")

    def to_dict(self):
        return {
            'id': self.id,
            'venueId': self.venue_id,
            'taskType': self.task_type,
            'status': self.status,
            'startedAt': self.started_at.isoformat() if self.started_at else None,
            'completedAt': self.completed_at.isoformat() if self.completed_at else None,
            'roomsFound': self.rooms_found,
            'problemsFound': self.problems_found,
            'errorMessage': self.error_message,
            'techReport': self.tech_report,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }
