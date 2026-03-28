#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manually update remaining GIS venues with PDF data
"""
import json
from datetime import datetime


# Manually extracted from PDF text files
GIS_REMAINING_ROOMS = {
    1498: [  # 集思烏日會議中心
        {
            "id": "1498-瓦特廳",
            "name": "瓦特廳",
            "nameEn": "Watt Hall",
            "area": 82.0,
            "areaUnit": "坪",
            "floor": "3樓",
            "capacity": {"standard": 200, "classroom": 200, "theater": 270},
            "price": {"weekday": 22000, "holiday": 24000},
            "source": "gis_pdf_2026"
        },
        {
            "id": "1498-巴本廳",
            "name": "巴本廳",
            "nameEn": "Babben Hall",
            "area": 23.0,
            "areaUnit": "坪",
            "floor": "3樓",
            "capacity": {"standard": 51, "classroom": 51, "theater": 66},
            "price": {"weekday": 8000, "holiday": 9000},
            "source": "gis_pdf_2026"
        },
        {
            "id": "1498-富蘭克林廳",
            "name": "富蘭克林廳",
            "nameEn": "Franklin Hall",
            "area": 48.0,
            "areaUnit": "坪",
            "floor": "4樓",
            "capacity": {"standard": 132, "classroom": 132, "theater": 156},
            "price": {"weekday": 14500, "holiday": 16000},
            "source": "gis_pdf_2026"
        },
        {
            "id": "1498-史蒂文生廳",
            "name": "史蒂文生廳",
            "nameEn": " Stevenson Hall",
            "area": 28.0,
            "areaUnit": "坪",
            "floor": "4樓",
            "capacity": {"standard": 51, "classroom": 51, "theater": 78},
            "price": {"weekday": 9000, "holiday": 10000},
            "source": "gis_pdf_2026"
        },
        {
            "id": "1498-4樓休息室",
            "name": "4樓休息室",
            "nameEn": "4F Lounge",
            "area": 4.0,
            "areaUnit": "坪",
            "floor": "4樓",
            "capacity": {"standard": 6},
            "price": {"weekday": 2500, "holiday": 2800},
            "source": "gis_pdf_2026"
        },
    ],
    1496: [  # 集思竹科會議中心
        {
            "id": "1496-愛因斯坦廳",
            "name": "愛因斯坦廳",
            "nameEn": "Einstein Hall",
            "area": 63.0,
            "areaUnit": "坪",
            "floor": "2樓",
            "capacity": {"standard": 155, "theater": 155},
            "price": {"weekday": 11000, "holiday": 12000},
            "source": "gis_pdf_2025"
        },
        {
            "id": "1496-愛迪生廳",
            "name": "愛迪生廳",
            "nameEn": "Edison Hall",
            "area": 28.0,
            "areaUnit": "坪",
            "floor": "2樓",
            "capacity": {"standard": 75, "theater": 75},
            "price": {"weekday": 7500, "holiday": 8000},
            "source": "gis_pdf_2025"
        },
        {
            "id": "1496-達爾文廳",
            "name": "達爾文廳",
            "nameEn": "Darwin Hall",
            "area": 33.0,
            "areaUnit": "坪",
            "floor": "2樓",
            "capacity": {"standard": 72, "theater": 72},
            "price": {"weekday": 7000, "holiday": 7500},
            "source": "gis_pdf_2025"
        },
        {
            "id": "1496-牛頓廳",
            "name": "牛頓廳",
            "nameEn": "Newton Hall",
            "area": 21.0,
            "areaUnit": "坪",
            "floor": "2樓",
            "capacity": {"standard": 42, "theater": 42},
            "price": {"weekday": 6000, "holiday": 6500},
            "source": "gis_pdf_2025"
        },
        {
            "id": "1496-莎士比亞廳",
            "name": "莎士比亞廳",
            "nameEn": "Shakespeare Hall",
            "area": None,
            "areaUnit": "坪",
            "floor": "2樓",
            "capacity": {"standard": 8, "theater": 8},
            "price": {"weekday": 2000, "holiday": 2000},
            "source": "gis_pdf_2025"
        },
        {
            "id": "1496-巴哈廳",
            "name": "巴哈廳",
            "nameEn": "Bach Hall",
            "area": 28.0,
            "areaUnit": "坪",
            "floor": "4樓",
            "capacity": {"standard": 60, "theater": 60},
            "price": {"weekday": 7000, "holiday": 7500},
            "source": "gis_pdf_2025"
        },
        {
            "id": "1496-羅西尼廳",
            "name": "羅西尼廳",
            "nameEn": "Rossini Hall",
            "area": 43.0,
            "areaUnit": "坪",
            "floor": "4樓",
            "capacity": {"standard": 81, "theater": 81},
            "price": {"weekday": 8500, "holiday": 9000},
            "source": "gis_pdf_2025"
        },
        {
            "id": "1496-鄧肯廳",
            "name": "鄧肯廳",
            "nameEn": "Duncan Hall",
            "area": 25.0,
            "areaUnit": "坪",
            "floor": "4樓",
            "capacity": {"standard": 30},
            "price": {"weekday": 5000, "holiday": 5000},
            "source": "gis_pdf_2025"
        },
        {
            "id": "1496-伽利略廳",
            "name": "伽利略廳",
            "nameEn": "Galileo Hall",
            "area": 18.0,
            "areaUnit": "坪",
            "floor": "2樓",
            "capacity": {"standard": 20},
            "source": "gis_pdf_2025"
        },
    ],
}


def main():
    print("="*80)
    print("Update Remaining GIS Venues with Manual PDF Data")
    print("="*80)
    print()

    # Backup
    import shutil
    from datetime import datetime as dt
    backup_name = f"venues.json.backup.gis_remaining_{dt.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy('venues.json', backup_name)
    print(f"Backup: {backup_name}")
    print()

    # Load venues
    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    updated_count = 0

    # Update each venue
    for venue_id, rooms in GIS_REMAINING_ROOMS.items():
        for venue in venues:
            if venue.get('id') == venue_id:
                venue['rooms'] = rooms

                # Calculate max capacity
                if rooms:
                    max_cap = 0
                    for room in rooms:
                        for cap_type, cap_val in room.get('capacity', {}).items():
                            if cap_val > max_cap:
                                max_cap = cap_val

                    venue['capacity'] = {'standard': max_cap}

                # Update metadata
                venue['metadata'] = {
                    'lastScrapedAt': datetime.now().isoformat(),
                    'scrapeVersion': 'GIS_PDF_Manual_V2',
                    'scrapeConfidenceScore': 100,
                    'totalRooms': len(rooms),
                    'source': 'gis_official_pdf'
                }

                updated_count += 1
                print(f"Updated: {venue['name']} ({len(rooms)} rooms)")
                break

    # Save
    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)

    print()
    print(f"[OK] Updated {updated_count} venues")
    print()

    # Summary
    print("="*80)
    print("Summary")
    print("="*80)
    print()

    total_rooms = 0
    for venue_id, rooms in GIS_REMAINING_ROOMS.items():
        total_rooms += len(rooms)

        for venue in venues:
            if venue.get('id') == venue_id:
                print(f"{venue['name']}: {len(rooms)} rooms")

                for room in rooms:
                    cap = room.get('capacity', {}).get('standard', 'N/A')
                    area = room.get('area', 'N/A')
                    price = room.get('price', {})
                    price_str = f"{price.get('weekday', 'N/A')}/{price.get('holiday', 'N/A')}" if price else 'N/A'
                    print(f"  - {room['name']}: {cap} people, {area} ping, NT${price_str}")

                print()

    print(f"Total: {total_rooms} rooms added")


if __name__ == '__main__':
    main()
