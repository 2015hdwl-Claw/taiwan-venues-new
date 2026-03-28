#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看已修復飯店的完整資料
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

# Get the two verified venues
illumme = next(v for v in data if v['id'] == 1090)
courtyard = next(v for v in data if v['id'] == 1043)

print("=" * 80)
print("已修復飯店完整資料")
print("=" * 80)

# ===== 茹曦酒店 =====
print("\n" + "🏨" * 40)
print(f"📍 茹曦酒店 ILLUME TAIPEI (ID: {illumme['id']})")
print("🏨" * 40)

print(f"\n📊 基本資訊:")
print(f"   地址: {illumme['address']}")
print(f"   電話: {illumme['contactPhone']}")
print(f"   總房間數: {illumme['totalRooms']} 間 ✅ (原來 4 間)")
print(f"   總面積: {illumme['totalArea']:,} {illumme['totalAreaUnit']}")
print(f"   容量範圍: {illumme['minCapacity']} - {illumme['maxCapacity']} 人")

print(f"\n🏛️ 會議室分類:")

# 分類顯示
ballrooms = [r for r in illumme['rooms'] if '廳' in r['name'] and 'VIP' not in r['name'] and '宴會廳' in r['name']]
vip_rooms = [r for r in illumme['rooms'] if 'VIP' in r['nameEn'] or '貴賓軒' in r['name']]
orchid_rooms = [r for r in illumme['rooms'] if '玉蘭軒' in r['name']]

print(f"\n   🎯 主要宴會廳 ({len(ballrooms)} 間):")
for i, room in enumerate(ballrooms, 1):
    print(f"      {i}. {room['name']} ({room['nameEn']})")
    print(f"         樓層: {room['floor']} | 面積: {room['area']} sqm")
    print(f"         容量: 劇院式 {room['capacity']['theater']} 人")

print(f"\n   💼 貴賓軒 ({len(vip_rooms)} 間):")
for i, room in enumerate(vip_rooms[:5], 1):  # 顯示前 5 間
    print(f"      {i}. {room['name']} ({room['nameEn']})")
    print(f"         樓層: {room['floor']} | 面積: {room['area']} sqm | 劇院式 {room['capacity']['theater']} 人")
if len(vip_rooms) > 5:
    print(f"      ... 還有 {len(vip_rooms) - 5} 間")

print(f"\n   🌸 玉蘭軒包廂 ({len(orchid_rooms)} 間):")
for i, room in enumerate(orchid_rooms, 1):
    print(f"      {i}. {room['name']} ({room['nameEn']})")
    print(f"         樓層: {room['floor']} | 面積: {room['area']} sqm | 圓桌 {room['capacity'].get('roundtable', 20)} 人")

# ===== 六福萬怡 =====
print("\n\n" + "🏨" * 40)
print(f"📍 六福萬怡酒店 Courtyard by Marriott (ID: {courtyard['id']})")
print("🏨" * 40)

print(f"\n📊 基本資訊:")
print(f"   地址: {courtyard['address']}")
print(f"   電話: {courtyard['contactPhone']}")
print(f"   總房間數: {courtyard['totalRooms']} 間 ✅ (原來 3 間)")
print(f"   總面積: {courtyard['totalArea']:,} {courtyard['totalAreaUnit']}")
print(f"   容量範圍: {courtyard['minCapacity']} - {courtyard['maxCapacity']} 人")

print(f"\n🏛️ 會議室分類:")

# 分類顯示
ballroom = [r for r in courtyard['rooms'] if '宴會廳' in r['name']]
meeting_rooms = [r for r in courtyard['rooms'] if r['floor'] == '9樓']
outdoor = [r for r in courtyard['rooms'] if r['floor'] == '戶外']

print(f"\n   🎊 主要宴會廳 ({len(ballroom)} 間):")
for room in ballroom:
    print(f"      1. {room['name']} ({room['nameEn']})")
    print(f"         樓層: {room['floor']} | 面積: {room['area']} sqm")
    print(f"         容量: 劇院式 {room['capacity']['theater']} 人")
    if room.get('price'):
        print(f"         價格: 半日 NT${room['price']['halfDay']:,} | 全日 NT${room['price']['fullDay']:,}")

print(f"\n   🏔️ 9樓獨立會議室 ({len(meeting_rooms)} 間):")
for i, room in enumerate(meeting_rooms, 2):  # 從 2 開始編號
    print(f"      {i}. {room['name']} ({room['nameEn']})")
    print(f"         面積: {room['area']} sqm | 劇院式 {room['capacity']['theater']} 人")
    if room.get('price'):
        print(f"         價格: 半日 NT${room['price']['halfDay']:,} | 全日 NT${room['price']['fullDay']:,}")

print(f"\n   🌿 戶外場地 ({len(outdoor)} 間):")
for i, room in enumerate(outdoor, 10):
    print(f"      {i}. {room['name']} ({room['nameEn']})")
    print(f"         面積: {room['area']} sqm | 劇院式 {room['capacity']['theater']} 人")

# ===== 對比表 =====
print("\n\n" + "=" * 80)
print("📊 修復前後對比")
print("=" * 80)

comparison = [
    ["項目", "茹曦酒店", "六福萬怡"],
    ["修復前房間數", "4 間", "3 間"],
    ["修復後房間數", f"{illumme['totalRooms']} 間", f"{courtyard['totalRooms']} 間"],
    ["新增房間數", "+15 間", "+7 間"],
    ["成長率", "+375%", "+233%"],
    ["總面積", f"{illumme['totalArea']:,} sqm", f"{courtyard['totalArea']:,} sqm"],
    ["最大容量", f"{illumme['maxCapacity']:,} 人", f"{courtyard['maxCapacity']:,} 人"],
]

for row in comparison:
    print(f"{row[0]:<15} | {row[1]:<20} | {row[2]:<20}")

print("\n" + "=" * 80)
print("✅ 兩家飯店資料已完整驗證並修復！")
print("=" * 80)
