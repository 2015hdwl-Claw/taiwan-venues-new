#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看 venues.json 中的場地資料
- 查看所有場地列表
- 查看特定場地的會議室資料
- 查看資料完整性統計
"""

import sys
import io
import json
from pathlib import Path

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def load_venues():
    """載入 venues.json"""
    with open('venues.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def list_all_venues(venues):
    """列出所有場地"""
    print('\n' + '=' * 80)
    print('所有場地列表')
    print('=' * 80)

    for i, venue in enumerate(venues, 1):
        vid = venue.get('id', 'N/A')
        name = venue.get('name', 'Unknown')[:40]
        vtype = venue.get('venueType', 'N/A')
        city = venue.get('city', 'N/A')

        rooms_count = len(venue.get('rooms', []))
        verified = '✅' if venue.get('verified') else '❌'

        print(f'{i:3d}. [{vid}] {name:40s} {vtype:12s} {city:6s} {verified} ({rooms_count} rooms)')


def show_venue_details(venues, venue_id):
    """顯示特定場地的詳細資料"""
    venue = next((v for v in venues if v.get('id') == venue_id), None)

    if not venue:
        print(f'\n❌ 找不到場地 ID: {venue_id}')
        return

    print('\n' + '=' * 80)
    print(f'場地詳細資料: {venue.get("name")} (ID: {venue_id})')
    print('=' * 80)

    # 基本信息
    print(f'\n【基本信息】')
    print(f'  名稱: {venue.get("name")}')
    print(f'  類型: {venue.get("venueType")}')
    print(f'  城市: {venue.get("city")}')
    print(f'  地址: {venue.get("address", "N/A")}')
    print(f'  URL: {venue.get("url", "N/A")}')

    # 聯絡資訊
    contact = venue.get('contact', {})
    if contact:
        print(f'\n【聯絡資訊】')
        print(f'  電話: {contact.get("phone", "N/A")}')
        print(f'  Email: {contact.get("email", "N/A")}')

    # 容量
    print(f'\n【容量資訊】')
    print(f'  劇院式: {venue.get("maxCapacityTheater", "N/A")} 人')
    print(f'  教室式: {venue.get("maxCapacityClassroom", "N/A")} 人')

    # 會議室
    rooms = venue.get('rooms', [])
    if rooms:
        print(f'\n【會議室列表】({len(rooms)} 個)')
        print('-' * 80)

        for i, room in enumerate(rooms, 1):
            name = room.get('name', 'N/A')
            capacity = room.get('capacity', {})
            if isinstance(capacity, dict):
                cap = capacity.get('theater', 'N/A')
            else:
                cap = capacity if capacity else 'N/A'

            area = room.get('area', 'N/A')
            price = room.get('price', 'N/A')

            if isinstance(price, dict):
                price_str = f"平日: NT${price.get('weekday', 'N/A'):,}, 假日: NT${price.get('holiday', 'N/A'):,}"
            elif isinstance(price, (int, float)):
                price_str = f"NT${price:,}"
            else:
                price_str = 'N/A'

            cap_str = str(cap) if cap != 'N/A' else 'N/A'
            area_str = str(area) if area != 'N/A' else 'N/A'
            print(f'{i:2d}. {name:30s} | {cap_str:5s} 人 | {area_str:6s} 坪 | {price_str}')

            # 顯示設備（如果有）
            equipment = room.get('equipment') or room.get('facilities')
            if equipment:
                print(f'     設備: {equipment[:70]}')
    else:
        print(f'\n【會議室】無會議室資料')

    # 元數據
    metadata = venue.get('metadata', {})
    if metadata:
        print(f'\n【爬蟲元數據】')
        print(f'  最後爬取: {metadata.get("lastScrapedAt", "N/A")}')
        print(f'  爬蟲版本: {metadata.get("scrapeVersion", "N/A")}')
        print(f'  總會議室: {metadata.get("totalRooms", len(rooms))}')


def show_statistics(venues):
    """顯示統計資訊"""
    print('\n' + '=' * 80)
    print('資料完整性統計')
    print('=' * 80)

    total_venues = len(venues)
    verified_venues = sum(1 for v in venues if v.get('verified'))

    total_rooms = sum(len(v.get('rooms', [])) for v in venues)

    venues_with_rooms = sum(1 for v in venues if v.get('rooms'))
    venues_with_contact = sum(1 for v in venues if v.get('contact'))
    venues_with_url = sum(1 for v in venues if v.get('url'))

    print(f'\n總場地數: {total_venues}')
    print(f'已驗證場地: {verified_venues} ({verified_venues*100//total_venues}%)')
    print(f'總會議室數: {total_rooms}')
    print(f'\n有會議室資料: {venues_with_rooms} ({venues_with_rooms*100//total_venues}%)')
    print(f'有聯絡資訊: {venues_with_contact} ({venues_with_contact*100//total_venues}%)')
    print(f'有網站 URL: {venues_with_url} ({venues_with_url*100//total_venues}%)')


def show_top10_summary(venues):
    """顯示 Top 10 場地摘要"""
    top10_ids = [1493, 1042, 1448, 1125, 1053, 1122, 1129, 1049, 1103, 1128]

    print('\n' + '=' * 80)
    print('Top 10 場地資料摘要')
    print('=' * 80)

    for vid in top10_ids:
        venue = next((v for v in venues if v.get('id') == vid), None)
        if venue:
            name = venue.get('name', 'Unknown')[:30]
            rooms = venue.get('rooms', [])
            rooms_count = len(rooms)

            # 檢查資料完整性
            has_capacity = sum(1 for r in rooms if r.get('capacity'))
            has_price = sum(1 for r in rooms if r.get('price'))
            has_area = sum(1 for r in rooms if r.get('area'))

            cap_coverage = f'{has_capacity*100//rooms_count}%' if rooms_count else 'N/A'
            price_coverage = f'{has_price*100//rooms_count}%' if rooms_count else 'N/A'
            area_coverage = f'{has_area*100//rooms_count}%' if rooms_count else 'N/A'

            status = '✅' if rooms_count > 0 else '❌'

            print(f'\n[{vid}] {name} {status}')
            print(f'     會議室: {rooms_count} | 容量: {cap_coverage} | 價格: {price_coverage} | 面積: {area_coverage}')


def main():
    """主程式"""
    import argparse

    parser = argparse.ArgumentParser(description='查看 venues.json 資料')
    parser.add_argument('--list', action='store_true', help='列出所有場地')
    parser.add_argument('--id', type=int, help='顯示特定場地詳細資料')
    parser.add_argument('--stats', action='store_true', help='顯示統計資訊')
    parser.add_argument('--top10', action='store_true', help='顯示 Top 10 摘要')

    args = parser.parse_args()

    # 載入資料
    print('載入 venues.json...')
    venues = load_venues()
    print(f'✅ 已載入 {len(venues)} 個場地')

    # 執行對應操作
    if args.list:
        list_all_venues(venues)
    elif args.id:
        show_venue_details(venues, args.id)
    elif args.stats:
        show_statistics(venues)
    elif args.top10:
        show_top10_summary(venues)
    else:
        # 預設顯示選單
        print('\n' + '=' * 80)
        print('請選擇操作:')
        print('=' * 80)
        print('1. 列出所有場地')
        print('2. 查看特定場地詳細資料')
        print('3. 查看統計資訊')
        print('4. 查看 Top 10 摘要')
        print('\n使用範例:')
        print('  python view_venues_data.py --list')
        print('  python view_venues_data.py --id 1128')
        print('  python view_venues_data.py --stats')
        print('  python view_venues_data.py --top10')


if __name__ == '__main__':
    main()
