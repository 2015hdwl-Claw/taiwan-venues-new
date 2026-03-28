#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批次執行 V4 全站爬蟲
"""

import json
import sys
from datetime import datetime

# Set UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from full_site_scraper_v4 import FullSiteScraper

# 讀取 venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    venues_data = json.load(f)

# 找出所有活躍場地
active_venues = [v for v in venues_data if v.get('status') != 'discontinued']

print(f"📊 總共 {len(active_venues)} 個活躍場地")
print(f"開始批次處理...\n")

# 創建 scraper 並處理
scraper = FullSiteScraper()
results = []

# 先處理前 10 個場地作為測試
test_venues = active_venues[:10]

print(f"🎯 先處理前 {len(test_venues)} 個場地作為測試\n")

for venue in test_venues:
    venue_id = venue['id']
    venue_name = venue['name']

    print(f"\n{'='*70}")
    print(f"# 處理場地 {venue_id}: {venue_name[:30]}")
    print(f"{'='*70}\n")

    try:
        result = scraper.scrape_venue(venue_id)
        results.append(result)

        print(f"\n✅ 完成:")
        print(f"   發現頁面: {result.get('pages_discovered', 0)}")
        print(f"   爬取頁面: {result.get('pages_scraped', 0)}")

    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)[:100]}")
        continue

# 儲存結果
scraper._save_data()

print(f"\n{'='*70}")
print(f"✅ 批次處理完成！")
print(f"{'='*70}")

# 統計
pages_discovered = sum(r.get('pages_discovered', 0) for r in results)
pages_scraped = sum(r.get('pages_scraped', 0) for r in results)

print(f"\n📊 統計:")
print(f"   處理場地: {len(results)}")
print(f"   總發現頁面: {pages_discovered}")
print(f"   總爬取頁面: {pages_scraped}")
print(f"   平均發現頁面/場地: {pages_discovered / len(results):.1f}")
print(f"   平均爬取頁面/場地: {pages_scraped / len(results):.1f}")
