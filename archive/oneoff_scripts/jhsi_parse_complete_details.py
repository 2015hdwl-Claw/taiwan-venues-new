#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整解析集思竹科和新烏日的會議室詳情頁
提取照片、尺寸、價格等完整資料
"""

from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import os
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("完整解析集思會議室詳情頁")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 竹科會議室
hcph_rooms = [
    {'name': '巴哈廳', 'file': 'jhsi_hcph_docs/巴哈廳_detail.html', 'eng': 'bach'},
    {'name': '羅西尼廳', 'file': 'jhsi_hcph_docs/羅西尼廳_detail.html', 'eng': 'rossini'},
    {'name': '鄧肯廳', 'file': 'jhsi_hcph_docs/鄧肯廳_detail.html', 'eng': 'duncan'},
    {'name': '愛因斯坦廳', 'file': 'jhsi_hcph_docs/愛因斯坦廳_detail.html', 'eng': 'einstein'},
    {'name': '愛迪生廳', 'file': 'jhsi_hcph_docs/愛迪生廳_detail.html', 'eng': 'edison'},
]

# 新烏日會議室（使用中文命名）
wuri_rooms = [
    {'name': '301會議室', 'file': 'jhsi_wuri_docs/301會議室_detail.html', 'venue': '瓦特廳', 'eng': '301'},
    {'name': '303會議室', 'file': 'jhsi_wuri_docs/303會議室_detail.html', 'venue': '巴本廳', 'eng': '303'},
    {'name': '401會議室', 'file': 'jhsi_wuri_docs/401會議室_detail.html', 'venue': '富蘭克林廳', 'eng': '401'},
    {'name': '402會議室', 'file': 'jhsi_wuri_docs/402會議室_detail.html', 'venue': '史蒂文生廳', 'eng': '402'},
]

all_data = {}

# 處理竹科
print("1. 竹科會議室")
print("-" * 100)

for room in hcph_rooms:
    print(f"\n{room['name']} ({room['eng']})")

    try:
        with open(room['file'], encoding='utf-8') as f:
            html = f.read()

        soup = BeautifulSoup(html, 'html.parser')

        # 提取照片
        photos = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if 'lease' in src.lower() and room['eng'] in src.lower():
                if not src.startswith('http'):
                    src = 'https://www.meeting.com.tw/hsp/' + src
                if src not in photos:
                    photos.append(src)

        # 提取文字內容
        text = soup.get_text()

        # 提取坪數
        area_ping = None
        match = re.search(r'(\d+\.?\d*)\s*坪', text)
        if match:
            area_ping = float(match.group(1))

        # 提取尺寸（長x寬）
        dimensions = None
        match = re.search(r'(\d+\.?\d*)\s*[米米]\s*[x×]\s*(\d+\.?\d*)\s*[米米]', text)
        if match:
            length = float(match.group(1))
            width = float(match.group(2))
            dimensions = {
                'length': length,
                'width': width
            }

        # 提取價格
        price = None
        price_patterns = [
            r'每時段.*?(\d{1,6})\s*元',
            r'時段.*?(\d{1,6})\s*元',
            r'租金.*?(\d{1,6})\s*元',
        ]
        for pattern in price_patterns:
            match = re.search(pattern, text)
            if match:
                price = int(match.group(1))
                if 1000 <= price <= 500000:
                    break

        # 提取樓層
        floor = None
        match = re.search(r'(\d+)F', text)
        if match:
            floor = match.group(1) + 'F'

        data = {
            'name': room['name'],
            'areaPing': area_ping,
            'dimensions': dimensions,
            'price': price,
            'floor': floor,
            'photos': photos,
            'photoCount': len(photos)
        }

        all_data[room['name']] = data

        print(f"  面積: {area_ping} 坪" if area_ping else "  面積: 未找到")
        print(f"  尺寸: {dimensions}" if dimensions else "  尺寸: 未找到")
        print(f"  價格: {price} 元/時段" if price else "  價格: 未找到")
        print(f"  樓層: {floor}" if floor else "  樓層: 未找到")
        print(f"  照片: {len(photos)} 張")

    except Exception as e:
        print(f"  ❌ 錯誤: {e}")

# 處理新烏日
print("\n\n2. 新烏日會議室")
print("-" * 100)

for room in wuri_rooms:
    print(f"\n{room['venue']} ({room['name']}, {room['eng']})")

    try:
        with open(room['file'], encoding='utf-8') as f:
            html = f.read()

        soup = BeautifulSoup(html, 'html.parser')

        # 提取照片
        photos = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if 'lease' in src.lower() and room['eng'] in src.lower():
                if not src.startswith('http'):
                    src = 'https://www.meeting.com.tw/xinwuri/' + src
                if src not in photos:
                    photos.append(src)

        # 提取文字內容
        text = soup.get_text()

        # 提取坪數
        area_ping = None
        match = re.search(r'(\d+\.?\d*)\s*坪', text)
        if match:
            area_ping = float(match.group(1))

        # 提取尺寸（長x寬）
        dimensions = None
        match = re.search(r'(\d+\.?\d*)\s*[米米]\s*[x×]\s*(\d+\.?\d*)\s*[米米]', text)
        if match:
            length = float(match.group(1))
            width = float(match.group(2))
            dimensions = {
                'length': length,
                'width': width
            }

        # 提取價格
        price = None
        price_patterns = [
            r'每時段.*?(\d{1,6})\s*元',
            r'時段.*?(\d{1,6})\s*元',
            r'租金.*?(\d{1,6})\s*元',
        ]
        for pattern in price_patterns:
            match = re.search(pattern, text)
            if match:
                price = int(match.group(1))
                if 1000 <= price <= 500000:
                    break

        # 提取樓層
        floor = None
        match = re.search(r'(\d+)F', text)
        if match:
            floor = match.group(1) + 'F'

        data = {
            'name': room['venue'],  # 使用 venue 名稱（瓦特廳等）
            'originalName': room['name'],  # 保留原名稱（301會議室等）
            'areaPing': area_ping,
            'dimensions': dimensions,
            'price': price,
            'floor': floor,
            'photos': photos,
            'photoCount': len(photos)
        }

        all_data[room['venue']] = data

        print(f"  面積: {area_ping} 坪" if area_ping else "  面積: 未找到")
        print(f"  尺寸: {dimensions}" if dimensions else "  尺寸: 未找到")
        print(f"  價格: {price} 元/時段" if price else "  價格: 未找到")
        print(f"  樓層: {floor}" if floor else "  樓層: 未找到")
        print(f"  照片: {len(photos)} 張")

    except Exception as e:
        print(f"  ❌ 錯誤: {e}")

# 儲存結果
output_file = 'jhsi_complete_room_data.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ 完整資料已儲存: {output_file}")

# 統計
print("\n" + "=" * 100)
print("統計")
print("=" * 100)

with_area = sum(1 for r in all_data.values() if r.get('areaPing'))
with_dimensions = sum(1 for r in all_data.values() if r.get('dimensions'))
with_price = sum(1 for r in all_data.values() if r.get('price'))
with_photos = sum(1 for r in all_data.values() if r.get('photos'))
total_photos = sum(len(r.get('photos', [])) for r in all_data.values())

print(f"總會議室: {len(all_data)}")
print(f"有面積: {with_area}/{len(all_data)}")
print(f"有尺寸: {with_dimensions}/{len(all_data)}")
print(f"有價格: {with_price}/{len(all_data)}")
print(f"有照片: {with_photos}/{len(all_data)}")
print(f"總照片數: {total_photos} 張")

print("\n" + "=" * 100)
print("✅ 解析完成")
print("=" * 100)
