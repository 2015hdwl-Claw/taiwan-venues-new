#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
進階 Playwright 腳本 - 繞過 Cloudflare 保護
使用多種技術模擬真實瀏覽器行為
"""
import asyncio
import random
from playwright.async_api import async_playwright
import json
from datetime import datetime


async def scrape_with_stealth():
    """使用隱蔽技術爬取"""
    url = "https://www.tainex.com.tw/"

    print("="*80)
    print("南港展覽館進階爬蟲（繞過 Cloudflare）")
    print("="*80)
    print(f"URL: {url}")
    print()

    async with async_playwright() as p:
        print("[1/7] 啟動瀏覽器（隱蔽模式）...")

        # 使用多種反偵測技術
        browser = await p.chromium.launch(
            headless=False,  # 設為 False 可能更容易繞過
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
            ]
        )

        print("[2/7] 建立瀏覽器上下文（模擬真實用戶）...")

        # 創建具有真實瀏覽器特徵的上下文
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='zh-TW',
            timezone_id='Asia/Taipei',
            geolocation={'latitude': 25.0478, 'longitude': 121.5318},  # 台北
            permissions=['geolocation'],
            color_scheme='light',
        )

        # 注入腳本來隱藏自動化特徵
        await context.add_init_script("""
            // 覆蓋 navigator.webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // 覆蓋 chrome 物件
            window.chrome = {
                runtime: {}
            };

            // 覆蓋 permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );

            // 覆蓋 plugins 長度
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            // 覆蓋 languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-TW', 'zh', 'en-US', 'en']
            });
        """)

        page = await context.new_page()

        print("[3/7] 模擬真實瀏覽行為...")

        # 先訪問首頁
        try:
            print("  - 訪問首頁...")
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)

            # 模擬人類行為：隨機等待
            await asyncio.sleep(random.uniform(1, 3))

            # 滾動頁面
            print("  - 滾動頁面...")
            await page.evaluate('window.scrollBy(0, window.innerHeight)')
            await asyncio.sleep(random.uniform(0.5, 1.5))

            await page.evaluate('window.scrollBy(0, window.innerHeight)')
            await asyncio.sleep(random.uniform(0.5, 1.5))

            # 滾動回頂部
            await page.evaluate('window.scrollTo(0, 0)')
            await asyncio.sleep(random.uniform(0.5, 1.5))

        except Exception as e:
            print(f"  錯誤: {e}")

        print("[4/7] 檢查是否被阻擋...")

        # 檢查頁面內容
        content = await page.content()
        title = await page.title()

        print(f"  標題: {title}")

        if 'blocked' in content.lower() or 'challenge' in content.lower():
            print("  ✗ 仍然被阻擋")

            # 嘗試等待 Cloudflare 驗證
            print("[5/7] 等待 Cloudflare 驗證...")
            await asyncio.sleep(10)  # 等待 10 秒

            # 檢查是否有驗證挑戰
            challenge = await page.query_selector('.cf-challenge, .captcha')
            if challenge:
                print("  發現 Cloudflare 驗證挑戰")
                print("  建議：手動完成驗證後再爬取")

            # 截圖
            await page.screenshot(path='nangang_blocked.png')
            print("  截圖: nangang_blocked.png")
        else:
            print("  ✓ 成功繞過阻擋！")

            print("[5/7] 提取會議室資料...")

            # 等待 JavaScript 執行
            await page.wait_for_timeout(3000)

            # 嘗試多種選擇器
            selectors = [
                '.room-item',
                '.meeting-room',
                '.venue-room',
                'table',
                '[class*="room"]',
                '[class*="venue"]',
            ]

            rooms = []
            for selector in selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        print(f"    找到 {len(elements)} 個 '{selector}'")

                        for elem in elements[:5]:
                            text = await elem.inner_text()
                            if text and len(text.strip()) > 0:
                                rooms.append({
                                    'selector': selector,
                                    'text': text.strip()[:200]
                                })
                except:
                    pass

            # 尋找會議室名稱
            print()
            print("[6/7] 搜尋會議室資訊...")

            # 嘗試從頁面文本中提取
            page_text = await page.evaluate('() => document.body.innerText')

            keywords = ['會議室', '展覽室', '宴會廳', '會議廳']
            for keyword in keywords:
                if keyword in page_text:
                    print(f"  ✓ 找到關鍵字: {keyword}")

            # 尋找連結
            links = await page.query_selector_all('a[href]')
            relevant_links = []

            for link in links:
                try:
                    href = await link.get_attribute('href')
                    text = await link.inner_text()

                    if href and any(kw in text.lower() or kw in href.lower() for kw in ['room', 'venue', '會議', '展覽', '樓', '廳']):
                        if href.startswith('/'):
                            href = 'https://www.tainex.com.tw' + href

                        relevant_links.append({
                            'text': text.strip(),
                            'url': href
                        })
                except:
                    pass

            if relevant_links:
                print(f"  找到 {len(relevant_links)} 個相關連結:")
                for link in relevant_links[:8]:
                    print(f"    - {link['text'][:50]}")
                    print(f"      {link['url']}")

            print("[7/7] 儲存結果...")

            # 截圖
            await page.screenshot(path='nangang_success.png', full_page=True)
            print("  截圖: nangang_success.png")

            # 儲存 HTML
            html = await page.content()
            with open('nangang_success.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print("  HTML: nangang_success.html")

        await browser.close()

        print()
        print("="*80)
        print("爬取完成")
        print("="*80)


async def try_alternative_urls():
    """嘗試替代 URL"""
    urls = [
        "https://www.tainex.com.tw/",
        "https://www.tainex.com.tw/venue/",
        "https://www.tainex.com.tw/venue/room-info/",
        "https://www.tainex.com.tw/venue/app-room",
    ]

    print()
    print("="*80)
    print("嘗試替代 URL")
    print("="*80)

    for url in urls:
        print(f"\n嘗試: {url}")

        try:
            import requests
            response = requests.get(url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                timeout=10
            )

            if 'blocked' not in response.text.lower():
                print(f"  ✓ 成功！HTTP {response.status_code}")
                print(f"  內容長度: {len(response.text)} bytes")

                # 檢查是否有會議室資料
                if '會議室' in response.text or '展覽' in response.text:
                    print(f"  ✓ 包含會議室相關資料")
            else:
                print(f"  ✗ 被阻擋")

        except Exception as e:
            print(f"  ✗ 錯誤: {e}")


async def main():
    # 嘗試隱蔽爬蟲
    await scrape_with_stealth()

    # 嘗試替代 URL
    await try_alternative_urls()


if __name__ == '__main__':
    asyncio.run(main())
