#!/usr/bin/env python3
"""
實際測試：多種爬蟲方法對比
看看到底能不能抓取這些"無頁面"場地
"""
import requests
from bs4 import BeautifulSoup
import sys

# 測試一個無頁面場地
test_venue_id = 1083  # citizenM
test_url = 'https://www.citizenm.com/hotels/asia/taipei/taipei-north-gate'

print(f'=== 測試場地 {test_venue_id}: citizenM ===')
print(f'URL: {test_url}\n')

# 方法 1: 簡單 requests + BeautifulSoup
print('[方法1] requests + BeautifulSoup (最基本)')
try:
    resp = requests.get(test_url, timeout=10, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    print(f'  狀態碼: {resp.status_code}')
    print(f'  實際URL: {resp.url}')

    soup = BeautifulSoup(resp.text, 'html.parser')

    # 找所有連結
    all_links = soup.find_all('a', href=True)
    print(f'  總連結數: {len(all_links)}')

    # 找會議相關連結
    meeting_links = [a for a in all_links if any(kw in a.get_text().lower() for kw in ['meeting', 'conference', 'event', 'banquet', '會議', '宴會'])]
    print(f'  會議相關連結: {len(meeting_links)}')

    if meeting_links:
        print('  找到的會議連結:')
        for link in meeting_links[:5]:
            print(f'    - {link.get_text().strip()[:50]}: {link["href"]}')

except Exception as e:
    print(f'  ❌ 失敗: {e}')

print()

# 方法 2: Scrapling Fetcher
print('[方法2] Scrapling Fetcher')
try:
    from scrapling.fetchers import Fetcher
    response = Fetcher.get(test_url, impersonate='chrome', timeout=15)
    links = response.css('a::attr(href)').getall()
    print(f'  總連結數: {len(links)}')

    # 分析連結文本
    link_texts = response.css('a::text').getall()
    meeting_links = [(link_texts[i], links[i]) for i in range(len(links))
                    if any(kw in link_texts[i].lower() for kw in ['meeting', 'conference', 'event', 'banquet'])]
    print(f'  會議相關連結: {len(meeting_links)}')

    if meeting_links:
        print('  找到的會議連結:')
        for text, url in meeting_links[:5]:
            print(f'    - {text.strip()[:50]}: {url}')

except Exception as e:
    print(f'  ❌ 失敗: {e}')

print()

# 方法 3: Playwright (如果有的話)
print('[方法3] Playwright (完整JS渲染)')
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(test_url, wait_until='networkidle', timeout=15000)

        # 等待一下讓JS執行
        page.wait_for_timeout(2000)

        # 取得所有連結
        links = page.query_selector_all('a')
        print(f'  總連結數: {len(links)}')

        # 找會議相關
        for link in links[:10]:
            text = link.text_content()
            href = link.get_attribute('href')
            if text and any(kw in text.lower() for kw in ['meeting', 'conference']):
                print(f'    - {text.strip()[:50]}: {href}')

        browser.close()
        print('  ✅ 成功')

except ImportError:
    print('  ⚠️  Playwright 未安裝')
except Exception as e:
    print(f'  ❌ 失敗: {e}')

print()
print('=== 結論 ===')
print('如果方法1（最簡單的requests）就能抓到內容，')
print('那表示V4的頁面發現邏輯有問題，不是網站的問題。')
