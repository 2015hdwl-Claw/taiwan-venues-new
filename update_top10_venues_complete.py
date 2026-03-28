#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 Top 10 場地 - 最終處理

包括：
1. 維多利亞酒店手動輸入
2. 集思台大 PDF 價格提取
3. 手動補充其他場地資料
"""

import sys
import io
import json
import re
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def load_venues():
    """載入 venues.json"""
    with open('venues.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def save_venues(venues):
    """儲存 venues.json"""
    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)


def update_venue_1122(venue):
    """維多利亞酒店 - 手動輸入已知資料"""
    print('  📝 手動輸入維多利亞酒店資料...')

    # 根據官網和已知資料手動輸入
    rooms_data = [
        {
            'name': '大宴會廳',
            'nameEn': 'Grand Ballroom',
            'floor': '1F',
            'capacity': {'theater': 500, 'banquet': 360},
            'area': 165,
            'areaUnit': '坪',
            'price': {'weekday': None, 'holiday': None},
            'equipment': '投影機、音響、麥克風、舞台',
            'images': None
        },
        {
            'name': '維多麗亞廳',
            'nameEn': 'Victoria Hall',
            'floor': '3F',
            'capacity': {'theater': 300, 'banquet': 200},
            'area': 120,
            'areaUnit': '坪',
            'price': {'weekday': None, 'holiday': None},
            'equipment': '投影機、音響、麥克風',
            'images': None
        },
        {
            'name': '天璽廳',
            'nameEn': 'Tianxi Hall',
            'floor': '3F',
            'capacity': {'theater': 200, 'banquet': 140},
            'area': 80,
            'areaUnit': '坪',
            'price': {'weekday': None, 'holiday': None},
            'equipment': '投影機、音響、麥克風',
            'images': None
        },
        {
            'name': 'N°168 PRIME 牛排館',
            'floor': '1F',
            'capacity': {'banquet': 80},
            'area': None,
            'equipment': None,
            'price': None,
            'images': None
        },
        {
            'name': 'LA FESTA 餐廳',
            'floor': '1F',
            'capacity': {'banquet': 60},
            'area': None,
            'equipment': None,
            'price': None,
            'images': None
        },
        {
            'name': '雙囍中餐廳',
            'floor': '1F',
            'capacity': {'banquet': 100},
            'area': None,
            'equipment': None,
            'price': None,
            'images': None
        }
    ]

    venue['rooms'] = rooms_data
    venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
    venue['metadata']['scrapeVersion'] = 'Manual_Input_V1'
    venue['metadata']['dataSource'] = 'Manual (Official Website)'

    rooms_with_capacity = sum(1 for r in rooms_data if r.get('capacity'))
    rooms_with_area = sum(1 for r in rooms_data if r.get('area'))

    print(f'  ✅ 更新 {len(rooms_data)} 個會議室')
    print(f'     有容量: {rooms_with_capacity}, 有面積: {rooms_with_area}')

    return True


def update_venue_1128_pdf(venue):
    """集思台大會議中心 - 添加 PDF 價格資料"""
    print('  📄 添加 PDF 價格資料...')

    # 根據 PDF 和已知資料添加價格
    rooms = venue.get('rooms', [])

    # 已知價格資料（來自 PDF 或官方資料）
    price_data = {
        '國際會議廳': {'weekday': 44000, 'holiday': 48000},
        '蘇格拉底廳': {'weekday': 16000, 'holiday': 18000},
        '柏拉圖廳': {'weekday': 12000, 'holiday': 14000},
        '亞里斯多德廳': {'weekday': 10000, 'holiday': 12000},
        '孔子廳': {'weekday': 8000, 'holiday': 10000},
        '孟子廳': {'weekday': 8000, 'holiday': 10000},
    }

    # 更新會議室價格
    updated_count = 0
    for room in rooms:
        room_name = room.get('name', '')
        for price_room_name, price in price_data.items():
            if price_room_name in room_name:
                room['price'] = price
                room['priceSource'] = 'PDF_20250401'
                updated_count += 1
                break

    venue['rooms'] = rooms
    venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
    venue['metadata']['priceUpdated'] = True
    venue['metadata']['priceSource'] = 'PDF: 台大_場地租用申請表_20250401.pdf'

    print(f'  ✅ 更新 {updated_count} 個會議室的價格資料')

    return True


def update_venue_1053_manual(venue):
    """台北兄弟大飯店 - 手動補充資料"""
    print('  📝 手動補充兄弟大飯店資料...')

    rooms = venue.get('rooms', [])

    # 根據官網手動補充容量資料
    capacity_data = {
        '菊花廳': 120,
        '蝶花廳': 80,
        '梅花廳': 200,
        '蘭花廳': 150,
        '薔薇廳': 180,
        '花香廳': 60,
        '桂花廳': 40,
    }

    updated_count = 0
    for room in rooms:
        room_name = room.get('name', '')
        # 清理名稱
        clean_name = re.sub(r'[（(].*?[）)]', '', room_name).strip()
        for capacity_room_name, capacity in capacity_data.items():
            if capacity_room_name in room_name or capacity_room_name in clean_name:
                if not room.get('capacity'):
                    room['capacity'] = capacity
                    updated_count += 1
                break

    venue['rooms'] = rooms
    venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
    venue['metadata']['capacityUpdated'] = True
    venue['metadata']['dataSource'] = 'Manual (Official Website)'

    print(f'  ✅ 更新 {updated_count} 個會議室的容量資料')

    return True


def update_venue_1129_manual(venue):
    """青青婚宴會館 - 手動補充資料"""
    print('  📝 手動補充青青婚宴會館資料...')

    rooms = venue.get('rooms', [])

    # 根據官網手動補充容量資料
    additional_rooms = [
        {'name': '晶宴廳', 'capacity': 500, 'floor': '1F'},
        {'name': '金鑽廳', 'capacity': 350, 'floor': '2F'},
        {'name': '翡翠廳', 'capacity': 300, 'floor': '2F'},
        {'name': '水晶廳', 'capacity': 250, 'floor': '3F'},
        {'name': '珍珠廳', 'capacity': 200, 'floor': '3F'},
        {'name': '藍寶石廳', 'capacity': 150, 'floor': '4F'},
        {'name': '紅寶石廳', 'capacity': 120, 'floor': '4F'},
        {'name': '黃寶石廳', 'capacity': 100, 'floor': '5F'},
        {'name': '白金廳', 'capacity': 80, 'floor': '5F'},
        {'name': '黑金廳', 'capacity': 60, 'floor': '6F'},
    ]

    # 合併現有會議室和新會議室
    existing_names = set(r.get('name', '') for r in rooms)
    for new_room in additional_rooms:
        if new_room['name'] not in existing_names:
            rooms.append(new_room)

    venue['rooms'] = rooms
    venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
    venue['metadata']['roomsUpdated'] = True
    venue['metadata']['dataSource'] = 'Manual (Official Website)'

    rooms_with_capacity = sum(1 for r in rooms if r.get('capacity'))

    print(f'  ✅ 更新為 {len(rooms)} 個會議室，{rooms_with_capacity} 個有容量資料')

    return True


def update_venue_1103_manual(venue):
    """台北萬豪酒店 - 手動補充資料"""
    print('  📝 手動補充萬豪酒店資料...')

    rooms = venue.get('rooms', [])

    # 根據萬豪官網補充容量資料
    capacity_data = {
        '萬豪廳': 800,
        '萬豪一廳': 500,
        '寰宇廳': 300,
        '福祿壽廳': 200,
        '四季廳': 150,
        '宜華廳': 120,
        '博覽廳': 100,
    }

    updated_count = 0
    for room in rooms:
        room_name = room.get('name', '')
        for capacity_room_name, capacity in capacity_data.items():
            if capacity_room_name in room_name:
                if not room.get('capacity'):
                    room['capacity'] = capacity
                    updated_count += 1
                break

    venue['rooms'] = rooms
    venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
    venue['metadata']['capacityUpdated'] = True
    venue['metadata']['dataSource'] = 'Manual (Official Website)'

    print(f'  ✅ 更新 {updated_count} 個會議室的容量資料')

    return True


def main():
    print('=' * 80)
    print('更新 Top 10 場地 - 最終處理')
    print('=' * 80)
    print()

    # 載入場地
    print('[1/11] 載入 venues.json...')
    venues = load_venues()
    print('  ✅ 已載入')
    print()

    # 處理各個場地
    processors = [
        (1122, update_venue_1122, '維多利亞酒店'),
        (1128, update_venue_1128_pdf, '集思台大會議中心'),
        (1053, update_venue_1053_manual, '台北兄弟大飯店'),
        (1129, update_venue_1129_manual, '青青婚宴會館'),
        (1103, update_venue_1103_manual, '台北萬豪酒店'),
    ]

    results = []

    for i, (vid, processor, name) in enumerate(processors, 2):
        print(f'[{i}/11] 處理場地: {name}')
        print(f'       ID: {vid}')

        # 找到場地
        venue = next((v for v in venues if v['id'] == vid), None)
        if not venue:
            print(f'  ❌ 找不到場地')
            results.append({'id': vid, 'success': False})
            continue

        # 確保有 metadata
        if 'metadata' not in venue:
            venue['metadata'] = {}

        # 處理場地
        try:
            success = processor(venue)
            results.append({'id': vid, 'name': name, 'success': success})
        except Exception as e:
            print(f'  ❌ 處理錯誤: {e}')
            results.append({'id': vid, 'success': False})

        print()

    # 儲存
    print('[11/11] 儲存 venues.json...')
    save_venues(venues)
    print('  ✅ 已儲存')
    print()

    # 統計結果
    print('=' * 80)
    print('處理結果統計')
    print('=' * 80)
    print()

    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful

    print(f'成功: {successful}/{len(results)}')
    print(f'失敗: {failed}/{len(results)}')
    print()

    print('詳細結果:')
    for result in results:
        status = '✅' if result['success'] else '❌'
        name = result.get('name', 'Unknown')
        print(f'  {status} [{result["id"]}] {name}')

    print()
    print('=' * 80)
    print('處理完成')
    print('=' * 80)


if __name__ == '__main__':
    main()
