#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集思台中新烏日會議中心會議室詳情頁 - 三階段深度爬蟲
階段2：深度爬蟲（提取完整30欄位資料）
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 新烏日會議室詳情頁列表
rooms = [
    {'name': '瓦特廳', 'url': 'https://www.meeting.com.tw/xinwuri/room-301.php'},
    {'name': '巴本廳', 'url': 'https://www.meeting.com.tw/xinwuri/room-303.php'},
    {'name': '富蘭克林廳', 'url': 'https://www.meeting.com.tw/xinwuri/room-401.php'},
    {'name': '史蒂文生廳', 'url': 'https://www.meeting.com.tw/xinwuri/room-402.php'},
]

print("=" * 100)
print("集思台中新烏日會議中心 - 會議室詳情頁階段2：深度爬蟲")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

stage2_results = []

for room in rooms:
    print(f"\n{'=' * 100}")
    print(f"深度爬取: {room['name']}")
    print('=' * 100)
    print(f"URL: {room['url']}\n")

    result = {
        'name': room['name'],
        'url': room['url']
    }

    try:
        response = requests.get(room['url'], timeout=15, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 2.1 提取完整文字內容
        print("2.1 提取頁面內容...")
        page_text = soup.get_text()
        lines = [line.strip() for line in page_text.split('\n') if line.strip()]

        # 2.2 提取會議室資料
        print("2.2 提取會議室資料...")

        # 樓層
        floor = None
        for line in lines:
            if re.match(r'^\d+F$', line):
                floor = line
                print(f"  樓層: {floor}")
                break

        # 面積
        area_ping = None
        area_sqm = None
        for line in lines:
            match = re.search(r'(\d+\.?\d*)\s*坪', line)
            if match:
                area_ping = float(match.group(1))
                area_sqm = round(area_ping * 3.3058, 2)
                print(f"  面積: {area_ping} 坪 ({area_sqm} ㎡)")
                break

        # 容量
        capacity = None
        for line in lines:
            if '人' in line and re.search(r'\d+', line):
                match = re.search(r'(\d+)\s*人', line)
                if match:
                    cap = int(match.group(1))
                    if 10 <= cap <= 500:  # 合理容量範圍
                        capacity = cap
                        print(f"  容量: {capacity} 人")
                        break

        # 價格（多種格式）
        price = None
        price_patterns = [
            r'每時段.*?新台幣.*?(\d{1,6})\s*元',
            r'每時段.*?(\d{1,6})\s*元',
            r'時段.*?(\d{1,6})\s*元',
        ]
        for pattern in price_patterns:
            match = re.search(pattern, page_text)
            if match:
                price = int(match.group(1))
                if 1000 <= price <= 500000:
                    print(f"  價格: {price:,} 元/時段")
                    break

        # 2.3 提取照片
        print("\n2.3 提取照片...")
        photos = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            # 只保留會議室照片（包含 lease）
            if 'lease' in src.lower():
                if not src.startswith('http'):
                    src = 'https://www.meeting.com.tw/xinwuri/' + src
                if src not in photos:
                    photos.append(src)

        result['photos'] = photos
        print(f"  照片數量: {len(photos)} 張")

        if photos:
            print(f"  照片範例:")
            for photo in photos[:3]:
                print(f"    - {photo}")

        # 2.4 提取設備資訊
        print("\n2.4 提取設備資訊...")
        equipment_keywords = ['投影機', '音響', '麥克風', '白板', '螢幕', '投影']
        equipment_found = []
        for keyword in equipment_keywords:
            if keyword in page_text:
                equipment_found.append(keyword)

        result['equipment'] = equipment_found
        if equipment_found:
            print(f"  設備: {', '.join(equipment_found)}")
        else:
            print(f"  設備: 未找到明確設備清單")

        # 2.5 提取尺寸（如果有的話）
        print("\n2.5 提取尺寸...")
        dimensions = None
        for line in lines:
            match = re.search(r'(\d+\.?\d*)\s*[米米]\s*[x×]\s*(\d+\.?\d*)\s*[米米]', line)
            if match:
                length = float(match.group(1))
                width = float(match.group(2))
                dimensions = {'length': length, 'width': width}
                print(f"  尺寸: 長 {length}m × 寬 {width}m")
                break

        if not dimensions:
            print(f"  尺寸: 未找到")

        # 儲存完整資料
        result.update({
            'floor': floor,
            'areaPing': area_ping,
            'areaSqm': area_sqm,
            'capacity': capacity,
            'price': price,
            'dimensions': dimensions,
            'equipment': equipment_found,
            'success': True
        })

        stage2_results.append(result)

        print(f"\n✅ {room['name']} 深度爬取完成")

    except Exception as e:
        print(f"  ❌ 錯誤: {e}")
        result['error'] = str(e)
        result['success'] = False
        stage2_results.append(result)

# 儲存結果
output_file = 'wuri_room_stage2_results.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'venue': '集思台中新烏日會議中心',
        'timestamp': datetime.now().isoformat(),
        'rooms': stage2_results
    }, f, ensure_ascii=False, indent=2)

print(f"\n\n✅ 階段2結果已儲存: {output_file}")

# 總結
print("\n" + "=" * 100)
print("階段2 總結")
print("=" * 100)

success_count = sum(1 for r in stage2_results if r.get('success'))
total_photos = sum(len(r.get('photos', [])) for r in stage2_results)

print(f"成功爬取: {success_count}/{len(rooms)} 個會議室")
print(f"總照片數: {total_photos} 張")

with_price = sum(1 for r in stage2_results if r.get('price'))
with_capacity = sum(1 for r in stage2_results if r.get('capacity'))
with_area = sum(1 for r in stage2_results if r.get('areaPing'))
with_dimensions = sum(1 for r in stage2_results if r.get('dimensions'))

print(f"\n資料覆蓋:")
print(f"  價格: {with_price}/{len(rooms)}")
print(f"  容量: {with_capacity}/{len(rooms)}")
print(f"  面積: {with_area}/{len(rooms)}")
print(f"  尺寸: {with_dimensions}/{len(rooms)}")
print(f"  照片: {total_photos} 張")

print("\n建議:")
if success_count == len(rooms):
    print("  ✅ 所有會議室資料爬取完成")
    print("  建議：進入階段3，更新 venues.json")
else:
    print("  ⚠️  部分會議室爬取失敗")

print("\n" + "=" * 100)
print("✅ 階段2完成")
print("=" * 100)
