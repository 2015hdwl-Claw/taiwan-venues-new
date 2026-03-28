#!/usr/bin/env python3
"""
測試為什麼 citizenM 在 V4 顯示 0 頁面
但測試顯示有 15 個 nav links
"""
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from scrapling.fetchers import Fetcher

url = 'https://www.citizenm.com/hotels/asia/taipei/taipei-north-gate'

print('=== Debugging citizenM 0-page issue ===')
print(f'URL: {url}\n')

# 模擬 V4 的抓取流程
response = Fetcher.get(url, impersonate='chrome', timeout=15)

print('1. Check HTML structure:')
print(f'   Has <nav>: {"YES" if response.css("nav") else "NO"}')
print(f'   Has <footer>: {"YES" if response.css("footer") else "NO"}')

print('\n2. Navigation links found:')
nav_links = response.css('nav a::attr(href)').getall()
print(f'   Total: {len(nav_links)}')
for i, link in enumerate(nav_links[:10], 1):
    print(f'   {i}. {link}')

print('\n3. Footer links found:')
footer_links = response.css('footer a::attr(href)').getall()
print(f'   Total: {len(footer_links)}')
for i, link in enumerate(footer_links[:5], 1):
    print(f'   {i}. {link}')

print('\n4. V4 URL pattern guessing would check:')
patterns = ['/meeting', '/meetings', '/banquet', '/access', '/contact']
for pattern in patterns:
    test_url = url.rstrip('/') + pattern
    print(f'   {pattern}')

print('\n5. Check if site uses JS rendering:')
js_indicators = [
    'react', 'vue', 'angular', 'next',
    'data-reactroot', 'ng-app', 'v-app',
    '__NEXT_DATA__', '__NUXT__'
]
html = response.text.lower()
found_js = [ind for ind in js_indicators if ind in html]
print(f'   JS frameworks detected: {found_js if found_js else "None"}')

print('\n6. Sample of navigation link text:')
nav_texts = response.css('nav a::text').getall()
for i, text in enumerate(nav_texts[:5], 1):
    print(f'   {i}. "{text.strip()}"')
