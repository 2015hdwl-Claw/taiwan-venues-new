#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
準備 MVP 資料
從 mvp_venues_day1.json 生成 mvp_venues_ready.json
使用場地的原照片 URL
"""

import json
import sys

def load_venues(filepath: str):
    """載入場地資料"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_district(address: str) -> str:
    """從地址提取行政區"""
    if not address:
        return '其他'

    districts = ['信義區', '中山區', '大安區', '松山區',
                 '中正區', '大同區', '萬華區', '文山區',
                 '南港區', '內湖區', '士林區', '北投區']

    for district in districts:
        if district in address:
            return district

    return '其他'

def get_capacity_level(capacity: int) -> str:
    """根據容量分級"""
    if not capacity:
        return '未知'

    if capacity < 50:
        return '小型(<50)'
    elif capacity <= 200:
        return '中型(50-200)'
    else:
        return '大型(200+)'

def get_price_level(price: int) -> str:
    """根據價格分級"""
    if not price or price == 0:
        return '未提供'

    if price < 10000:
        return '經濟型(<$10000)'
    elif price <= 30000:
        return '標準型($10000-$30000)'
    else:
        return '高級型(>$30000)'

def prepare_mvp_venues(venues: list) -> list:
    """準備 MVP 場地資料"""
    mvp_ready = []

    for venue in venues:
        # 提取基本資料
        venue_id = venue.get('id')
        name = venue.get('name')
        city = venue.get('city', '')
        address = venue.get('address', '')
        venue_type = venue.get('venueType', '')

        # 容量和價格
        capacity = venue.get('maxCapacityTheater', 0)
        price_half = venue.get('priceHalfDay', 0)
        price_full = venue.get('priceFullDay', 0)

        # 照片（使用原 URL）
        images = venue.get('images', {})
        main_photo = images.get('main', '')
        gallery = images.get('gallery', [])

        # 確保至少有 3 張 gallery photos
        if len(gallery) < 3:
            continue

        # 聯絡資訊
        contact = venue.get('contact', {})
        phone = contact.get('phone', '') if isinstance(contact, dict) else ''

        # 建立標籤
        tags = {
            'district': get_district(address),
            'capacity_level': get_capacity_level(capacity),
            'price_level': get_price_level(price_half)
        }

        # 建立場地物件
        mvp_venue = {
            'id': venue_id,
            'name': name,
            'city': city,
            'address': address,
            'venueType': venue_type,
            'capacity': capacity,
            'price': price_half,
            'priceFull': price_full,
            'tags': tags,
            'photos': {
                'main': main_photo,
                'gallery': gallery[:3]  # 只取前 3 張
            },
            'contact': {
                'phone': phone
            }
        }

        mvp_ready.append(mvp_venue)

    return mvp_ready

def main():
    print('Preparing MVP venues data...')
    print('=' * 50)

    # 1. 載入 Day 1 結果
    try:
        venues = load_venues('mvp_venues_day1.json')
        print(f'Loaded {len(venues)} venues from Day 1')
    except FileNotFoundError:
        print('ERROR: mvp_venues_day1.json not found')
        print('Please run Day 1 first: python3 day1_photo_filter.py')
        return 1

    # 2. 準備 MVP 資料
    mvp_venues = prepare_mvp_venues(venues)

    print(f'Prepared {len(mvp_venues)} MVP venues')

    # 3. 儲存結果
    with open('mvp_venues_ready.json', 'w', encoding='utf-8') as f:
        json.dump(mvp_venues, f, ensure_ascii=False, indent=2)

    print(f'Saved to mvp_venues_ready.json')

    # 4. 統計標籤分佈
    print('\nTag distribution:')

    districts = {}
    for venue in mvp_venues:
        district = venue['tags']['district']
        districts[district] = districts.get(district, 0) + 1

    print('\nDistricts:')
    for district, count in sorted(districts.items(), key=lambda x: x[1], reverse=True):
        print(f'  {district}: {count}')

    capacity_levels = {}
    for venue in mvp_venues:
        level = venue['tags']['capacity_level']
        capacity_levels[level] = capacity_levels.get(level, 0) + 1

    print('\nCapacity levels:')
    for level, count in sorted(capacity_levels.items(), key=lambda x: x[1], reverse=True):
        print(f'  {level}: {count}')

    price_levels = {}
    for venue in mvp_venues:
        level = venue['tags']['price_level']
        price_levels[level] = price_levels.get(level, 0) + 1

    print('\nPrice levels:')
    for level, count in sorted(price_levels.items(), key=lambda x: x[1], reverse=True):
        print(f'  {level}: {count}')

    print(f'\n✅ MVP data ready!')
    print(f'Next: Create index.html, app.js, style.css')

    return 0

if __name__ == '__main__':
    sys.exit(main())
