#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Display final verification of 六福萬怡酒店 data
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

# Get 六福萬怡 hotel
courtyard = next(v for v in data if v['id'] == 1043)

print("="*80)
print("六福萬怡酒店 - 官方資料驗證")
print("="*80)

print(f"\n📞 聯絡資訊:")
print(f"   電話: {courtyard['contactPhone']}")
print(f"   分機: {courtyard.get('contactPhoneExt', 'N/A')}")
print(f"   Email: {courtyard['contactEmail']}")

print(f"\n📊 基本資訊:")
print(f"   總房間數: {courtyard['totalRooms']} 間")
print(f"   總面積: {courtyard['totalArea']:,} {courtyard['totalAreaUnit']}")
print(f"   最大容量: {courtyard['maxCapacity']} 人")
print(f"   最小容量: {courtyard['minCapacity']} 人")

print(f"\n📋 官方資料來源:")
if 'metadata' in courtyard and 'dataSource' in courtyard['metadata']:
    for source in courtyard['metadata']['dataSource']:
        print(f"   • {source}")

if 'metadata' in courtyard and 'dimensionSources' in courtyard['metadata']:
    print(f"\n   維度資料來源:")
    for source in courtyard['metadata']['dimensionSources']:
        print(f"   • {source}")

print(f"\n🏛️ 會議室清單 ({len(courtyard['rooms'])} 間):")
print(f"{'編號':<6} {'名稱':<12} {'英文名':<20} {'樓層':<6} {'面積':<8} {'容量':<8} {'天花板':<10} {'照片':<6} {'價格':<6}")
print("-"*100)

for i, room in enumerate(courtyard['rooms'], 1):
    name = room['name']
    name_en = room['nameEn']
    floor = room['floor']
    area = f"{room['area']} sqm"
    capacity = f"{room['capacity']['theater']}人"
    ceiling = f"{room.get('ceilingHeight', 'N/A')}M"
    has_image = "✓" if room.get('images') and len(room['images']) > 0 else "✗"
    has_price = "✓" if room.get('price') else "✗"

    print(f"{i:<6} {name:<12} {name_en:<20} {floor:<6} {area:<8} {capacity:<8} {ceiling:<10} {has_image:<6} {has_price:<6}")

print(f"\n📸 照片統計:")
rooms_with_images = sum(1 for r in courtyard['rooms'] if r.get('images') and len(r['images']) > 0)
print(f"   有照片: {rooms_with_images}/{len(courtyard['rooms'])} 間")

print(f"\n💰 價格統計:")
rooms_with_prices = sum(1 for r in courtyard['rooms'] if r.get('price'))
print(f"   有價格: {rooms_with_prices}/{len(courtyard['rooms'])} 間")

print(f"\n📐 天花板高度統計:")
rooms_with_ceiling = sum(1 for r in courtyard['rooms'] if r.get('ceilingHeight'))
print(f"   有天花板高度: {rooms_with_ceiling}/{len(courtyard['rooms'])} 間")

print(f"\n✅ 驗證狀態:")
verification_items = [
    ("電話號碼正確", courtyard['contactPhone'] == "02-6615-6565"),
    ("包含分機號碼", courtyard.get('contactPhoneExt') == "8915, 8911"),
    ("Email 正確", courtyard['contactEmail'] == "service@courtyardtaipei.com"),
    ("所有房間都有照片", rooms_with_images == len(courtyard['rooms'])),
    ("所有房間都有價格", rooms_with_prices == len(courtyard['rooms'])),
    ("所有室內房間都有天花板高度", rooms_with_ceiling == 9),  # 9 室內房間
    ("資料來自官方文件", courtyard.get('metadata', {}).get('dimensionsVerified', False)),
]

all_passed = True
for item, passed in verification_items:
    status = "✅" if passed else "❌"
    print(f"   {status} {item}")
    if not passed:
        all_passed = False

print(f"\n{'='*80}")
if all_passed:
    print("🎉 所有驗證項目通過！六福萬怡酒店資料已 100% 來自官方來源。")
else:
    print("⚠️  部分驗證項目未通過，請檢查。")
print("="*80)
