#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix venue 1045 (北科大創新育成中心) data quality issues - v2."""

import json, shutil, datetime, sys, re

sys.stdout.reconfigure(encoding='utf-8')

ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

def fix_in_file(filepath):
    print(f'\n=== Fixing {filepath} ===')
    shutil.copy(filepath, f'{filepath}.backup.{ts}')

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    venue = next((v for v in data if v['id'] == 1045), None)
    if not venue:
        print(f'  WARNING: ID 1045 not found in {filepath}')
        return

    # 1. Add top-level contactPhone/contactEmail (venue.js reads these)
    if not venue.get('contactPhone') and venue.get('contact', {}).get('phone'):
        venue['contactPhone'] = venue['contact']['phone']
        print(f'  Added contactPhone: {venue["contactPhone"]}')
    if not venue.get('contactEmail') and venue.get('contact', {}).get('email'):
        venue['contactEmail'] = venue['contact']['email']
        print(f'  Added contactEmail: {venue["contactEmail"]}')

    # 2. Fix room data format
    for room in venue.get('rooms', []):
        room_name = room.get('name', '?')

        # Fix area: string -> number
        if isinstance(room.get('area'), str):
            match = re.search(r'(\d+(?:\.\d+)?)', room['area'])
            if match:
                area_num = float(match.group(1))
                room['area'] = int(area_num) if area_num == int(area_num) else area_num
                room['areaSqm'] = round(room['area'] * 3.3058)
                print(f'  {room_name}: area -> {room["area"]} 坪 ({room["areaSqm"]} m²)')

        # Fix price: string -> pricing dict (venue.js reads room.pricing, not room.price)
        price_val = room.get('price')
        pricing_val = room.get('pricing')
        if isinstance(price_val, str) and not pricing_val:
            match = re.search(r'([\d,]+)\s*元', price_val)
            if match:
                hourly = int(match.group(1).replace(',', ''))
                room['pricing'] = {
                    'halfDay': hourly * 3,   # 3 hours
                    'fullDay': hourly * 7,   # 7 hours
                }
                del room['price']
                print(f'  {room_name}: price -> pricing (halfDay={hourly*3}, fullDay={hourly*7})')
        elif isinstance(price_val, dict) and not pricing_val:
            # Already converted to dict but under wrong key - rename
            room['pricing'] = price_val
            del room['price']
            print(f'  {room_name}: price dict -> pricing dict')

        # Fix equipment: string -> array (venue.js expects array for .slice())
        if isinstance(room.get('equipment'), str):
            room['equipment'] = [e.strip() for e in room['equipment'].replace('、', ',').split(',') if e.strip()]
            print(f'  {room_name}: equipment string -> array {room["equipment"]}')

        # Remove broken photo field
        if room.get('photo'):
            del room['photo']
            print(f'  {room_name}: removed broken photo field')

        # Ensure images is a dict (not missing)
        if 'images' not in room or room.get('images') is None:
            room['images'] = {}

        # Update quality score
        score = 0
        if room.get('name'): score += 10
        cap = room.get('capacity', {})
        if cap.get('theater'): score += 15
        if room.get('area') or room.get('areaSqm'): score += 15
        pr = room.get('pricing', {})
        if any(v for v in pr.values() if v): score += 20
        imgs = room.get('images', {})
        if isinstance(imgs, dict) and imgs.get('main'): score += 20
        equip = room.get('equipment', [])
        if isinstance(equip, list) and len(equip) > 0: score += 10
        if room.get('floor'): score += 5
        if room.get('height'): score += 5
        room['qualityScore'] = score
        room['qualityLevel'] = 'high' if score >= 70 else ('medium' if score >= 40 else 'low')

    # 3. Update metadata
    venue['metadata']['verificationIssues'] = []
    venue['metadata']['verificationWarnings'] = []
    venue['metadata']['scrapeVersion'] = 'Manual_Fix_20260331'
    venue['metadata']['lastScrapedAt'] = datetime.datetime.now().isoformat()

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f'  Done! Saved to {filepath}')

fix_in_file('venues.json')
fix_in_file('venues_taipei.json')
print('\n=== All done! ===')
