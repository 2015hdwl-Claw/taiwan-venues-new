#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

target_ids = [1049, 1128, 1122]

for venue in venues:
    if venue.get('id') in target_ids:
        name = venue.get('name')
        rooms = venue.get('rooms', [])

        print(f'=== {name} ===')
        print(f'會議室數: {len(rooms)}')
        print()

        for i, room in enumerate(rooms[:5], 1):
            print(f'{i}. {room.get("name")}')
            print(f'   面積: {room.get("areaSqm")} ㎡')

            dims = room.get('dimensions')
            if dims:
                print(f'   尺寸: {dims.get("length")}×{dims.get("width")}×{dims.get("height")} m')
            else:
                print(f'   尺寸: None')

            cap = room.get('capacity')
            if isinstance(cap, dict):
                print(f'   容量: {cap}')
            elif isinstance(cap, int):
                print(f'   容量: {cap}')
            else:
                print(f'   容量: None')

            price = room.get('price')
            if isinstance(price, dict):
                print(f'   價格: 平日={price.get("weekday")}')
            else:
                print(f'   價格: {price}')
            print()

        if len(rooms) > 5:
            print(f'... 還有 {len(rooms) - 5} 個會議室')
        print()
