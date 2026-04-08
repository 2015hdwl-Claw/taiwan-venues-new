#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 Playwright 提取 TICC 會議室照片
URL: https://www.ticc.com.tw/wSite/sp?xdUrl=/wSite/ap/lp_VenueSearch.jsp&ctNode=322&CtUnit=99&BaseDSD=7&mp=1
"""
import json
import asyncio
import os
from datetime import datetime
from playwright.async_api import async_playwright


async def extract_ticc_photos():
    """提取 TICC 會議室照片"""
    url = "https://www.ticc.com.tw/wSite/sp?xdUrl=/wSite/ap/lp_VenueSearch.jsp&ctNode=322&CtUnit=99&BaseDSD=7&mp=1"

    print("="*80)
    print("TICC 會議室照片提取")
    print("="*80)
    print(f"URL: {url}")
    print()

    async with async_playwright() as p:
        print("[1/6] 啟動瀏覽器...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print("[2/6] 載入網頁...")
        try:
            await page.goto(url, wait_until='networkidle', timeout=30000)
            print(f"    狀態: {page.url}")
            print(f"    標題: {await page.title()}")
        except Exception as e:
            print(f"    錯誤: {e}")
            await browser.close()
            return None

        print("[3/6] 等待內容載入...")
        await page.wait_for_timeout(3000)

        print("[4/6] 尋找會議室照片...")

        photos = []

        # 嘗試不同的選擇器
        selectors = [
            '.room-photo img',
            '.meeting-room img',
            '.venue-photo img',
            '.room img',
            '.photo img',
            '.image img',
            'img[src*="room"]',
            'img[src*="venue"]',
            'img[alt*="會議室"]',
            'img[alt*="廳"]',
        ]

        for selector in selectors:
            try:
                images = await page.query_selector_all(selector)
                if images:
                    print(f"    ✓ 選擇器 '{selector}': {len(images)} 張照片")

                    for img in images[:10]:  # 最多 10 張
                        try:
                            src = await img.get_attribute('src')
                            alt = await img.get_attribute('alt')

                            if src:
                                # 處理相對路徑
                                if src.startswith('/'):
                                    src = 'https://www.ticc.com.tw' + src
                                elif not src.startswith('http'):
                                    src = 'https://www.ticc.com.tw/' + src

                                photos.append({
                                    'src': src,
                                    'alt': alt or '',
                                    'selector': selector
                                })
                        except Exception as e:
                            print(f"      錯誤: {e}")
            except Exception as e:
                print(f"    ✗ 選擇器 '{selector}': {e}")

        # 如果沒找到，嘗試所有圖片
        if not photos:
            print()
            print("    嘗試尋找所有圖片...")
            try:
                all_images = await page.query_selector_all('img')
                print(f"    找到 {len(all_images)} 張圖片")

                for img in all_images[:20]:
                    try:
                        src = await img.get_attribute('src')
                        alt = await img.get_attribute('alt')
                        width = await img.get_attribute('width')
                        height = await img.get_attribute('height')

                        if src and not src.endswith('.gif'):  # 排除裝飾性 GIF
                            # 處理相對路徑
                            if src.startswith('/'):
                                src = 'https://www.ticc.com.tw' + src
                            elif not src.startswith('http'):
                                src = 'https://www.ticc.com.tw/' + src

                            photos.append({
                                'src': src,
                                'alt': alt or '',
                                'width': width or '',
                                'height': height or ''
                            })
                    except:
                        pass
            except Exception as e:
                print(f"    錯誤: {e}")

        # 尋找會議室名稱
        print()
        print("[5/6] 尋找會議室名稱...")

        room_names = await page.evaluate('''
            () => {
                const names = [];
                // 尋找標題
                const headings = document.querySelectorAll('h1, h2, h3, h4, .title, .room-name, .room-title');
                headings.forEach(h => {
                    const text = h.textContent.trim();
                    if(text && text.length < 100 && text.length > 2) {
                        names.push(text);
                    }
                });
                return [...new Set(names)];  // 去重
            }
        ''')

        if room_names:
            print(f"    找到 {len(room_names)} 個可能的名稱:")
            for name in room_names[:10]:
                print(f"      - {name}")

        # 截圖
        screenshot_path = 'ticc_photos_page.png'
        await page.screenshot(path=screenshot_path, full_page=True)
        print()
        print(f"[INFO] 截圖: {screenshot_path}")

        await browser.close()

        # 整理結果
        print()
        print("[6/6] 整理結果...")

        if photos:
            # 去重
            unique_photos = []
            seen_urls = set()

            for photo in photos:
                if photo['src'] not in seen_urls:
                    unique_photos.append(photo)
                    seen_urls.add(photo['src'])

            print(f"    照片數量: {len(photos)} (去重後: {len(unique_photos)})")

            # 顯示前 5 張
            print()
            print("    前 5 張照片:")
            for i, photo in enumerate(unique_photos[:5], 1):
                print(f"      {i}. {photo['src']}")
                if photo['alt']:
                    print(f"         Alt: {photo['alt'][:50]}")

            return unique_photos

        return None


async def download_photos(photos, download_dir='ticc_photos'):
    """下載照片"""
    if not photos:
        return

    import aiohttp
    from pathlib import Path

    Path(download_dir).mkdir(exist_ok=True)

    print()
    print("="*80)
    print("下載照片")
    print("="*80)
    print()

    async with aiohttp.ClientSession() as session:
        for i, photo in enumerate(photos[:20], 1):  # 最多下載 20 張
            url = photo['src']
            filename = f"room_{i:02d}.jpg"
            filepath = os.path.join(download_dir, filename)

            try:
                print(f"[{i}/{min(len(photos), 20)}] 下載 {filename}...")
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status == 200:
                        content = await resp.read()

                        with open(filepath, 'wb') as f:
                            f.write(content)

                        print(f"      ✓ 已儲存: {filepath} ({len(content)} bytes)")
                    else:
                        print(f"      ✗ HTTP {resp.status}")
            except Exception as e:
                print(f"      ✗ 錯誤: {e}")

    print()
    print(f"[OK] 照片已儲存到 {download_dir}/")


async def update_venues_with_photos(photos):
    """更新 venues.json 添加照片資訊"""
    if not photos:
        return

    print()
    print("="*80)
    print("更新 venues.json")
    print("="*80)
    print()

    import shutil
    from datetime import datetime

    # 備份
    backup = f'venues.json.backup.ticc_photos_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    shutil.copy('venues.json', backup)
    print(f"備份: {backup}")

    # 載入
    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    # 更新 TICC
    for venue in venues:
        if venue['id'] == 1448:
            # 添加照片資訊
            if 'photos' not in venue:
                venue['photos'] = []

            for photo in photos[:10]:  # 只添加前 10 張
                venue['photos'].append({
                    'url': photo['src'],
                    'alt': photo.get('alt', ''),
                    'added_at': datetime.now().isoformat()
                })

            if 'metadata' not in venue:
                venue['metadata'] = {}

            venue['metadata']['total_photos'] = len(venue['photos'])
            venue['metadata']['photos_updated_at'] = datetime.now().isoformat()

            print(f"✓ TICC (ID 1448): 添加 {len(venue['photos'])} 張照片")
            break

    # 儲存
    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)

    print("[OK] venues.json 已更新")


async def main():
    photos = await extract_ticc_photos()

    if photos:
        # 詢問是否下載
        print()
        print("="*80)
        print("下一步")
        print("="*80)
        print()
        print("找到照片後可以：")
        print("  1. 下載照片到本地")
        print("  2. 更新 venues.json 添加照片 URL")
        print("  3. 只顯示結果，不下載")
        print()
        print("預設：執行選項 1 + 2")
        print()

        try:
            # 下載照片
            await download_photos(photos)

            # 更新 venues.json
            await update_venues_with_photos(photos)

        except Exception as e:
            print(f"錯誤: {e}")
            import traceback
            traceback.print_exc()
    else:
        print()
        print("[建議] 請檢查:")
        print("  1. ticc_photos_page.png - 查看頁面截圖")
        print("  2. 手動訪問網址確認照片位置")


if __name__ == '__main__':
    asyncio.run(main())
