"""
Admin API - 後台管理介面端點
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from pathlib import Path

from app.database import get_db
from app.models.problem import Problem as ProblemModel
from app.models.scrape_task import ScrapeTask as ScrapeTaskModel
from app.models.conversation import Conversation as ConversationModel
from app.models.query_log import QueryLog as QueryLogModel


router = APIRouter(tags=["admin"])

# 取得專案根目錄 (eventmaster-api/)
# __file__ is backend/app/api/admin.py, so we need to go up 4 levels
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
VENUES_JSON_PATH = PROJECT_ROOT / "venues.json"


@router.get("/venues-json")
async def get_venues_json():
    """
    取得 venues.json 的內容（與前端靜態網站同步）

    讓管理面板可以直接讀取與前端相同的資料來源
    """
    import json

    if not VENUES_JSON_PATH.exists():
        raise HTTPException(status_code=404, detail="venues.json 檔案不存在")

    with open(VENUES_JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data


@router.put("/venues/{venue_id}/rooms/{room_id}/status")
async def update_room_status(
    venue_id: int,
    room_id: str,
    is_active: bool = Query(..., description="會議室是否上架"),
    db: Session = Depends(get_db)
):
    """
    更新會議室的上架狀態（寫回 venues.json）

    與前端靜態網站同步，確保資料一致性
    """
    import json
    from tempfile import NamedTemporaryFile
    import shutil

    if not VENUES_JSON_PATH.exists():
        raise HTTPException(status_code=404, detail="venues.json 檔案不存在")

    # 讀取現有資料
    with open(VENUES_JSON_PATH, 'r', encoding='utf-8') as f:
        venues = json.load(f)

    # 找到目標場地
    venue = next((v for v in venues if v['id'] == venue_id), None)
    if not venue:
        raise HTTPException(status_code=404, detail=f"找不到場地 ID {venue_id}")

    # 找到目標會議室
    target_room = None
    target_room_index = -1

    # 先嘗試用 ID 找
    if 'rooms' in venue:
        for i, room in enumerate(venue['rooms']):
            if room.get('id') == room_id or room.get('name') == room_id:
                target_room = room
                target_room_index = i
                break

    if target_room is None:
        raise HTTPException(status_code=404, detail=f"找不到會議室 {room_id}")

    # 更新狀態
    old_status = target_room.get('isActive')
    venue['rooms'][target_room_index]['isActive'] = is_active

    # 備份原檔案
    backup_path = VENUES_JSON_PATH.with_suffix('.json.bak')
    shutil.copy2(VENUES_JSON_PATH, backup_path)

    # 寫回檔案（使用原子寫入避免資料損壞）
    with NamedTemporaryFile(
        mode='w',
        encoding='utf-8',
        dir=VENUES_JSON_PATH.parent,
        delete=False
    ) as tmp_file:
        json.dump(venues, tmp_file, ensure_ascii=False, indent=2)
        tmp_path = tmp_file.name

    # 原子替換
    shutil.move(tmp_path, VENUES_JSON_PATH)

    return {
        "success": True,
        "venue_id": venue_id,
        "room_id": room_id,
        "room_name": target_room.get('name'),
        "old_status": old_status,
        "new_status": is_active
    }


@router.put("/venues/{venue_id}")
async def update_venue(
    venue_id: int,
    payload: dict,
    db: Session = Depends(get_db)
):
    """
    更新場地資料（寫回 venues.json）

    支援所有欄位的編輯，包含照片 URL
    """
    import json
    from tempfile import NamedTemporaryFile
    import shutil

    if not VENUES_JSON_PATH.exists():
        raise HTTPException(status_code=404, detail="venues.json 檔案不存在")

    # 讀取現有資料
    with open(VENUES_JSON_PATH, 'r', encoding='utf-8') as f:
        venues = json.load(f)

    # 找到目標場地
    venue_index = next(
        (i for i, v in enumerate(venues) if v['id'] == venue_id),
        None
    )
    if venue_index is None:
        raise HTTPException(status_code=404, detail=f"找不到場地 ID {venue_id}")

    # 保留不可修改的欄位
    protected_fields = {'id'}
    for key in protected_fields:
        if key in payload:
            del payload[key]

    # 深度合併更新（保留嵌套物件中未修改的欄位）
    def deep_merge(base, update):
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                deep_merge(base[key], value)
            else:
                base[key] = value

    deep_merge(venues[venue_index], payload)

    # 備份原檔案
    backup_path = VENUES_JSON_PATH.with_suffix('.json.bak')
    shutil.copy2(VENUES_JSON_PATH, backup_path)

    # 原子寫入
    with NamedTemporaryFile(
        mode='w',
        encoding='utf-8',
        dir=VENUES_JSON_PATH.parent,
        delete=False
    ) as tmp_file:
        json.dump(venues, tmp_file, ensure_ascii=False, indent=2)
        tmp_path = tmp_file.name

    shutil.move(tmp_path, VENUES_JSON_PATH)

    return {
        "success": True,
        "venue_id": venue_id,
        "venue_name": venues[venue_index].get('name'),
        "updated_fields": list(payload.keys())
    }


# ===== Request/Response Schemas =====

class DashboardStats(BaseModel):
    """儀表板統計資料"""
    total_venues: int
    venues_with_problems: int
    open_problems: int
    recent_conversations: int
    scrape_success_rate: float


class ProblemItem(BaseModel):
    """問題項目"""
    id: int
    venueId: int
    problemType: str
    field: str
    severity: str
    diagnosis: Optional[str] = None
    canFix: Optional[bool] = None
    fixAction: Optional[str] = None
    status: str
    firstSeen: str
    lastSeen: str
    occurrences: int
    notes: Optional[str] = None


class ProblemListResponse(BaseModel):
    """問題列表回應"""
    total: int
    items: List[ProblemItem]


class ScrapeTaskItem(BaseModel):
    """爬蟲任務項目"""
    id: int
    venueId: int
    taskType: str
    status: str
    startedAt: Optional[str] = None
    completedAt: Optional[str] = None
    roomsFound: int
    problemsFound: int
    errorMessage: Optional[str] = None
    techReport: Optional[dict] = None
    createdAt: str


class ConversationItem(BaseModel):
    """對話記錄項目"""
    id: int
    sessionId: str
    userQuery: str
    aiResponse: str
    venuesRecommended: Optional[list] = None
    feedback: Optional[int] = None
    createdAt: str
    userFingerprint: Optional[str] = None


class AnalyticsData(BaseModel):
    """分析資料"""
    total_conversations: int
    avg_feedback: Optional[float] = None
    top_queries: List[dict]
    popular_venues: List[dict]
    daily_stats: List[dict]


# ===== Dashboard Endpoint =====

@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard(db: Session = Depends(get_db)):
    """儀表板統計資料"""
    from app.models.venue import Venue
    from sqlalchemy import func, and_

    # 場地總數
    total_venues = db.query(func.count(Venue.id)).scalar() or 0

    # 有問題的場地數量
    venues_with_problems = db.query(
        func.count(func.distinct(ProblemModel.venue_id))
    ).scalar() or 0

    # 未解決問題數量
    open_problems = db.query(ProblemModel).filter(
        ProblemModel.status.in_(['open', 'diagnosing', 'fixing'])
    ).count()

    # 最近 24 小時對話數量
    since_yesterday = datetime.utcnow() - timedelta(days=1)
    recent_conversations = db.query(ConversationModel).filter(
        ConversationModel.created_at >= since_yesterday
    ).count()

    # 爬蟲成功率（最近 100 個任務）
    success_tasks = db.query(ScrapeTaskModel).filter(
        ScrapeTaskModel.status == 'success'
    ).count()
    total_tasks = db.query(ScrapeTaskModel).count()
    scrape_success_rate = success_tasks / total_tasks if total_tasks > 0 else 0.0

    return DashboardStats(
        total_venues=total_venues,
        venues_with_problems=venues_with_problems,
        open_problems=open_problems,
        recent_conversations=recent_conversations,
        scrape_success_rate=round(scrape_success_rate * 100, 1)
    )


# ===== Problems Endpoints =====

@router.get("/problems", response_model=ProblemListResponse)
async def list_problems(
    venue_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    problem_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """問題列表"""
    query = db.query(ProblemModel)

    if venue_id is not None:
        query = query.filter(ProblemModel.venue_id == venue_id)
    if status:
        query = query.filter(ProblemModel.status == status)
    if problem_type:
        query = query.filter(ProblemModel.problem_type == problem_type)
    if severity:
        query = query.filter(ProblemModel.severity == severity)

    total = query.count()
    problems = query.order_by(ProblemModel.last_seen.desc()).offset(offset).limit(limit).all()

    items = [p.to_dict() for p in problems]

    return ProblemListResponse(total=total, items=items)


@router.post("/problems/{problem_id}/diagnose")
async def diagnose_problem(
    problem_id: int,
    db: Session = Depends(get_db)
):
    """觸發 LLM 診斷問題"""
    problem = db.query(ProblemModel).filter(ProblemModel.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    # 更新狀態為診斷中
    problem.status = 'diagnosing'
    db.commit()

    try:
        # 調用 LLM 診斷（這裡需要整合 llm_diagnostic.py）
        from tools.llm_diagnostic import LLMDiagnostic

        diagnostic = LLMDiagnostic()
        result = diagnostic.diagnose(
            venue_id=problem.venue_id,
            problem_type=problem.problem_type,
            field=problem.field
        )

        # 更新問題記錄
        problem.diagnosis = result.get('reason')
        problem.can_fix = result.get('canFix')
        problem.fix_action = result.get('fixAction')

        if result.get('canFix') is not None:
            problem.status = 'fixing' if result.get('canFix') else 'wontfix'
        else:
            problem.status = 'open'  # 不確定，保持開啟

        db.commit()

        return {"success": True, "diagnosis": result}

    except Exception as e:
        problem.status = 'open'
        db.commit()
        raise HTTPException(status_code=500, detail=f"Diagnosis failed: {e}")


@router.put("/problems/{problem_id}/status")
async def update_problem_status(
    problem_id: int,
    status: str = Query(..., description="New status"),
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """更新問題狀態"""
    problem = db.query(ProblemModel).filter(ProblemModel.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    valid_statuses = ['open', 'diagnosing', 'fixing', 'fixed', 'wontfix', 'confirmed_absent']
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {valid_statuses}")

    problem.status = status
    if notes:
        old_notes = problem.notes or ''
        problem.notes = f"{old_notes}\n{datetime.utcnow().isoformat()}: {notes}"

    db.commit()

    return {"success": True, "problem": problem.to_dict()}


# ===== Scrape Tasks Endpoints =====

@router.get("/scrape-tasks", response_model=List[ScrapeTaskItem])
async def list_scrape_tasks(
    venue_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """爬蟲任務列表"""
    query = db.query(ScrapeTaskModel)

    if venue_id is not None:
        query = query.filter(ScrapeTaskModel.venue_id == venue_id)
    if status:
        query = query.filter(ScrapeTaskModel.status == status)

    tasks = query.order_by(ScrapeTaskModel.created_at.desc()).limit(limit).all()
    return [t.to_dict() for t in tasks]


@router.post("/scrape-tasks")
async def create_scrape_task(
    venue_ids: List[int],
    task_type: str = Query('full', description="Task type: full, incremental, verify"),
    db: Session = Depends(get_db)
):
    """建立爬蟲任務"""
    from app.models.venue import Venue

    created_tasks = []
    for venue_id in venue_ids:
        # 驗證場地存在
        venue = db.query(Venue).filter(Venue.id == venue_id).first()
        if not venue:
            continue

        task = ScrapeTaskModel(
            venue_id=venue_id,
            task_type=task_type,
            status='pending'
        )
        db.add(task)
        created_tasks.append(task)

    db.commit()

    # 重新載入以取得 ID
    for task in created_tasks:
        db.refresh(task)

    return {
        "success": True,
        "created": len(created_tasks),
        "tasks": [t.to_dict() for t in created_tasks]
    }


# ===== Conversations Endpoints =====

@router.get("/conversations", response_model=List[ConversationItem])
async def list_conversations(
    session_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """對話記錄列表"""
    query = db.query(ConversationModel)

    if session_id:
        query = query.filter(ConversationModel.session_id == session_id)

    conversations = query.order_by(
        ConversationModel.created_at.desc()
    ).offset(offset).limit(limit).all()

    return [c.to_dict() for c in conversations]


# ===== Analytics Endpoints =====

@router.get("/analytics", response_model=AnalyticsData)
async def get_analytics(
    days: int = Query(30, description="Days of data to analyze"),
    db: Session = Depends(get_db)
):
    """使用分析資料"""
    since_date = datetime.utcnow() - timedelta(days=days)

    # 總對話數
    total_conversations = db.query(ConversationModel).filter(
        ConversationModel.created_at >= since_date
    ).count()

    # 平均評分
    from sqlalchemy import func

    avg_feedback_result = db.query(
        func.avg(ConversationModel.feedback)
    ).filter(
        ConversationModel.created_at >= since_date,
        ConversationModel.feedback.isnot(None)
    ).first()

    avg_feedback = float(avg_feedback_result[0]) if avg_feedback_result and avg_feedback_result[0] else None

    # 熱門查詢（從 query_logs）
    top_endpoints = db.query(
        QueryLogModel.endpoint,
        func.count(QueryLogModel.id).label('count')
    ).filter(
        QueryLogModel.created_at >= since_date
    ).group_by(
        QueryLogModel.endpoint
    ).order_by(
        func.count(QueryLogModel.id).desc()
    ).limit(10).all()

    top_queries = [
        {"endpoint": ep, "count": count}
        for ep, count in top_endpoints
    ]

    # 熱門場地（從對話記錄的推薦）
    # 這需要在實際使用時根據 venues_recommended 欄位分析

    # 每日統計
    daily_stats = []
    for i in range(days):
        day_date = datetime.utcnow() - timedelta(days=i)
        day_start = day_date.replace(hour=0, minute=0, second=0)
        day_end = day_date.replace(hour=23, minute=59, second=59)

        day_convos = db.query(ConversationModel).filter(
            ConversationModel.created_at >= day_start,
            ConversationModel.created_at <= day_end
        ).count()

        daily_stats.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "conversations": day_convos
        })

    daily_stats.reverse()

    return AnalyticsData(
        total_conversations=total_conversations,
        avg_feedback=avg_feedback,
        top_queries=top_queries,
        popular_venues=[],  # 待實作
        daily_stats=daily_stats
    )


# ===== Health Check =====

@router.get("/health")
async def admin_health():
    """Admin API 健康檢查"""
    return {
        "status": "healthy",
        "service": "EventMaster Admin API",
        "version": "1.0.0"
    }
