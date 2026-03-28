#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成最終處理報告
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

# 統計各種狀態
total = len(data)
active = [v for v in data if v.get('status') != 'discontinued']
discontinued = [v for v in data if v.get('status') == 'discontinued']

# 統計有爬取記錄的
scraped = [v for v in data if v.get('metadata', {}).get('lastScrapedAt')]
not_scraped = [v for v in active if not v.get('metadata', {}).get('lastScrapedAt')]

# 統計失敗的
failed_venues = [1035, 1048, 1059, 1065, 1066, 1073, 1080, 1084, 1092]

print("="*100)
print("最終處理報告")
print("="*100)
print()

print(f"總場地數: {total}")
print(f"活躍場地: {len(active)}")
print(f"下架場地: {len(discontinued)}")
print()

print(f"已爬取場地: {len(scraped)}")
print(f"未爬取場地: {len(not_scraped)}")
print()

print("="*100)
print("爬取成功場地:")
print("="*100)
for v in scraped:
    name = v['name']
    venue_id = v['id']
    email = v.get('email', 'N/A')
    phone = v.get('phone', 'N/A')
    images = v.get('metadata', {}).get('imagesFound', 0)
    pdfs = len(v.get('metadata', {}).get('pdfLinks', []))
    print(f"✅ {name} (ID: {venue_id})")
    if email != 'N/A':
        print(f"   Email: {email}")
    if phone != 'N/A':
        print(f"   Phone: {phone}")
    if images > 0:
        print(f"   Images: {images}")
    if pdfs > 0:
        print(f"   PDFs: {pdfs}")
    print()

print("="*100)
print("爬取失敗場地 (需要下架或特殊處理):")
print("="*100)
for venue_id in failed_venues:
    venue = next((v for v in data if v['id'] == venue_id), None)
    if venue:
        print(f"❌ {venue['name']} (ID: {venue_id})")
        print(f"   URL: {venue.get('url', 'N/A')}")
        print()

print("="*100)
print("尚未爬取場地:")
print("="*100)
for v in not_scraped:
    print(f"⏳ {v['name']} (ID: {v['id']})")
    print(f"   URL: {v.get('url', 'N/A')}")
    print()

print("="*100)
print(f"處理完成率: {len(scraped)}/{len(active)} = {len(scraped)*100//len(active)}%")
print("="*100)
