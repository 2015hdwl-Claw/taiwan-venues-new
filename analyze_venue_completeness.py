#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from datetime import datetime

def calculate_completeness(room):
    if not room: return 0
    score = 0
    if room.get('id'): score += 1
    if room.get('name'): score += 1
    if room.get('nameEn'): score += 1
    if room.get('floor'): score += 1
    if room.get('area') is not None: score += 1
    if room.get('areaSqm'): score += 1
    if room.get('areaPing'): score += 1
    if room.get('areaUnit'): score += 1
    dims = room.get('dimensions')
    if isinstance(dims, dict):
        if dims.get('length'): score += 1
        if dims.get('width'): score += 1
        if dims.get('height'): score += 1
    cap = room.get('capacity')
    if isinstance(cap, dict):
        if cap.get('theater'): score += 1
        if cap.get('banquet'): score += 1
        if cap.get('classroom'): score += 1
        if cap.get('uShape'): score += 1
        if cap.get('cocktail'): score += 1
        if cap.get('roundTable'): score += 1
    elif isinstance(cap, int):
        score += 1
    price = room.get('price')
    if isinstance(price, dict):
        if any([price.get(k) for k in ['weekday', 'holiday', 'fullDay', 'hourly']]):
            score += 4
    elif isinstance(price, int):
        score += 4
    if room.get('equipment') or room.get('equipmentList'):
        score += 2
    if room.get('features'): score += 1
    if room.get('source'): score += 1
    if room.get('lastUpdated'): score += 1
    return score

def check_capacity(room):
    cap = room.get('capacity')
    if isinstance(cap, dict):
        return cap.get('theater')
    elif isinstance(cap, int):
        return True
    return False

def check_price(room):
    price = room.get('price')
    if isinstance(price, dict):
        return any([price.get(k) for k in ['weekday', 'holiday', 'fullDay', 'hourly']])
    elif isinstance(price, int):
        return True
    return False

venues = json.load(open('venues.json', encoding='utf-8'))
results = []

for venue in venues:
    if venue.get('verified'):
        rooms = venue.get('rooms', [])
        if rooms:
            total_score = sum(calculate_completeness(r) for r in rooms)
            avg_score = total_score / len(rooms)
            
            price_count = sum(1 for r in rooms if check_price(r))
            cap_count = sum(1 for r in rooms if check_capacity(r))
            area_count = sum(1 for r in rooms if r.get('areaSqm'))
            
            results.append({
                'id': venue['id'],
                'name': venue['name'],
                'rooms': len(rooms),
                'completeness': round(avg_score, 1),
                'price': f'{price_count}/{len(rooms)}',
                'capacity': f'{cap_count}/{len(rooms)}',
                'area': f'{area_count}/{len(rooms)}'
            })

results.sort(key=lambda x: x['completeness'], reverse=True)

print('='*110)
print(f'{"排名":<4} {"完整度":<8} {"會議室":<8} {"價格":<10} {"容量":<10} {"面積":<10} {"場地名稱":<40}')
print('='*110)
for i, r in enumerate(results[:10], 1):
    print(f'{i:<4} {r["completeness"]:<8.1f} {r["rooms"]:<8} {r["price"]:<10} {r["capacity"]:<10} {r["area"]:<10} {r["name"][:38]}')

print()
print('='*110)
print('未完成場地（完整度 < 20）')
print('='*110)

incomplete = [r for r in results if r['completeness'] < 20]
if incomplete:
    for r in incomplete:
        print(f"⚠️  {r['name'][:40]} (ID: {r['id']})")
        print(f"    完整度: {r['completeness']}, 會議室: {r['rooms']}, 價格: {r['price']}, 容量: {r['capacity']}, 面積: {r['area']}")
        print()
else:
    print('✅ Top10 場地完整度皆良好（20+）')

no_price = [r for r in results if int(r['price'].split('/')[0]) == 0]
if no_price:
    print()
    print('='*110)
    print(f'缺少價格資料的場地（共 {len(no_price)} 個）')
    print('='*110)
    for r in no_price:
        print(f"⚠️  {r['name'][:40]} (ID: {r['id']}) - {r['price']}")

with open('venue_completeness_analysis.json', 'w', encoding='utf-8') as f:
    json.dump({'top10': results[:10], 'incomplete': incomplete, 'no_price': no_price, 'date': datetime.now().isoformat()}, f, indent=2, ensure_ascii=False)
