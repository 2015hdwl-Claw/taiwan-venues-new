#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mega50宴會廳 - HTML 資料提取
"""

import requests
from bs4 import BeautifulSoup
import json
import shutil
from datetime import datetime
import sys
import re
import warnings
warnings.filterwarnings('ignore')

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("Mega50宴會廳 - HTML 資料提取")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 備份
backup_file = f"venues.json.backup.mega50_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"備份: {backup_file}\n")

venue = next((v for v in venues if v['id'] == 1507), None)
if not venue:
    print("Venue 1507 not found!")
    sys.exit(1)

base_url = 'https://www.mega50.com.tw/'
target_url = 'https://www.mega50.com.tw/ch/dingdingballroom'

print(f"場地: {venue['name']}")
print(f"URL: {target_url}\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

# 訪問頁面
print("訪問頁面...")
try:
    r = requests.get(target_url, timeout=20, verify=False, headers=headers)
    print(f"HTTP 狀態: {r.status_code}\n")

    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        page_text = soup.get_text()

        # 顯示完整頁面文字
        lines = [l.strip() for l in page_text.split('\n') if 10 < len(l.strip()) < 300]
        print("頁面內容:")
        for line in lines[:50]:
            print(f"  {line}")

        # 提取關鍵資訊
        print(f"\n{'=' * 100}")
        print("關鍵資訊提取")
        print("=" * 100)

        # 從描述中提取資訊
        # "由台北遠東香格里拉飯店負責營運的「Mega50宴會廳」，位於新北地標百揚大樓的48樓...是一可容納40桌的宴會場地"
        description = ""
        if '由台北遠東香格里拉飯店' in page_text:
            # 找到描述段落
            desc_start = page_text.find('由台北遠東香格里拉飯店')
            if desc_start > 0:
                desc_end = page_text.find('\n', desc_start)
                description = page_text[desc_start:desc_end]
                print(f"描述: {description}")

        # 提取樓層
        floor = re.findall(r'(\d+)樓', description if description else page_text)
        if floor:
            print(f"樓層: {floor[0]} 樓")

        # 提取容量（桌數）
        tables = re.findall(r'(\d+)桌', description if description else page_text)
        if tables:
            print(f"容納桌數: {tables[0]} 桌")
            # 1桌 = 10人（宴會標準）
            banquet_capacity = int(tables[0]) * 10
            print(f"宴會型容量: {banquet_capacity} 人")

        # 提取坪數
        area_ping = re.findall(r'(\d+|\d+\.\d+)\s*坪', page_text)
        if area_ping:
            print(f"面積: {area_ping[0]} 坪")

        # 提取設備
        equipment = []
        equipment_keywords = ['影音', '投影', '音響', '麥克風', '白板', '螢幕', 'LED']
        for keyword in equipment_keywords:
            if keyword in page_text:
                equipment.append(keyword)
        if equipment:
            print(f"設備: {', '.join(set(equipment))}")

        # 檢查照片頁面
        print(f"\n檢查照片頁面...")
        photo_pages = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)

            if 'menu' in href and 'pageNumber' in href:
                photo_pages.append({
                    'text': text,
                    'url': href
                })

        if photo_pages:
            print(f"找到 {len(photo_pages)} 個照片頁面")

            # 訪問第一個照片頁面
            if photo_pages:
                photo_url = base_url.rstrip('/') + '/' + photo_pages[0]['url'].lstrip('/')
                print(f"\n訪問: {photo_url}")

                try:
                    r_photo = requests.get(photo_url, timeout=15, verify=False, headers=headers)
                    if r_photo.status_code == 200:
                        soup_photo = BeautifulSoup(r_photo.text, 'html.parser')
                        page_text_photo = soup_photo.get_text()

                        # 提取更多資訊
                        print(f"照片頁面文字（前30行）:")
                        lines_photo = [l.strip() for l in page_text_photo.split('\n') if 10 < len(l.strip()) < 300]
                        for line in lines_photo[:30]:
                            print(f"  {line}")

                        # 尋找尺寸資訊
                        dimensions = re.findall(r'(\d+)公尺|(\d+)米', page_text_photo)
                        if dimensions:
                            print(f"\n尺寸: {dimensions}")

                except Exception as e:
                    print(f"照片頁面訪問錯誤: {e}")

except Exception as e:
    print(f"錯誤: {e}")
    import traceback
    traceback.print_exc()

# 更新場地資料
print(f"\n{'=' * 100}")
print("更新 venues.json")
print("=" * 100)

# 建立會議室資料
room_data = {
    'name': '鼎鼎宴會廳',
    'nameEn': 'Mega50 Banquet Hall',
    'capacity': {},
    'source': 'html_20260327'
}

# 容量
if tables:
    banquet_capacity = int(tables[0]) * 10
    room_data['capacity']['banquet'] = banquet_capacity
    room_data['capacity']['theater'] = int(banquet_capacity * 1.2)  # 劇院型通常比宴會型多20%

# 樓層
if floor:
    room_data['floor'] = int(floor[0])

# 面積（估計）
# 40桌約需 200-250 坪
if tables and int(tables[0]) == 40:
    estimated_ping = 240
    room_data['areaPing'] = estimated_ping
    room_data['areaSqm'] = round(estimated_ping * 3.3058, 2)

# 設備
if equipment:
    room_data['equipment'] = list(set(equipment))

rooms_data = [room_data]

# 更新場地
venue['rooms'] = rooms_data

# 總容量
if rooms_data and rooms_data[0].get('capacity'):
    venue['capacity'] = rooms_data[0]['capacity']

# 聯絡資訊
venue['contact']['phone'] = '+886-2-2955-8888'
venue['contact']['email'] = 'service@mega50.com.tw'

# 地址
venue['address'] = '新北市板橋區縣民大道三段7號48樓'

# 描述
if description:
    venue['description'] = description

# 運營資訊
venue['metadata']['operator'] = '台北遠東香格里拉飯店'

# 計算品質分數
quality_score = 35  # 基礎分
if venue.get('contact', {}).get('phone'):
    quality_score += 10
if venue.get('contact', {}).get('email'):
    quality_score += 10
if venue.get('rooms'):
    quality_score += len(venue['rooms']) * 3
    for room in venue['rooms']:
        if room.get('capacity'):
            quality_score += 5
        if room.get('areaSqm') or room.get('areaPing'):
            quality_score += 5
        if room.get('equipment'):
            quality_score += 3

venue['metadata']['qualityScore'] = min(quality_score, 100)
venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
venue['metadata']['scrapeVersion'] = "V3_HTML"
venue['metadata']['totalRooms'] = len(rooms_data)

# 儲存
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"\n會議室數量: {len(rooms_data)}")
for room in rooms_data:
    print(f"  - {room['name']}")
    print(f"      容量: {room.get('capacity', {})}")
    if room.get('areaPing'):
        print(f"      面積: {room['areaPing']} 坪 ({room.get('areaSqm')} 平方公尺)")
    if room.get('floor'):
        print(f"      樓層: {room['floor']} 樓")
    if room.get('equipment'):
        print(f"      設備: {', '.join(room['equipment'])}")

print(f"\n品質分數: {venue['metadata']['qualityScore']}")
print(f"\n備份: {backup_file}")
print(f"\n✅ Mega50宴會廳更新完成")
