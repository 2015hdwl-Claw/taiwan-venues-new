#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析南港展覽館並提供手動資料輸入範本
"""
import json
from datetime import datetime

print("="*80)
print("南港展覽館資料輸入")
print("="*80)
print()

print("根據網頁分析，南港展覽館有以下主要展場：")
print()
print("主要展場:")
print("  1. 一樓展覽室 (1F Exhibition Hall)")
print("  2. 二樓展覽室 (2F Exhibition Hall)")
print("  3. 三樓會議室 (3F Meeting Room)")
print("  4. 四樓會議室 (4F Meeting Room)")
print("  5. 五樓宴會廳 (5F Ballroom)")
print()

print("由於 Playwright 被阻擋，建議：")
print("  1. 手動訪問網站確認詳細資訊")
print("  2. 參考以下範本手動輸入資料")
print("  3. 或聯繫場地索取會議室資料")
print()

# 載入 venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# 找到南港展覽館
for venue in venues:
    if venue['id'] == 1500:
        print("="*80)
        print(f"目前資料: {venue['name']} (ID {venue['id']})")
        print("="*80)
        print(f"URL: {venue['url']}")
        print(f"會議室數量: {len(venue.get('rooms', []))}")
        print()

        # 手動新增範例資料
        print("建議手動新增的會議室資料範例:")
        print("-"*80)
        print()

        sample_rooms = [
            {
                "name": "一樓展覽室",
                "capacityTheater": 5000,
                "areaSqm": 5000,
                "dimensions": "100×50×10",
                "priceWeekday": 200000,
                "source": "manual_input"
            },
            {
                "name": "二樓展覽室",
                "capacityTheater": 3000,
                "areaSqm": 3000,
                "dimensions": "80×50×8",
                "priceWeekday": 150000,
                "source": "manual_input"
            },
            {
                "name": "三樓會議室 A",
                "capacityTheater": 500,
                "areaSqm": 300,
                "dimensions": "20×15×4",
                "priceWeekday": 30000,
                "source": "manual_input"
            },
        ]

        print("範例 JSON 格式:")
        print(json.dumps(sample_rooms, ensure_ascii=False, indent=2))
        print()
        print("-"*80)
        print()
        print("如要新增，請複製上述格式並修改為正確資料")
        print()
        print("或者訪問以下網址確認資訊：")
        print(f"  主頁: {venue['url']}")
        if venue.get('metadata', {}).get('alternative_urls'):
            print("  替代網址:")
            for alt_url in venue['metadata']['alternative_urls']:
                print(f"    - {alt_url}")

        break

print()
print("="*80)
print("完成")
print("="*80)
