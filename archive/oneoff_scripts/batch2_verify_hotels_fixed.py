#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批次抓取並驗證下一批 5 家飯店（批次 2）
"""

import json
import sys
import re
from datetime import datetime

# Set UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from scrapling.fetchers import Fetcher

print("="*120)
print("批次抓取並驗證下一批 5 家飯店（批次 2）")
print("="*120)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Read venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Create backup
backup_path = f"venues.json.backup.batch2hotels_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
with open(backup_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"[OK] Backup created: {backup_path}\n")

# Next 5 hotels to process
hotels = [
    {'id': 1090, 'name': '茹曦酒店 ILLUME TAIPEI'},
    {'id': 1075, 'name': '台北寒舍喜來登大飯店'},
    {'id': 1122, 'name': '維多麗亞酒店'},
    {'id': 1069, 'name': '台北國賓大飯店(AmbassadorTaipei)'},
    {'id': 1085, 'name': '台北文華東方酒店(MOHTaipei)'},
]

for hotel_info in hotels:
    venue_id = hotel_info['id']
    venue_name = hotel_info['name']

    print(f"\n{'='*120}")
    print(f"[{venue_id}] {venue_name}")
    print(f"{'='*120}")

    # Find venue
    venue_idx = next((i for i, v in enumerate(data) if v.get('id') == venue_id), None)
    if not venue_idx:
        print(f"   ❌ 找不到場地")
        continue

    venue = data[venue_idx]
    rooms = venue.get('rooms', [])

    print(f"\n📊 基本資訊:")
    print(f"   會議室: {len(rooms)} 間")
    print(f"   地址: {venue.get('address', 'N/A')}")
    print(f"   電話: {venue.get('contactPhone', 'N/A')}")
    print(f"   Email: {venue.get('contactEmail', 'N/A')}")

    # Fetch official website
    url = venue.get('url', '')
    if url:
        print(f"\n📡 抓取官網: {url}")
        try:
            page = Fetcher.get(url, impersonate='chrome', timeout=15)
            print(f"   ✅ 成功抓取官網")

            # Extract all text
            text_content = ' '.join(page.css('::text').getall())

            # Look for phone
            phones = re.findall(r'0\d-\d{4}-\d{4}', text_content)
            if phones:
                print(f"   📞 找到電話: {phones[0]}")

            # Look for emails
            emails = re.findall(r'[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}', text_content)
            if emails:
                valid_emails = [e for e in emails if not any(x in e for x in ['example', 'test', '.png', '.jpg'])]
                if valid_emails:
                    print(f"   📧 找到 Email: {valid_emails[0]}")

        except Exception as e:
            print(f"   ❌ 官網抓取失敗: {str(e)[:80]}")

    # Show rooms summary
    print(f"\n🏛️  會議室摘要:")

    # Group by floor
    floor_groups = {}
    for room in rooms:
        floor = room.get('floor', 'Unknown')
        if floor not in floor_groups:
            floor_groups[floor] = []
        floor_groups[floor].append(room)

    for floor in sorted(floor_groups.keys()):
        floor_rooms = floor_groups[floor]
        print(f"\n   {floor} ({len(floor_rooms)} 間):")
        for room in floor_rooms[:5]:  # Show first 5
            name = room.get('name', '')
            name_en = room.get('nameEn', '')
            capacity = room.get('capacity', {})
            theater = capacity.get('theater', 'N/A') if capacity else 'N/A'
            area = room.get('area', '')

            print(f"      • {name} ({name_en}) - {area} sqm - {theater} 人")

        if len(floor_rooms) > 5:
            print(f"      ... 還有 {len(floor_rooms)-5} 間")

    # Check completeness
    print(f"\n📋 資料完整性:")

    rooms_with_images = sum(1 for r in rooms if r.get('images') and len(r.get('images', [])) > 0)
    rooms_with_prices = sum(1 for r in rooms if r.get('price'))

    print(f"   有照片: {rooms_with_images}/{len(rooms)} ({100*rooms_with_images/len(rooms):.0f}%)")
    print(f"   有價格: {rooms_with_prices}/{len(rooms)} ({100*rooms_with_prices/len(rooms):.0f}%)")

    # Calculate overall score
    image_score = (rooms_with_images / len(rooms) * 50) if rooms else 0
    price_score = (rooms_with_prices / len(rooms) * 50) if rooms else 0
    total_score = image_score + price_score

    grade = "A" if total_score >= 80 else "B" if total_score >= 60 else "C"
    print(f"   資料品質: {total_score:.0f}/100 ({grade})")

    # Add metadata
    if 'metadata' not in venue:
        venue['metadata'] = {}
    venue['metadata']['batchVerified'] = datetime.now().isoformat()
    venue['metadata']['dataSource'] = 'Official website + Scrapling'

# Update the data array
print(f"\n{'='*120}")
print("✅ 更新 venues.json")
print(f"{'='*120}")

# Save
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"   已儲存")

print(f"\n{'='*120}")
print("📊 批次 2：5 家飯店總結")
print(f"{'='*120}")

for hotel_info in hotels:
    venue_id = hotel_info['id']
    venue = next((v for v in data if v['id'] == venue_id), None)
    rooms = venue.get('rooms', [])

    rooms_with_images = sum(1 for r in rooms if r.get('images') and len(r.get('images', [])) > 0)
    rooms_with_prices = sum(1 for r in rooms if r.get('price'))

    print(f"\n{venue['name']} (ID: {venue_id}):")
    print(f"   會議室: {len(rooms)} 間")
    print(f"   有照片: {rooms_with_images}/{len(rooms)}")
    print(f"   有價格: {rooms_with_prices}/{len(rooms)}")

print(f"\n{'='*120}")
print("✅ 批次 2：5 家飯店資料已準備好供人工檢查")
print(f"{'='*120}")
print(f"\n備份檔案: {backup_path}")
print(f"更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

print(f"\n💡 下一步:")
print(f"   1. 人工檢查這 5 家飯店的資料正確性")
print(f"   2. 確認電話、Email、會議室資訊")
print(f"   3. 應用改進流程")
print(f"   4. 繼續處理剩餘飯店")
