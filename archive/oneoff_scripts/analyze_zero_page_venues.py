#!/usr/bin/env python3
import json

with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

active = [v for v in data if v.get('status') != 'discontinued']
zero_page_venues = [v for v in active if v.get('metadata', {}).get('pagesDiscovered', 0) == 0]

print('=== Zero Page Venues Analysis ===')
print(f'Total zero-page venues: {len(zero_page_venues)}')
print()

# 分類分析
categories = {
    'no_url': [],
    'meeting_com_tw': [],
    'international_hotels': [],
    'others': []
}

for v in zero_page_venues:
    url = v.get('url', '')
    if not url or url == 'N/A':
        categories['no_url'].append(v)
    elif 'meeting.com.tw' in url:
        categories['meeting_com_tw'].append(v)
    elif any(hotel in url.lower() for hotel in ['marriott', 'citizenm', 'eclathotels', 'mandarinoriental', 'regent', 'sheraton', 'hilton']):
        categories['international_hotels'].append(v)
    else:
        categories['others'].append(v)

print('By Category:')
print(f'1. No URL: {len(categories["no_url"])}')
print(f'2. meeting.com.tw (404): {len(categories["meeting_com_tw"])}')
print(f'3. International hotels: {len(categories["international_hotels"])}')
print(f'4. Others: {len(categories["others"])}')
print()

print('=== International Hotels (JS-rendered) ===')
for v in categories['international_hotels']:
    print(f'ID {v["id"]}: {v["url"]}')

print()
print('=== meeting.com.tw (404 errors) ===')
for v in categories['meeting_com_tw']:
    print(f'ID {v["id"]}: {v["url"]}')

print()
print('=== No URL ===')
for v in categories['no_url']:
    print(f'ID {v["id"]}: {v.get("name", "Unknown")}')
