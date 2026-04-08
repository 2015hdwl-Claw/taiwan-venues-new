#!/usr/bin/env python3
import json

with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

active = [v for v in data if v.get('status') != 'discontinued']
pages = sum(v.get('metadata', {}).get('pagesDiscovered', 0) for v in active)

print(f'Total venues: {len(data)}')
print(f'Active: {len(active)}')
print(f'Total pages: {pages}')
print(f'Avg pages/venue: {pages/len(active):.1f}')

# Version breakdown
v4_count = sum(1 for v in active if 'V4' in v.get('metadata', {}).get('scrapeVersion', ''))
practical_count = sum(1 for v in active if 'Practical' in v.get('metadata', {}).get('scrapeVersion', ''))
parallel_count = sum(1 for v in active if 'Parallel' in v.get('metadata', {}).get('scrapeVersion', ''))

print(f'\nScrape versions:')
print(f'  V4: {v4_count}')
print(f'  V4-Practical: {practical_count}')
print(f'  Fast-Parallel: {parallel_count}')
