#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正 MVP 資料 - 使用會議室資料而不是場地資料
"""

import json
import sys

def load_venues(filepath: str):
    """載入場地資料"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_meeting_rooms(venues: list) -> list:
    """
    從場地資料中提取所有會議室
    每個會議室成為獨立的搜尋項目
    """
    meeting_rooms = []

    for venue in venues:
        # 只處理台北市的場地
        if venue.get('city') != '台北市':
            continue

        rooms = venue.get('rooms', [])
        if not rooms or len(rooms) == 0:
            continue

        # 處理每個會議室
        for room in rooms:
            # 使用會議室的照片，如果沒有則用場地照片
            room_images = room.get('images', {})
            venue_images = venue.get('images', {})

            # 處理 images 可能是 list 的情況
            if isinstance(room_images, list):
                # 如果是 list，使用第一個作為 main photo
                main_photo = room_images[0] if room_images else ''
                gallery_photos = room_images[1:4] if len(room_images) > 1 else []
            else:
                # 如果是 dict，正常處理
                main_photo = room_images.get('main', '')
                gallery_photos = []
                if 'gallery' in room_images:
                    gallery_photos = room_images['gallery'][:3]

            # 如果沒有會議室主照片，使用場地照片
            if not main_photo:
                if isinstance(venue_images, list):
                    main_photo = venue_images[0] if venue_images else ''
                    if len(gallery_photos) == 0 and len(venue_images) > 1:
                        gallery_photos = venue_images[1:4]
                else:
                    main_photo = venue_images.get('main', '')
                    if len(gallery_photos) == 0 and 'gallery' in venue_images:
                        gallery_photos = venue_images['gallery'][:3]

            gallery_photos = []
            if 'gallery' in room_images:
                gallery_photos = room_images['gallery'][:3]
            elif len(gallery_photos) == 0 and 'gallery' in venue_images:
                gallery_photos = venue_images['gallery'][:3]

            # 如果都沒有照片，跳過
            if not main_photo:
                continue

            # 建立會議室物件
            meeting_room = {
                'id': f"{venue.get('id')}-{room.get('id', '')}",
                'name': f"{venue.get('name')} - {room.get('name')}",
                'original_venue': venue.get('name'),
                'room_name': room.get('name'),
                'venueType': venue.get('venueType', ''),
                'city': venue.get('city', ''),
                'address': venue.get('address', ''),

                # 容量和價格
                'capacity': (room.get('capacity', {}).get('theater', 0)
                            if isinstance(room.get('capacity'), dict)
                            else (room.get('capacity', 0)
                                 if isinstance(room.get('capacity'), (int, float))
                                 else 0)),
                'area': room.get('area', 0) or 0,
                'areaUnit': room.get('areaUnit', '㎡') or '㎡',
                'floor': room.get('floor', '') or '',

                # 價格（優先使用會議室價格）
                'price': ((room.get('price', {}).get('note')
                          if isinstance(room.get('price'), dict) and room.get('price', {}).get('note')
                          else venue.get('priceHalfDay', 0)) or 0),
                'priceType': ('note'
                             if (isinstance(room.get('price'), dict) and
                                 room.get('price', {}).get('note'))
                             else 'half_day'),

                # 照片
                'photos': {
                    'main': main_photo,
                    'gallery': gallery_photos
                },

                # 額外資訊
                'dimensions': room.get('dimensions', {}),
                'capacityType': room.get('capacityType', ''),

                # 聯絡資訊
                'contact': venue.get('contact', {}),
                'url': venue.get('url', '')
            }

            meeting_rooms.append(meeting_room)

    return meeting_rooms

def prepare_tags(meeting_rooms: list):
    """為每個會議室生成標籤"""
    for room in meeting_rooms:
        capacity = room['capacity'] or 0

        # 容量等級
        if capacity < 50:
            capacity_level = '小型(<50)'
        elif capacity <= 200:
            capacity_level = '中型(50-200)'
        else:
            capacity_level = '大型(200+)'

        # 價格等級
        price = room.get('price', 0)
        if isinstance(price, str):
            price_level = '需聯繫'
        elif price and price < 10000:
            price_level = '經濟型(<$10000)'
        elif price and price <= 30000:
            price_level = '標準型($10000-$30000)'
        elif price and price > 30000:
            price_level = '高級型(>$30000)'
        else:
            price_level = '未提供'

        # 行政區
        address = room.get('address', '')
        districts = ['信義區', '中山區', '大安區', '松山區',
                     '中正區', '大同區', '萬華區', '文山區',
                     '南港區', '內湖區', '士林區', '北投區']
        district = '其他'
        for d in districts:
            if d in address:
                district = d
                break

        room['tags'] = {
            'district': district,
            'capacity_level': capacity_level,
            'price_level': price_level
        }

def main():
    print('修正 MVP 資料 - 提取會議室')
    print('=' * 50)

    # 1. 載入場地資料
    try:
        venues = load_venues('venues.json')
        print(f'載入 {len(venues)} 個場地')
    except FileNotFoundError:
        print('ERROR: venues.json not found')
        return 1

    # 2. 提取會議室
    meeting_rooms = extract_meeting_rooms(venues)
    print(f'提取出 {len(meeting_rooms)} 個會議室')

    # 3. 準備標籤
    prepare_tags(meeting_rooms)

    # 4. 儲存結果
    with open('mvp_venues_ready.json', 'w', encoding='utf-8') as f:
        json.dump(meeting_rooms, f, ensure_ascii=False, indent=2)

    print(f'已儲存到 mvp_venues_ready.json')

    # 5. 統計
    print(f'\n統計:')
    print(f'  總會議室數: {len(meeting_rooms)}')

    venues_count = {}
    for room in meeting_rooms:
        venue = room['original_venue']
        venues_count[venue] = venues_count.get(venue, 0) + 1

    print(f'  來自場地數: {len(venues_count)}')

    print(f'\n會議室最多的前 5 個場地:')
    sorted_venues = sorted(venues_count.items(), key=lambda x: x[1], reverse=True)
    for venue, count in sorted_venues[:5]:
        print(f'  {venue}: {count} 個會議室')

    return 0

if __name__ == '__main__':
    sys.exit(main())
