"""
資料庫模型 - 問題追蹤
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.venue import Base


class Problem(Base):
    """資料問題追蹤"""
    __tablename__ = 'problems'

    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey('venues.id'), nullable=False, index=True)
    problem_type = Column(String(50), nullable=False, index=True)  # missing_rooms, missing_pricing, ...
    field = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False)  # critical, high, medium, low
    diagnosis = Column(Text)
    can_fix = Column(Boolean, nullable=True)
    fix_action = Column(Text)
    status = Column(String(20), nullable=False, default='open', index=True)  # open, diagnosing, fixing, fixed, wontfix, confirmed_absent
    first_seen = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    occurrences = Column(Integer, default=1, nullable=False)
    notes = Column(Text)

    # 關聯
    venue = relationship("Venue", back_populates="problems")

    def to_dict(self):
        return {
            'id': self.id,
            'venueId': self.venue_id,
            'problemType': self.problem_type,
            'field': self.field,
            'severity': self.severity,
            'diagnosis': self.diagnosis,
            'canFix': self.can_fix,
            'fixAction': self.fix_action,
            'status': self.status,
            'firstSeen': self.first_seen.isoformat() if self.first_seen else None,
            'lastSeen': self.last_seen.isoformat() if self.last_seen else None,
            'occurrences': self.occurrences,
            'notes': self.notes,
        }
