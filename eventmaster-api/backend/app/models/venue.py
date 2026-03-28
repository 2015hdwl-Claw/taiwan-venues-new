"""
SQLAlchemy Models - 場地資料模型
"""

from sqlalchemy import Column, Integer, String, Text, DECIMAL, Boolean, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Venue(Base):
    """場地主表"""
    __tablename__ = 'venues'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    name_en = Column(String(255))
    type = Column(String(50), nullable=False, index=True)
    city = Column(String(50), nullable=False, index=True)
    address = Column(Text, nullable=False)
    contact_phone = Column(String(20))
    contact_email = Column(String(255))
    url = Column(Text)

    # 地理位置
    latitude = Column(DECIMAL(9, 6))
    longitude = Column(DECIMAL(9, 6))

    # 敘述
    description = Column(Text)
    description_en = Column(Text)

    # 價格
    price_half_day = Column(Integer)
    price_full_day = Column(Integer)

    # 設備標籤 (JSONB)
    amenities = Column(JSON)

    # 時間戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    meeting_rooms = relationship("MeetingRoom", back_populates="venue", cascade="all, delete-orphan")
    hidden_knowledge = relationship("HiddenKnowledge", back_populates="venue", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_venues_location', 'latitude', 'longitude'),
    )


class MeetingRoom(Base):
    """會議室"""
    __tablename__ = 'meeting_rooms'

    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey('venues.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False)

    # 尺寸（公尺）
    length = Column(DECIMAL(5, 2))
    width = Column(DECIMAL(5, 2))
    height = Column(DECIMAL(5, 2))
    area = Column(DECIMAL(7, 2))  # 平方公尺

    # 容量
    capacity_theater = Column(Integer, index=True)
    capacity_banquet = Column(Integer)
    capacity_classroom = Column(Integer)
    capacity_reception = Column(Integer)

    # 設備 (JSONB)
    amenities = Column(JSON)

    # 照片 (JSONB)
    images = Column(JSON)

    # 價格
    price_half_day = Column(Integer)
    price_full_day = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    venue = relationship("Venue", back_populates="meeting_rooms")


class HiddenKnowledge(Base):
    """隱藏知識"""
    __tablename__ = 'hidden_knowledge'

    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey('venues.id', ondelete='CASCADE'), nullable=False)

    # 知識類型
    knowledge_type = Column(String(50), nullable=False, index=True)
    # booking_tips, common_pitfalls, pro_tips, vendor_relationships

    title = Column(String(255))
    content = Column(Text, nullable=False)

    # 來源
    source = Column(String(100))
    verified = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    venue = relationship("Venue", back_populates="hidden_knowledge")


class Availability(Base):
    """可用性"""
    __tablename__ = 'availability'

    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey('venues.id', ondelete='CASCADE'))
    room_id = Column(Integer, ForeignKey('meeting_rooms.id', ondelete='CASCADE'))

    date = Column(DateTime, nullable=False, index=True)
    time_slot = Column(String(20))  # morning, afternoon, full_day

    status = Column(String(20), nullable=False)  # available, booked, unavailable

    # 價格（可能因日期而異）
    price_half_day = Column(Integer)
    price_full_day = Column(Integer)

    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_availability_venue_date', 'venue_id', 'date'),
    )
