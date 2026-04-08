#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
確認所有場地狀態 - 台北、新北、台中、高雄
"""

import json
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

print("=" * 100)
print("台灣各城市場地狀態")
print("=" * 100)

# 統計各城市
cities = ['台北市', '新北市', '台中市', '高雄市']

for city in cities:
    city_venues = [v for v in venues if v.get('city') == city]
    city_venues = sorted(city_venues, key=lambda x: x['id'])

    print(f"\n{'=' * 100}")
    print(f"城市: {city}")
    print(f"總數: {len(city_venues)}")
    print("=" * 100)

    # 按品質分數分類
    high_quality = [v for v in city_venues if v.get('metadata', {}).get('qualityScore', 0) >= 75]
    medium_quality = [v for v in city_venues if 50 <= v.get('metadata', {}).get('qualityScore', 0) < 75]
    low_quality = [v for v in city_venues if v.get('metadata', {}).get('qualityScore', 0) < 50]
    no_quality = [v for v in city_venues if not v.get('metadata', {}).get('qualityScore')]

    print(f"\n品質分數分佈:")
    print(f"  高品質 (≥75): {len(high_quality)}")
    print(f"  中品質 (50-74): {len(medium_quality)}")
    print(f"  低品質 (<50): {len(low_quality)}")
    print(f"  無分數: {len(no_quality)}")

    # 列出需要改進的場地
    needs_work = low_quality + no_quality
    if needs_work:
        print(f"\n需要改進的場地 ({len(needs_work)}):")
        for v in sorted(needs_work, key=lambda x: x.get('metadata', {}).get('qualityScore', 0)):
            quality = v.get('metadata', {}).get('qualityScore', 'N/A')
            print(f"  ID {v['id']:4d}: {v['name']:50s} Quality: {str(quality):>3s}")
    else:
        print(f"\n✅ {city} 所有場地已完成！")

# 總結
print(f"\n{'=' * 100}")
print("總結")
print("=" * 100)

total_venues = len(venues)
total_with_quality = sum(1 for v in venues if v.get('metadata', {}).get('qualityScore'))
high_quality_all = sum(1 for v in venues if v.get('metadata', {}).get('qualityScore', 0) >= 75)

print(f"總場地數: {total_venues}")
print(f"已評分: {total_with_quality}")
print(f"高品質 (≥75): {high_quality_all}")
print(f"完成率: {high_quality_all/total_venues*100:.1f}%")
