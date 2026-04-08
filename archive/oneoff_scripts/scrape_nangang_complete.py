#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整爬取南港展覽館所有會議室資料
"""
import asyncio
import json
import re
from playwright.async_api import async_playwright
from datetime import datetime


# 所有要爬取的頁面
PAGES = [
    {"hall": "1", "floor": "3", "url": "https://www.tainex.com.tw/venue/room-info/1/3"},
    {"hall": "1", "floor": "4", "url": "https://www.tainex.com.tw/venue/room-info/1/4/401"},
    {"hall": "1", "floor": "5", "url": "https://www.tainex.com.tw/venue/room-info/1/5/500"},
    {"hall": "2", "floor": "7", "url": "https://www.tainex.com.tw/venue/room-info/2/7/701"},
]


async def scrape_page(browser, page_info):
    """爬取單一頁面"""
    url = page_info["url"]
    hall = page_info["hall"]
    floor = page_info["floor"]

    print(f"  爬取 {hall}館 {floor}樓...")

    try:
        page = await browser.new_page(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        await page.goto(url, timeout=60000, wait_until='domcontentloaded')
        await asyncio.sleep(3)

        content = await page.content()

        if len(content) < 10000 or 'blocked' in content.lower():
            await page.close()
            return None

        await asyncio.sleep(2)

        # 解析會議室資料
        rooms = parse_rooms_from_html(content, hall, floor)

        await page.close()
        return rooms

    except Exception as e:
        print(f"    錯誤: {e}")
        return None


def parse_rooms_from_html(html, hall, floor):
    """從 HTML 解析會議室資料"""
    rooms = []

    # 移除換行和多余空格
    html_clean = re.sub(r'\s+', ' ', html)

    # 尋找會議室名稱和資料表格
    # 模式1: 福軒類型（單一房間）
    pattern1 = r'<td[^>]*>會議室</td>\s*<td[^>]*>([^<]+)</td>'
    match1 = re.search(pattern1, html)

    if match1:
        room_name = match1.group(1).strip()

        # 尋找面積
        area_match = re.search(r'<td[^>]*>面積.*?</td>\s*<td[^>]*>([\d.]+)</td>', html)
        area = float(area_match.group(1)) if area_match else None

        # 尋找高度
        height_match = re.search(r'<td[^>]*>高度.*?</td>\s*<td[^>]*>([\d.]+)</td>', html)
        height = float(height_match.group(1)) if height_match else None

        # 尋找容量
        capacity = {}
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

        # 尋找價格
        price = {}
        price_pattern = r'週一至週五.*?未稅.*?>(\$[\d,]+)</'
        price_match = re.search(price_pattern, html)
        if price_match:
            price_str = price_match.group(1).replace('$', '').replace(',', '')
            price["weekday"] = int(price_str)

        price_pattern2 = r'夜間.*?未稅.*?>(\$[\d,]+)</'
        price_match2 = re.search(price_pattern2, html)
        if price_match2:
            price_str = price_match2.group(1).replace('$', '').replace(',', '')
            price["holiday"] = int(price_str)

        rooms.append({
            "id": f"1500-{hall}{floor}-{room_name}",
            "name": f"{room_name}（{hall}館{floor}樓）",
            "nameEn": room_name,
            "area": area,
            "areaUnit": "㎡",
            "height": height,
            "capacity": capacity,
            "price": price,
            "floor": f"{hall}館{floor}樓",
            "source": "tainex_official"
        })

    # 模式2: 宴會廳類型（多個房間）
    # 尋找宴會廳、宴會廳A、宴會廳B、貴賓室
    banquet_rooms = ['宴會廳全室', '宴會廳A', '宴會廳B', '貴賓室']

    # 先判斷這個頁面是否有宴會廳
    if '宴會廳' in html:
        # 提取宴會廳的容量資料
        # 模式: 宴會廳全室、宴會廳A、宴會廳B

        # 尋找容量表
        cap_rows = re.findall(r'<tr[^>]*>\s*<td[^>]*>(宴會廳[全室AB]*|\w+室)</td>\s*<td[^>]*>(\d+)</td>\s*<td[^>]*>(\d+)</td>\s*<td[^>]*>(\d+)</td>\s*<td[^>]*>(\d+)</td>\s*<td[^>]*>(\d+)</td>\s*</tr>', html)

        room_areas = {}
        area_matches = re.findall(r'<td[^>]*>面積.*?</td>.*?<td[^>]*>(\w+)</td>\s*<td[^>]*>([\d.]+)</td>', html)

        for area_match in area_matches:
            room_name = area_match[0]
            area_value = float(area_match[1])
            room_areas[room_name] = area_value

        for row in cap_rows:
            room_name = row[0].strip()
            theater = int(row[1])
            standard = int(row[2])
            classroom = int(row[3])
            uShape = int(row[4])
            horseshoe = int(row[5])

            # 決定完整名稱
            if '全室' in room_name:
                full_name = f"宴會廳（{hall}館{floor}樓全室）"
            elif 'A' in room_name or '朝南' in room_name:
                full_name = f"宴會廳A（{hall}館{floor}樓）"
            elif 'B' in room_name or '朝北' in room_name:
                full_name = f"宴會廳B（{hall}館{floor}樓）"
            else:
                full_name = f"{room_name}（{hall}館{floor}樓）"

            # 取得面積
            area_key = None
            for key in room_areas.keys():
                if key.replace('宴會廳', '') == room_name.replace('宴會廳', '').replace('全室', '') or \
                   key == room_name or \
                   (room_name == '宴會廳全室' and key == '宴會廳'):
                    area_key = key
                    break

            area = room_areas.get(area_key)

            # 處理價格（宴會廳特殊處理）
            price = {}

            rooms.append({
                "id": f"1500-{hall}{floor}-{room_name}",
                "name": full_name,
                "nameEn": room_name,
                "area": area,
                "areaUnit": "㎡",
                "height": 3.9,
                "capacity": {
                    "theater": theater,
                    "standard": standard,
                    "classroom": classroom,
                    "uShape": uShape,
                    "horseshoe": horseshoe
                },
                "price": price,
                "floor": f"{hall}館{floor}樓",
                "source": "tainex_official"
            })

    print(f"    找到 {len(rooms)} 個會議室")
    return rooms


async def scrape_all():
    """爬取所有頁面"""
    print("="*80)
    print("南港展覽館完整爬蟲")
    print("="*80)
    print()

    all_rooms = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )

            for page_info in PAGES:
                print(f"[{page_info['hall']}館 {page_info['floor']}樓]")
                rooms = await scrape_page(browser, page_info)

                if rooms:
                    all_rooms.extend(rooms)
                    print(f"  [OK] {len(rooms)} 個會議室")
                else:
                    print(f"  [SKIP] 無資料")

                print()

                await asyncio.sleep(2)

            await browser.close()

        # 輸出結果
        print("="*80)
        print("爬取完成")
        print("="*80)
        print()
        print(f"總共找到 {len(all_rooms)} 個會議室")
        print()

        # 儲存結果
        with open('nangang_rooms.json', 'w', encoding='utf-8') as f:
            json.dump(all_rooms, f, ensure_ascii=False, indent=2)

        print("已儲存: nangang_rooms.json")
        print()

        # 顯示摘要
        print("會議室列表:")
        for room in all_rooms:
            print(f"  - {room['name']}")
            if room.get('capacity'):
                cap = room['capacity']
                print(f"    容量: 劇院型 {cap.get('theater', '-')}, "
                      f"標準型 {cap.get('standard', '-')}, "
                      f"教室型 {cap.get('classroom', '-')}")
            if room.get('area'):
                print(f"    面積: {room['area']} {room['areaUnit']}")

        return all_rooms

    except Exception as e:
        print(f"錯誤: {e}")
        import traceback
        traceback.print_exc()
        return []


async def main():
    rooms = await scrape_all()

    print()
    print("="*80)
    print("下一步")
    print("="*80)
    print()
    print("1. 查看 nangang_rooms.json")
    print("2. 更新到 venues.json")
    print("3. 驗證資料完整性")


if __name__ == '__main__':
    asyncio.run(main())
