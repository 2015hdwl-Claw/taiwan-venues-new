#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根據 PDF 內容手動更新集思會議中心資料
"""
import json
from datetime import datetime


# 從 PDF 手動提取的資料
GIS_PDF_ROOMS = {
    1128: [  # 集思台大會議中心
        {
            "id": "1128-國際會議廳",
            "name": "國際會議廳",
            "nameEn": "International Conference Hall",
            "area": 253.6,
            "areaUnit": "坪",
            "capacity": {"standard": 400, "classroom": 400},
            "floor": "3樓",
            "source": "gis_pdf_2025"
        },
        {
            "id": "1128-蘇格拉底廳",
            "name": "蘇格拉底廳",
            "nameEn": "Socrates Hall",
            "area": 59.8,
            "areaUnit": "坪",
            "capacity": {"standard": 145, "theater": 145},
            "floor": "3樓",
            "source": "gis_pdf_2025"
        },
        {
            "id": "1128-柏拉圖廳",
            "name": "柏拉圖廳",
            "nameEn": "Plato Hall",
            "area": 69.3,
            "areaUnit": "坪",
            "capacity": {"standard": 150, "classroom": 150},
            "floor": "3樓",
            "source": "gis_pdf_2025"
        },
        {
            "id": "1128-洛克廳",
            "name": "洛克廳",
            "nameEn": "Locke Hall",
            "area": 37.7,
            "areaUnit": "坪",
            "capacity": {"standard": 90, "classroom": 90},
            "floor": "3樓",
            "source": "gis_pdf_2025"
        },
        {
            "id": "1128-亞歷山大廳",
            "name": "亞歷山大廳",
            "nameEn": "Aristotle Hall",
            "area": 31.3,
            "areaUnit": "坪",
            "capacity": {"standard": 54, "classroom": 54},
            "floor": "3樓",
            "source": "gis_pdf_2025"
        },
        {
            "id": "1128-阿基米德廳",
            "name": "阿基米德廳",
            "nameEn": "Archimedes Hall",
            "area": 31.3,
            "areaUnit": "坪",
            "capacity": {"standard": 54, "classroom": 54},
            "floor": "3樓",
            "source": "gis_pdf_2025"
        },
        {
            "id": "1128-達文西廳",
            "name": "達文西廳",
            "nameEn": "Da Vinci Hall",
            "area": 41.4,
            "areaUnit": "坪",
            "capacity": {"standard": 48, "theater": 48},
            "floor": "3樓",
            "source": "gis_pdf_2025"
        },
        {
            "id": "1128-拉斐爾廳",
            "name": "拉斐爾廳",
            "nameEn": "Raphael Hall",
            "area": 41.4,
            "areaUnit": "坪",
            "capacity": {"standard": 72, "theater": 72},
            "floor": "3樓",
            "source": "gis_pdf_2025"
        },
        {
            "id": "1128-米開朗基羅廳",
            "name": "米開朗基羅廳",
            "nameEn": "Michelangelo Hall",
            "area": 41.4,
            "areaUnit": "坪",
            "capacity": {"standard": 72, "theater": 72},
            "floor": "3樓",
            "source": "gis_pdf_2025"
        },
        {
            "id": "1128-尼采廳",
            "name": "尼采廳",
            "nameEn": "Nietzsche Hall",
            "area": 41.4,
            "areaUnit": "坪",
            "capacity": {"standard": 48, "theater": 48},
            "floor": "3樓",
            "source": "gis_pdf_2025"
        },
        {
            "id": "1128-講者休息室",
            "name": "講者休息室",
            "nameEn": "Speaker Lounge",
            "area": 5.1,
            "areaUnit": "坪",
            "capacity": {"standard": 6},
            "floor": "3樓",
            "source": "gis_pdf_2025"
        },
    ],
    1494: [  # 集思交通部會議中心
        {
            "id": "1494-國際會議廳",
            "name": "國際會議廳",
            "nameEn": "International Conference Hall",
            "area": 121.0,
            "areaUnit": "坪",
            "capacity": {"standard": 193, "theater": 193},
            "floor": "3樓",
            "source": "gis_pdf_2025"
        },
        {
            "id": "1494-142廳",
            "name": "142廳",
            "nameEn": "Hall 142",
            "area": 60.0,
            "areaUnit": "坪",
            "capacity": {"standard": 60},
            "floor": "2樓",
            "source": "gis_pdf_2025"
        },
        {
            "id": "1494-108廳",
            "name": "108廳",
            "nameEn": "Hall 108",
            "area": 34.0,
            "areaUnit": "坪",
            "capacity": {"standard": 40},
            "floor": "2樓",
            "source": "gis_pdf_2025"
        },
        {
            "id": "1494-會議室",
            "name": "多功能會議室",
            "nameEn": "Multi-function Room",
            "area": 30.0,
            "areaUnit": "坪",
            "capacity": {"standard": 30},
            "floor": "2樓",
            "source": "gis_pdf_2025"
        },
    ],
    1497: [  # 集思中國醫會議中心
        {
            "id": "1497-201",
            "name": "201會議室",
            "nameEn": "Room 201",
            "area": 63.0,
            "areaUnit": "坪",
            "capacity": {"standard": 63},
            "floor": "2樓",
            "source": "gis_pdf_2025"
        },
        {
            "id": "1497-202",
            "name": "202會議室",
            "nameEn": "Room 202",
            "area": 28.0,
            "areaUnit": "坪",
            "capacity": {"standard": 48},
            "floor": "2樓",
            "source": "gis_pdf_2025"
        },
        {
            "id": "1497-203",
            "name": "203會議室",
            "nameEn": "Room 203",
            "area": 33.0,
            "areaUnit": "坪",
            "capacity": {"standard": 50},
            "floor": "2樓",
            "source": "gis_pdf_2025"
        },
        {
            "id": "1497-205",
            "name": "205會議室",
            "nameEn": "Room 205",
            "area": 21.0,
            "areaUnit": "坪",
            "capacity": {"standard": 35},
            "floor": "2樓",
            "source": "gis_pdf_2025"
        },
        {
            "id": "1497-401",
            "name": "401會議室",
            "nameEn": "Room 401",
            "area": 28.0,
            "areaUnit": "坪",
            "capacity": {"standard": 40},
            "floor": "4樓",
            "source": "gis_pdf_2025"
        },
        {
            "id": "1497-402",
            "name": "402會議室",
            "nameEn": "Room 402",
            "area": 28.0,
            "areaUnit": "坪",
            "capacity": {"standard": 40},
            "floor": "4樓",
            "source": "gis_pdf_2025"
        },
        {
            "id": "1497-501",
            "name": "501會議室",
            "nameEn": "Room 501",
            "area": 21.0,
            "areaUnit": "坪",
            "capacity": {"standard": 35},
            "floor": "5樓",
            "source": "gis_pdf_2025"
        },
    ],
}


def main():
    print("="*80)
    print("Update GIS venues with PDF data")
    print("="*80)
    print()

    # 讀取 venues.json
    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    updated_count = 0

    # 更新每個場地
    for venue_id, rooms in GIS_PDF_ROOMS.items():
        for venue in venues:
            if venue.get('id') == venue_id:
                venue['rooms'] = rooms

                # 計算最大容量
                if rooms:
                    max_cap = 0
                    for room in rooms:
                        if room.get('capacity', {}).get('standard', 0) > max_cap:
                            max_cap = room['capacity']['standard']

                    venue['capacity'] = {'standard': max_cap}

                # 更新 metadata
                venue['metadata'] = {
                    'lastScrapedAt': datetime.now().isoformat(),
                    'scrapeVersion': 'GIS_PDF_Manual',
                    'scrapeConfidenceScore': 100,
                    'totalRooms': len(rooms),
                    'source': 'gis_official_pdf'
                }

                updated_count += 1
                print(f"Updated: {venue['name']} ({len(rooms)} rooms)")
                break

    # 儲存
    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)

    print()
    print(f"[OK] Updated {updated_count} venues")
    print()

    # 顯示摘要
    print("="*80)
    print("Summary")
    print("="*80)
    print()

    total_rooms = 0
    for venue_id, rooms in GIS_PDF_ROOMS.items():
        total_rooms += len(rooms)

        for venue in venues:
            if venue.get('id') == venue_id:
                print(f"{venue['name']}: {len(rooms)} rooms")

                for room in rooms:
                    cap = room['capacity']['standard']
                    area = room['area']
                    print(f"  - {room['name']}: {cap} people, {area} ping")

                print()

    print(f"Total: {total_rooms} rooms")


if __name__ == '__main__':
    main()
