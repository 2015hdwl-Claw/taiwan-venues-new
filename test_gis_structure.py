#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試集思會議中心網站結構
"""
import asyncio
from playwright.async_api import async_playwright


GIS_VENUES = [
    {"id": 1494, "name": "集思交通部會議中心(MOTC)", "url": "https://www.meeting.com.tw/motc/"},
    {"id": 1495, "name": "集思北科技會議中心(Tech)", "url": "https://www.meeting.com.tw/ntut/"},
    {"id": 1496, "name": "集思台師大会議中心(HSPH)", "url": "https://www.meeting.com.tw/hsp/"},
    {"id": 1497, "name": "集思中國醫會議中心(TC)", "url": "https://www.meeting.com.tw/tc/"},
    {"id": 1498, "name": "集思烏日會議中心(WURI)", "url": "https://www.meeting.com.tw/wuri/"},
    {"id": 1499, "name": "集思高雄會議中心(KHH)", "url": "https://www.meeting.com.tw/khh/"},
]


async def test_gis_website(venue_info):
    """測試單一集思場地"""
    url = venue_info["url"]
    name = venue_info["name"]

    print("="*80)
    print(f"測試: {name}")
    print("="*80)
    print(f"URL: {url}")
    print()

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            await page.goto(url, timeout=60000, wait_until='domcontentloaded')
            await asyncio.sleep(5)

            # 檢查標題
            title = await page.title()
            print(f"標題: {title}")

            # 檢查 URL
            current_url = page.url
            print(f"URL: {current_url}")

            # 檢查內容
            content = await page.content()

            if 'blocked' in content.lower() or len(content) < 10000:
                print("[WARNING] 可能被阻擋或內容太短")
                await browser.close()
                return False

            print(f"內容長度: {len(content)} bytes")

            # 尋找會議室相關關鍵字
            page_text = await page.evaluate('() => document.body.innerText')

            keywords = ['會議室', '會議空間', '場地', '租借', '容納', '坪', '樓']
            found = [kw for kw in keywords if kw in page_text]

            if found:
                print(f"找到關鍵字: {found}")
            else:
                print("未找到會議室關鍵字")

            # 尋找會議室連結
            links = await page.query_selector_all('a[href]')
            room_links = []

            for link in links:
                try:
                    href = await link.get_attribute('href')
                    text = await link.inner_text()

                    if href and text:
                        # 尋找可能的會議室頁面
                        if any(kw in text.lower() or kw in href.lower()
                               for kw in ['room', 'venue', 'space', '會議', '場地', '空間']):
                            if 0 < len(text.strip()) < 100:
                                room_links.append({
                                    'text': text.strip(),
                                    'url': href
                                })
                except:
                    pass

            # 尋找 PDF 連結
            pdf_links = []
            for link in links:
                try:
                    href = await link.get_attribute('href')
                    if href and '.pdf' in href.lower():
                        text = await link.inner_text()
                        pdf_links.append({
                            'text': text.strip(),
                            'url': href
                        })
                except:
                    pass

            print()
            print(f"會議室相關連結: {len(room_links)}")

            if room_links:
                print()
                print("找到的連結:")
                for link in room_links[:10]:
                    print(f"  - {link['text'][:70]}")
                    print(f"    {link['url']}")

            print()
            print(f"PDF 連結: {len(pdf_links)}")

            if pdf_links:
                print()
                print("找到的 PDF:")
                for pdf in pdf_links[:5]:
                    print(f"  - {pdf['text'][:70]}")
                    print(f"    {pdf['url']}")

            # 儲存 HTML
            filename = f"gis_{venue_info['id']}_home.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)

            print()
            print(f"[OK] 已儲存: {filename}")

            await browser.close()

            return len(room_links) > 0 or len(pdf_links) > 0

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    print("="*80)
    print("集思會議中心網站結構測試")
    print("="*80)
    print()

    # 先測試一個
    print("[測試 1/6] 集思交通部會議中心")
    print()

    success = await test_gis_website(GIS_VENUES[0])

    print()
    print("="*80)
    print("測試結果")
    print("="*80)

    if success:
        print("[SUCCESS] 找到會議室相關資料")
        print()
        print("下一步:")
        print("  1. 分析找到的連結")
        print("  2. 設計通用爬蟲")
        print("  3. 批次處理所有集思場地")
    else:
        print("[FAILED] 未找到會議室資料")
        print()
        print("建議:")
        print("  1. 手動檢視網頁結構")
        print("  2. 聯繫場地索取資料")


if __name__ == '__main__':
    asyncio.run(main())
