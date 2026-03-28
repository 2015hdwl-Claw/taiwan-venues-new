#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 undetected-playwright 爬取南港展覽館
undetected-playwright 專門設計用來繞過 Cloudflare 和反爬蟲檢測
"""
import asyncio
import json
from datetime import datetime
from undetected_playwright.async_api import async_playwright
import random


async def scrape_with_undetected():
    """使用 undetected-playwright 爬取"""
    url = "https://www.tainex.com.tw/venue/room-info/1/3"

    print("="*80)
    print("Undetected Playwright 測試 - 南港展覽館")
    print("="*80)
    print(f"URL: {url}")
    print()

    print("[1/5] 啟動 undetected chromium...")

    try:
        async with async_playwright() as up:
            # undetected_playwright 會自動繞過檢測
            browser = await up.chromium.launch(
                headless=False,  # 非無頭模式更像真人
            )

            print("[2/5] 建立瀏覽器上下文...")

            # 創建上下文
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                locale='zh-TW',
                timezone_id='Asia/Taipei',
            )

            page = await context.new_page()

            print("[3/5] 訪問網頁...")

            # 訪置額外的等待時間模擬真人
            await page.goto(url, timeout=60000)

            # 等待 JavaScript 執行
            await asyncio.sleep(5)

            # 檢查頁面標題
            title = await page.title()
            print(f"    標題: {title}")

            # 檢查 URL
            current_url = page.url
            print(f"    URL: {current_url}")

            # 檢查是否被阻擋
            content = await page.content()

            if b'blocked' in content.lower() or b'access denied' in content.lower():
                print("    被阻擋")
                success = False
            elif b'challenge' in content.lower() or b'captcha' in content.lower():
                print("    需要驗證（Cloudflare Challenge）")

                # 截圖以便查看
                await page.screenshot(path='nangang_challenge.png')
                print("    截圖: nangang_challenge.png")

                success = False
            elif len(content) < 10000:
                print(f"    內容太短: {len(content)} bytes")

                # 檢查實際內容
                text = await page.inner_text()
                print(f"    文字長度: {len(text)} 字元")
                print(f"    前 300 字元:")
                print(f"    {text[:300]}")

                success = False
            else:
                print("    成功！")
                print(f"    內容長度: {len(content)} bytes")
                success = True

                # 等待更多動態內容載入
                print()
                print("[4/5] 等待動態內容載入...")
                await asyncio.sleep(5)

                # 嘗試滾動頁面觸發更多內容
                await page.evaluate('window.scrollBy(0, window.innerHeight)')
                await asyncio.sleep(2)

                # 尋找會議室資料
                print()
                print("    尋找會議室資料...")

                # 嘗試多種選擇器
                selectors = [
                    '.room-item',
                    '.meeting-room',
                    '.venue-room',
                    'table',
                    '[class*="room"]',
                    '[class*="venue"]',
                ]

                for selector in selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        if elements:
                            print(f"      找到 {len(elements)} 個 '{selector}'")

                            # 顯示前幾個元素的內容
                            for i, elem in enumerate(elements[:3]):
                                text = await elem.inner_text()
                                if text and len(text.strip()) > 0:
                                    print(f"        元素 {i+1}: {text.strip()[:100]}...")
                    except Exception as e:
                        pass

                # 尋找所有文字中的關鍵字
                page_text = await page.inner_text()
                keywords = ['會議室', '展覽室', '容量', '坪', '樓', '廳', 'room', 'venue']
                found = [kw for kw in keywords if kw in page_text]

                if found:
                    print(f"    找到關鍵字: {found}")
                else:
                    print("    未找到會議室關鍵字")

                # 尋找連結
                links = await page.query_selector_all('a[href]')
                meeting_links = []

                for link in links:
                    try:
                        href = await link.get_attribute('href')
                        text = await link.inner_text()

                        if href and text:
                            if any(kw in text.lower() or kw in href.lower()
                                   for kw in ['room', 'venue', '會議', '展覽', '樓', '廳']):
                                if 0 < len(text.strip()) < 100:
                                    meeting_links.append({
                                        'text': text.strip(),
                                        'url': href
                                    })
                    except:
                        pass

                print(f"    會議室連結: {len(meeting_links)} 個")

                if meeting_links:
                    print()
                    print("    找到的連結:")
                    for link in meeting_links[:10]:
                        print(f"      - {link['text'][:70]}")
                        print(f"        {link['url']}")

                # 截圖
                await page.screenshot(path='nangang_undetected.png', full_page=True)
                print()
                print("    截圖: nangang_undetected.png")

                # 儲存 HTML
                html_content = await page.content()
                with open('nangang_undetected.html', 'w', encoding='utf-8') as f:
                    f.write(html_content.decode('utf-8', errors='ignore'))

                print("    HTML: nangang_undetected.html")

            await browser.close()

            return success

    except Exception as e:
        print(f"錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_homepage_first():
    """先測試首頁"""
    print()
    print("="*80)
    print("先測試首頁")
    print("="*80)

    try:
        async with async_playwright() as up:
            browser = await up.chromium.launch(headless=False)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                locale='zh-TW',
            )
            page = await context.new_page()

            print("訪問首頁...")
            await page.goto('https://www.tainex.com.tw/', timeout=60000)

            await asyncio.sleep(3)

            title = await page.title()
            print(f"標題: {title}")

            # 尋找會議室相關連結
            links = await page.query_selector_all('a[href]')
            meeting_links = []

            for link in links:
                try:
                    href = await link.get_attribute('href')
                    text = await link.inner_text()

                    if href and text:
                        if any(kw in text.lower() or kw in href.lower()
                               for kw in ['room', 'venue', '會議', '展覽', '樓']):
                            if 0 < len(text.strip()) < 100:
                                meeting_links.append({
                                    'text': text.strip(),
                                    'url': href
                                })
                except:
                    pass

            print(f"會議室連結: {len(meeting_links)}")

            if meeting_links:
                print()
                print("找到的連結:")
                for link in meeting_links[:10]:
                    print(f"  - {link['text'][:70]}")
                    print(f"    {link['url']}")

            await browser.close()

            return len(meeting_links) > 0

    except Exception as e:
        print(f"錯誤: {e}")
        return False


async def main():
    print("="*80)
    print("Undetected Playwright 完整測試")
    print("="*80)
    print()
    print("Undetected Playwright 特點:")
    print("  - 自動修改瀏覽器特徵")
    print("  - 繞過自動化檢測")
    print("  - 模擬真實用戶行為")
    print("  - 專門對抗 Cloudflare")
    print()

    # 先測試首頁
    homepage_ok = await test_homepage_first()

    if homepage_ok:
        print()
        print("首頁成功，測試會議室頁面...")
        print()
        success = await scrape_with_undetected()

        if success:
            print()
            print("="*80)
            print("[SUCCESS] 突破成功！")
            print("="*80)
            print()
            print("下一步:")
            print("  1. 查看 nangang_undetected.html")
            print("  2. 檢查是否有會議室資料")
            print("  3. 提取並更新到 venues.json")
        else:
            print()
            print("="*80)
            print("[PARTIAL SUCCESS]")
            print("="*80)
            print()
            print("首頁可訪問，但會議室頁面仍有困難")
            print("建議: 從首頁找到的連結逐一測試")
    else:
        print()
        print("="*80)
        print("[FAILED]")
        print("="*80)
        print()
        print("Undetected Playwright 也無法完全突破")
        print("建議回歸手動輸入或聯繫場地")


if __name__ == '__main__':
    asyncio.run(main())
