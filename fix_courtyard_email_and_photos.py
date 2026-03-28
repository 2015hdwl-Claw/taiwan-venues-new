#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update 六福萬怡酒店 - Email and room photos from official website
"""

import json
import sys
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Read current data
with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Create backup
backup_path = f"venues.json.backup.courtyard_email_photos_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
with open(backup_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"[OK] Backup created: {backup_path}")

# Find 六福萬怡 hotel
courtyard_idx = next(i for i, v in enumerate(data) if v.get('id') == 1043)
courtyard = data[courtyard_idx]

# Update email address
courtyard['contactEmail'] = "service@courtyardtaipei.com"
print(f"[OK] Email updated: {courtyard['contactEmail']}")

# Define room photos from official website
# Source: https://www.courtyardtaipei.com.tw/wedding/list
room_photos = {
    "1043-01": ["https://www.courtyardtaipei.com.tw/wedding/uploads/sites/1/3f6aa2ab135425a2705f52032083f313.jpg"],  # 超新星宴會廳
    "1043-02": ["https://www.courtyardtaipei.com.tw/wedding/uploads/sites/2/c3119072a2a84456acf5c4db406ed3b2.jpg"],  # 山廳
    "1043-03": ["https://www.courtyardtaipei.com.tw/wedding/uploads/sites/2/c3119072a2a84456acf5c4db406ed3b2.jpg"],  # 海廳 (same 9F photo)
    "1043-04": ["https://www.courtyardtaipei.com.tw/wedding/uploads/sites/2/c3119072a2a84456acf5c4db406ed3b2.jpg"],  # 林廳 (same 9F photo)
    "1043-05": ["https://www.courtyardtaipei.com.tw/wedding/uploads/sites/2/c3119072a2a84456acf5c4db406ed3b2.jpg"],  # 水廳 (same 9F photo)
    "1043-06": ["https://www.courtyardtaipei.com.tw/wedding/uploads/sites/2/c3119072a2a84456acf5c4db406ed3b2.jpg"],  # 晶廳 (same 9F photo)
    "1043-07": ["https://www.courtyardtaipei.com.tw/wedding/uploads/sites/2/c3119072a2a84456acf5c4db406ed3b2.jpg"],  # 雲廳 (same 9F photo)
    "1043-08": ["https://www.courtyardtaipei.com.tw/wedding/uploads/sites/2/c3119072a2a84456acf5c4db406ed3b2.jpg"],  # 風廳 (same 9F photo)
    "1043-09": ["https://www.courtyardtaipei.com.tw/wedding/uploads/sites/2/c3119072a2a84456acf5c4db406ed3b2.jpg"],  # 光廳 (same 9F photo)
    "1043-10": ["https://www.courtyardtaipei.com.tw/wedding/uploads/sites/3/f28f0b334efdd05cee53b1f4c12867ac.jpg"],  # 戶外證婚區
}

# Update room images
rooms_updated = 0
for room in courtyard['rooms']:
    room_id = room.get('id')
    if room_id in room_photos:
        room['images'] = room_photos[room_id]
        rooms_updated += 1
        print(f"[OK] Updated images for {room['name']} ({room['nameEn']})")

# Update metadata
if 'metadata' not in courtyard:
    courtyard['metadata'] = {}
courtyard['metadata']['lastUpdated'] = datetime.now().isoformat()
courtyard['metadata']['photoSource'] = 'Official website: https://www.courtyardtaipei.com.tw/wedding/list'
courtyard['metadata']['emailSource'] = 'Official website: https://www.courtyardtaipei.com.tw/wedding/meeting'

# Update the data array
data[courtyard_idx] = courtyard

# Save updated data
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n[OK] 六福萬怡酒店 updated successfully!")
print(f"   - Email: {courtyard['contactEmail']}")
print(f"   - Rooms with photos: {rooms_updated}/{len(courtyard['rooms'])}")
print(f"\n   Photo mapping:")
print(f"   - 超新星宴會廳: Individual photo")
print(f"   - 山、海、林、水、晶、雲、風、光廳: Shared 9F meeting rooms photo")
print(f"   - 戶外證婚區: Individual photo")
