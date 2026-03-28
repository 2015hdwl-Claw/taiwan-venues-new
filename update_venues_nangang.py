#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
將南港展覽館會議室資料更新到 venues.json
"""
import json
from datetime import datetime


def main():
    # 讀取南港展覽館會議室資料
    with open('nangang_rooms_final.json', 'r', encoding='utf-8') as f:
        nangang_rooms = json.load(f)

    # 讀取 venues.json
    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    # 找到南港展覽館 (ID: 1500)
    venue_1500 = None
    venue_index = None

    for i, venue in enumerate(venues):
        if venue.get('id') == 1500:
            venue_1500 = venue
            venue_index = i
            break

    if not venue_1500:
        print("[ERROR] 找不到 ID 1500 (南港展覽館)")
        return

    print("="*80)
    print("更新南港展覽館 (ID: 1500)")
    print("="*80)
    print()

    # 更新會議室資料
    venue_1500['rooms'] = nangang_rooms
    venue_1500['metadata'] = {
        'lastScrapedAt': datetime.now().isoformat(),
        'scrapeVersion': 'V2_Nangang',
        'scrapeConfidenceScore': 95,
        'totalRooms': len(nangang_rooms),
        'source': 'tainex_official'
    }

    # 更新最大容量
    max_theater = 0
    for room in nangang_rooms:
        if room.get('capacity', {}).get('theater', 0) > max_theater:
            max_theater = room['capacity']['theater']

    venue_1500['capacity'] = {
        'theater': max_theater
    }

    # 更新聯絡資訊（從官網）
    venue_1500['contact'] = {
        'phone': '+886-2-2725-5200',
        'extension': '5527',
        'email': 'tainex1@taitra.org.tw'
    }

    # 更新地址
    venue_1500['address'] = '台北市南港區經貿二路1號'

    # 更新 URL
    venue_1500['url'] = 'https://www.tainex.com.tw/venue/room-info/1/3'

    # 更新 verified 狀態
    venue_1500['verified'] = True

    # 儲存更新後的 venues.json
    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)

    print(f"[OK] 已更新 {len(nangang_rooms)} 個會議室")
    print(f"[OK] 最大容量: {max_theater} 人 (劇院型)")
    print()

    # 顯示會議室摘要
    print("會議室列表:")
    for room in nangang_rooms:
        print(f"  - {room['name']}")
        if room.get('capacity'):
            cap = room['capacity']
            print(f"    容量: {cap['theater']} (劇院型) / {cap['standard']} (標準型) / {cap['classroom']} (教室型)")
        if room.get('area'):
            print(f"    面積: {room['area']} {room['areaUnit']}")
        if room.get('price') and room['price'].get('weekday'):
            price = room['price']
            weekday_price = price.get('weekday', 0)
            holiday_price = price.get('holiday', weekday_price)
            print(f"    價格: ${weekday_price:,} (平日) / ${holiday_price:,} (假日)")

    print()
    print("="*80)
    print("完成！已更新 venues.json")
    print("="*80)


if __name__ == '__main__':
    main()
