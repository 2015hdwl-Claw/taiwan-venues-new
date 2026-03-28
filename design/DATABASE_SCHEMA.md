# 資料庫Schema設計

**資料庫**: PostgreSQL 15
**ORM**: SQLAlchemy 2.0
**設計日期**: 2026-04-01

---

## 資料表設計

### 1. venues (場地)

```sql
CREATE TABLE venues (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    name_en VARCHAR(255),
    type VARCHAR(50) NOT NULL,  -- hotel, convention_center, etc.
    city VARCHAR(50) NOT NULL,
    address TEXT NOT NULL,
    contact_phone VARCHAR(20),
    contact_email VARCHAR(255),
    url TEXT,

    -- 地理位置
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),

    -- 敘述
    description TEXT,
    description_en TEXT,

    -- 價格
    price_half_day INT,
    price_full_day INT,

    -- 設備標籤
    amenities JSONB,  -- ["parking", "wifi", "projector"]

    -- 時間戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 索引
    CONSTRAINT url_format CHECK (url ~* '^https?://')
);

CREATE INDEX idx_venues_city ON venues(city);
CREATE INDEX idx_venues_type ON venues(type);
CREATE INDEX idx_venues_location ON venues USING GIST(
    point(longitude, latitude)
);
```

### 2. meeting_rooms (會議室)

```sql
CREATE TABLE meeting_rooms (
    id SERIAL PRIMARY KEY,
    venue_id INT REFERENCES venues(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,

    -- 尺寸
    length DECIMAL(5,2),  -- 公尺
    width DECIMAL(5,2),
    height DECIMAL(5,2),
    area DECIMAL(7,2),    -- 平方公尺

    -- 容量
    capacity_theater INT,
    capacity_banquet INT,
    capacity_classroom INT,
    capacity_reception INT,

    -- 設備
    amenities JSONB,

    -- 照片
    images JSONB,  -- {"main": "url", "gallery": ["url1", "url2"]}

    -- 價格
    price_half_day INT,
    price_full_day INT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_rooms_venue ON meeting_rooms(venue_id);
CREATE INDEX idx_rooms_capacity ON meeting_rooms(capacity_theater);
```

### 3. hidden_knowledge (隱藏知識)

```sql
CREATE TABLE hidden_knowledge (
    id SERIAL PRIMARY KEY,
    venue_id INT REFERENCES venues(id) ON DELETE CASCADE,

    -- 知識類型
    knowledge_type VARCHAR(50) NOT NULL,
    -- booking_tips, common_pitfalls, pro_tips, vendor_relationships

    -- 知識內容
    title VARCHAR(255),
    content TEXT NOT NULL,

    -- 來源
    source VARCHAR(100),  -- 專家姓名或來源
    verified BOOLEAN DEFAULT false,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_knowledge_venue ON hidden_knowledge(venue_id);
CREATE INDEX idx_knowledge_type ON hidden_knowledge(knowledge_type);
```

### 4. availability (可用性)

```sql
CREATE TABLE availability (
    id SERIAL PRIMARY KEY,
    venue_id INT REFERENCES venues(id) ON DELETE CASCADE,
    room_id INT REFERENCES meeting_rooms(id) ON DELETE CASCADE,

    date DATE NOT NULL,
    time_slot VARCHAR(20),  -- morning, afternoon, full_day

    status VARCHAR(20) NOT NULL,  -- available, booked, unavailable

    -- 價格（可能因日期而異）
    price_half_day INT,
    price_full_day INT,

    -- 備註
    notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(venue_id, room_id, date, time_slot)
);

CREATE INDEX idx_availability_date ON availability(date);
CREATE INDEX idx_availability_venue_date ON availability(venue_id, date);
```

### 5. api_keys (API金鑰)

```sql
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    key_prefix VARCHAR(10) NOT NULL,  -- em_***

    user_name VARCHAR(255),
    email VARCHAR(255),

    -- 權限
    permissions JSONB,  -- ["read:venues", "read:availability"]

    -- 限制
    rate_limit INT DEFAULT 1000,  -- 每月請求數

    -- 狀態
    is_active BOOLEAN DEFAULT true,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    last_used_at TIMESTAMP
);

CREATE INDEX idx_api_keys_prefix ON api_keys(key_prefix);
```

### 6. usage_logs (使用記錄)

```sql
CREATE TABLE usage_logs (
    id SERIAL PRIMARY KEY,
    api_key_id INT REFERENCES api_keys(id),

    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INT NOT NULL,

    response_time_ms INT,

    ip_address INET,
    user_agent TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_logs_api_key ON usage_logs(api_key_id);
CREATE INDEX idx_logs_created ON usage_logs(created_at);
```

---

## SQLAlchemy Models

```python
# models/venue.py
from sqlalchemy import Column, Integer, String, Text, DECIMAL, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Venue(Base):
    __tablename__ = 'venues'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    name_en = Column(String(255))
    type = Column(String(50), nullable=False)
    city = Column(String(50), nullable=False)
    address = Column(Text, nullable=False)
    contact_phone = Column(String(20))
    contact_email = Column(String(255))
    url = Column(Text)

    latitude = Column(DECIMAL(9, 6))
    longitude = Column(DECIMAL(9, 6))

    description = Column(Text)
    description_en = Column(Text)

    price_half_day = Column(Integer)
    price_full_day = Column(Integer)

    amenities = Column(JSONB)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    meeting_rooms = relationship("MeetingRoom", back_populates="venue", cascade="all, delete-orphan")
    hidden_knowledge = relationship("HiddenKnowledge", back_populates="venue", cascade="all, delete-orphan")

class MeetingRoom(Base):
    __tablename__ = 'meeting_rooms'

    id = Column(Integer, primary_key=True)
    venue_id = Column(Integer, ForeignKey('venues.id'), nullable=False)
    name = Column(String(255), nullable=False)

    length = Column(DECIMAL(5, 2))
    width = Column(DECIMAL(5, 2))
    height = Column(DECIMAL(5, 2))
    area = Column(DECIMAL(7, 2))

    capacity_theater = Column(Integer)
    capacity_banquet = Column(Integer)
    capacity_classroom = Column(Integer)
    capacity_reception = Column(Integer)

    amenities = Column(JSONB)
    images = Column(JSONB)

    price_half_day = Column(Integer)
    price_full_day = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    venue = relationship("Venue", back_populates="meeting_rooms")

class HiddenKnowledge(Base):
    __tablename__ = 'hidden_knowledge'

    id = Column(Integer, primary_key=True)
    venue_id = Column(Integer, ForeignKey('venues.id'), nullable=False)

    knowledge_type = Column(String(50), nullable=False)
    title = Column(String(255))
    content = Column(Text, nullable=False)

    source = Column(String(100))
    verified = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    venue = relationship("Venue", back_populates="hidden_knowledge")
```

---

## ER圖

```
┌─────────────┐
│   venues    │
├─────────────┤
│ id (PK)     │
│ name        │
│ city        │
│ address     │
│ ...         │
└──────┬──────┘
       │
       ├──┬──────────────────┐
       │                     │
       ▼                     ▼
┌──────────────┐     ┌──────────────────┐
│meeting_rooms │     │ hidden_knowledge │
├──────────────┤     ├──────────────────┤
│ id (PK)      │     │ id (PK)          │
│ venue_id (FK)│     │ venue_id (FK)    │
│ name         │     │ knowledge_type   │
│ ...          │     │ content          │
└──────────────┘     └──────────────────┘

┌──────────────┐
│ availability │
├──────────────┤
│ id (PK)      │
│ venue_id (FK)│
│ room_id (FK) │
│ date         │
│ ...          │
└──────────────┘
```

---

**文檔所有者**: Jobs (CTO)
**完成日期**: 2026-04-01
**版本**: 1.0
