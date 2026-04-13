#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
資料庫初始化腳本

建立所有資料庫表格並導入初始資料
"""

import sys
import os

# 加入專案路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from app.database import init_db, sync_engine, SyncSessionLocal
from app.models.venue import Venue, MeetingRoom
from app.models.problem import Problem
from app.models.scrape_task import ScrapeTask
from app.models.conversation import Conversation
from app.models.query_log import QueryLog
from sqlalchemy import text


def create_admin_user():
    """建立預設管理員使用者（如果需要）"""
    print("[初始化] 管理員使用者...")
    # 這裡可以預設建立管理員帳號
    # 如果使用 API Key 認證，可以跳過
    print("  使用 API Key 認證，跳過密碼使用者")


def import_venues_from_json():
    """從 venues.json 導入場地到資料庫"""
    print("[初始化] 從 venues.json 導入場地資料...")

    import json
    venues_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'venues.json')

    if not os.path.exists(venues_file):
        print(f"  警告: 找不到 {venues_file}，跳過導入")
        return

    with open(venues_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    venues = data if isinstance(data, list) else data.get('venues', [])
    print(f"  找到 {len(venues)} 個場地")

    from sqlalchemy.orm import Session

    with Session(sync_engine) as session:
        existing_count = session.query(Venue).count()
        print(f"  資料庫中已有 {existing_count} 個場地")

        # 如果資料庫已有資料，跳過
        if existing_count > 0:
            print("  資料庫已有資料，跳過導入")
            return

        imported = 0
        for venue_data in venues[:10]:  # 先導入前 10 個測試
            try:
                venue = Venue(
                    id=venue_data.get('id'),
                    name=venue_data.get('name'),
                    name_en=venue_data.get('nameEn'),
                    type=venue_data.get('venueType'),
                    city=venue_data.get('city'),
                    address=venue_data.get('address', ''),
                    contact_phone=venue_data.get('contactPerson'),
                    contact_email=venue_data.get('contactEmail'),
                    url=venue_data.get('url'),
                    description=venue_data.get('description'),
                    amenities=venue_data.get('equipment'),
                )
                session.add(venue)
                imported += 1
            except Exception as e:
                print(f"  導入場地 {venue_data.get('id')} 失敗: {e}")

        session.commit()
        print(f"  導入 {imported} 個場地")


def main():
    """主流程"""
    print("=" * 60)
    print("EventMaster 資料庫初始化")
    print("=" * 60)
    print()

    # Step 1: 建立所有表格
    print("[Step 1] 建立資料庫表格...")
    try:
        init_db()
    except Exception as e:
        print(f"  錯誤: {e}")
        print("  提示: 請確認 PostgreSQL 已啟動且連線字串正確")
        return 1

    # Step 2: 建立預設資料
    print()
    print("[Step 2] 建立預設資料...")
    create_admin_user()

    # Step 3: 導入場地資料（可選）
    print()
    import_venues_from_json()

    print()
    print("=" * 60)
    print("✅ 資料庫初始化完成")
    print("=" * 60)
    print()
    print("下一步:")
    print("  1. 啟動 API 伺服器: cd eventmaster-api/backend && python main.py")
    print("  2. 查看文件: http://localhost:8000/docs")
    print("  3. 測試 admin API: http://localhost:8000/api/v1/admin/dashboard")

    return 0


if __name__ == '__main__':
    sys.exit(main())
