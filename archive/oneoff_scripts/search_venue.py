#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜尋特定場地
"""
import json
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 搜尋選項
print("="*100)
print("場地搜尋工具")
print("="*100)
print()
print("1. 依 ID 搜尋")
print("2. 依名稱搜尋")
print("3. 列出所有有 Email 的場地")
print("4. 列出所有有電話的場地")
print("5. 列出所有有完整會議室資料的場地")
print()

choice = input("請選擇搜尋方式 (1-5): ").strip()

if choice == '1':
    venue_id = input("請輸入場地 ID: ").strip()
    try:
        venue_id = int(venue_id)
        venue = next((v for v in data if v.get('id') == venue_id), None)
        if venue:
            print(json.dumps(venue, indent=2, ensure_ascii=False))
        else:
            print(f"找不到 ID 為 {venue_id} 的場地")
    except:
        print("無效的 ID")

elif choice == '2':
    keyword = input("請輸入關鍵字: ").strip()
    venues = [v for v in data if keyword.lower() in v.get('name', '').lower()]
    print(f"\n找到 {len(venues)} 個場地:\n")
    for venue in venues:
        print(f"- {venue['name']} (ID: {venue['id']})")

elif choice == '3':
    venues = [v for v in data if v.get('email')]
    print(f"\n有 Email 的場地 ({len(venues)} 個):\n")
    for venue in venues:
        print(f"- {venue['name']}: {venue['email']}")

elif choice == '4':
    venues = [v for v in data if v.get('phone')]
    print(f"\n有電話的場地 ({len(venues)} 個):\n")
    for venue in venues:
        print(f"- {venue['name']}: {venue['phone']}")

elif choice == '5':
    venues = [v for v in data if v.get('rooms') and len(v.get('rooms', [])) > 0]
    print(f"\n有會議室的場地 ({len(venues)} 個):\n")
    for venue in venues:
        room_count = len(venue.get('rooms', []))
        print(f"- {venue['name']}: {room_count} 間會議室")

else:
    print("無效的選擇")
