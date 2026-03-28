#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集思會議中心通用爬蟲
"""
import asyncio
import json
import re
from playwright.async_api import async_playwright
from datetime import datetime


# 所有沒有資料的集思場地
GIS_VENUES = [
    {"id": 1494, "name": "集思交通部會議中心(MOTC)", "url": "https://www.meeting.com.tw/motc/"},
    {"id": 1495, "name": "集思北科技會議中心(Tech)", "url": "https://www.meeting.com.tw/ntut/"},
    {"id": 1496, "name": "集思台師大会議中心(HSPH)", "url": "https://www.meeting.com.tw/hsp/"},
    {"id": 1497, "name": "集思中國醫會議中心(TC)", "url": "https://www.meeting.com.tw/tc/"},
    {"id": 1498, "name": "集思烏日會議中心(WURI)", "url": "https://www.meeting.com.tw/wuri/"},
    {"id": 1499, "name": "集思高雄會議中心(KHH)", "url": "https://www.meeting.com.tw/khh/"},
]


async def discover_rooms(venue_info):
    """Discover all rooms in venue"""
    url = venue_info["url"]
    venue_id = venue_info["id"]
    name = venue_info["name"]

    print(f"[Discover] {name}")
    print(f"  URL: {url}")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            await page.goto(url, timeout=60000, wait_until='domcontentloaded')
            await asyncio.sleep(3)

            content = await page.content()

            if len(content) < 10000:
                print(f"  [SKIP] Content too short")
                await browser.close()
                return []

            # Find room links
            room_links = []

            # Pattern 1: room-xxx.php
            pattern1 = r'href="(room-\d+\.php)"'
            matches1 = re.findall(pattern1, content)
            room_links.extend([(match, "room") for match in matches1])

            # Pattern 2: plenary-hall.php
            pattern2 = r'href="(plenary-hall\.php)"'
            matches2 = re.findall(pattern2, content)
            room_links.extend([(match, "plenary") for match in matches2])

            # Pattern 3: any link with room
            pattern3 = r'href="([^"]*room[^"]*\.php)"'
            matches3 = re.findall(pattern3, content)
            for match in matches3:
                if match not in [link[0] for link in room_links]:
                    room_links.append((match, "other"))

            # Remove duplicates
            seen = set()
            unique_links = []
            for link, link_type in room_links:
                if link not in seen:
                    seen.add(link)
                    unique_links.append((link, link_type))

            print(f"  [OK] Found {len(unique_links)} room links")

            # Save home HTML
            filename = f"gis_{venue_id}_home.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)

            await browser.close()

            return unique_links

    except Exception as e:
        print(f"  [ERROR] {e}")
        return []


async def scrape_room_page(venue_info, room_link):
    """爬取單一會議室頁面"""
    venue_id = venue_info["id"]
    base_url = venue_info["url"]
    room_filename = room_link[0]

    # 構建完整 URL
    if room_filename.startswith('http'):
        room_url = room_filename
    else:
        # 從基礎 URL 提取路徑
        base_path = '/'.join(base_url.split('/')[:-1])
        room_url = f"{base_path}/{room_filename}"

    print(f"    爬取: {room_filename}")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            await page.goto(room_url, timeout=60000, wait_until='domcontentloaded')
            await asyncio.sleep(3)

            content = await page.content()

            if len(content) < 5000:
                print(f"      [SKIP] 內容太短")
                await browser.close()
                return None

            # 解析會議室資料
            room_data = parse_gis_room(content, room_filename, venue_info)

            await browser.close()

            return room_data

    except Exception as e:
        print(f"      [ERROR] {e}")
        return None


def parse_gis_room(html, filename, venue_info):
    """解析集思會議室資料"""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, 'html.parser')

    # 提取會議室名稱
    # 通常在標題或 h1, h2 中
    title = soup.find('title')
    if title:
        title_text = title.get_text().strip()
        # 移除後綴
        room_name = title_text.replace(' - 集思會議中心', '').replace(' | 集思會議中心', '').strip()
    else:
        # 從 filename 推斷
        if 'plenary-hall' in filename:
            room_name = "國際會議廳"
        elif 'room-' in filename:
            room_num = filename.replace('room-', '').replace('.php', '')
            room_name = f"{room_num}會議室"
        else:
            room_name = filename.replace('.php', '').strip()

    # 提取容量
    capacity = {}
    page_text = soup.get_text()

    # 尋找容量資料
    # 常見格式: "容納 XX 人" 或 "容量 XX"
    cap_pattern = r'容納?\s*容量?\s*(\d+)\s*人'
    cap_match = re.search(cap_pattern, page_text)

    if cap_match:
        capacity['standard'] = int(cap_match.group(1))

    # 尋找面積
    area = None
    area_pattern = r'(\d+(?:\.\d+)?)\s*坪'
    area_match = re.search(area_pattern, page_text)

    if area_match:
        area = float(area_match.group(1))

    # 尋找尺寸
    dimensions = None
    dim_pattern = r'(\d+(?:\.\d+)?)\s*[米m]\s*[x×]\s*(\d+(?:\.\d+)?)\s*[米m]'
    dim_match = re.search(dim_pattern, page_text)

    if dim_match:
        dimensions = f"{dim_match.group(1)}m x {dim_match.group(2)}m"

    # 尋找樓層
    floor = None
    floor_pattern = r'(\d+)?[樓Ff層]'
    floor_match = re.search(floor_pattern, page_text)

    if floor_match:
        floor = f"{floor_match.group(1)}樓"

    # 生成 ID
    venue_id = venue_info["id"]
    room_id_base = filename.replace('.php', '').replace('-', '_')
    room_id = f"{venue_id}-{room_id_base}"

    return {
        "id": room_id,
        "name": room_name,
        "nameEn": room_name,
        "area": area,
        "areaUnit": "坪" if area else None,
        "dimensions": dimensions,
        "floor": floor,
        "capacity": capacity,
        "source": "gis_official"
    }


async def scrape_venue(venue_info):
    """爬取單一場地的所有會議室"""
    print()
    print("="*80)
    print(f"爬取: {venue_info['name']}")
    print("="*80)

    # 發現會議室
    room_links = await discover_rooms(venue_info)

    if not room_links:
        print(f"  [SKIP] 未找到會議室")
        return []

    print(f"  [OK] 找到 {len(room_links)} 個會議室")

    # 爬取每個會議室
    rooms = []

    for room_link, link_type in room_links:
        room_data = await scrape_room_page(venue_info, (room_link, link_type))

        if room_data:
            rooms.append(room_data)
            print(f"      [OK] {room_data['name']} - {room_data.get('capacity', {}).get('standard', 'N/A')} 人")

        await asyncio.sleep(2)

    return rooms


async def main():
    print("="*80)
    print("GIS meeting centers batch scraping")
    print("="*80)
    print()

    all_results = []

    for i, venue_info in enumerate(GIS_VENUES, 1):
        print(f"[{i}/{len(GIS_VENUES)}] Venue ID: {venue_info['id']}")

        try:
            rooms = await scrape_venue(venue_info)

            if rooms:
                all_results.append({
                    'venue_id': venue_info['id'],
                    'venue_name': venue_info['name'],
                    'rooms': rooms,
                    'total': len(rooms)
                })

            await asyncio.sleep(3)

        except Exception as e:
            print(f"  [ERROR] {e}")
            import traceback
            traceback.print_exc()

    # 儲存結果
    print()
    print("="*80)
    print("爬取完成")
    print("="*80)
    print()

    with open('gis_scrape_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print("已儲存: gis_scrape_results.json")
    print()

    # 顯示摘要
    print("爬取摘要:")
    print()

    total_rooms = 0
    for result in all_results:
        venue_name = result['venue_name']
        count = result['total']
        total_rooms += count

        print(f"  {venue_name}: {count} 個會議室")

        for room in result['rooms']:
            print(f"    - {room['name']} ({room.get('capacity', {}).get('standard', 'N/A')} 人)")

    print()
    print(f"總計: {total_rooms} 個會議室")

    print()
    print("下一步: 更新到 venues.json")


if __name__ == '__main__':
    asyncio.run(main())
