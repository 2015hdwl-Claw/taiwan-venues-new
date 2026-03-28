#!/usr/bin/env python3
import json

with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

v4_venues = [v for v in data if v.get('status') != 'discontinued' and v.get('metadata', {}).get('fullSiteScraped')]

pages_list = []
for v in v4_venues:
    pages = v.get('metadata', {}).get('pagesDiscovered', 0)
    pages_list.append((v['id'], v['name'], pages))

pages_list.sort(key=lambda x: x[2], reverse=True)

print('Top 15 venues by pagesDiscovered:')
print('='*60)
for venue_id, name, pages in pages_list[:15]:
    print(f'{venue_id}: {pages:3d} pages - {name[:40]}')

print()
print(f'Total venues: {len(pages_list)}')
print(f'Total pages: {sum(p[2] for p in pages_list)}')
print(f'Average pages: {sum(p[2] for p in pages_list) / len(pages_list):.1f}')
