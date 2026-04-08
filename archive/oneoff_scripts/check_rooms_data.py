#!/usr/bin/env python3
import json

with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 檢查 Fast-Parallel 爬取的場地
parallel_venues = [v for v in data if v.get('metadata', {}).get('scrapeVersion', '') == 'Fast-Parallel']

print(f'Fast-Parallel 爬取的場地: {len(parallel_venues)}')
print()

# 檢查前5個的 rooms 資料
for venue in parallel_venues[:5]:
    venue_id = venue['id']
    name = venue.get('name', '')
    rooms = venue.get('rooms', [])
    room_count = len(rooms)

    print(f'ID {venue_id}: {name}')
    print(f'  Rooms: {room_count}')

    if room_count > 0:
        print('  Sample room:', rooms[0].get('name', ''))
    else:
        print('  ❌ No rooms data!')
    print()

# 統計
no_rooms = [v for v in parallel_venues if not v.get('rooms') or len(v.get('rooms', [])) == 0]
print(f'Fast-Parallel 中沒有 rooms 資料的: {len(no_rooms)}/{len(parallel_venues)}')
