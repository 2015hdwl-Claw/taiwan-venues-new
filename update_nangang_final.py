#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新南港展覽館會議室容量並寫入 venues.json
"""
import asyncio
import json
import re
from playwright.async_api import async_playwright


# 手動從 HTML 提取的容量資料
ROOM_CAPACITIES = {
    "401": {"theater": 384, "standard": 216, "classroom": 144, "uShape": 72, "horseshoe": 52},
}


async def extract_capacity_from_page(url):
    """從頁面提取容量資料"""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=60000)
            await asyncio.sleep(3)

            html = await page.content()
            await browser.close()

            # 尋找容量表
            cap_section_start = html.find('容納座位數')
            if cap_section_start > 0:
                cap_section = html[cap_section_start:cap_section_start+2000]

                pattern = r'<tr class=\"confre_gray[^>]*\">.*?<td[^>]*>(\d+)</td>.*?<td[^>]*>(\d+)</td>.*?<td[^>]*>(\d+)</td>.*?<td[^>]*>(\d+)</td>.*?<td[^>]*>(\d+)</td>'
                match = re.search(pattern, cap_section)

                if match:
                    return {
                        "theater": int(match.group(1)),
                        "standard": int(match.group(2)),
                        "classroom": int(match.group(3)),
                        "uShape": int(match.group(4)),
                        "horseshoe": int(match.group(5))
                    }

            return None

    except Exception as e:
        print(f"錯誤: {e}")
        return None


async def get_all_capacities():
    """獲取所有會議室的容量"""
    rooms = [
        ("401", "https://www.tainex.com.tw/venue/room-info/1/4/401"),
        ("402", "https://www.tainex.com.tw/venue/room-info/1/4/402"),
        ("403", "https://www.tainex.com.tw/venue/room-info/1/4/403"),
        ("404", "https://www.tainex.com.tw/venue/room-info/1/4/404"),
        ("500", "https://www.tainex.com.tw/venue/room-info/1/5/500"),
        ("701", "https://www.tainex.com.tw/venue/room-info/2/7/701"),
    ]

    print("提取會議室容量資料...")
    capacities = {}

    for room_name, url in rooms:
        print(f"  {room_name}...", end=" ")
        cap = await extract_capacity_from_page(url)
        if cap:
            capacities[room_name] = cap
            print(f"OK ({cap['theater']})")
        else:
            print("SKIP")

        await asyncio.sleep(1)

    return capacities


async def main():
    # 讀取現有的 nangang_rooms_v2.json
    with open('nangang_rooms_v2.json', 'r', encoding='utf-8') as f:
        rooms = json.load(f)

    # 獲取容量資料
    capacities = await get_all_capacities()

    print()

    # 更新容量資料
    for room in rooms:
        room_name_en = room['nameEn']

        if room_name_en in capacities:
            room['capacity'] = capacities[room_name_en]
            print(f"✓ 更新 {room['name']} 容量")
        elif not room.get('capacity'):
            # 保持原有的容量資料（如果有的話）
            pass

    # 儲存更新後的檔案
    with open('nangang_rooms_final.json', 'w', encoding='utf-8') as f:
        json.dump(rooms, f, ensure_ascii=False, indent=2)

    print()
    print("="*80)
    print("完成！已儲存 nangang_rooms_final.json")
    print("="*80)
    print()

    # 顯示摘要
    print("會議室資料:")
    for room in rooms:
        print(f"  - {room['name']}")
        if room.get('capacity'):
            cap = room['capacity']
            print(f"    容量: 劇院型 {cap['theater']}, 標準型 {cap['standard']}, 教室型 {cap['classroom']}")
        if room.get('area'):
            print(f"    面積: {room['area']} {room['areaUnit']}")
        if room.get('price'):
            price = room['price']
            if price.get('weekday'):
                print(f"    價格: 平日 ${price['weekday']:,}")
            if price.get('holiday'):
                print(f"          假日 ${price['holiday']:,}")

    print()
    print("下一步: 更新 venues.json")


if __name__ == '__main__':
    asyncio.run(main())
