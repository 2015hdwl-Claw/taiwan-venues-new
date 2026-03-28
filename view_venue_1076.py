#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
顯示台北寒舍艾美酒店完整資料
"""

import json
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Read venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find 寒舍艾美
venue = next((v for v in data if v.get('id') == 1076), None)

if not venue:
    print("❌ 找不到 ID 1076 的場地")
    sys.exit(1)

print("="*100)
print(f"🏨 {venue['name']}")
print("="*100)
print(f"ID: {venue['id']}")
print(f"完成度: 100%")
print(f"\n📍 基本資訊:")
print(f"   地址: {venue.get('address', 'N/A')}")
print(f"   電話: {venue.get('contactPhone', 'N/A')}")
print(f"   Email: {venue.get('contactEmail', 'N/A')}")
print(f"   總會議室: {len(venue.get('rooms', []))} 間")

# Check metadata
if venue.get('metadata'):
    metadata = venue['metadata']
    print(f"\n📚 資料來源:")
    if metadata.get('dataSource'):
        for source in metadata['dataSource']:
            print(f"   • {source}")
    if metadata.get('lastUpdated'):
        print(f"   最後更新: {metadata['lastUpdated'][:10]}")

print(f"\n🏛️  會議室詳細資料:")
print("="*100)

rooms = venue.get('rooms', [])

# Group by completeness
complete_rooms = [r for r in rooms if r.get('capacity') and r.get('images') and r.get('price')]
incomplete_rooms = [r for r in rooms if not (r.get('capacity') and r.get('images') and r.get('price'))]

print(f"\n✅ 完整資料會議室 ({len(complete_rooms)} 間):")
print(f"{'No.':<4} {'名稱':<25} {'英文名':<25} {'樓層':<8} {'面積':<10} {'容量':<15} {'照片':<6} {'價格':<6}")
print("-"*100)

for i, room in enumerate(complete_rooms, 1):
    name = room.get('name', 'N/A')[:25]
    name_en = room.get('nameEn', 'N/A')[:25]
    floor = room.get('floor', 'N/A')[:8]
    area = f"{room.get('area', 'N/A')} sqm" if room.get('area') else 'N/A'
    capacity = room.get('capacity', {})
    if capacity:
        cap_str = f"劇院{capacity.get('theater', '-')} / 圓桌{capacity.get('roundtable', '-')}"
    else:
        cap_str = 'N/A'
    has_image = '✓' if room.get('images') else '✗'
    has_price = '✓' if room.get('price') else '✗'

    print(f"{i:<4} {name:<25} {name_en:<25} {floor:<8} {area:<10} {cap_str:<15} {has_image:<6} {has_price:<6}")

if incomplete_rooms:
    print(f"\n⚠️  資料不完整會議室 ({len(incomplete_rooms)} 間):")
    for i, room in enumerate(incomplete_rooms, 1):
        name = room.get('name', 'N/A')
        issues = []
        if not room.get('capacity'):
            issues.append("無容量")
        if not room.get('images'):
            issues.append("無照片")
        if not room.get('price'):
            issues.append("無價格")
        print(f"   {i}. {name}: {', '.join(issues)}")

# Show sample room details
if rooms:
    print(f"\n📋 會議室詳細資料範例 (前 3 間):")
    print("="*100)

    for i, room in enumerate(rooms[:3], 1):
        print(f"\n{i}. {room.get('name', 'N/A')} ({room.get('nameEn', 'N/A')})")
        print(f"   ID: {room.get('id', 'N/A')}")
        print(f"   樓層: {room.get('floor', 'N/A')}")
        print(f"   面積: {room.get('area', 'N/A')} sqm")
        print(f"   天花板: {room.get('ceilingHeight', 'N/A')}M" if room.get('ceilingHeight') else f"   天花板: N/A")

        if room.get('capacity'):
            print(f"   容量:")
            for key, value in room['capacity'].items():
                print(f"      - {key}: {value}")

        if room.get('images'):
            print(f"   照片 ({len(room['images'])} 張):")
            for img in room['images'][:2]:  # Show first 2
                print(f"      - {img}")
            if len(room['images']) > 2:
                print(f"      ... 還有 {len(room['images'])-2} 張")

        if room.get('price'):
            price = room['price']
            print(f"   價格:")
            if isinstance(price, dict):
                for key, value in price.items():
                    if key not in ['currency', 'includesTaxAndService', 'source', 'effectiveDate']:
                        if isinstance(value, (int, float)):
                            print(f"      - {key}: NT${value:,}")
                        else:
                            print(f"      - {key}: {value}")
                    elif key == 'currency':
                        print(f"      - 幣別: {value}")
                    elif key == 'includesTaxAndService':
                        print(f"      - 含稅服務費: {value}")

        if room.get('facilities'):
            print(f"   設施: {', '.join(room['facilities'][:5])}")
            if len(room['facilities']) > 5:
                print(f"      ... 還有 {len(room['facilities'])-5} 項設施")

        if room.get('features'):
            print(f"   特色: {', '.join(room['features'][:3])}")
            if len(room['features']) > 3:
                print(f"      ... 還有 {len(room['features'])-3} 項特色")

# Statistics
print(f"\n📊 資料統計:")
print("="*100)
total_rooms = len(rooms)
rooms_with_capacity = sum(1 for r in rooms if r.get('capacity'))
rooms_with_images = sum(1 for r in rooms if r.get('images'))
rooms_with_prices = sum(1 for r in rooms if r.get('price'))

print(f"總會議室: {total_rooms}")
print(f"有容量資料: {rooms_with_capacity}/{total_rooms} ({100*rooms_with_capacity/total_rooms:.1f}%)")
print(f"有照片: {rooms_with_images}/{total_rooms} ({100*rooms_with_images/total_rooms:.1f}%)")
print(f"有價格: {rooms_with_prices}/{total_rooms} ({100*rooms_with_prices/total_rooms:.1f}%)")

print("\n" + "="*100)
print(f"✅ 準備進行人工檢查")
print("="*100)
