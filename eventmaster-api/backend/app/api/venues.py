"""
Venues API - 場地端點（使用真實資料庫）
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.venue import Venue, MeetingRoom

router = APIRouter()

# ===== Pydantic Schemas =====

class ContactInfo(BaseModel):
    """聯絡資訊"""
    phone: Optional[str] = None
    email: Optional[str] = None

class Location(BaseModel):
    """地理位置"""
    lat: Optional[float] = None
    lng: Optional[float] = None

class VenueSummary(BaseModel):
    """場地摘要"""
    total_rooms: int
    max_capacity: Optional[int] = None

class VenueListItem(BaseModel):
    """場地列表項"""
    id: int
    name: str
    type: str
    city: str
    address: str
    contact: Optional[ContactInfo] = None
    location: Optional[Location] = None
    summary: VenueSummary
    suitability_score: float = Field(default=0.8, ge=0, le=1)

class MeetingRoomItem(BaseModel):
    """會議室項目"""
    id: int
    name: str
    area: Optional[float] = None
    capacity_theater: Optional[int] = None
    capacity_banquet: Optional[int] = None
    capacity_classroom: Optional[int] = None

class VenueDetail(BaseModel):
    """場地詳情"""
    id: int
    name: str
    type: str
    city: str
    address: str
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    location: Optional[Location] = None
    meeting_rooms: List[MeetingRoomItem] = []

# ===== 端點實作 =====

@router.get("/", response_model=dict)
async def list_venues(
    city: Optional[str] = Query(None, description="城市篩選"),
    capacity_min: Optional[int] = Query(None, ge=1, description="最小容量"),
    page: int = Query(1, ge=1, description="頁碼"),
    limit: int = Query(20, ge=1, le=100, description="每頁數量"),
    db: Session = Depends(get_db)
):
    """
    取得場地列表

    支援篩選、分頁
    """
    # 建立查詢
    query = db.query(Venue)

    # 城市篩選
    if city:
        query = query.filter(Venue.city == city)

    # 容量篩選（透過會議室）
    if capacity_min:
        query = query.join(Venue.meeting_rooms).filter(
            MeetingRoom.capacity_theater >= capacity_min
        )

    # 總數
    total = query.count()

    # 分頁
    total_pages = (total + limit - 1) // limit
    offset = (page - 1) * limit
    venues = query.offset(offset).limit(limit).all()

    # 序列化
    venues_data = []
    for venue in venues:
        # 計算摘要
        total_rooms = len(venue.meeting_rooms)
        max_capacity = max(
            [room.capacity_theater or 0 for room in venue.meeting_rooms],
            default=0
        )

        venues_data.append({
            "id": venue.id,
            "name": venue.name,
            "type": venue.type,
            "city": venue.city,
            "address": venue.address,
            "contact": {
                "phone": venue.contact_phone,
                "email": venue.contact_email
            } if venue.contact_phone or venue.contact_email else None,
            "location": {
                "lat": float(venue.latitude) if venue.latitude else None,
                "lng": float(venue.longitude) if venue.longitude else None
            } if venue.latitude and venue.longitude else None,
            "summary": {
                "total_rooms": total_rooms,
                "max_capacity": max_capacity if max_capacity > 0 else None
            },
            "suitability_score": 0.8,  # TODO: 計算真實分數
            "why_recommended": f"{venue.name} 位於{venue.city}，交通便利"
        })

    return {
        "success": True,
        "data": {
            "venues": venues_data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": total_pages
            }
        },
        "meta": {
            "request_id": "mock-uuid",
            "timestamp": datetime.utcnow().isoformat()
        }
    }

@router.get("/{venue_id}")
async def get_venue(
    venue_id: int,
    db: Session = Depends(get_db)
):
    """
    取得單一場地詳情
    """
    # 查詢場地
    venue = db.query(Venue).filter(Venue.id == venue_id).first()

    if not venue:
        raise HTTPException(status_code=404, detail=f"Venue {venue_id} not found")

    # 序列化會議室
    rooms_data = []
    for room in venue.meeting_rooms:
        rooms_data.append({
            "id": room.id,
            "name": room.name,
            "area": float(room.area) if room.area else None,
            "capacity_theater": room.capacity_theater,
            "capacity_banquet": room.capacity_banquet,
            "capacity_classroom": room.capacity_classroom
        })

    return {
        "success": True,
        "data": {
            "venue": {
                "id": venue.id,
                "name": venue.name,
                "type": venue.type,
                "city": venue.city,
                "address": venue.address,
                "contact_phone": venue.contact_phone,
                "contact_email": venue.contact_email,
                "url": venue.url,
                "description": venue.description,
                "location": {
                    "lat": float(venue.latitude) if venue.latitude else None,
                    "lng": float(venue.longitude) if venue.longitude else None
                } if venue.latitude and venue.longitude else None,
                "meeting_rooms": rooms_data
            }
        }
    }

@router.get("/{venue_id}/rooms")
async def get_venue_rooms(
    venue_id: int,
    db: Session = Depends(get_db)
):
    """
    取得場地的所有會議室
    """
    venue = db.query(Venue).filter(Venue.id == venue_id).first()

    if not venue:
        raise HTTPException(status_code=404, detail=f"Venue {venue_id} not found")

    rooms_data = []
    for room in venue.meeting_rooms:
        rooms_data.append({
            "id": room.id,
            "name": room.name,
            "dimensions": {
                "area": float(room.area) if room.area else None
            },
            "capacity": {
                "theater": room.capacity_theater,
                "banquet": room.capacity_banquet,
                "classroom": room.capacity_classroom
            },
            "amenities": room.amenities,
            "images": room.images
        })

    return {
        "success": True,
        "data": {
            "rooms": rooms_data
        }
    }
