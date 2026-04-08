#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TOP10 場地完整度驗證 - 逐一檢查每個欄位
避免「看起來有資料」但實際不完整的問題
"""

import json
import sys
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("TOP10 場地完整度驗證")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# TOP10 場地 ID（根據 venue_completeness_analysis.md）
top10_ids = [
    (1103, "台北萬豪", 16.5),
    (1085, "台北文華東方", 16.2),
    (1017, "南港展覽館", 15.0),
    (1049, "台北世貿", 13.8),
    (1128, "集思台大", 13.0),
    (None, "台北怡亨", 9.0),
    (None, "台北北門世民", 9.0),
    (None, "台北艾美", 9.0),
    (1122, "維多麗亞", 7.0),
    (1034, "NUZONE", 6.0)
]

# 讀取 venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

def check_room_completeness(room):
    """檢查單一會議室完整度"""
    missing = []
    present = []

    # 1. 基本資料
    if room.get('name'):
        present.append('name')
    else:
        missing.append('name')

    if room.get('nameEn'):
        present.append('nameEn')
    else:
        missing.append('nameEn')

    if room.get('floor'):
        present.append('floor')
    else:
        missing.append('floor')

    # 2. 面積資料（關鍵！）
    has_area = False
    if room.get('areaSqm'):
        present.append('areaSqm')
        has_area = True
    else:
        missing.append('areaSqm')

    if room.get('areaPing'):
        present.append('areaPing')
        has_area = True
    else:
        missing.append('areaPing')

    # 3. 尺寸資料（關鍵！）
    dims = room.get('dimensions')
    if dims and isinstance(dims, dict):
        if dims.get('length') and dims.get('width'):
            present.append('dimensions')
        else:
            missing.append('dimensions (L×W)')
    else:
        missing.append('dimensions')

    # 4. 容量資料（關鍵！）
    cap = room.get('capacity')
    if cap:
        if isinstance(cap, dict):
            if any(cap.values()):
                present.append('capacity')
            else:
                missing.append('capacity (empty)')
        elif isinstance(cap, int):
            # 舊格式：直接是數字
            present.append('capacity (old format)')
        else:
            missing.append('capacity (invalid)')
    else:
        missing.append('capacity')

    # 5. 價格資料（關鍵！）
    price = room.get('price')
    if price:
        if isinstance(price, dict):
            if any(price.values()):
                present.append('price')
            else:
                missing.append('price (empty)')
        elif isinstance(price, (int, float)):
            # 舊格式：直接是數字
            present.append('price (old format)')
        else:
            missing.append('price (invalid)')
    else:
        missing.append('price')

    return {
        'has_area': has_area,
        'missing_count': len(missing),
        'present_count': len(present),
        'missing': missing,
        'present': present
    }

def find_venue_by_name(name):
    """根據名稱尋找場地"""
    for venue in venues:
        if name in venue.get('name', ''):
            return venue
    return None

# 逐一驗證
results = []

for venue_id, venue_name, expected_score in top10_ids:
    print(f"\n{'=' * 100}")
    print(f"檢查: {venue_name}")
    print(f"預期完整度: {expected_score}/30")
    print('=' * 100)

    # 尋找場地
    if venue_id:
        venue = next((v for v in venues if v.get('id') == venue_id), None)
    else:
        venue = find_venue_by_name(venue_name)

    if not venue:
        print(f"❌ 找不到場地")
        results.append({
            'name': venue_name,
            'status': 'NOT_FOUND',
            'rooms_checked': 0,
            'issues': ['場地不存在']
        })
        continue

    print(f"ID: {venue.get('id')}")
    print(f"完整名稱: {venue.get('name')}")

    rooms = venue.get('rooms', [])
    if not rooms:
        print(f"❌ 沒有會議室資料")
        results.append({
            'name': venue_name,
            'status': 'NO_ROOMS',
            'rooms_checked': 0,
            'issues': ['沒有會議室']
        })
        continue

    print(f"會議室數: {len(rooms)}\n")

    # 檢查每個會議室
    room_issues = []
    missing_area_rooms = []
    missing_capacity_rooms = []
    missing_price_rooms = []

    for i, room in enumerate(rooms[:5], 1):  # 只檢查前 5 個
        print(f"會議室 {i}: {room.get('name', 'Unknown')}")

        check = check_room_completeness(room)

        if check['missing_count'] > 0:
            print(f"  ⚠️ 缺少 {check['missing_count']} 個欄位: {', '.join(check['missing'][:5])}")
            room_issues.append(f"{room.get('name')}: {check['missing']}")
        else:
            print(f"  ✅ 完整")

        if not check['has_area']:
            missing_area_rooms.append(room.get('name'))

        cap = room.get('capacity')
        if not cap or (isinstance(cap, dict) and not any(cap.values())):
            missing_capacity_rooms.append(room.get('name'))

        price = room.get('price')
        if not price or (isinstance(price, dict) and not any(price.values())):
            missing_price_rooms.append(room.get('name'))

    # 統計
    total_rooms = len(rooms)
    area_coverage = len([r for r in rooms if r.get('areaSqm') or r.get('areaPing')])

    def has_capacity(r):
        cap = r.get('capacity')
        if cap:
            if isinstance(cap, dict):
                return any(cap.values())
            else:
                return True
        return False

    def has_price(r):
        price = r.get('price')
        if price:
            if isinstance(price, dict):
                return any(price.values())
            else:
                return True
        return False

    capacity_coverage = len([r for r in rooms if has_capacity(r)])
    price_coverage = len([r for r in rooms if has_price(r)])

    print(f"\n統計:")
    print(f"  總會議室: {total_rooms}")
    print(f"  面積覆蓋: {area_coverage}/{total_rooms} ({area_coverage*100//total_rooms if total_rooms else 0}%)")
    print(f"  容量覆蓋: {capacity_coverage}/{total_rooms} ({capacity_coverage*100//total_rooms if total_rooms else 0}%)")
    print(f"  價格覆蓋: {price_coverage}/{total_rooms} ({price_coverage*100//total_rooms if total_rooms else 0}%)")

    # 判斷狀態
    status = 'OK'
    issues = []

    if area_coverage < total_rooms:
        status = 'INCOMPLETE'
        issues.append(f'缺少面積: {total_rooms - area_coverage}/{total_rooms}')

    if capacity_coverage < total_rooms:
        status = 'INCOMPLETE'
        issues.append(f'缺少容量: {total_rooms - capacity_coverage}/{total_rooms}')

    if price_coverage < total_rooms:
        status = 'INCOMPLETE'
        issues.append(f'缺少價格: {total_rooms - price_coverage}/{total_rooms}')

    results.append({
        'name': venue_name,
        'id': venue.get('id'),
        'status': status,
        'rooms_checked': total_rooms,
        'area_coverage': f'{area_coverage}/{total_rooms}',
        'capacity_coverage': f'{capacity_coverage}/{total_rooms}',
        'price_coverage': f'{price_coverage}/{total_rooms}',
        'issues': issues
    })

# 總結
print("\n" + "=" * 100)
print("TOP10 完整度總結")
print("=" * 100)

incomplete_count = 0
for r in results:
    status_icon = "❌" if r['status'] == 'INCOMPLETE' else "✅" if r['status'] == 'OK' else "⚠️"
    print(f"\n{status_icon} {r['name']}")
    print(f"   會議室: {r['rooms_checked']}")
    if r['status'] != 'OK':
        print(f"   問題: {', '.join(r['issues'])}")
        incomplete_count += 1

print(f"\n" + "=" * 100)
print(f"需要改進的場地: {incomplete_count}/10")
print("=" * 100)
