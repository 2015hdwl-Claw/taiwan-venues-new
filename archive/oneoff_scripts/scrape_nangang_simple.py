#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單 Playwright 測試 - 南港展覽館
"""
import asyncio
from playwright.async_api import async_playwright


async def scrape_simple():
    """最簡單的 Playwright 測試"""
    url = "https://www.tainex.com.tw/venue/room-info/1/3"

    print("="*80)
    print("Playwright 簡單測試 - 南港展覽館")
    print("="*80)
    print(f"URL: {url}")
    print()

    try:
        print("[1/3] 啟動瀏覽器...")

        async with async_playwright() as p:
            # 使用 headless=False 模擬真人
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                ]
            )

            print("[2/3] 訪問網頁...")

            # 建立頁面
            page = await browser.new_page(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            # 訪問網頁
            await page.goto(url, timeout=60000, wait_until='domcontentloaded')

            # 等待
            await asyncio.sleep(5)

            # 檢查標題
            title = await page.title()
            print(f"    標題: {title}")

            # 檢查 URL
            current_url = page.url
            print(f"    URL: {current_url}")

            # 檢查內容
            content = await page.content()
            print(f"    內容長度: {len(content)} bytes")

            # 檢查是否被阻擋
            content_lower = content.lower()
            if 'blocked' in content_lower or 'access denied' in content_lower:
                print("    被阻擋")
                success = False
            elif 'challenge' in content_lower or 'captcha' in content_lower:
                print("    需要 Cloudflare 驗證")
                print("    請手動完成驗證（30秒）...")
                await asyncio.sleep(30)

                # 重新檢查
                content = await page.content()
                if 'challenge' not in content.lower():
                    print("    驗證完成！")
                    success = True
                else:
                    print("    仍在驗證中")
                    success = False
            elif len(content) < 10000:
                print(f"    內容太短: {len(content)} bytes")
                success = False
            else:
                print("    成功！")
                success = True

            if success:
                print()
                print("[3/3] 提取資料...")

                # 等待動態內容
                await asyncio.sleep(3)

                # 滾動頁面
                await page.evaluate('window.scrollBy(0, 500)')
                await asyncio.sleep(2)

                # 尋找會議室資料
                page_text = await page.evaluate('() => document.body.innerText')
                keywords = ['會議室', '展覽', '容量', '坪', '樓', '廳']
                found = [kw for kw in keywords if kw in page_text]

                if found:
                    print(f"    找到關鍵字: {found}")
                else:
                    print("    未找到會議室關鍵字")

                # 截圖
                await page.screenshot(path='nangang_simple.png', full_page=True)
                print("    截圖: nangang_simple.png")

                # 儲存 HTML
                with open('nangang_simple.html', 'w', encoding='utf-8') as f:
                    f.write(content)

                print("    HTML: nangang_simple.html")

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
    print("Playwright 簡單測試")
    print("="*80)
    print()

    success = await scrape_simple()

    print()
    print("="*80)
    print("測試結果")
    print("="*80)

    if success:
        print("[SUCCESS] 成功獲取內容！")
        print()
        print("下一步:")
        print("  1. 查看 nangang_simple.html")
        print("  2. 檢查是否有會議室資料")
    else:
        print("[FAILED]")
        print()
        print("建議:")
        print("  1. 手動輸入資料")
        print("  2. 聯繫場地索取")


if __name__ == '__main__':
    asyncio.run(main())
