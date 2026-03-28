#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速查看場地摘要
"""
import json
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("="*120)
print(f"{'場地名稱':<40} {'Email':<35} {'電話':<20} {'會議室':<10}")
print("="*120)

for venue in data:
    if venue.get('status') != 'discontinued':
        name = venue.get('name', '')[:38]
        email = venue.get('email', 'N/A')[:33]
        phone = venue.get('phone', 'N/A')[:18]
        room_count = len(venue.get('rooms', []))
        
        print(f"{name:<40} {email:<35} {phone:<20} {room_count:>3} 間")

print("="*120)
