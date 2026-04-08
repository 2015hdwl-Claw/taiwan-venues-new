#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

data = json.load(open('venues.json', 'r', encoding='utf-8'))
active = [v for v in data if v.get('status') != 'discontinued']
discontinued = [v for v in data if v.get('status') == 'discontinued']

print('Total venues:', len(data))
print('Active venues:', len(active))
print('Discontinued venues:', len(discontinued))

active_rooms = sum(len(v.get('rooms', [])) for v in active)
print('Active rooms:', active_rooms)

print('\n下架場地:')
for v in discontinued:
    print(f"  - {v['name']} (ID: {v['id']})")
    print(f"    原因: {v['metadata'].get('discontinueReason', 'N/A')}")
