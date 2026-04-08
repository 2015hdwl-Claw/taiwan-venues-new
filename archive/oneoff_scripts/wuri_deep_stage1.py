#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集思台中新烏日會議中心會議室詳情頁 - 三階段深度爬蟲
階段1：技術檢測
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 新烏日會議室詳情頁列表
rooms = [
    {'name': '瓦特廳', 'url': 'https://www.meeting.com.tw/xinwuri/room-301.php'},
    {'name': '巴本廳', 'url': 'https://www.meeting.com.tw/xinwuri/room-303.php'},
    {'name': '富蘭克林廳', 'url': 'https://www.meeting.com.tw/xinwuri/room-401.php'},
    {'name': '史蒂文生廳', 'url': 'https://www.meeting.com.tw/xinwuri/room-402.php'},
]

print("=" * 100)
print("集思台中新烏日會議中心 - 會議室詳情頁階段1：技術檢測")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

stage1_results = []

for room in rooms:
    print(f"\n{'=' * 100}")
    print(f"檢測: {room['name']}")
    print('=' * 100)
    print(f"URL: {room['url']}\n")

    result = {
        'name': room['name'],
        'url': room['url']
    }

    # 1.1 HTTP 狀態碼
    print("1.1 HTTP 狀態碼檢測...")
    try:
        response = requests.get(room['url'], timeout=15, verify=False)
        http_status = response.status_code
        result['http_status'] = http_status
        print(f"  HTTP 狀態: {http_status}")

        if http_status != 200:
            result['error'] = f"HTTP {http_status}"
            stage1_results.append(result)
            continue

        # 1.2 Content-Type
        print("\n1.2 Content-Type 檢測...")
        content_type = response.headers.get('Content-Type', '')
        result['content_type'] = content_type
        print(f"  Content-Type: {content_type}")

        # 1.3 頁面結構分析
        print("\n1.3 頁面結構分析...")
        soup = BeautifulSoup(response.text, 'html.parser')

        # 檢查是否有 JavaScript 動態內容
        scripts = soup.find_all('script')
        result['script_count'] = len(scripts)
        print(f"  Script 標籤: {len(scripts)} 個")

        # 檢查圖片數量
        images = soup.find_all('img')
        result['image_count'] = len(images)
        print(f"  IMG 標籤: {len(images)} 個")

        # 1.4 照片分析
        print("\n1.4 照片分析...")
        room_images = []
        for img in images:
            src = img.get('src', '')
            if 'lease' in src.lower() and 'logo' not in src.lower():
                room_images.append(src)

        result['room_images'] = len(room_images)
        print(f"  會議室照片: {len(room_images)} 張")

        if room_images:
            print(f"  照片範例:")
            for img in room_images[:3]:
                print(f"    - {img}")

        # 1.5 關鍵資訊檢測
        print("\n1.5 關鍵資訊檢測...")
        page_text = soup.get_text()

        # 價格
        price_match = re.search(r'每時段.*?(\d{1,6})\s*元', page_text)
        result['has_price'] = price_match is not None
        if price_match:
            print(f"  價格: 有 ({price_match.group(0)})")
        else:
            print(f"  價格: 未找到")

        # 容量
        capacity_match = re.search(r'容量.*?(\d+)\s*人', page_text)
        result['has_capacity'] = capacity_match is not None
        if capacity_match:
            print(f"  容量: 有 ({capacity_match.group(0)})")
        else:
            print(f"  容量: 未找到")

        # 面積
        area_match = re.search(r'(\d+\.?\d*)\s*坪', page_text)
        result['has_area'] = area_match is not None
        if area_match:
            print(f"  面積: 有 ({area_match.group(0)})")
        else:
            print(f"  面積: 未找到")

        # 樓層
        floor_match = re.search(r'(\d+)F', page_text)
        result['has_floor'] = floor_match is not None
        if floor_match:
            print(f"  樓層: 有 ({floor_match.group(0)})")
        else:
            print(f"  樓層: 未找到")

        # 1.6 反爬蟲檢測
        print("\n1.6 反爬蟲檢測...")
        server = response.headers.get('Server', '')
        result['server'] = server
        print(f"  Server: {server}")

        cookies = len(response.cookies)
        result['cookies'] = cookies
        print(f"  Cookies: {cookies} 個")

        stage1_results.append(result)

    except Exception as e:
        print(f"  ❌ 錯誤: {e}")
        result['error'] = str(e)
        stage1_results.append(result)

# 儲存結果
output_file = 'wuri_room_stage1_results.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'venue': '集思台中新烏日會議中心',
        'timestamp': datetime.now().isoformat(),
        'rooms': stage1_results
    }, f, ensure_ascii=False, indent=2)

print(f"\n\n✅ 階段1結果已儲存: {output_file}")

# 總結
print("\n" + "=" * 100)
print("階段1 總結")
print("=" * 100)

success_count = sum(1 for r in stage1_results if r.get('http_status') == 200)
total_images = sum(r.get('room_images', 0) for r in stage1_results)

print(f"成功檢測: {success_count}/{len(rooms)} 個會議室")
print(f"總照片數: {total_images} 張")

with_price = sum(1 for r in stage1_results if r.get('has_price'))
with_capacity = sum(1 for r in stage1_results if r.get('has_capacity'))
with_area = sum(1 for r in stage1_results if r.get('has_area'))

print(f"\n資料覆蓋:")
print(f"  價格: {with_price}/{len(rooms)}")
print(f"  容量: {with_capacity}/{len(rooms)}")
print(f"  面積: {with_area}/{len(rooms)}")

print("\n建議:")
if success_count == len(rooms):
    print("  ✅ 所有頁面都可訪問，建議進入階段2深度爬取")
else:
    print("  ⚠️  部分頁面無法訪問，建議檢查網路或URL")

print("\n" + "=" * 100)
print("✅ 階段1完成")
print("=" * 100)
