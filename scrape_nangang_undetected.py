#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 undetected-playwright 爬取南港展覽館
使用 stealth_async API
"""
import asyncio
import json
from datetime import datetime
from undetected_playwright import stealth_async
import random


async def scrape_tainex_undetected():
    """使用 stealth_async 爬取"""
    url = "https://www.tainex.com.tw/venue/room-info/1/3"

    print("="*80)
    print("Undetected Playwright 測試 - 南港展覽館")
    print("="*80)
    print(f"URL: {url}")
    print()

    print("[1/5] 使用 stealth_async 啟動...")

    try:
        # stealth_async 是 undetected_playwright 的核心 API
        async with stealth_async.open(
            browser="chromium",
            headless=False,  # 非無頭模式更像真人
        ) as browser:

            print("[2/5] 建立頁面...")

            page = await browser.new_page()

            print("[3/5] 訪問網頁...")

            # 訪置額外的請求頭
            await page.set_extra_http_headers({
                'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            })

            # 訪問網頁
            await page.goto(url, timeout=60000)

            # 模擬人類行為：等待
            await asyncio.sleep(3)

            # 檢查頁面
            title = await page.title()
            print(f"    標題: {title}")

            current_url = page.url
            print(f"    URL: {current_url}")

            # 檢查是否被阻擋
            content = await page.content()

            if b'blocked' in content.lower() or b'access denied' in content.lower():
                print("    被阻擋")
                await page.screenshot(path='nangang_blocked_undetected.png')
                return False

            elif b'challenge' in content.lower() or b'captcha' in content.lower():
                print("    需要 Cloudflare 驗證")

                # 等待用戶手動完成驗證（如果使用 headless=False）
                print("    請手動完成 Cloudflare 驗證...")
                print("    腳本將等待 30 秒...")
                await asyncio.sleep(30)

                # 重新檢查
                content = await page.content()

            # 檢查內容長度
            print(f"    內容長度: {len(content)} bytes")

            if len(content) > 10000:
                print("    [SUCCESS] 成功獲取內容！")

                # 等待 JavaScript 動態內容
                await asyncio.sleep(5)

                # 滾動頁面
                await page.evaluate('window.scrollBy(0, window.innerHeight)')
                await asyncio.sleep(2)

                # 尋找會議室資料
                print()
                print("[4/5] 提取會議室資料...")

                # 嘗試多種選擇器
                selectors = [
                    '.room-item',
                    '.meeting-room',
                    '.venue-room',
                    'table',
                    '[class*="room"]',
                    '[class*="venue"]',
                ]

                rooms_found = False

                for selector in selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        if elements:
                            print(f"    選擇器 '{selector}': {len(elements)} 個元素")

                            for i, elem in enumerate(elements[:3]):
                                text = await elem.inner_text()
                                if text and len(text.strip()) > 0:
                                    print(f"      元素 {i+1}: {text.strip()[:100]}...")
                                    rooms_found = True
                    except:
                        pass

                # 尋找所有文字中的關鍵字
                page_text = await page.inner_text()
                keywords = ['會議室', '展覽室', '容量', '坪', '樓', '廳']
                found = [kw for kw in keywords if kw in page_text]

                if found:
                    print(f"    找到關鍵字: {found}")
                    rooms_found = True

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

                print(f"    會議室連結: {len(meeting_links)}")

                if meeting_links:
                    print()
                    print("    找到的連結:")
                    for link in meeting_links[:10]:
                        print(f"      - {link['text'][:70]}")
                        print(f"        {link['url']}")

                # 截圖
                await page.screenshot(path='nangang_undetected_success.png', full_page=True)
                print()
                print("[5/5] 儲存結果...")

                # 儲存 HTML
                html_content = await page.content()
                with open('nangang_undetected.html', 'w', encoding='utf-8') as f:
                    f.write(html_content.decode('utf-8', errors='ignore'))

                print("    已儲存: nangang_undetected.html")

                # 儲存報告
                report = {
                    'url': url,
                    'title': title,
                    'status': 'success',
                    'content_length': len(content),
                    'keywords_found': found,
                    'meeting_links_count': len(meeting_links),
                    'timestamp': datetime.now().isoformat()
                }

                with open('nangang_undetected_report.json', 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2)

                print("    已儲存: nangang_undetected_report.json")

                return rooms_found

            else:
                print(f"    [WARNING] 內容太短: {len(content)} bytes")
                text = content.decode('utf-8', errors='ignore')
                print(f"    前 300 字元:")
                print(f"    {text[:300]}")

                return False

    except Exception as e:
        print(f"錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    print("="*80)
    print("Undetected Playwright 完整測試")
    print("="*80)
    print()

    success = await scrape_tainex_undetected()

    print()
    print("="*80)
    print("測試結果")
    print("="*80)

    if success:
        print("[SUCCESS] Undetected Playwright 成功突破！")
        print()
        print("下一步:")
        print("  1. 查看 nangang_undetected.html")
        print("  2. 查看 nangang_undetected_report.json")
        print("  3. 如果有會議室資料，提取並更新 venues.json")
    else:
        print("[FAILED] 無法突破或無資料")
        print()
        print("建議:")
        print("  - 手動輸入資料")
        print("  - 聯繫場地索取資料")


if __name__ == '__main__':
    asyncio.run(main())
