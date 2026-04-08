#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 stealth 技術爬取南港展覽館
"""
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime


async def scrape_with_stealth():
    """使用 stealth_async 套件"""
    url = "https://www.tainex.com.tw/venue/room-info/1/3"

    print("="*80)
    print("Playwright + Stealth 測試")
    print("="*80)
    print(f"URL: {url}")
    print()

    print("[1/5] 啟動瀏覽器...")

    try:
        async with async_playwright() as p:
            # 使用 stealth_async 修飾瀏覽器
            browser = await p.chromium.launch(headless=False)

        print("[2/5] 應用 stealth...")
        print("    使用手動反檢測腳本")

        print("[3/5] 建立頁面...")

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='zh-TW',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        )

        page = await context.new_page()

        # 注入反檢測腳本
        await page.add_init_script("""
            // 覆蓋 navigator.webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
                configurable: true
            });

            // 覆蓋 chrome
            window.chrome = {
                runtime: {}
            };

            // 覆蓋 plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
                configurable: true
            });

            // 覆蓋 languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-TW', 'zh', 'en-US', 'en'],
                configurable: true
            });
        """)

        print("[4/5] 訪問網頁...")

        try:
            await page.goto(url, timeout=60000, wait_until='domcontentloaded')

            # 等待 JavaScript
            await asyncio.sleep(5)

            # 檢查標題
            title = await page.title()
            print(f"    標題: {title}")

            # 檢查當前 URL
            current_url = page.url
            print(f"    URL: {current_url}")

            # 檢查內容
            content = await page.content()
            print(f"    內容長度: {len(content)} bytes")

            # 檢查是否被阻擋
            if b'blocked' in content.lower():
                print("    被阻擋")
                success = False
            elif b'challenge' in content.lower():
                print("    需要 Cloudflare 驗證")

                # 等待手動完成驗證
                print("    請手動完成 Cloudflare 驗證...")
                print("    等待 30 秒...")

                await asyncio.sleep(30)

                # 重新檢查
                content = await page.content()

                if b'challenge' not in content.lower():
                    print("    驗證完成！")
                    success = True
                else:
                    print("    仍在驗證中")
                    success = False
            else:
                print("    成功！")
                success = True

            if success and len(content) > 10000:
                print()
                print("[5/5] 提取資料...")

                # 等待動態內容
                await asyncio.sleep(3)

                # 滾動頁面
                await page.evaluate('window.scrollBy(0, 500)')
                await asyncio.sleep(2)

                # 尋找會議室資料
                page_text = await page.inner_text()
                keywords = ['會議室', '展覽', '容量', '坪', '樓', '廳']
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

                        if href and any(kw in text.lower() or kw in href.lower()
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
                    for link in meeting_links[:8]:
                        print(f"      - {link['text'][:70]}")
                        print(f"        {link['url']}")

                # 截圖
                await page.screenshot(path='nangang_stealth_success.png', full_page=True)

                # 儲存 HTML
                html = await page.content()
                with open('nangang_stealth.html', 'w', encoding='utf-8') as f:
                    f.write(html.decode('utf-8', errors='ignore'))

                print()
                print("    已儲存:")
                print("      - nangang_stealth_success.png")
                print("      - nangang_stealth.html")

        except Exception as e:
            print(f"    錯誤: {e}")
            import traceback
            traceback.print_exc()

            await browser.close()

            return success

    except Exception as e:
        print(f"錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    print()
    print("="*80)
    print("Playwright + Stealth 自動化")
    print("="*80)
    print()
    print("使用手動 stealth 技術...")
    print()

    success = await scrape_with_stealth()

    print()
    print("="*80)
    print("測試結果")
    print("="*80)

    if success:
        print("[SUCCESS] 突破 Cloudflare 成功！")
        print()
        print("下一步:")
        print("  查看 nangang_stealth.html")
    else:
        print("[FAILED]")
        print()
        print("建議:")
        print("  1. 手動輸入資料")
        print("  2. 聯繫場地索取")


if __name__ == '__main__':
    asyncio.run(main())
