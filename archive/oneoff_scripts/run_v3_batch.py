#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量執行 V3 爬蟲 - 處理所有剩餘場地
"""

import json
import sys
from datetime import datetime

# Set UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 導入 IntelligentScraper
from intelligent_scraper_v3 import IntelligentScraper

# 讀取 venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# 找出所有未處理的場地
unprocessed = []
for venue in venues:
    if venue.get('status') == 'discontinued':
        continue
    if 'scrapeConfidenceScore' not in venue.get('metadata', {}):
        unprocessed.append(venue['id'])

print(f"📊 總共 {len(unprocessed)} 個未處理場地")
print(f"開始批次處理...\n")

# 創建 scraper 實例
scraper = IntelligentScraper()

# 每次處理 5 個場地
batch_size = 5
results = []

for i in range(0, len(unprocessed), batch_size):
    batch = unprocessed[i:i+batch_size]
    batch_num = i // batch_size + 1
    total_batches = (len(unprocessed) + batch_size - 1) // batch_size

    print(f"\n{'='*70}")
    print(f"批次 {batch_num}/{total_batches}")
    print(f"處理場地：{batch}")
    print(f"{'='*70}\n")

    # 逐個處理每個場地
    for venue_id in batch:
        print(f"\n{'#'*70}")
        print(f"# 處理場地 {venue_id}")
        print(f"{'#'*70}\n")

        result = scraper.scrape_venue(venue_id)
        results.append(result)

        print(f"✅ 場地 {venue_id} 處理完成")
        print(f"   分數：{result.confidence_score}")
        print(f"   等級：{result.confidence_level}")

    # 儲存進度
    scraper._save_data()
    print(f"\n✅ 批次 {batch_num} 完成")

print(f"\n{'='*70}")
print("🎉 所有批次處理完成！")
print(f"{'='*70}\n")

# 生成最終報告
print("生成最終報告...")
report = scraper.generate_report(results)
report_path = f"scraping_report_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report)
print(f"✅ 報告已生成：{report_path}")
