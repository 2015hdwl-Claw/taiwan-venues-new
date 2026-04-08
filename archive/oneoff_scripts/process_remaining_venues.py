#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from intelligent_scraper_v3 import IntelligentScraper

# 讀取 venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    venues_data = json.load(f)

# 找出所有未處理的場地
unprocessed_ids = []
for venue in venues_data:
    if venue.get('status') == 'discontinued':
        continue
    if 'scrapeConfidenceScore' not in venue.get('metadata', {}):
        unprocessed_ids.append(venue['id'])

print(f"Processing {len(unprocessed_ids)} venues...")

# 創建 scraper 並處理
scraper = IntelligentScraper()
results = []

for venue_id in unprocessed_ids:
    print(f"\nProcessing venue {venue_id}...")
    result = scraper.scrape_venue(venue_id)
    results.append(result)
    print(f"  Score: {result.confidence_score}, Level: {result.confidence_level}")

    # 每 5 個保存一次
    if len(results) % 5 == 0:
        scraper._save_data()

scraper._save_data()

# 生成報告
print("\nGenerating final report...")
report = scraper.generate_report(results)
with open('scraping_report_final.md', 'w', encoding='utf-8') as f:
    f.write(report)

print("Done!")
