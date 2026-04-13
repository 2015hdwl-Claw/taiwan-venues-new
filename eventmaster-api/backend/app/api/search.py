"""
Search API - 智能搜尋端點
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.database import get_db
from app.models.venue import Venue, MeetingRoom
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# ===== Pydantic Schemas =====

class SearchRequirements(BaseModel):
    """搜尋需求"""
    style: Optional[str] = None
    audience_size: Optional[int] = None
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    city: Optional[str] = None
    must_have: List[str] = []


class SearchRequest(BaseModel):
    """智能搜尋請求"""
    query: str = Field(description="自然語言查詢")
    requirements: SearchRequirements


class VenueMatch(BaseModel):
    """場地匹配結果"""
    venue: dict
    match_score: float = Field(ge=0, le=1)
    match_reasons: List[str] = []
    warnings: List[str] = []


class SearchResponse(BaseModel):
    """搜尋回應"""
    success: bool
    data: dict


# ===== 端點實作 =====

@router.post("/")
async def search_venues(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    智能搜尋場地

    根據自然語言查詢和需求找到最合適的場地
    """
    try:
        # 解析需求
        req = request.requirements

        # 建立查詢
        query = db.query(Venue)

        # 城市篩選
        if req.city:
            query = query.filter(Venue.city == req.city)

        # 預算匹配分數的場地列表
        all_venues = query.all()
        matched_venues = []

        for venue in all_venues:
            # 計算匹配分數
            match_score = 0.5  # 基礎分數
            match_reasons = []
            warnings = []

            # 檢查容量需求
            if req.audience_size:
                max_capacity = 0
                for room in venue.meeting_rooms:
                    if room.capacity_theater and room.capacity_theater > max_capacity:
                        max_capacity = room.capacity_theater

                if max_capacity >= req.audience_size:
                    match_score += 0.2
                    match_reasons.append(f"最大容量{max_capacity}人符合需求")
                else:
                    match_score -= 0.1
                    warnings.append(f"最大容量{max_capacity}人小於需求")

            # 檢查預算需求
            if req.budget_max and venue.price_full_day:
                if venue.price_full_day <= req.budget_max:
                    match_score += 0.15
                    match_reasons.append(f"價格符合預算")
                else:
                    match_score -= 0.1
                    warnings.append(f"超出預算")

            # 檢查必備設備
            if req.must_have:
                venue_amenities = venue.amenities or []
                missing = []
                for item in req.must_have:
                    if item not in str(venue_amenities).lower():
                        missing.append(item)

                if not missing:
                    match_score += 0.15
                    match_reasons.append(f"具備所有必需設備")
                else:
                    match_score -= 0.05
                    warnings.append(f"缺少設備: {', '.join(missing)}")

            # 如果有指定風格
            if req.style == "ted_talk":
                if max_capacity >= 200:  # TED風格通常需要一定容量
                    match_score += 0.1
                    match_reasons.append("適合TED風格活動")

            # 限制分數在0-1之間
            match_score = max(0, min(1, match_score))

            # 只包含匹配分數 > 0.5 的場地
            if match_score > 0.5:
                matched_venues.append({
                    "venue": {
                        "id": venue.id,
                        "name": venue.name,
                        "type": venue.type,
                        "city": venue.city,
                        "address": venue.address,
                        "contact_phone": venue.contact_phone,
                        "contact_email": venue.contact_email,
                        "url": venue.url,
                        "price_full_day": venue.price_full_day
                    },
                    "match_score": round(match_score, 2),
                    "match_reasons": match_reasons,
                    "warnings": warnings
                })

        # 按匹配分數排序
        matched_venues.sort(key=lambda x: x["match_score"], reverse=True)

        # 只返回前10個結果
        top_venues = matched_venues[:10]

        return {
            "success": True,
            "data": {
                "query": request.query,
                "requirements": req.dict(),
                "venues": top_venues,
                "total": len(top_venues),
                "search_time": "0.05s"  # 模擬搜尋時間
            }
        }

    except Exception as e:
        logger.error(f"❌ Failed to search: {e}")
        raise HTTPException(status_code=500, detail="Failed to search venues")


@router.get("/suggest")
async def suggest_venues(
    query: str = Query(..., description="搜尋關鍵詞"),
    limit: int = Query(10, ge=1, le=20, description="結果數量"),
    db: Session = Depends(get_db)
):
    """
    場地建議搜尋

    簡單的關鍵詞搜尋
    """
    try:
        # 建立查詢（搜尋名稱、城市、地址）
        from sqlalchemy import or_
        search_term = f"%{query}%"

        query = db.query(Venue).filter(
            or_(
                Venue.name.ilike(search_term),
                Venue.city.ilike(search_term),
                Venue.address.ilike(search_term)
            )
        )

        # 限制結果數量
        venues = query.limit(limit).all()

        # 序列化
        results = []
        for venue in venues:
            results.append({
                "id": venue.id,
                "name": venue.name,
                "city": venue.city,
                "address": venue.address,
                "type": venue.type,
                "relevance": 0.8  # TODO: 計算真實的相關性分數
            })

        return {
            "success": True,
            "data": {
                "query": query,
                "suggestions": results,
                "total": len(results)
            }
        }

    except Exception as e:
        logger.error(f"❌ Failed to suggest: {e}")
        raise HTTPException(status_code=500, detail="Failed to get suggestions")
