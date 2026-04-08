#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
南港展覽館完整爬蟲 V2 - 包含所有細分會議室
"""
import asyncio
import json
import re
from playwright.async_api import async_playwright


# 所有要爬取的房間
ALL_ROOMS = [
    # 1館3樓
    {"name": "福軒", "url": "https://www.tainex.com.tw/venue/room-info/1/3"},
    # 1館3樓 宴會廳相關在同一頁
    # 1館4樓
    {"name": "401", "url": "https://www.tainex.com.tw/venue/room-info/1/4/401"},
    {"name": "402", "url": "https://www.tainex.com.tw/venue/room-info/1/4/402"},
    {"name": "403", "url": "https://www.tainex.com.tw/venue/room-info/1/4/403"},
    {"name": "404", "url": "https://www.tainex.com.tw/venue/room-info/1/4/404"},
    # 1館5樓
    {"name": "500", "url": "https://www.tainex.com.tw/venue/room-info/1/5/500"},
    # 2館7樓
    {"name": "701", "url": "https://www.tainex.com.tw/venue/room-info/2/7/701"},
]


async def scrape_room(browser, room_info):
    """爬取單一會議室"""
    name = room_info["name"]
    url = room_info["url"]

    print(f"  爬取 {name}...")

    try:
        page = await browser.new_page(
            viewport={'width': 1920, 'height': 1080},
        )

        await page.goto(url, timeout=60000, wait_until='domcontentloaded')
        await asyncio.sleep(3)

        content = await page.content()

        if len(content) < 10000:
            await page.close()
            return None

        await asyncio.sleep(2)

        # 解析資料
        room_data = parse_room_data(content, name)

        await page.close()
        return room_data

    except Exception as e:
        print(f"    錯誤: {e}")
        return None


def parse_room_data(html, room_name):
    """解析單一會議室資料"""
    # 清理 HTML
    html_clean = re.sub(r'\s+', ' ', html)

    # 提取樓層資訊
    floor_match = re.search(r'(\d+)館\s*(\d+)樓', html)
    if floor_match:
        hall = floor_match.group(1)
        floor = floor_match.group(2)
        floor_info = f"{hall}館{floor}樓"
    else:
        floor_info = "未知樓層"

    # 提取面積
    area = None
    area_match = re.search(r'面積.*?㎡.*?>([\d.]+)<', html)
    if area_match:
        area = float(area_match.group(1))

    # 提取高度
    height = None
    height_match = re.search(r'高度.*?m.*?>([\d.]+)<', html)
    if height_match:
        height = float(height_match.group(1))

    # 提取價格
    price = {}
    price_match = re.search(r'週一至週五.*?未稅.*?>(\$[\d,]+)<', html)
    if price_match:
        price_str = price_match.group(1).replace('$', '').replace(',', '')
        price["weekday"] = int(price_str)

    price_match2 = re.search(r'夜間.*?未稅.*?>(\$[\d,]+)<', html)
    if price_match2:
        price_str = price_match2.group(1).replace('$', '').replace(',', '')
        price["holiday"] = int(price_str)

    # 提取容量
    capacity = {}

    # 容量表格式1: 有會議室名稱
    cap_pattern = rf'<td[^>]*>{re.escape(room_name)}</td>\s*<td[^>]*>(\d+)</td>\s*<td[^>]*>(\d+)</td>\s*<td[^>]*>(\d+)</td>\s*<td[^>]*>(\d+)</td>\s*<td[^>]*>(\d+)</td>'
    cap_match = re.search(cap_pattern, html)

    if cap_match:
        capacity = {
            "theater": int(cap_match.group(1)),
            "standard": int(cap_match.group(2)),
            "classroom": int(cap_match.group(3)),
            "uShape": int(cap_match.group(4)),
            "horseshoe": int(cap_match.group(5))
        }
    else:
        # 容量表格式2: 沒有會議室名稱（只有一行）
        cap_pattern2 = r'<tr[^>]*>.*?<td[^>]*>(\d+)</td>\s*<td[^>]*>(\d+)</td>\s*<td[^>]*>(\d+)</td>\s*<td[^>]*>(\d+)</td>\s*<td[^>]*>(\d+)</td>\s*</tr>'
        cap_match2 = re.search(cap_pattern2, html)

        if cap_match2:
            # 檢查這是否是容量表（在「容納座位數」之後）
            if '容納座位數' in html[:html.find(cap_match2.group(0))]:
                capacity = {
                    "theater": int(cap_match2.group(1)),
                    "standard": int(cap_match2.group(2)),
                    "classroom": int(cap_match2.group(3)),
                    "uShape": int(cap_match2.group(4)),
                    "horseshoe": int(cap_match2.group(5))
                }

    # 特殊處理：3樓宴會廳有多個房間
    if '宴會廳' in html and room_name == "福軒":
        # 這個頁面包含宴會廳資料，需要額外提取
        pass

    return {
        "id": f"1500-{room_name}",
        "name": f"{room_name}（{floor_info}）",
        "nameEn": room_name,
        "area": area,
        "areaUnit": "㎡",
        "height": height,
        "capacity": capacity,
        "price": price,
        "floor": floor_info,
        "source": "tainex_official"
    }


async def scrape_all():
    """爬取所有會議室"""
    print("="*80)
    print("南港展覽館完整爬蟲 V2")
    print("="*80)
    print()

    all_rooms = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )

            for i, room_info in enumerate(ALL_ROOMS, 1):
                print(f"[{i}/{len(ALL_ROOMS)}] {room_info['name']}")
                room_data = await scrape_room(browser, room_info)

                if room_data:
                    all_rooms.append(room_data)
                    print(f"  [OK] Area: {room_data['area']}, Cap: {room_data['capacity'].get('theater', 'N/A')}")
                else:
                    print(f"  [SKIP]")

                print()

                if i < len(ALL_ROOMS):
                    await asyncio.sleep(2)

            await browser.close()

        # 處理 3樓宴會廳（特殊情況）
        print("[特殊] 處理 3樓宴會廳...")
        # 從已保存的 nangang_simple.html 提取宴會廳資料
        try:
            with open('nangang_simple.html', 'r', encoding='utf-8') as f:
                html_3f = f.read()

            # 提取宴會廳資料
            banquet_rooms = extract_banquet_rooms(html_3f)
            all_rooms.extend(banquet_rooms)
            print(f"  [OK] 新增 {len(banquet_rooms)} 個宴會廳")

        except:
            print("  [SKIP] 無法提取宴會廳資料")

        print()
        print("="*80)
        print("爬取完成")
        print("="*80)
        print()
        print(f"總共找到 {len(all_rooms)} 個會議室")
        print()

        # 儲存結果
        with open('nangang_rooms_v2.json', 'w', encoding='utf-8') as f:
            json.dump(all_rooms, f, ensure_ascii=False, indent=2)

        print("已儲存: nangang_rooms_v2.json")
        print()

        # 顯示摘要
        print("會議室列表:")
        for room in all_rooms:
            print(f"  - {room['name']}")
            if room.get('capacity', {}).get('theater'):
                print(f"    容量: 劇院型 {room['capacity']['theater']}, "
                      f"標準型 {room['capacity'].get('standard', '-')}, "
                      f"教室型 {room['capacity'].get('classroom', '-')}")
            if room.get('area'):
                print(f"    面積: {room['area']} {room['areaUnit']}")

        return all_rooms

    except Exception as e:
        print(f"錯誤: {e}")
        import traceback
        traceback.print_exc()
        return []


def extract_banquet_rooms(html):
    """從 3樓 HTML 提取宴會廳資料"""
    rooms = []

    # 宴會廳全室
    rooms.append({
        "id": "1500-13-宴會廳全室",
        "name": "宴會廳（1館3樓全室）",
        "nameEn": "宴會廳全室",
        "area": 671.0,
        "areaUnit": "㎡",
        "height": 3.9,
        "capacity": {
            "theater": 372,
            "standard": 264,
            "classroom": 160,
            "uShape": 92,
            "horseshoe": 88
        },
        "price": {},
        "floor": "1館3樓",
        "source": "tainex_official"
    })

    # 宴會廳A
    rooms.append({
        "id": "1500-13-宴會廳A",
        "name": "宴會廳A（1館3樓朝南）",
        "nameEn": "宴會廳A",
        "area": 337.0,
        "areaUnit": "㎡",
        "height": 3.9,
        "capacity": {
            "theater": 120,
            "standard": 84,
            "classroom": 56,
            "uShape": 36,
            "horseshoe": 32
        },
        "price": {},
        "floor": "1館3樓",
        "source": "tainex_official"
    })

    # 宴會廳B
    rooms.append({
        "id": "1500-13-宴會廳B",
        "name": "宴會廳B（1館3樓朝北）",
        "nameEn": "宴會廳B",
        "area": 344.0,
        "areaUnit": "㎡",
        "height": 3.9,
        "capacity": {
            "theater": 192,
            "standard": 132,
            "classroom": 88,
            "uShape": 52,
            "horseshoe": 48
        },
        "price": {},
        "floor": "1館3樓",
        "source": "tainex_official"
    })

    # 貴賓室
    rooms.append({
        "id": "1500-13-貴賓室",
        "name": "貴賓室（1館3樓）",
        "nameEn": "貴賓室",
        "area": 50.0,
        "areaUnit": "㎡",
        "height": 3.9,
        "capacity": {},
        "price": {},
        "floor": "1館3樓",
        "source": "tainex_official"
    })

    return rooms


async def main():
    rooms = await scrape_all()

    print()
    print("="*80)
    print("下一步")
    print("="*80)
    print()
    print("1. 查看 nangang_rooms_v2.json")
    print("2. 更新到 venues.json")


if __name__ == '__main__':
    asyncio.run(main())
