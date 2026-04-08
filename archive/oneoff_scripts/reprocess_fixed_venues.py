#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新處理修正後的場地
"""
import sys

try:
    if sys.platform == 'win32':
        import locale
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except:
    pass

from full_site_scraper_v4 import FullSiteScraper

# 剛剛修正的場地ID
fixed_venue_ids = [1495, 1496, 1497, 1498, 1499, 1075, 1082, 1083, 1086, 1103]

print('=== Re-processing Fixed Venues ===')
print(f'Total: {len(fixed_venue_ids)} venues\n')

scraper = FullSiteScraper()
results = []

for venue_id in fixed_venue_ids:
    print(f'\n{"="*70}')
    print(f'# Re-processing venue {venue_id}')
    print(f'{"="*70}\n')

    try:
        result = scraper.scrape_venue_full_site(venue_id)
        results.append(result)

        pages = result.get('pages_discovered', 0)
        print(f'\n[OK] Completed: {pages} pages discovered')

        if pages > 0:
            print(f'[SUCCESS] Breakthrough! Found {pages} pages')
        else:
            print(f'[INFO] Still 0 pages - need alternative approach')

    except Exception as e:
        print(f'[ERROR] {str(e)[:100]}')
        continue

# 儲存結果
scraper._save_data()
print(f'\n\n{"="*70}')
print('Re-processing Complete!')
print(f'{"="*70}\n')

# 統計
success_count = sum(1 for r in results if r.get('pages_discovered', 0) > 0)
total_pages = sum(r.get('pages_discovered', 0) for r in results)

print(f'[STATS] Results:')
print(f'   Processed: {len(results)}')
print(f'   Breakthroughs: {success_count}')
print(f'   Total pages: {total_pages}')

if success_count > 0:
    print(f'\n[SUCCESS] Breakthrough venues:')
    for r in results:
        if r.get('pages_discovered', 0) > 0:
            print(f'   - Venue {r["id"]}: {r["pages_discovered"]} pages')
