#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台北市 TOP10 場地 - 完整欄位檢查
逐一檢查每個會議室的每個欄位，確實驗證完整性
"""

import json
import sys
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("台北市 TOP10 場地 - 完整欄位檢查")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取資料
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# 台北市 TOP10（依會議室數）
top10_ids = [1042, 1500, 1448, 1125, 1053, 1103, 1493, 1128, 1129, 1085]

# 30 欄位標準檢查
def check_30_fields(room):
    """檢查 30 欄位完整性"""

    def get_nested(obj, key, default=None):
        """安全提取嵌套值"""
        if isinstance(obj, dict):
            return obj.get(key, default)
        return default

    cap = room.get('capacity')
    if isinstance(cap, dict):
        capacity = cap
    else:
        capacity = {}

    price = room.get('price')
    if isinstance(price, dict):
        price_obj = price
    else:
        price_obj = {}

    dims = room.get('dimensions')
    if isinstance(dims, dict):
        dimensions = dims
    else:
        dimensions = {}

    fields = {
        # 基本資料 (5)
        'id': bool(room.get('id')),
        'name': bool(room.get('name')),
        'nameEn': bool(room.get('nameEn')),
        'floor': bool(room.get('floor')),
        'areaUnit': bool(room.get('areaUnit')),

        # 面積資料 (3)
        'areaSqm': bool(room.get('areaSqm')),
        'areaPing': bool(room.get('areaPing')),
        'area': bool(room.get('area')),

        # 尺寸資料 (3)
        'dimensions_length': bool(dimensions.get('length')),
        'dimensions_width': bool(dimensions.get('width')),
        'dimensions_height': bool(dimensions.get('height')),

        # 容量資料 (6)
        'capacity_theater': bool(capacity.get('theater')),
        'capacity_banquet': bool(capacity.get('banquet')),
        'capacity_classroom': bool(capacity.get('classroom')),
        'capacity_uShape': bool(capacity.get('uShape')),
        'capacity_cocktail': bool(capacity.get('cocktail')),
        'capacity_roundTable': bool(capacity.get('roundTable')),

        # 價格資料 (8)
        'price_weekday': bool(price_obj.get('weekday')),
        'price_holiday': bool(price_obj.get('holiday')),
        'price_morning': bool(price_obj.get('morning')),
        'price_afternoon': bool(price_obj.get('afternoon')),
        'price_evening': bool(price_obj.get('evening')),
        'price_fullDay': bool(price_obj.get('fullDay')),
        'price_hourly': bool(price_obj.get('hourly')),
        'price_note': bool(price_obj.get('note')),

        # 設備資料 (2)
        'equipment': bool(room.get('equipment')),
        'equipmentList': bool(room.get('equipmentList')),

        # 其他資料 (2)
        'features': bool(room.get('features')),
        'source': bool(room.get('source'))
    }

    return fields

all_issues = {}

for venue_id in top10_ids:
    venue = next((v for v in venues if v.get('id') == venue_id), None)
    if not venue:
        continue

    print(f"\n{'=' * 100}")
    print(f"檢查: {venue['name']} (ID: {venue_id})")
    print(f"會議室數: {len(venue.get('rooms', []))}")
    print('=' * 100)

    rooms = venue.get('rooms', [])
    venue_issues = []

    # 檢查每個會議室
    for room_idx, room in enumerate(rooms, 1):
        fields = check_30_fields(room)
        missing = [k for k, v in fields.items() if not v]

        if missing:
            room_issues = {
                'room_name': room.get('name', 'Unknown'),
                'missing_fields': missing,
                'missing_count': len(missing)
            }
            venue_issues.append(room_issues)

            # 只顯示前 3 個有問題的會議室
            if len(venue_issues) <= 3:
                print(f"\n會議室 {room_idx}: {room['name']}")
                print(f"  缺少 {len(missing)} 個欄位")
                print(f"  缺失: {', '.join(missing[:10])}")
                if len(missing) > 10:
                    print(f"  ... 還有 {len(missing) - 10} 個")

    if venue_issues:
        all_issues[venue['name']] = {
            'id': venue_id,
            'total_rooms': len(rooms),
            'rooms_with_issues': len(venue_issues),
            'issues': venue_issues
        }
        print(f"\n⚠️ 總計: {len(venue_issues)}/{len(rooms)} 個會議室有缺漏")
    else:
        print(f"\n✅ 完整度: 100%")

# 總結
print("\n" + "=" * 100)
print("台北市 TOP10 - 欄位缺漏總結")
print("=" * 100)

if all_issues:
    for venue_name, data in all_issues.items():
        print(f"\n❌ {venue_name} (ID: {data['id']})")
        print(f"   會議室: {data['total_rooms']}")
        print(f"   有問題: {data['rooms_with_issues']}")
        print(f"   主要缺漏:")

        # 統計最常見的缺漏
        missing_count = {}
        for issue in data['issues']:
            for field in issue['missing_fields']:
                missing_count[field] = missing_count.get(field, 0) + 1

        # 顯示前 5 個最常見缺漏
        sorted_missing = sorted(missing_count.items(), key=lambda x: -x[1])[:5]
        for field, count in sorted_missing:
            print(f"      - {field}: {count} 個會議室")
else:
    print("\n✅ 所有場地完整度 100%")
