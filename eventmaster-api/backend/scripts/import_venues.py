"""
從 venues.json 導入場地資料到 PostgreSQL
"""

import sys
import os
import json
from pathlib import Path

# 加入專案根目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import SyncSessionLocal, init_db
from app.models.venue import Venue, MeetingRoom
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def import_venues_from_json(json_file: str):
    """從 JSON 導入場地資料"""

    # 讀取 venues.json
    with open(json_file, 'r', encoding='utf-8') as f:
        venues_data = json.load(f)

    logger.info(f"📂 讀取 {len(venues_data)} 個場地")

    # 建立資料庫 session
    db: Session = SyncSessionLocal()

    try:
        # 計數器
        venue_count = 0
        room_count = 0

        for venue_data in venues_data:
            # 檢查是否已存在
            existing = db.query(Venue).filter(Venue.id == venue_data.get('id')).first()
            if existing:
                logger.info(f"⏭️  跳過已存在的場地: {venue_data.get('name')} (ID: {venue_data.get('id')})")
                continue

            # 建立 Venue 物件
            venue = Venue(
                id=venue_data.get('id'),
                name=venue_data.get('name'),
                type=venue_data.get('venueType'),
                city=venue_data.get('city'),
                address=venue_data.get('address'),
                contact_phone=venue_data.get('contactPhone'),
                contact_email=venue_data.get('contactEmail'),
                url=venue_data.get('url'),
                description=venue_data.get('description'),
                price_half_day=venue_data.get('priceHalfDay'),
                price_full_day=venue_data.get('priceFullDay')
            )

            # 處理會議室
            rooms_data = venue_data.get('rooms', [])
            for room_data in rooms_data:
                room = MeetingRoom(
                    venue_id=venue.id,
                    name=room_data.get('name'),
                    # dimensions（如果有）
                    area=room_data.get('sqm'),
                    # capacity
                    capacity_theater=room_data.get('capacity', {}).get('theater'),
                    capacity_banquet=room_data.get('capacity', {}).get('banquet'),
                    capacity_classroom=room_data.get('capacity', {}).get('classroom'),
                    # images
                    images=room_data.get('images'),
                    # price（如果有）
                    price_half_day=room_data.get('priceHalfDay'),
                    price_full_day=room_data.get('priceFullDay')
                )
                venue.meeting_rooms.append(room)
                room_count += 1

            # 新增到資料庫
            db.add(venue)
            venue_count += 1

            logger.info(f"✅ 匯入場地: {venue.name} ({len(venue.meeting_rooms)} 個會議室)")

        # 提交交易
        db.commit()

        logger.info(f"🎉 匯入完成！")
        logger.info(f"   場地: {venue_count}")
        logger.info(f"   會議室: {room_count}")

    except Exception as e:
        db.rollback()
        logger.error(f"❌ 匯入失敗: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # 路徑設定
    project_root = Path(__file__).parent.parent.parent
    json_file = project_root / "../venues.json"

    if not json_file.exists():
        logger.error(f"❌ 找不到 venues.json: {json_file}")
        sys.exit(1)

    # 初始化資料庫
    logger.info("🔧 初始化資料庫...")
    init_db()

    # 匯入資料
    import_venues_from_json(str(json_file))
