#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新集思會議中心資料到 venues.json
"""
import json
from datetime import datetime


def main():
    # 讀取爬取結果
    with open('gis_scrape_results.json', 'r', encoding='utf-8') as f:
        scrape_results = json.load(f)

    # 讀取 venues.json
    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    print("="*80)
    print("Update GIS meeting centers to venues.json")
    print("="*80)
    print()

    updated_count = 0

    for result in scrape_results:
        venue_id = result['venue_id']
        venue_name = result['venue_name']
        rooms = result['rooms']
        total = result['total']

        # 找到對應的場地
        for venue in venues:
            if venue.get('id') == venue_id:
                print(f"Update: {venue_name} (ID: {venue_id})")
                print(f"  Rooms: {total}")

                # 更新會議室資料
                venue['rooms'] = rooms

                # 更新最大容量
                max_capacity = 0
                for room in rooms:
                    if room.get('capacity', {}).get('standard', 0) > max_capacity:
                        max_capacity = room['capacity']['standard']

                if max_capacity > 0:
                    venue['capacity'] = {'standard': max_capacity}

                # 更新 metadata
                venue['metadata'] = {
                    'lastScrapedAt': datetime.now().isoformat(),
                    'scrapeVersion': 'GIS_Generic',
                    'scrapeConfidenceScore': 85,
                    'totalRooms': total,
                    'source': 'gis_official'
                }

                updated_count += 1
                print(f"  [OK] Updated")
                print()

                break

    # 儲存更新後的 venues.json
    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)

    print("="*80)
    print(f"Updated {updated_count} venues")
    print("="*80)
    print()

    # 顯示摘要
    print("Summary:")
    print()

    for result in scrape_results:
        venue_name = result['venue_name']
        total = result['total']
        print(f"  {venue_name}: {total} rooms")

        for room in result['rooms']:
            area = room.get('area', 'N/A')
            floor = room.get('floor', 'N/A')
            print(f"    - {room['name']}: {area} ping, {floor}")

    print()
    print("Next step: Add capacity data")


if __name__ == '__main__':
    main()
