#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下載南港展覽館官方資料 - 使用 headless=False
"""
import asyncio
import requests
from playwright.async_api import async_playwright


async def download_pdf_with_requests():
    """使用 requests 下載 PDF"""
    pdf_url = "https://www.tainex.com.tw/2021/api/app/40/%E5%A4%96%E8%B2%BF%E5%8D%94%E6%9C%83%E5%8F%B0%E5%8C%97%E5%8D%97%E6%B8%AF%E5%B1%95%E8%A6%BD%E9%A4%A8%E1%84%BC%E9%A4%A8%E6%9C%83%E8%AD%B0%E5%AE%A4%E7%A7%9F%E7%94%A8%E6%94%B6%E8%B2%BB%E5%9F%BA%E6%BA%96.pdf"

    print("下載官方 PDF (requests)...")
    print(f"URL: {pdf_url}")
    print()

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        response = requests.get(pdf_url, headers=headers, timeout=30)

        if response.status_code == 200:
            content = response.content
            filename = "nangang_official.pdf"
            with open(filename, 'wb') as f:
                f.write(content)

            print(f"[OK] 已儲存: {filename}")
            print(f"     大小: {len(content):,} bytes")
            return filename
        else:
            print(f"[ERROR] HTTP {response.status_code}")
            return None

    except Exception as e:
        print(f"[ERROR] {e}")
        return None


async def scrape_transportation_headful():
    """使用 headless=False 爬取交通資訊"""
    url = "https://www.tainex.com.tw/service/transportation/drive"

    print()
    print("爬取交通資訊 (headless=False)...")
    print(f"URL: {url}")
    print()

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            await page.goto(url, timeout=60000)
            await asyncio.sleep(5)

            html = await page.content()

            # 檢查是否被阻擋
            if 'blocked' in html.lower() or len(html) < 10000:
                print("[WARNING] 可能被阻擋")
                await browser.close()
                return None

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
    print("南港展覽館官方資料下載 V2")
    print("="*80)
    print()

    # 下載 PDF
    pdf_file = await download_pdf_with_requests()

    # 爬取交通資訊
    transport_file = await scrape_transportation_headful()

    print()
    print("="*80)
    print("完成")
    print("="*80)


if __name__ == '__main__':
    asyncio.run(main())
