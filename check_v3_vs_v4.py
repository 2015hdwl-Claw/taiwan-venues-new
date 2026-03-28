#!/usr/bin/env python3
import json

with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

active = [v for v in data if v.get('status') != 'discontinued']

# 檢查 V4 使用情況
v4_venues = [v for v in active if v.get('metadata', {}).get('scrapeVersion') == 'V4']

# 檢查 V3 使用情況（舊的指標）
v3_venues = [v for v in active if 'scrapeConfidenceScore' in v.get('metadata', {})]

# 檢查未處理的場地
no_version = [v for v in active if not v.get('metadata', {}).get('scrapeVersion')]

print('=== V3 vs V4 Usage Analysis ===')
print(f'Total active venues: {len(active)}')
print()
print(f'Versions:')
print(f'  V4 processed: {len(v4_venues)}')
print(f'  V3 indicators: {len(v3_venues)}')
print(f'  No version: {len(no_version)}')
print()

if len(v3_venues) > 0:
    print('Venues with V3 metadata (old format):')
    for v in v3_venues[:10]:
        print(f'  ID {v["id"]}: scrapeConfidenceScore exists, scrapeVersion={v.get("metadata", {}).get("scrapeVersion", "N/A")}')

print()
print('Conclusion:')
if len(v4_venues) == len(active):
    print('  All active venues use V4 - V3 is deprecated')
else:
    print(f'  {len(active) - len(v4_venues)} venues still not processed by V4')
