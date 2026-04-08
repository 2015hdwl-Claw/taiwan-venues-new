#!/usr/bin/env python3
"""
測試 StealthyFetcher 突破 JS 渲染網站
"""
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from scrapling.fetchers import Fetcher, StealthyFetcher

test_urls = [
    ('台北怡亨酒店', 'https://www.eclathotels.com/zt/taipei'),
    ('台北北門世民', 'https://www.citizenm.com/hotels/asia/taipei/taipei-north-gate'),
    ('台北喜來登', 'https://www.sheratongrandtaipei.com'),
]

print('=== Testing Fetcher vs StealthyFetcher ===\n')

for name, url in test_urls:
    print(f'[{name}]')
    print(f'URL: {url}')

    # 測試普通 Fetcher
    try:
        print('  [Fetcher] Testing...')
        response = Fetcher.get(url, impersonate='chrome', timeout=15)
        links = response.css('a::attr(href)').getall()
        nav_links = response.css('nav a::attr(href)').getall()
        print(f'    → Success! Found {len(links)} total links, {len(nav_links)} nav links')
    except Exception as e:
        print(f'    → Failed: {str(e)[:60]}')

    # 測試 StealthyFetcher
    try:
        print('  [StealthyFetcher] Testing...')
        response = StealthyFetcher.get(url, timeout=20)
        links = response.css('a::attr(href)').getall()
        nav_links = response.css('nav a::attr(href)').getall()
        print(f'    → Success! Found {len(links)} total links, {len(nav_links)} nav links')
    except Exception as e:
        print(f'    → Failed: {str(e)[:60]}')

    print()
