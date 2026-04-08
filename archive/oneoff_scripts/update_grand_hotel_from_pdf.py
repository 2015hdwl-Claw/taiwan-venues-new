#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新圓山大飯店會議室容量資料（從官方 PDF）
並為所有 52 個場地新增交通資訊欄位
"""

import json
import sys
from datetime import datetime

# Set UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*100)
print("更新圓山大飯店會議室容量資料")
print("="*100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Read venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Create backup
backup_path = f"venues.json.backup.grandhotelpdf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
with open(backup_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"[OK] Backup created: {backup_path}\n")

# 容量資料從官方 PDF 提取
# Source: https://www.grand-hotel.org/fileupload/Ballroom/P_1.pdf
capacity_data = {
    "大會議廳": {
        "theater": 1000,
        "reception": 450,
        "banquet": 1200,
        "western": 500,
        "eastern": 1494
    },
    "崑崙廳": {
        "theater": 300,
        "reception": 160,
        "classroom": 50,
        "hollowSquare": 60,
        "uShape": 200,
        "western": 150,
        "eastern": 396
    },
    "國際會議廳": {
        "theater": 440
    },
    "大會議廳": {  # 12F 大會廳 (The Grand Ballroom)
        "theater": 1000,
        "reception": 450,
        "banquet": 1200,
        "western": 500,
        "eastern": 1494
    },
    "光崙廳": {  # 12F 崑崙廳 (Kunlun Hall)
        "theater": 300,
        "reception": 160,
        "classroom": 50,
        "hollowSquare": 60,
        "uShape": 200,
        "western": 150,
        "eastern": 396
    },
    "國際會議廳": {  # 10F Auditorium
        "theater": 385
    },
    "長青廳": {  # 10F Chang Chin Room
        "theater": 100,
        "reception": 60,
        "classroom": 40,
        "hollowSquare": 40,
        "uShape": 60,
        "eastern": 255
    },
    "松柏廳": {  # 10F Song Bo Room
        "theater": 200,
        "reception": 80,
        "classroom": 50,
        "hollowSquare": 46,
        "uShape": 150,
        "western": 120,
        "eastern": 310
    },
    "敦睦廳": {  # VF Int'l Reception Hall
        "theater": 350,
        "reception": 180,
        "classroom": 66,
        "hollowSquare": 102,
        "uShape": 400,
        "western": 240,
        "eastern": 540
    },
    "宴會廳": {  # BF Banquet Hall
        "banquet": 1500,
        "eastern": 800
    },
    "大宴會廳": {  # BF Banquet Hall
        "banquet": 1500,
        "eastern": 800
    },
    "富貴廳": {  # BF Fu Gui Room
        "theater": 180,
        "reception": 108,
        "classroom": 48,
        "hollowSquare": 72,
        "uShape": 300,
        "western": 160,
        "eastern": 478
    },
    "吉祥廳": {  # BF Ji Shiang Room
        "theater": 500,
        "reception": 225,
        "uShape": 700,
        "western": 340,
        "eastern": 640
    },
    "麒麟宴會廳": {  # VF Chi Lin Banquet Room
        "eastern": 276
    },
    "國宴廳": {  # VF State Banquet Room
        "eastern": 160
    }
}

# Find 圓山大飯店
grand_hotel_idx = next((i for i, v in enumerate(data) if v.get('id') == 1072), None)
if grand_hotel_idx is None:
    print("❌ 找不到圓山大飯店")
    sys.exit(1)

grand_hotel = data[grand_hotel_idx]

print(f"找到圓山大飯店: {grand_hotel['name']}")
print(f"會議室數量: {len(grand_hotel.get('rooms', []))}\n")

# Update room capacities
updated_count = 0
for room in grand_hotel.get('rooms', []):
    room_name = room.get('name', '')

    # Try to find capacity data
    capacity = None
    if room_name in capacity_data:
        capacity = capacity_data[room_name]

    if capacity:
        if 'capacity' not in room:
            room['capacity'] = {}

        # Update capacities
        for key, value in capacity.items():
            if value and value != '---':
                room['capacity'][key] = value

        updated_count += 1
        print(f"✅ 更新 {room_name}: {room['capacity']}")

print(f"\n共更新 {updated_count} 間會議室容量")

# Add data source metadata
if 'metadata' not in grand_hotel:
    grand_hotel['metadata'] = {}

grand_hotel['metadata']['capacitySource'] = 'https://www.grand-hotel.org/fileupload/Ballroom/P_1.pdf'
grand_hotel['metadata']['capacityUpdatedAt'] = datetime.now().isoformat()

data[grand_hotel_idx] = grand_hotel

# Now add transportation info to ALL venues
print(f"\n{'='*100}")
print("為所有場地新增交通資訊欄位")
print(f"{'='*100}\n")

transport_added = 0
for venue in data:
    if 'transportation' not in venue:
        venue['transportation'] = {
            "car": "",
            "publicTransport": "",
            "mrt": "",
            "bus": "",
            "parking": "",
            "notes": ""
        }
        transport_added += 1

print(f"✅ 為 {transport_added} 個場地新增交通資訊欄位")

# Update venues.json
print(f"\n{'='*100}")
print("更新 venues.json")
print(f"{'='*100}")

with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ 已儲存\n")

# Show updated Grand Hotel rooms
print(f"{'='*100}")
print("圓山大飯店更新後的會議室容量")
print(f"{'='*100}\n")

for room in grand_hotel.get('rooms', []):
    name = room.get('name', '')
    floor = room.get('floor', '')
    area = room.get('area', '')
    capacity = room.get('capacity', {})

    print(f"{name} ({floor})")
    print(f"  面積: {area} sqm")
    if capacity:
        print(f"  容量: {capacity}")
    print()

print(f"{'='*100}")
print("✅ 圓山大飯店容量資料已更新")
print(f"{'='*100}")
print(f"\n備份檔案: {backup_path}")
print(f"更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

print(f"\n💡 下一步:")
print(f"   1. 人工檢查圓山大飯店容量資料正確性")
print(f"   2. 為每個場地填寫交通資訊")
print(f"   3. 繼續處理其他飯店資料")
