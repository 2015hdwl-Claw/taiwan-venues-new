#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根據官方 PDF 更新南港展覽館正確的會議室資料
"""
import json
from datetime import datetime


# 從 PDF 提取的完整會議室資料
PDF_ROOMS = [
    # 3樓
    {
        "id": "1500-3-福軒",
        "name": "福軒（1館3樓）",
        "nameEn": "福軒",
        "floor": "1館3樓",
        "area": 83.5,
        "areaUnit": "㎡",
        "areaPing": 25.3,
        "dimensions": "9.6 x 8.7 x 3.9",
        "height": 3.9,
        "capacity": {
            "theater": 60,
            "classroom": 32,
            "standard": 48,
            "horseshoe": 20,
            "uShape": 28
        },
        "price": {
            "weekday": 13800,
            "holiday": 16600
        },
        "source": "tainex_pdf_2026"
    },

    # 4樓
    {
        "id": "1500-4-401",
        "name": "401（1館4樓）",
        "nameEn": "401",
        "floor": "1館4樓",
        "area": 375.7,
        "areaUnit": "㎡",
        "areaPing": 113.7,
        "dimensions": "20.2 x 18.6 x 3.5",
        "height": 3.5,
        "capacity": {
            "theater": 384,
            "classroom": 144,
            "standard": 216,
            "horseshoe": 52,
            "uShape": 72
        },
        "price": {
            "weekday": 39900,
            "holiday": 47900
        },
        "source": "tainex_pdf_2026"
    },
    {
        "id": "1500-4-402",
        "name": "402（1館4樓）",
        "nameEn": "402",
        "floor": "1館4樓",
        "area": 372.6,
        "areaUnit": "㎡",
        "areaPing": 112.7,
        "dimensions": "27.0 x 13.8 x 3.5",
        "height": 3.5,
        "capacity": {
            "theater": 396,
            "classroom": 168,
            "standard": 224,
            "horseshoe": 62,
            "uShape": 80
        },
        "price": {
            "weekday": 39400,
            "holiday": 47300
        },
        "source": "tainex_pdf_2026"
    },
    {
        "id": "1500-4-402a",
        "name": "402A（1館4樓）",
        "nameEn": "402a",
        "floor": "1館4樓",
        "area": 121.4,
        "areaUnit": "㎡",
        "areaPing": 36.7,
        "dimensions": "8.8 x 13.8 x 3.5",
        "height": 3.5,
        "capacity": {
            "theater": 100,
            "classroom": 56,
            "standard": 72,
            "horseshoe": 26,
            "uShape": 36
        },
        "price": {
            "weekday": 12900,
            "holiday": 15500
        },
        "source": "tainex_pdf_2026"
    },
    {
        "id": "1500-4-402b",
        "name": "402B（1館4樓）",
        "nameEn": "402b",
        "floor": "1館4樓",
        "area": 122.8,
        "areaUnit": "㎡",
        "areaPing": 37.1,
        "dimensions": "8.9 x 13.8 x 3.5",
        "height": 3.5,
        "capacity": {
            "theater": 110,
            "classroom": 56,
            "standard": 72,
            "horseshoe": 26,
            "uShape": 36
        },
        "price": {
            "weekday": 12900,
            "holiday": 15500
        },
        "source": "tainex_pdf_2026"
    },
    {
        "id": "1500-4-402c",
        "name": "402C（1館4樓）",
        "nameEn": "402c",
        "floor": "1館4樓",
        "area": 128.3,
        "areaUnit": "㎡",
        "areaPing": 38.8,
        "dimensions": "9.3 x 13.8 x 3.5",
        "height": 3.5,
        "capacity": {
            "theater": 110,
            "classroom": 56,
            "standard": 72,
            "horseshoe": 26,
            "uShape": 36
        },
        "price": {
            "weekday": 13600,
            "holiday": 16300
        },
        "source": "tainex_pdf_2026"
    },
    {
        "id": "1500-4-402a+b",
        "name": "402A+B（1館4樓）",
        "nameEn": "402a+b",
        "floor": "1館4樓",
        "area": 244.3,
        "areaUnit": "㎡",
        "areaPing": 73.9,
        "dimensions": "17.7 x 13.8 x 3.5",
        "height": 3.5,
        "capacity": {
            "theater": 234,
            "classroom": 108,
            "standard": 144,
            "horseshoe": 42,
            "uShape": 56
        },
        "price": {
            "weekday": 25800,
            "holiday": 31000
        },
        "source": "tainex_pdf_2026"
    },
    {
        "id": "1500-4-402b+c",
        "name": "402B+C（1館4樓）",
        "nameEn": "402b+c",
        "floor": "1館4樓",
        "area": 251.2,
        "areaUnit": "㎡",
        "areaPing": 76.0,
        "dimensions": "18.2 x 13.8 x 3.5",
        "height": 3.5,
        "capacity": {
            "theater": 234,
            "classroom": 108,
            "standard": 144,
            "horseshoe": 42,
            "uShape": 56
        },
        "price": {
            "weekday": 26500,
            "holiday": 31800
        },
        "source": "tainex_pdf_2026"
    },
    {
        "id": "1500-4-403",
        "name": "403（1館4樓）",
        "nameEn": "403",
        "floor": "1館4樓",
        "area": 149.5,
        "areaUnit": "㎡",
        "areaPing": 45.2,
        "dimensions": "8.4 x 17.8 x 3.5",
        "height": 3.5,
        "capacity": {
            "theater": 125,
            "classroom": 68,
            "standard": 92,
            "horseshoe": 34,
            "uShape": 44
        },
        "price": {
            "weekday": 15600,
            "holiday": 18700
        },
        "source": "tainex_pdf_2026"
    },
    {
        "id": "1500-4-404",
        "name": "404（1館4樓）",
        "nameEn": "404",
        "floor": "1館4樓",
        "area": 133.5,
        "areaUnit": "㎡",
        "areaPing": 40.4,
        "dimensions": "9.3 x 12.9 x 3.5",
        "height": 3.5,
        "capacity": {
            "theater": 90,
            "classroom": 48,
            "standard": 72,
            "horseshoe": 26,
            "uShape": 36
        },
        "price": {
            "weekday": 14000,
            "holiday": 16800
        },
        "source": "tainex_pdf_2026"
    },

    # 5樓
    {
        "id": "1500-5-500",
        "name": "500（1館5樓）",
        "nameEn": "500",
        "floor": "1館5樓",
        "area": 159.8,
        "areaUnit": "㎡",
        "areaPing": 48.3,
        "dimensions": "9.7 x 18.6 x 2.8",
        "height": 2.8,
        "capacity": {
            "theater": 140,
            "classroom": 72,
            "standard": 116,
            "horseshoe": 46,
            "uShape": 52
        },
        "price": {
            "weekday": 16700,
            "holiday": 20000
        },
        "source": "tainex_pdf_2026"
    },
    {
        "id": "1500-5-501",
        "name": "501（1館5樓）",
        "nameEn": "501",
        "floor": "1館5樓",
        "area": 131.1,
        "areaUnit": "㎡",
        "areaPing": 39.7,
        "dimensions": "9.3 x 14.1 x 2.8",
        "height": 2.8,
        "capacity": {
            "theater": 105,
            "classroom": 56,
            "standard": 84,
            "horseshoe": 30,
            "uShape": 36
        },
        "price": {
            "weekday": 13800,
            "holiday": 16600
        },
        "source": "tainex_pdf_2026"
    },
    {
        "id": "1500-5-502",
        "name": "502（1館5樓）",
        "nameEn": "502",
        "floor": "1館5樓",
        "area": 102.3,
        "areaUnit": "㎡",
        "areaPing": 30.9,
        "dimensions": "7.6 x 12.0 x 2.8",
        "height": 2.8,
        "capacity": {
            "theater": 95,
            "classroom": 34,
            "standard": 68,
            "horseshoe": 26,
            "uShape": 32
        },
        "price": {
            "weekday": 10700,
            "holiday": 12800
        },
        "source": "tainex_pdf_2026"
    },
    {
        "id": "1500-5-503",
        "name": "503（1館5樓）",
        "nameEn": "503",
        "floor": "1館5樓",
        "area": 150.9,
        "areaUnit": "㎡",
        "areaPing": 45.7,
        "dimensions": "9.7 x 14.2 x 2.8",
        "height": 2.8,
        "capacity": {
            "theater": 110,
            "classroom": 56,
            "standard": 84,
            "horseshoe": 30,
            "uShape": 36
        },
        "price": {
            "weekday": 15600,
            "holiday": 18700
        },
        "source": "tainex_pdf_2026"
    },
    {
        "id": "1500-5-504",
        "name": "504（1館5樓）",
        "nameEn": "504",
        "floor": "1館5樓",
        "area": 505.4,
        "areaUnit": "㎡",
        "areaPing": 152.9,
        "dimensions": "26.6 x 19.0 x 2.8",
        "height": 2.8,
        "capacity": {
            "theater": 504,
            "classroom": 224,
            "standard": 360,
            "horseshoe": 68,
            "uShape": 84
        },
        "price": {
            "weekday": 52700,
            "holiday": 63300
        },
        "source": "tainex_pdf_2026"
    },
    {
        "id": "1500-5-504a",
        "name": "504A（1館5樓）",
        "nameEn": "504a",
        "floor": "1館5樓",
        "area": 184.3,
        "areaUnit": "㎡",
        "areaPing": 55.8,
        "dimensions": "9.7 x 19.0 x 2.8",
        "height": 2.8,
        "capacity": {
            "theater": 165,
            "classroom": 80,
            "standard": 120,
            "horseshoe": 38,
            "uShape": 44
        },
        "price": {
            "weekday": 19300,
            "holiday": 23200
        },
        "source": "tainex_pdf_2026"
    },
    {
        "id": "1500-5-504b",
        "name": "504B（1館5樓）",
        "nameEn": "504b",
        "floor": "1館5樓",
        "area": 169.1,
        "areaUnit": "㎡",
        "areaPing": 51.2,
        "dimensions": "8.9 x 19.0 x 2.8",
        "height": 2.8,
        "capacity": {
            "theater": 150,
            "classroom": 80,
            "standard": 120,
            "horseshoe": 38,
            "uShape": 44
        },
        "price": {
            "weekday": 17600,
            "holiday": 21100
        },
        "source": "tainex_pdf_2026"
    },
    {
        "id": "1500-5-504c",
        "name": "504C（1館5樓）",
        "nameEn": "504c",
        "floor": "1館5樓",
        "area": 152.0,
        "areaUnit": "㎡",
        "areaPing": 46.0,
        "dimensions": "8.0 x 19.0 x 2.8",
        "height": 2.8,
        "capacity": {
            "theater": 150,
            "classroom": 80,
            "standard": 120,
            "horseshoe": 38,
            "uShape": 44
        },
        "price": {
            "weekday": 15800,
            "holiday": 19000
        },
        "source": "tainex_pdf_2026"
    },
    {
        "id": "1500-5-504a+b",
        "name": "504A+B（1館5樓）",
        "nameEn": "504a+b",
        "floor": "1館5樓",
        "area": 353.4,
        "areaUnit": "㎡",
        "areaPing": 106.9,
        "dimensions": "18.6 x 19.0 x 2.8",
        "height": 2.8,
        "capacity": {
            "theater": 336,
            "classroom": 144,
            "standard": 216,
            "horseshoe": 48,
            "uShape": 64
        },
        "price": {
            "weekday": 36900,
            "holiday": 44300
        },
        "source": "tainex_pdf_2026"
    },
    {
        "id": "1500-5-504b+c",
        "name": "504B+C（1館5樓）",
        "nameEn": "504b+c",
        "floor": "1館5樓",
        "area": 321.1,
        "areaUnit": "㎡",
        "areaPing": 97.1,
        "dimensions": "16.9 x 19.0 x 2.8",
        "height": 2.8,
        "capacity": {
            "theater": 312,
            "classroom": 128,
            "standard": 216,
            "horseshoe": 48,
            "uShape": 64
        },
        "price": {
            "weekday": 33400,
            "holiday": 40100
        },
        "source": "tainex_pdf_2026"
    },
    {
        "id": "1500-5-505",
        "name": "505（1館5樓）",
        "nameEn": "505",
        "floor": "1館5樓",
        "area": 511.1,
        "areaUnit": "㎡",
        "areaPing": 154.6,
        "dimensions": "26.9 x 19.0 x 2.7",
        "height": 2.7,
        "capacity": {
            "theater": 504,
            "classroom": 224,
            "standard": 360,
            "horseshoe": 68,
            "uShape": 84
        },
        "price": {
            "weekday": 53300,
            "holiday": 64000
        },
        "source": "tainex_pdf_2026"
    },
    {
        "id": "1500-5-505a",
        "name": "505A（1館5樓）",
        "nameEn": "505a",
        "floor": "1館5樓",
        "area": 178.6,
        "areaUnit": "㎡",
        "areaPing": 54.0,
        "dimensions": "9.4 x 19.0 x 2.7",
        "height": 2.7,
        "capacity": {
            "theater": 165,
            "classroom": 80,
            "standard": 120,
            "horseshoe": 38,
            "uShape": 44
        },
        "price": {
            "weekday": 18600,
            "holiday": 22300
        },
        "source": "tainex_pdf_2026"
    },
    {
        "id": "1500-5-505b",
        "name": "505B（1館5樓）",
        "nameEn": "505b",
        "floor": "1館5樓",
        "area": 171.0,
        "areaUnit": "㎡",
        "areaPing": 51.7,
        "dimensions": "9.0 x 19.0 x 2.7",
        "height": 2.7,
        "capacity": {
            "theater": 150,
            "classroom": 80,
            "standard": 120,
            "horseshoe": 38,
            "uShape": 44
        },
        "price": {
            "weekday": 17800,
            "holiday": 21400
        },
        "source": "tainex_pdf_2026"
    },
    {
        "id": "1500-5-505c",
        "name": "505C（1館5樓）",
        "nameEn": "505c",
        "floor": "1館5樓",
        "area": 161.5,
        "areaUnit": "㎡",
        "areaPing": 48.9,
        "dimensions": "8.5 x 19.0 x 2.7",
        "height": 2.7,
        "capacity": {
            "theater": 150,
            "classroom": 80,
            "standard": 120,
            "horseshoe": 38,
            "uShape": 44
        },
        "price": {
            "weekday": 16900,
            "holiday": 20300
        },
        "source": "tainex_pdf_2026"
    },
    {
        "id": "1500-5-505a+b",
        "name": "505A+B（1館5樓）",
        "nameEn": "505a+b",
        "floor": "1館5樓",
        "area": 349.6,
        "areaUnit": "㎡",
        "areaPing": 105.7,
        "dimensions": "18.4 x 19.0 x 2.7",
        "height": 2.7,
        "capacity": {
            "theater": 336,
            "classroom": 144,
            "standard": 216,
            "horseshoe": 48,
            "uShape": 64
        },
        "price": {
            "weekday": 36400,
            "holiday": 43700
        },
        "source": "tainex_pdf_2026"
    },
    {
        "id": "1500-5-505b+c",
        "name": "505B+C（1館5樓）",
        "nameEn": "505b+c",
        "floor": "1館5樓",
        "area": 332.5,
        "areaUnit": "㎡",
        "areaPing": 100.6,
        "dimensions": "17.5 x 19.0 x 2.7",
        "height": 2.7,
        "capacity": {
            "theater": 312,
            "classroom": 128,
            "standard": 216,
            "horseshoe": 48,
            "uShape": 64
        },
        "price": {
            "weekday": 34700,
            "holiday": 41700
        },
        "source": "tainex_pdf_2026"
    },
    {
        "id": "1500-5-506",
        "name": "506（1館5樓）",
        "nameEn": "506",
        "floor": "1館5樓",
        "area": 176.7,
        "areaUnit": "㎡",
        "areaPing": 53.5,
        "dimensions": "9.3 x 19.0 x 2.7",
        "height": 2.7,
        "capacity": {
            "theater": 165,
            "classroom": 80,
            "standard": 120,
            "horseshoe": 38,
            "uShape": 44
        },
        "price": {
            "weekday": 18500,
            "holiday": 22200
        },
        "source": "tainex_pdf_2026"
    },
    {
        "id": "1500-5-507",
        "name": "507（1館5樓）",
        "nameEn": "507",
        "floor": "1館5樓",
        "area": 176.7,
        "areaUnit": "㎡",
        "areaPing": 53.5,
        "dimensions": "9.3 x 19.0 x 2.7",
        "height": 2.7,
        "capacity": {
            "theater": 165,
            "classroom": 80,
            "standard": 120,
            "horseshoe": 38,
            "uShape": 44
        },
        "price": {
            "weekday": 18500,
            "holiday": 22200
        },
        "source": "tainex_pdf_2026"
    },
]


def main():
    print("="*80)
    print("根據官方 PDF 更新南港展覽館資料")
    print("="*80)
    print()

    print(f"PDF 中的會議室總數: {len(PDF_ROOMS)}")
    print()

    # 讀取 venues.json
    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    # 找到南港展覽館
    for venue in venues:
        if venue.get('id') == 1500:
            print("更新南港展覽館 (ID: 1500)...")

            # 更新會議室資料
            venue['rooms'] = PDF_ROOMS

            # 更新最大容量
            max_theater = 0
            for room in PDF_ROOMS:
                if room.get('capacity', {}).get('theater', 0) > max_theater:
                    max_theater = room['capacity']['theater']

            venue['capacity'] = {
                'theater': max_theater
            }

            # 更新 metadata
            venue['metadata'] = {
                'lastScrapedAt': datetime.now().isoformat(),
                'scrapeVersion': 'PDF_2026_Official',
                'scrapeConfidenceScore': 100,
                'totalRooms': len(PDF_ROOMS),
                'source': 'tainex_official_pdf_2026',
                'pdfEffectiveDate': '2026-01-01'
            }

            print(f"  會議室數量: {len(PDF_ROOMS)}")
            print(f"  最大容量: {max_theater} 人 (劇院型)")
            print(f"  資料來源: 官方 PDF (生效日期 2026-01-01)")
            print()

            break

    # 儲存更新後的 venues.json
    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)

    print("[OK] 已更新 venues.json")
    print()

    # 顯示會議室清單
    print("="*80)
    print("會議室清單")
    print("="*80)
    print()

    # 按樓層分組
    floors = {}
    for room in PDF_ROOMS:
        floor = room['floor']
        if floor not in floors:
            floors[floor] = []
        floors[floor].append(room)

    for floor in sorted(floors.keys()):
        print(f"{floor}:")
        for room in floors[floor]:
            cap = room['capacity']
            price = room['price']
            print(f"  - {room['name']}")
            print(f"    容量: {cap['theater']} (劇院) / {cap['standard']} (標準) / {cap['classroom']} (教室)")
            print(f"    面積: {room['area']}㎡ ({room['areaPing']}坪)")
            print(f"    價格: ${price['weekday']:,} (平日) / ${price['holiday']:,} (假日)")

    print()
    print("="*80)
    print("完成！")
    print("="*80)


if __name__ == '__main__':
    main()
