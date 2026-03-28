#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下載南港展覽館官方資料
"""
import asyncio
from playwright.async_api import async_playwright


async def download_pdf():
    """下載官方 PDF"""
    pdf_url = "https://www.tainex.com.tw/2021/api/app/40/%E5%A4%96%E8%B2%BF%E5%8D%94%E6%9C%83%E5%8F%B0%E5%8C%97%E5%8D%97%E6%B8%AF%E5%B1%95%E8%A6%BD%E9%A4%A8%E1%84%BC%E9%A4%A8%E6%9C%83%E8%AD%B0%E5%AE%A4%E7%A7%9F%E7%94%A8%E6%94%B6%E8%B2%BB%E5%9F%BA%E6%BA%96.pdf"

    print("下載官方 PDF...")
    print(f"URL: {pdf_url}")
    print()

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # 監聽回應
            async def handle_response(response):
                if response.status == 200 and response.url.endswith('.pdf'):
                    print(f"  找到 PDF: {len(await response.body())} bytes")

                    content = await response.body()
                    filename = "nangang_official.pdf"
                    with open(filename, 'wb') as f:
                        f.write(content)

                    print(f"[OK] 已儲存: {filename}")
                    print(f"     大小: {len(content):,} bytes")
                    return filename

            page.on('response', handle_response)

            await page.goto(pdf_url, timeout=60000)
            await asyncio.sleep(3)

            await browser.close()

            # 檢查檔案是否存在
            import os
            if os.path.exists('nangang_official.pdf'):
                size = os.path.getsize('nangang_official.pdf')
                print(f"[OK] 已下載 PDF: {size:,} bytes")
                return 'nangang_official.pdf'
            else:
                print("[ERROR] PDF 下載失敗")
                return None

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return None


async def scrape_transportation():
    """爬取交通資訊頁面"""
    url = "https://www.tainex.com.tw/service/transportation/drive"

    print()
    print("爬取交通資訊...")
    print(f"URL: {url}")
    print()

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=60000)
            await asyncio.sleep(3)

            html = await page.content()

            # 儲存 HTML
            filename = "nangang_transportation.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html)

            print(f"[OK] 已儲存: {filename}")

            # 提取關鍵資訊
            page_text = await page.evaluate('() => document.body.innerText')

            # 儲存文字內容
            text_filename = "nangang_transportation.txt"
            with open(text_filename, 'w', encoding='utf-8') as f:
                f.write(page_text)

            print(f"[OK] 已儲存: {text_filename}")

            await browser.close()

            return filename

    except Exception as e:
        print(f"[ERROR] {e}")
        return None


async def main():
    print("="*80)
    print("南港展覽館官方資料下載")
    print("="*80)
    print()

    # 下載 PDF
    pdf_file = await download_pdf()

    # 爬取交通資訊
    transport_file = await scrape_transportation()

    print()
    print("="*80)
    print("完成")
    print("="*80)
    print()

    if pdf_file:
        print("下一步:")
        print("  1. 使用 PDF 解析工具提取收費基準")
        print("  2. 對比並更新 venues.json 中的價格資料")
        print()

    if transport_file:
        print("下一步:")
        print("  1. 檢視 nangang_transportation.txt")
        print("  2. 提取 MRT、公車、停車場資訊")
        print("  3. 更新 venues.json 的 traffic 欄位")


if __name__ == '__main__':
    asyncio.run(main())
