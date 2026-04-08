#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V4 Direct Batch Processing - Process specified venues
"""

import json
import sys
from datetime import datetime

# Try to set UTF-8 encoding for Windows
try:
    if sys.platform == 'win32':
        import locale
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except:
    pass

from full_site_scraper_v4 import FullSiteScraper

# 讀取 venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    venues_data = json.load(f)

# 未處理的場地 ID
unprocessed_ids = [
    1051, 1082, 1083, 1085, 1121, 1122, 1124, 1125, 1126, 1128,
    1129, 1334, 1448, 1493, 1494, 1495, 1496, 1497, 1498, 1499
]

print(f"[INFO] Processing {len(unprocessed_ids)} unprocessed venues")
print(f"[INFO] Starting batch processing...\n")

# 創建 scraper
scraper = FullSiteScraper()
results = []

# 每次處理 5 個場地
batch_size = 5
for i in range(0, len(unprocessed_ids), batch_size):
    batch = unprocessed_ids[i:i+batch_size]
    batch_num = i // batch_size + 1
    total_batches = (len(unprocessed_ids) + batch_size - 1) // batch_size

    print(f"\n{'='*70}")
    print(f"Batch {batch_num}/{total_batches}")
    print(f"Processing venues: {batch}")
    print(f"{'='*70}\n")

    for venue_id in batch:
        print(f"\n{'#'*70}")
        print(f"# Processing venue {venue_id}")
        print(f"{'#'*70}\n")

        try:
            result = scraper.scrape_venue_full_site(venue_id)
            results.append(result)

            pages = result.get('pages_discovered', 0)
            print(f"[OK] Completed: {pages} pages discovered")

        except Exception as e:
            print(f"[ERROR] Error: {str(e)[:100]}")
            continue

    # Save progress
    scraper._save_data()
    print(f"\n[OK] Batch {batch_num} completed")

print(f"\n{'='*70}")
print("[SUCCESS] All batches completed!")
print(f"{'='*70}\n")

# Statistics
success_count = sum(1 for r in results if 'error' not in r)
total_pages = sum(r.get('pages_discovered', 0) for r in results)

print(f"[STATS] Final statistics:")
print(f"   Venues processed: {len(results)}")
print(f"   Successful: {success_count}")
print(f"   Total pages discovered: {total_pages}")
if len(results) > 0:
    print(f"   平均頁面/場地：{total_pages / len(results):.1f}")
