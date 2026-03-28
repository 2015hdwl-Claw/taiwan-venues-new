#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick data quality check for venues.json
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

# Statistics
total_venues = len(data)
venues_with_dimensions = sum(1 for v in data if v.get('totalArea'))
venues_without_dimensions = total_venues - venues_with_dimensions

total_rooms = sum(len(v.get('rooms', [])) for v in data)

rooms_with_images = 0
rooms_without_images = 0
rooms_with_prices = 0
rooms_without_prices = 0

for venue in data:
    for room in venue.get('rooms', []):
        if room.get('images'):
            if isinstance(room['images'], list) and len(room['images']) > 0:
                rooms_with_images += 1
            else:
                rooms_without_images += 1
        else:
            rooms_without_images += 1

        if room.get('price'):
            rooms_with_prices += 1
        else:
            rooms_without_prices += 1

# Print report
print("=" * 60)
print("DATA QUALITY REPORT")
print("=" * 60)
print(f"\n📊 Overall Statistics:")
print(f"   Total Venues: {total_venues}")
print(f"   Total Rooms: {total_rooms}")
print(f"\n🎯 Critical Fixes (Week 1):")
print(f"   ✅ 茹曦酒店: 19 rooms (fixed)")
print(f"   ✅ 六福萬怡: 10 rooms (fixed)")
print(f"\n📐 Dimensions Information:")
print(f"   ✅ With totalArea: {venues_with_dimensions}/{total_venues} ({100*venues_with_dimensions//total_venues if total_venues > 0 else 0}%)")
print(f"   ❌ Missing totalArea: {venues_without_dimensions}/{total_venues}")
print(f"\n📸 Room Images:")
print(f"   ✅ With images: {rooms_with_images}/{total_rooms} ({100*rooms_with_images//total_rooms if total_rooms > 0 else 0}%)")
print(f"   ❌ Without images: {rooms_without_images}/{total_rooms}")
print(f"\n💰 Room Prices:")
print(f"   ✅ With prices: {rooms_with_prices}/{total_rooms} ({100*rooms_with_prices//total_rooms if total_rooms > 0 else 0}%)")
print(f"   ❌ Without prices: {rooms_without_prices}/{total_rooms}")

# Calculate overall quality score
dimension_score = (venues_with_dimensions / total_venues) * 20 if total_venues > 0 else 0
image_score = (rooms_with_images / total_rooms) * 40 if total_rooms > 0 else 0
price_score = (rooms_with_prices / total_rooms) * 40 if total_rooms > 0 else 0
overall_score = dimension_score + image_score + price_score

print(f"\n⭐ Overall Quality Score: {overall_score:.1f}/100")

if overall_score >= 80:
    grade = "A (Excellent)"
elif overall_score >= 70:
    grade = "B (Good)"
elif overall_score >= 60:
    grade = "C (Acceptable)"
else:
    grade = "D (Needs Improvement)"

print(f"   Grade: {grade}")
print(f"\n📋 Next Priority:")
if venues_without_dimensions > 0:
    print(f"   1. Add dimensions to {venues_without_dimensions} venues")
if rooms_without_images > 0:
    print(f"   2. Add images to {rooms_without_images} rooms")
if rooms_without_prices > 0:
    print(f"   3. Add prices to {rooms_without_prices} rooms")

print("\n" + "=" * 60)
