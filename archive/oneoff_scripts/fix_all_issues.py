#!/usr/bin/env python3
"""Comprehensive fix for all venue data issues."""
import json, sys, copy, re
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

stats = {'equipment_fixed': 0, 'pricing_added': 0, 'images_fixed': 0, 'takedown': 0}

for v in venues:
    vid = v['id']

    # === Takedown ID 1045 ===
    if vid == 1045:
        v['active'] = False
        stats['takedown'] += 1
        print(f"  TAKEDOWN v{vid} {v['name']}")
        continue

    # === Fix venue 1126 example.com images ===
    if vid == 1126:
        v['images'] = {
            "main": "https://www.riverview.com.tw/images/banner-02.jpg",
            "gallery": [
                "https://www.riverview.com.tw/images/banner-02.jpg",
                "https://www.riverview.com.tw/images/meeting-01.jpg",
                "https://www.riverview.com.tw/images/meeting-02.jpg"
            ],
            "source": "https://www.riverview.com.tw/",
            "verified": True,
            "verifiedAt": datetime.now().isoformat(),
            "lastUpdated": "2026-03-31",
            "needsUpdate": False
        }
        stats['images_fixed'] += 1
        print(f"  IMAGES v{vid} {v['name']}: fixed example.com → riverview.com.tw")

    # === Fix all rooms ===
    for room in v.get('rooms', []):
        rid = room.get('id', '?')

        # --- 1. Fix equipment: string → array ---
        eq = room.get('equipment')
        if isinstance(eq, str):
            if not eq.strip():
                room['equipment'] = []
            elif eq.startswith('['):
                # Try parsing as JSON array string
                try:
                    room['equipment'] = json.loads(eq)
                except:
                    room['equipment'] = [eq]
            else:
                # Split by common delimiters
                # Try Chinese delimiters first, then English
                if '、' in eq:
                    room['equipment'] = [x.strip() for x in eq.split('、') if x.strip()]
                elif '，' in eq:
                    room['equipment'] = [x.strip() for x in eq.split('，') if x.strip()]
                elif ',' in eq and len(eq) > 10:
                    room['equipment'] = [x.strip() for x in eq.split(',') if x.strip()]
                else:
                    room['equipment'] = [eq]
            stats['equipment_fixed'] += 1

        # --- 2. Fix pricing: add pricing from price ---
        p = room.get('price')
        pr = room.get('pricing')
        if isinstance(p, dict) and not pr:
            mapping = {}

            # Map common price keys to pricing format
            # halfDay / morning
            if 'halfDay' in p:
                mapping['halfDay'] = p['halfDay']
            elif 'halfDayAM' in p:
                mapping['halfDay'] = p['halfDayAM']
            elif 'morning' in p and p['morning']:
                mapping['halfDay'] = p['morning']
            elif 'weekdayDaytime' in p:
                mapping['halfDay'] = p['weekdayDaytime']
            elif 'weekdayHalfDay' in p:
                mapping['halfDay'] = p['weekdayHalfDay']
            elif 'weekday' in p and p['weekday']:
                mapping['halfDay'] = p['weekday']
            elif 'amount' in p and p.get('amount'):
                mapping['halfDay'] = p['amount']

            # fullDay
            if 'fullDay' in p and p['fullDay']:
                mapping['fullDay'] = p['fullDay']
            elif 'weekdayFullDay' in p:
                mapping['fullDay'] = p['weekdayFullDay']

            # overtime
            if 'overtime' in p and p['overtime']:
                mapping['overtime'] = p['overtime']

            # note
            if 'note' in p and p['note']:
                mapping['note'] = p['note']

            if mapping:
                room['pricing'] = mapping
                stats['pricing_added'] += 1

        # --- 3. Fix relative image paths for 1494 ---
        if vid == 1494:
            imgs = room.get('images', {})
            if isinstance(imgs, dict) and 'gallery' in imgs:
                base = 'https://www.meeting.com.tw/motc/'
                fixed_gallery = []
                for img in imgs['gallery']:
                    if not img.startswith('http'):
                        fixed_gallery.append(base + img)
                    else:
                        fixed_gallery.append(img)
                imgs['gallery'] = fixed_gallery
                if 'main' not in imgs or not imgs.get('main'):
                    imgs['main'] = fixed_gallery[0] if fixed_gallery else ''
                stats['images_fixed'] += 1

with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"\n{'='*60}")
print(f"Equipment fixed: {stats['equipment_fixed']}")
print(f"Pricing added:   {stats['pricing_added']}")
print(f"Images fixed:    {stats['images_fixed']}")
print(f"Takedowns:       {stats['takedown']}")
print(f"{'='*60}")
