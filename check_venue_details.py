#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查閱場地詳細資料
"""
import json
import sys

# Set UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Read venues.json
with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("="*100)
print("場地資料查閱工具")
print("="*100)
print()

# 1. 顯示已爬取場地的詳細資料
scraped_venues = [v for v in data if v.get('metadata', {}).get('lastScrapedAt')]

print(f"總共 {len(scraped_venues)} 個場地已爬取\n")

for venue in scraped_venues:
    name = venue['name']
    venue_id = venue['id']
    
    print("="*100)
    print(f"📍 {name} (ID: {venue_id})")
    print("="*100)
    
    # 基本資料
    print(f"\n📧 聯絡資訊:")
    if venue.get('email'):
        print(f"   Email: {venue['email']}")
    if venue.get('phone'):
        print(f"   Phone: {venue['phone']}")
    
    # 官網
    if venue.get('url'):
        print(f"\n🌐 官網: {venue['url']}")
    
    # 會議室
    rooms = venue.get('rooms', [])
    if rooms:
        print(f"\n🏛️  會議室數量: {len(rooms)} 間")
        for i, room in enumerate(rooms[:5], 1):  # 只顯示前 5 間
            print(f"   {i}. {room.get('name', 'N/A')}")
            if room.get('capacity'):
                print(f"      容量: {room['capacity']} 人")
            if room.get('price'):
                print(f"      價格: {room['price']}")
        if len(rooms) > 5:
            print(f"   ... 還有 {len(rooms) - 5} 間會議室")
    
    # Metadata
    metadata = venue.get('metadata', {})
    if metadata:
        print(f"\n📊 資料來源:")
        if metadata.get('emailSource'):
            print(f"   Email 來源: {metadata['emailSource']}")
        if metadata.get('phoneSource'):
            print(f"   Phone 來源: {metadata['phoneSource']}")
        if metadata.get('imagesFound'):
            print(f"   發現圖片: {metadata['imagesFound']} 張")
        if metadata.get('pdfLinks'):
            print(f"   PDF 連結: {len(metadata['pdfLinks'])} 個")
        if metadata.get('lastScrapedAt'):
            from datetime import datetime
            scraped_time = metadata['lastScrapedAt']
            print(f"   爬取時間: {scraped_time}")
        if metadata.get('scrapeStatus'):
            print(f"   狀態: {metadata['scrapeStatus']}")
    
    print()

print("="*100)
print("查閱完成")
print("="*100)
