#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Top 10 場地缺漏分析
"""

import json
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 過濾已下架的場地
active_venues = [v for v in venues if v.get('active', True)]

# 按品質分數排序
sorted_venues = sorted(active_venues, key=lambda x: x.get('qualityScore', 0), reverse=True)

print('=' * 100)
print('Top 10 場地缺漏分析')
print('=' * 100)

for i, venue in enumerate(sorted_venues[:10], 1):
    print(f'\n{i}. {venue.get("name")} (ID: {venue.get("id")})')
    print(f'   品質分數: {venue.get("qualityScore", 0)}')

    # 檢查 rooms
    rooms = venue.get('rooms', [])
    if rooms:
        print(f'   會議室數: {len(rooms)}')

        # 檢查欄位完整度
        with_name = sum(1 for r in rooms if r.get('name'))

        # 容量（處理 int 或 dict）
        with_capacity = 0
        for r in rooms:
            cap = r.get('capacity')
            if isinstance(cap, dict):
                if cap.get('theater'):
                    with_capacity += 1
            elif isinstance(cap, int):
                with_capacity += 1

        with_area = sum(1 for r in rooms if r.get('areaPing'))
        with_price = sum(1 for r in rooms if r.get('price', {}).get('weekday'))
        with_dimensions = sum(1 for r in rooms if r.get('dimensions'))
        with_equipment = sum(1 for r in rooms if r.get('equipment'))

        print(f'   欄位覆蓋:')
        print(f'     名稱: {with_name}/{len(rooms)}')
        print(f'     容量: {with_capacity}/{len(rooms)}')
        print(f'     面積: {with_area}/{len(rooms)}')
        print(f'     價格: {with_price}/{len(rooms)}')
        print(f'     尺寸: {with_dimensions}/{len(rooms)}')
        print(f'     設備: {with_equipment}/{len(rooms)}')

        # 缺漏項目
        missing = []
        if with_capacity < len(rooms):
            missing.append(f'容量({len(rooms)-with_capacity})')
        if with_area < len(rooms):
            missing.append(f'面積({len(rooms)-with_area})')
        if with_price < len(rooms):
            missing.append(f'價格({len(rooms)-with_price})')
        if with_dimensions < len(rooms):
            missing.append(f'尺寸({len(rooms)-with_dimensions})')
        if with_equipment < len(rooms):
            missing.append(f'設備({len(rooms)-with_equipment})')

        if missing:
            print(f'   缺漏: {", ".join(missing)}')
        else:
            print(f'   狀態: 完整')
    else:
        print(f'   狀態: 無會議室資料')

print('\n' + '=' * 100)
print('分析完成')
print('=' * 100)
