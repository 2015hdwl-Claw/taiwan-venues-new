#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復 TICC 和南港展覽館的會議室資料
"""
import json
from datetime import datetime
import shutil

print("="*80)
print("修復關鍵場地的會議室資料")
print("="*80)
print()

# Backup
backup = f'venues.json.backup.fix_1448_1500_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('venues.json', backup)
print(f"備份: {backup}")
print()

# Load
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# Load TICC PDF data
with open('ticc_rooms_parsed_v2.json', 'r', encoding='utf-8') as f:
    ticc_data = json.load(f)

# Fix TICC (ID 1448)
print("[1/2] 修復 TICC (ID 1448)")
print("-"*80)

for venue in venues:
    if venue['id'] == 1448:
        # 重新構建會議室資料，使用 PDF 的完整資料
        rooms = []

        for pdf_room in ticc_data['rooms']:
            room = {
                'name': pdf_room['name'],
                'capacityTheater': pdf_room.get('capacity_theater'),
                'capacityClassroom': pdf_room.get('capacity_classroom'),
                'capacityU': pdf_room.get('capacity_u'),
                'areaSqm': pdf_room.get('area_sqm'),
                'areaPing': pdf_room.get('area_ping'),
                'dimensions': pdf_room.get('dimensions'),
                'priceWeekday': pdf_room.get('price_weekday'),
                'priceWeekend': pdf_room.get('price_weekend'),
                'priceExhibition': pdf_room.get('price_exhibition'),
                'source': 'pdf_v2_complete'
            }
            rooms.append(room)

        venue['rooms'] = rooms

        # Update metadata
        if 'metadata' not in venue:
            venue['metadata'] = {}
        venue['metadata']['pdf_source'] = 'ticc_pdf_parsed_v2_complete'
        venue['metadata']['total_rooms_from_pdf'] = len(rooms)
        venue['metadata']['pdf_updated_at'] = datetime.now().isoformat()
        venue['metadata']['data_quality'] = 'complete_from_pdf'

        print(f"[OK] TICC 更新完成")
        print(f"   會議室: {len(rooms)} 個")
        print(f"   資料來源: PDF 完整解析")
        print()

        # 顯示前 5 個
        print("   前 5 個會議室:")
        for i, room in enumerate(rooms[:5], 1):
            cap = room.get('capacityTheater', 'N/A')
            area_sqm = room.get('areaSqm', 'N/A')
            area_ping = room.get('areaPing', 'N/A')
            price = room.get('priceWeekday', 'N/A')

            print(f"   {i}. {room['name']}")
            print(f"      容量(劇院): {cap} 人")
            if area_sqm:
                print(f"      面積: {area_sqm} ㎡ / {area_ping} 坪")
            if price:
                print(f"      平日價: ${price:,}")

        if len(rooms) > 5:
            print(f"   ... 還有 {len(rooms) - 5} 個會議室")

        break

# Check ID 1500 (南港展覽館)
print()
print("[2/2] 檢查 ID 1500 (南港展覽館)")
print("-"*80)

for venue in venues:
    if venue['id'] == 1500:
        print(f"名稱: {venue['name']}")
        print(f"類型: {venue['venueType']}")
        print(f"URL: {venue['url']}")

        rooms = venue.get('rooms', [])
        print(f"會議室: {len(rooms)} 個")

        if len(rooms) == 0:
            print("[X] 會議室資料是空的")
            print()
            print("可能原因:")
            print("- 南港展覽館的官網可能沒有會議室資訊頁面")
            print("- 或者資料在 JavaScript 需要特殊處理")
            print("- 或者需要手動新增會議室資料")
        else:
            print("✅ 有會議室資料")

        break

# Check if ID 1550 exists
id_1550_exists = any(v['id'] == 1550 for v in venues)
print()
print(f"ID 1550: {'存在' if id_1550_exists else '不存在'}")

if not id_1550_exists:
    print("[!] 找不到 ID 1550")
    print("    可能是 ID 1500 (南港展覽館) 的筆誤？")

# Save
print()
print("儲存更新...")
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print("✅ venues.json 已更新")
print()
print("="*80)
print("修復完成")
print("="*80)
