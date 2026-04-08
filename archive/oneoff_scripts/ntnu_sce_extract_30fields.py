#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
師大進修 - 從 HTML 提取完整 30 欄位會議室資料
"""

from bs4 import BeautifulSoup
import json
import sys
import re
from datetime import datetime
from urllib.parse import urljoin

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("師大進修推廣學院 - 提取 30 欄位會議室資料")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取保存的 HTML
html_file = "ntnu_sce_space_20260326_204212.html"

with open(html_file, 'r', encoding='utf-8') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')

# 提取會議室資訊
print("提取會議室資訊...")

rooms_data = []

# 尋找所有包含會議室資訊的元素
# 模式: 文字包含 "樓" + 類型 + "數字人" 或 "數字-數字人"
for img in soup.find_all('img'):
    alt = img.get('alt', '')
    src = img.get('src', '')

    # 尋找模式: "樓 + 類型 + (數字人)"
    match = re.search(r'(\d+樓)?([^（(]+)[（(]?\s*(\d+)(\s*[-~]\s*\d+)?\s*[人）)]', alt)
    if match:
        floor = match.group(1) if match.group(1) else None
        room_type = match.group(2).strip()
        capacity = int(match.group(3))

        # 清理類型名稱
        room_type = room_type.replace('（', '').replace('）', '').strip()

        room = {
            'name': room_type,
            'nameEn': None,
            'floor': floor,
            'capacity': {
                'theater': capacity,
                'banquet': None,
                'classroom': None,
                'uShape': None,
                'cocktail': None,
                'roundTable': None
            },
            'areaPing': None,
            'areaSqm': None,
            'dimensions': None,
            'price': {
                'weekday': None,
                'holiday': None,
                'note': None
            },
            'equipment': None,
            'equipmentList': [],
            'source': f'https://www.sce.ntnu.edu.tw{src}' if src.startswith('/') else src,
            'lastUpdated': datetime.now().isoformat()
        }

        rooms_data.append(room)

# 去重（基於名稱）
seen = set()
unique_rooms = []
for room in rooms_data:
    key = f"{room['floor']}_{room['name']}"
    if key not in seen:
        seen.add(key)
        unique_rooms.append(room)

print(f"找到會議室: {len(unique_rooms)} 間\n")

# 顯示會議室列表
for i, room in enumerate(unique_rooms, 1):
    floor_str = f"{room['floor']} " if room['floor'] else ""
    capacity_str = room['capacity']['theater']
    print(f"{i}. {floor_str}{room['name']} ({capacity_str} 人)")

# 建立 30 欄位資料結構
print("\n" + "=" * 100)
print("建立 30 欄位資料結構")
print("=" * 100)

venue_id = 1493
complete_rooms = []

for i, room_data in enumerate(unique_rooms, 1):
    room_id = f"{venue_id}-{str(i).zfill(2)}"

    # 英文名稱（簡單翻譯）
    name_en_map = {
        '演講堂': 'Lecture Hall',
        '視聽教室': 'Audio-Visual Classroom',
        '會議室': 'Meeting Room',
        '大教室': 'Large Classroom',
        '小教室': 'Small Classroom',
        '講座教室': 'Seminar Classroom',
        '電腦教室': 'Computer Classroom',
        '視訊會議室': 'Video Conference Room',
        '研討室': 'Seminar Room',
        '階梯教室': 'Tiered Classroom'
    }

    name_en = name_en_map.get(room_data['name'], room_data['name'])

    complete_room = {
        'id': room_id,
        'name': room_data['name'],
        'nameEn': name_en,
        'floor': room_data['floor'],
        'capacity': room_data['capacity'],
        'areaPing': None,
        'areaSqm': None,
        'area': None,
        'dimensions': None,
        'price': {
            'weekday': None,
            'holiday': None,
            'morning': None,
            'afternoon': None,
            'evening': None,
            'fullDay': None,
            'hourly': None,
            'note': '對外開放，需申請'
        },
        'equipment': None,
        'equipmentList': [],
        'features': '對外開放租借',
        'source': room_data['source'],
        'lastUpdated': datetime.now().isoformat()
    }

    complete_rooms.append(complete_room)

print(f"✅ 建立了 {len(complete_rooms)} 個會議室的完整資料結構")

# 計算完整度
complete_fields = 0
total_fields = len(complete_rooms) * 30  # 30 fields per room

for room in complete_rooms:
    # 基本資料 (5)
    if room['id']: complete_fields += 1
    if room['name']: complete_fields += 1
    if room['nameEn']: complete_fields += 1
    if room['floor']: complete_fields += 1
    if room.get('areaUnit') is not None: complete_fields += 1

    # 面積 (3)
    if room.get('areaPing') is not None: complete_fields += 1
    if room.get('areaSqm') is not None: complete_fields += 1
    if room.get('area') is not None: complete_fields += 1

    # 尺寸 (3)
    if room.get('dimensions'): complete_fields += 3

    # 容量 (6)
    capacity = room['capacity']
    if capacity.get('theater'): complete_fields += 1
    if capacity.get('banquet') is not None: complete_fields += 1
    if capacity.get('classroom') is not None: complete_fields += 1
    if capacity.get('uShape') is not None: complete_fields += 1
    if capacity.get('cocktail') is not None: complete_fields += 1
    if capacity.get('roundTable') is not None: complete_fields += 1

    # 價格 (8)
    price = room['price']
    if price.get('weekday') is not None: complete_fields += 1
    if price.get('holiday') is not None: complete_fields += 1
    if price.get('morning') is not None: complete_fields += 1
    if price.get('afternoon') is not None: complete_fields += 1
    if price.get('evening') is not None: complete_fields += 1
    if price.get('fullDay') is not None: complete_fields += 1
    if price.get('hourly') is not None: complete_fields += 1
    if price.get('note'): complete_fields += 1

    # 設備 (2)
    if room.get('equipment'): complete_fields += 1
    if room.get('equipmentList'): complete_fields += 1

    # 其他 (2)
    if room.get('features'): complete_fields += 1
    if room.get('source'): complete_fields += 1

completeness = (complete_fields / total_fields * 100) if total_fields > 0 else 0

print(f"\n完整度: {completeness:.1f}% ({complete_fields}/{total_fields} 欄位)")

# 儲存結果
result = {
    'venue': '師大進修推廣學院',
    'venue_id': venue_id,
    'total_rooms': len(complete_rooms),
    'completeness': f"{completeness:.1f}%",
    'rooms': complete_rooms,
    'timestamp': datetime.now().isoformat()
}

result_file = f'ntnu_sce_rooms_30fields_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
with open(result_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"✅ 30 欄位資料已儲存: {result_file}")

# 統計
print("\n" + "=" * 100)
print("統計資訊")
print("=" * 100)

# 容量範圍
capacities = [room['capacity']['theater'] for room in complete_rooms if room['capacity'].get('theater')]
if capacities:
    print(f"容量範圍:")
    print(f"  最小: {min(capacities)} 人")
    print(f"  最大: {max(capacities)} 人")
    print(f"  平均: {sum(capacities)//len(capacities)} 人")

# 樓層分布
floors = {}
for room in complete_rooms:
    floor = room.get('floor', 'Unknown')
    floors[floor] = floors.get(floor, 0) + 1

print(f"\n樓層分布:")
# Handle None values in floor keys
sorted_floors = sorted([(f if f is not None else 'Unknown', f) for f in floors.keys()], key=lambda x: x[0])
for floor_key, _ in sorted_floors:
    print(f"  {floor_key}: {floors[_]} 間")

print("\n" + "=" * 100)
print("✅ 師大進修 30 欄位資料提取完成")
print("=" * 100)
