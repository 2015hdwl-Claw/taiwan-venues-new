#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Scrapling with 六福萬怡酒店 website
"""

import json
import sys
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Test 1: Basic Fetcher
print("="*80)
print("TEST 1: Basic Fetcher - 六福萬怡 meeting page")
print("="*80)

from scrapling.fetchers import Fetcher

try:
    page = Fetcher.get('https://www.courtyardtaipei.com.tw/wedding/meeting')
    print(f"✅ Fetcher.get() succeeded")
    print(f"   Status: {page}")
    print(f"   URL: {page.url}")

    # Try to extract phone number
    phone_elements = page.css('*:contains("02-")')
    print(f"\n   Found {len(phone_elements)} elements with '02-'")

    # Extract text content
    text_content = page.css('body::text').getall()
    full_text = ' '.join([t.strip() for t in text_content if t.strip()])

    # Look for phone patterns
    import re
    phones = re.findall(r'0\d-\d{4}-\d{4}', full_text)
    if phones:
        print(f"\n   📞 Found phone numbers: {phones}")

    # Look for email patterns
    emails = re.findall(r'[\w.]+@[\w.]+', full_text)
    if emails:
        print(f"   📧 Found emails: {emails}")

except Exception as e:
    print(f"❌ Fetcher.get() failed: {e}")

# Test 2: StealthyFetcher (if available)
print("\n" + "="*80)
print("TEST 2: StealthyFetcher - 繞過 Cloudflare/反爬蟲")
print("="*80)

try:
    from scrapling.fetchers import StealthyFetcher

    print("Trying StealthyFetcher (may take longer)...")
    page_stealth = StealthyFetcher.fetch(
        'https://www.courtyardtaipei.com.tw/wedding/meeting',
        headless=True
    )
    print(f"✅ StealthyFetcher.fetch() succeeded")
    print(f"   URL: {page_stealth.url}")

except Exception as e:
    print(f"❌ StealthyFetcher.fetch() failed: {e}")

# Test 3: Fetcher with different methods
print("\n" + "="*80)
print("TEST 3: Fetcher with impersonate (模擬瀏覽器)")
print("="*80)

try:
    page_impersonate = Fetcher.get(
        'https://www.courtyardtaipei.com.tw/wedding/meeting',
        impersonate='chrome'  # 模擬 Chrome 瀏覽器
    )
    print(f"✅ Fetcher with impersonate succeeded")
    print(f"   URL: {page_impersonate.url}")

    # Test CSS selectors
    title = page_impersonate.css('title::text').get()
    print(f"   📄 Page title: {title}")

    # Look for meeting room information
    room_sections = page_impersonate.css('.meeting-room, .venue, .room')
    print(f"   🏛️  Found {len(room_sections)} potential room sections")

except Exception as e:
    print(f"❌ Fetcher with impersonate failed: {e}")

# Test 4: Parse existing venues.json
print("\n" + "="*80)
print("TEST 4: Parse venues.json for batch processing")
print("="*80)

try:
    with open('venues.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"✅ venues.json loaded successfully")
    print(f"   Total venues: {len(data)}")

    # Find venues with official websites
    venues_with_websites = [v for v in data if v.get('official_website')]
    print(f"   Venues with websites: {len(venues_with_websites)}")

    # Show first 5
    print(f"\n   First 5 venues:")
    for v in venues_with_websites[:5]:
        print(f"      - {v['name']}: {v.get('official_website', 'N/A')}")

except Exception as e:
    print(f"❌ Failed to load venues.json: {e}")

# Test 5: Concurrent requests
print("\n" + "="*80)
print("TEST 5: AsyncFetcher - 並發請求測試")
print("="*80)

try:
    import asyncio
    from scrapling.fetchers import AsyncFetcher

    async def fetch_multiple():
        # Test with 3 hotel websites
        urls = [
            'https://www.courtyardtaipei.com.tw/wedding/meeting',
            'https://www.theillumehotel.com/zh/',
            'https://www.mandarinoriental.com/taipei'
        ]

        print(f"   Fetching {len(urls)} URLs concurrently...")
        async with AsyncFetcher() as session:
            tasks = [session.get(url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        successful = sum(1 for r in results if not isinstance(r, Exception))
        print(f"   ✅ Successful: {successful}/{len(urls)}")

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"      ❌ URL {i+1}: {str(result)[:50]}")
            else:
                print(f"      ✅ URL {i+1}: {result.url[:50]}")

    asyncio.run(fetch_multiple())

except Exception as e:
    print(f"❌ AsyncFetcher test failed: {e}")

print("\n" + "="*80)
print("✅ Scrapling 測試完成！")
print("="*80)
print(f"\n測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("\n下一步：建立完整的爬蟲腳本來批次抓取場地資料")
