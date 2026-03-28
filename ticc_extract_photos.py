#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TICC - 提取場地照片
"""

import requests
from bs4 import BeautifulSoup
import json
import sys
from datetime import datetime
from urllib.parse import urljoin

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("TICC - 提取場地照片")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 場地照片 URL
venue_photo_url = "https://www.ticc.com.tw/wSite/sp?xdUrl=/wSite/ap/lp_VenueIntroduction.jsp&ctNode=321&CtUnit=98&BaseDSD=7&mp=1"

print(f"訪問場地照片頁面...")
print(f"URL: {venue_photo_url}\n")

try:
    session = requests.Session()
    response = session.get(venue_photo_url, timeout=15, verify=False)
    print(f"HTTP 狀態: {response.status_code}")

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # 儲存頁面
        page_file = f"ticc_venue_photos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(page_file, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        print(f"✅ 頁面已儲存: {page_file}\n")

        # 尋找所有圖片
        all_images = []

        # 方法1: 尋找 <img> 標籤
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src:
                # 轉換為完整 URL
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = urljoin('https://www.ticc.com.tw/', src)

                alt = img.get('alt', '')

                # 過濾掉小圖示和裝飾圖
                if any(skip in src.lower() for skip in ['icon', 'logo', 'btn', 'arrow', 'bg']):
                    continue

                all_images.append({
                    'url': src,
                    'alt': alt,
                    'source': 'img_tag'
                })

        # 方法2: 尋找背景圖片 (CSS)
        for div in soup.find_all(['div', 'section'], style=True):
            style = div.get('style', '')
            if 'background-image' in style:
                import re
                match = re.search(r'url\(["\']?([^"\'()]+)["\']?\)', style)
                if match:
                    bg_url = match.group(1)
                    if bg_url.startswith('//'):
                        bg_url = 'https:' + bg_url
                    elif bg_url.startswith('/'):
                        bg_url = urljoin('https://www.ticc.com.tw/', bg_url)

                    all_images.append({
                        'url': bg_url,
                        'alt': div.get('class', ['background'])[0] if div.get('class') else 'background',
                        'source': 'css_background'
                    })

        # 去重
        seen_urls = set()
        unique_images = []
        for img in all_images:
            if img['url'] not in seen_urls:
                seen_urls.add(img['url'])
                unique_images.append(img)

        print(f"找到圖片: {len(unique_images)} 個\n")

        # 分類顯示
        venue_images = [img for img in unique_images if any(kw in img['url'].lower() for kw in ['venue', 'hall', 'room', 'meeting', '會議', '廳', '室'])]
        other_images = [img for img in unique_images if img not in venue_images]

        print(f"場地相關圖片: {len(venue_images)} 個")
        for img in venue_images[:10]:
            print(f"  - {img['url'][:80]}...")
            if img['alt']:
                print(f"    Alt: {img['alt']}")

        if len(other_images) > 0:
            print(f"\n其他圖片: {len(other_images)} 個")
            for img in other_images[:5]:
                print(f"  - {img['url'][:80]}...")

        # 儲存結果
        result = {
            'venue': 'TICC',
            'venue_id': 1448,
            'url': venue_photo_url,
            'total_images': len(unique_images),
            'venue_images': len(venue_images),
            'images': unique_images,
            'timestamp': datetime.now().isoformat()
        }

        result_file = f'ticc_photos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 照片資料已儲存: {result_file}")

        # 更新 venues.json
        print("\n" + "=" * 100)
        print("更新 venues.json")
        print("=" * 100)

        with open('venues.json', encoding='utf-8') as f:
            venues = json.load(f)

        # 找到 TICC
        for venue in venues:
            if venue.get('id') == 1448:
                # 更新 photos
                venue['photos'] = [
                    {
                        'url': img['url'],
                        'alt': img['alt'],
                        'source': img['source'],
                        'added_at': datetime.now().isoformat()
                    }
                    for img in venue_images
                ]

                # 更新 metadata
                if 'metadata' not in venue:
                    venue['metadata'] = {}

                venue['metadata'].update({
                    'total_photos': len(venue_images),
                    'photos_updated_at': datetime.now().isoformat(),
                    'photos_source': venue_photo_url,
                    'completeness': venue['metadata'].get('completeness', {})
                })

                venue['metadata']['completeness']['images'] = True

                print(f"✅ 更新 {len(venue_images)} 張場地照片")
                break

        # 儲存
        with open('venues.json', 'w', encoding='utf-8') as f:
            json.dump(venues, f, ensure_ascii=False, indent=2)

        print("✅ venues.json 已更新")

    else:
        print(f"❌ 頁面訪問失敗: {response.status_code}")

except Exception as e:
    print(f"❌ 錯誤: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 100)
print("✅ TICC 場地照片提取完成")
print("=" * 100)
