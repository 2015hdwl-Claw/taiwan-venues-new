#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 Playwright 爬取南港展覽館會議室資料
URL: https://www.tainex.com.tw/venue/room-info/1/3
"""
import json
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright


async def scrape_nangang_playwright():
    """使用 Playwright 爬取南港展覽館"""
    url = "https://www.tainex.com.tw/venue/room-info/1/3"

    print("="*80)
    print("南港展覽館 Playwright 爬蟲")
    print("="*80)
    print(f"URL: {url}")
    print()

    async with async_playwright() as p:
        print("[1/5] 啟動瀏覽器...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print("[2/5] 載入網頁...")
        try:
            await page.goto(url, wait_until='networkidle', timeout=30000)
            print(f"    狀態: {page.url}")
            print(f"    標題: {await page.title()}")
        except Exception as e:
            print(f"    錯誤: {e}")
            await browser.close()
            return None

        print("[3/5] 等待 JavaScript 執行...")
        await page.wait_for_timeout(3000)  # 等待 3 秒讓 JS 執行

        print("[4/5] 嘗試多種選擇器...")

        rooms = []

        # 嘗試不同的選擇器
        selectors_to_try = [
            ('.room-item', 'room-item'),
            ('.meeting-room', 'meeting-room'),
            ('.venue-room', 'venue-room'),
            ('.exhibition-hall', 'exhibition-hall'),
            ('.hall', 'hall'),
            ('table tr', 'table rows'),
            ('.card', 'card'),
            ('[class*="room"]', 'room in class'),
            ('[class*="venue"]', 'venue in class'),
        ]

        for selector, desc in selectors_to_try:
            try:
                elements = await page.query_selector_all(selector)
                if elements:
                    print(f"    ✓ 找到 {len(elements)} 個 '{desc}' 元素")

                    # 提取前幾個元素的內容
                    for i, elem in enumerate(elements[:3]):
                        try:
                            text = await elem.inner_text()
                            print(f"      元素 {i+1}: {text[:100]}...")
                        except:
                            pass

                    # 如果是表格，特別處理
                    if 'tr' in selector:
                        rows = await page.query_selector_all('table tr')
                        for row in rows[:5]:
                            cells = await row.query_selector_all('td, th')
                            if cells:
                                row_data = []
                                for cell in cells:
                                    text = await cell.inner_text()
                                    row_data.append(text.strip()[:30])
                                print(f"      表格行: {' | '.join(row_data)}")

            except Exception as e:
                print(f"    ✗ '{desc}': {e}")

        # 嘗試尋找包含關鍵字的元素
        print()
        print("[5/5] 搜尋關鍵字...")
        keywords = ['會議室', '展覽館', '宴會廳', '會議廳', '樓', '廳', '容量', '坪']

        for keyword in keywords:
            try:
                elements = await page.query_selector_all(f"text='{keyword}'")
                if elements:
                    print(f"    找到 '{keyword}': {len(elements)} 處")
                    # 顯示上下文
                    for elem in elements[:2]:
                        try:
                            parent = await elem.evaluate('el => el.parentElement.textContent')
                            print(f"      上下文: {parent.strip()[:80]}...")
                        except:
                            pass
            except:
                pass

        # 截圖保存
        screenshot_path = 'nangang_screenshot.png'
        await page.screenshot(path=screenshot_path, full_page=True)
        print()
        print(f"[INFO] 截圖已儲存: {screenshot_path}")

        # 儲存 HTML
        html_content = await page.content()
        with open('nangang_rendered.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"[INFO] 渲染後的 HTML 已儲存: nangang_rendered.html")

        # 分析頁面結構
        print()
        print("[分析] 頁面結構:")

        # 檢查是否有特定的容器
        body = await page.query_selector('#body')
        if body:
            body_html = await body.inner_html()
            print(f"    #body 容器長度: {len(body_html)} 字元")

            # 檢查是否有動態內容
            if len(body_html) > 1000:
                print(f"    ✓ 發現動態內容")

                # 嘗試提取會議室資料
                # 尋找可能的會議室名稱
                possible_rooms = await page.evaluate('''
                    () => {
                        const rooms = [];
                        // 尋找所有標題
                        const headings = document.querySelectorAll('h1, h2, h3, h4, .title, .room-name');
                        headings.forEach(h => {
                            const text = h.textContent.trim();
                            if(text && text.length < 100 && text.length > 2) {
                                rooms.push(text);
                            }
                        });
                        return rooms.slice(0, 10);
                    }
                ''')

                if possible_rooms:
                    print(f"    可能的會議室名稱:")
                    for room in possible_rooms:
                        print(f"      - {room}")

        await browser.close()

        return rooms


async def main():
    rooms = await scrape_nangang_playwright()

    print()
    print("="*80)
    print("爬取完成")
    print("="*80)

    if rooms:
        print(f"找到 {len(rooms)} 個會議室")
    else:
        print()
        print("[建議] 請檢查:")
        print("  1. nangang_rendered.html - 查看完整 HTML")
        print("  2. nangang_screenshot.png - 查看頁面截圖")
        print()
        print("根據檢查結果，可以:")
        print("  - 調整選擇器")
        print("  - 手動新增會議室資料")
        print("  - 聯繫場地索取資料")


if __name__ == '__main__':
    asyncio.run(main())
