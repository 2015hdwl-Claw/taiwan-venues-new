#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
場地完整度分析
找出還未完成的場地
"""

import json
from datetime import datetime
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print('=' * 100)
print('場地完整度分析')
print('=' * 100)
print()

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 只分析 active 的場地
active_venues = [v for v in venues if v.get('active', True)]

print(f'總共 {len(active_venues)} 個活躍場地\n')

def get_completeness_score(venue):
    """計算場地完整度分數"""
    score = 0
    max_score = 0

    # 基本資料 (20 分)
    max_score += 20
    if venue.get('name'): score += 5
    if venue.get('url'): score += 5
    if venue.get('address'): score += 5
    contact = venue.get('contact')
    if contact:
        if contact.get('phone') or contact.get('email'):
            score += 5

    # 會議室資料 (40 分)
    rooms = venue.get('rooms', [])
    if rooms:
        max_score += 40
        room_score = 0

        # 價格覆蓋 (20 分)
        with_price = 0
        for r in rooms:
            price = r.get('price')
            if isinstance(price, dict):
                if price.get('weekday'):
                    with_price += 1
            elif isinstance(price, (int, float)):
                with_price += 1

        if rooms:
            room_score += (with_price / len(rooms)) * 20

        # 容量覆蓋 (10 分)
        with_capacity = sum(1 for r in rooms if r.get('capacity'))
        if rooms:
            room_score += (with_capacity / len(rooms)) * 10

        # 面積覆蓋 (10 分)
        with_area = sum(1 for r in rooms if r.get('areaPing') or r.get('areaSqm'))
        if rooms:
            room_score += (with_area / len(rooms)) * 10

        score += room_score
    else:
        max_score += 40

    # 照片 (20 分)
    max_score += 20
    total_photos = 0
    for r in rooms:
        images = r.get('images')
        if isinstance(images, dict):
            gallery = images.get('gallery', [])
            if isinstance(gallery, list):
                total_photos += len(gallery)

    if total_photos > 0:
        score += min(total_photos / 5, 20)

    # 資料新鮮度 (20 分)
    max_score += 20
    last_scraped = venue.get('metadata', {}).get('lastScrapedAt')
    if last_scraped:
        score += 20

    return int((score / max_score) * 100) if max_score > 0 else 0

def get_missing_info(venue):
    """列出缺失的資訊"""
    missing = []

    # 基本資料
    if not venue.get('address'):
        missing.append('地址')
    if not venue.get('contact', {}).get('phone') and not venue.get('contact', {}).get('email'):
        missing.append('聯絡資訊')

    # 會議室資料
    rooms = venue.get('rooms', [])
    if rooms:
        with_price = sum(1 for r in rooms if r.get('price'))
        with_capacity = sum(1 for r in rooms if r.get('capacity'))
        with_area = sum(1 for r in rooms if r.get('areaPing') or r.get('areaSqm'))

        if with_price == 0:
            missing.append('所有價格')
        elif with_price < len(rooms):
            missing.append(f'部分價格 ({with_price}/{len(rooms)})')

        if with_capacity == 0:
            missing.append('所有容量')
        elif with_capacity < len(rooms):
            missing.append(f'部分容量 ({with_capacity}/{len(rooms)})')

        if with_area == 0:
            missing.append('所有面積')
        elif with_area < len(rooms):
            missing.append(f'部分面積 ({with_area}/{len(rooms)})')
    else:
        missing.append('會議室資料')

    return missing

# 計算每個場地的完整度
venue_scores = []
for venue in active_venues:
    score = get_completeness_score(venue)
    venue_scores.append({
        'id': venue.get('id'),
        'name': venue.get('name'),
        'score': score,
        'rooms': len(venue.get('rooms', [])),
        'city': venue.get('city', 'Unknown'),
        'missing': get_missing_info(venue)
    })

# 排序：分數低的在前
venue_scores.sort(key=lambda x: x['score'])

# 顯示需要改進的場地（分數 < 70）
print('=' * 100)
print('需要改進的場地（完整度 < 70 分）')
print('=' * 100)
print()

need_improvement = [v for v in venue_scores if v['score'] < 70]

if need_improvement:
    print(f"{'分數':<5} {'ID':<5} {'場地名稱':<40} {'會議室':<8} {'城市':<10} {'缺失資訊'}")
    print('-' * 100)

    for v in need_improvement[:30]:  # 顯示前 30 個
        missing_str = ', '.join(v['missing']) if v['missing'] else '-'
        print(f"{v['score']:>3}分  | {v['id']:>4} | {v['name']:<38} | {v['rooms']:>2} 間  | {v['city']:<10} | {missing_str}")

    print()
    print(f'總共 {len(need_improvement)} 個場地需要改進（完整度 < 70 分）')

    # 統計
    print()
    print('統計：')
    print(f'  - 0-40 分: {sum(1 for v in need_improvement if v["score"] < 40)} 個')
    print(f'  - 40-60 分: {sum(1 for v in need_improvement if 40 <= v["score"] < 60)} 個')
    print(f'  - 60-70 分: {sum(1 for v in need_improvement if 60 <= v["score"] < 70)} 個')

else:
    print('✅ 所有場地完整度都 >= 70 分')

print()
print('=' * 100)
print('完整度最高的場地（優質範例，分數 >= 85 分）')
print('=' * 100)
print()

high_quality = [v for v in venue_scores if v['score'] >= 85]

if high_quality:
    print(f"{'分數':<5} {'ID':<5} {'場地名稱':<40} {'會議室':<8} {'城市':<10}")
    print('-' * 100)

    for v in high_quality[::-1][:10]:  # 顯示前 10 個
        print(f"{v['score']:>3}分  | {v['id']:>4} | {v['name']:<38} | {v['rooms']:>2} 間  | {v['city']:<10}")

    print()
    print(f'總共 {len(high_quality)} 個高品質場地（完整度 >= 85 分）')

print()
print('=' * 100)
print('完整度統計總覽')
print('=' * 100)
print()

all_scores = [v['score'] for v in venue_scores]
print(f'平均完整度: {sum(all_scores) // len(all_scores)} 分')
print(f'最高完整度: {max(all_scores)} 分')
print(f'最低完整度: {min(all_scores)} 分')
print()

# 分數分佈
ranges = [
    (0, 40, '嚴重不足'),
    (40, 60, '需要改進'),
    (60, 70, '尚可'),
    (70, 85, '良好'),
    (85, 100, '優質')
]

for low, high, label in ranges:
    count = sum(1 for s in all_scores if low <= s < high)
    pct = (count / len(all_scores)) * 100
    bar = '█' * int(pct / 2)
    print(f'{label:>8} ({low:2d}-{high:2d}分): {count:3d} 個 ({pct:5.1f}%) {bar}')

print()
print('=' * 100)
