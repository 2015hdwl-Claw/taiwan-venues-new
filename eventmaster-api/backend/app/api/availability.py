"""
Availability API - 即時可用性端點
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.venue import Venue, MeetingRoom
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/{venue_id}/availability")
async def get_venue_availability(
    venue_id: int,
    start_date: str = Query(..., description="開始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="結束日期 YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """
    取得場地即時可用性

    查詢指定日期範圍內的場地可用性
    """
    try:
        # 驗證日期格式
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else start
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        # 檢查日期範圍
        if end < start:
            raise HTTPException(status_code=400, detail="end_date must be after start_date")

        # 查詢場地
        venue = db.query(Venue).filter(Venue.id == venue_id).first()
        if not venue:
            raise HTTPException(status_code=404, detail=f"Venue {venue_id} not found")

        # 查詢會議室
        rooms = db.query(MeetingRoom).filter(MeetingRoom.venue_id == venue_id).all()

        # 生成可用性資料（模擬）
        availability_data = []
        current_date = start

        while current_date <= end:
            import random
            rooms_data = []
            for room in rooms:
                statuses = ["available", "booked", "unavailable"]
                morning = statuses[random.randint(0, 2)]
                afternoon = statuses[random.randint(0, 2)]
                full_day = "available" if morning == "available" and afternoon == "available" else "booked"

                rooms_data.append({
                    "room_id": room.id,
                    "room_name": room.name,
                    "morning": morning,
                    "afternoon": afternoon,
                    "full_day": full_day,
                    "price": {
                        "half_day": room.price_half_day,
                        "full_day": room.price_full_day
                    } if room.price_half_day else None
                })

            availability_data.append({
                "date": current_date.isoformat(),
                "rooms": rooms_data
            })
            current_date += timedelta(days=1)

        return {
            "success": True,
            "data": {
                "venue_id": venue_id,
                "venue_name": venue.name,
                "availability": availability_data,
                "date_range": {
                    "start": start.isoformat(),
                    "end": end.isoformat()
                },
                "total_rooms": len(rooms)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get availability: {e}")
        raise HTTPException(status_code=500, detail="Failed to get availability")
