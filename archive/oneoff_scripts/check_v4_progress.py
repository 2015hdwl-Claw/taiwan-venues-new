#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

active = [v for v in data if v.get('status') != 'discontinued']
v4_processed = [v for v in active if v.get('metadata', {}).get('fullSiteScraped') == True]
unprocessed = [v for v in active if not v.get('metadata', {}).get('fullSiteScraped') == True]

print(f'V4 Progress Report:')
print(f'===================')
print(f'Total active venues: {len(active)}')
print(f'V4 processed: {len(v4_processed)} ({len(v4_processed)/len(active)*100:.1f}%)')
print(f'Unprocessed: {len(unprocessed)}')
print()

if unprocessed:
    print(f'Unprocessed venues ({len(unprocessed)}):')
    for v in unprocessed:
        print(f"  - {v['id']}: {v['name'][:40]}")
