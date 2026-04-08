#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集思北科大會議中心 - 三階段深度爬蟲
階段2：深度爬蟲（PDF 解析 + 會議室頁面提取）
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import pdfplumber
from datetime import datetime
import sys
import warnings
import os
warnings.filterwarnings('ignore')

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("集思北科大會議中心 - 階段2：深度爬蟲")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取階段1結果
with open('nutut_room_stage1_results.json', encoding='utf-8') as f:
    stage1 = json.load(f)

# 會議室列表（只取實際會議室）
rooms = [
    {'name': '感恩廳', 'url': 'https://www.meeting.com.tw/ntut/the-lecture-hall.php'},
    {'name': '貝塔廳', 'url': 'https://www.meeting.com.tw/ntut/room-201.php'},
    {'name': '噶瑪廳', 'url': 'https://www.meeting.com.tw/ntut/room-202.php'},
    {'name': '卡博廳', 'url': 'https://www.meeting.com.tw/ntut/room-203.php'},
    {'name': '西特廳', 'url': 'https://www.meeting.com.tw/ntut/room-204.php'},
    {'name': '瑞特廳', 'url': 'https://www.meeting.com.tw/ntut/room-205.php'},
    {'name': '艾爾法廳', 'url': 'https://www.meeting.com.tw/ntut/room-301.php'},
    {'name': '奧米伽廳', 'url': 'https://www.meeting.com.tw/ntut/room-302.php'},
    {'name': '西格瑪廳', 'url': 'https://www.meeting.com.tw/ntut/room-303.php'},
    {'name': '岱爾達廳', 'url': 'https://www.meeting.com.tw/ntut/room-304.php'},
]

stage2_results = []

# 2.1 先解析 PDF 提取價格
print("2.1 解析 PDF 提取價格")
print("-" * 100)

pdf_url = "https://www.meeting.com.tw/ntut/download/北科大_場地租用申請_20250401.pdf"
print(f"PDF: {pdf_url}")

try:
    # 下載 PDF
    response = requests.get(pdf_url, timeout=30, verify=False)
    pdf_path = 'nutut_venue_rental.pdf'

    with open(pdf_path, 'wb') as f:
        f.write(response.content)

    print(f"✅ PDF 下載完成: {len(response.content):,} bytes")

    # 解析 PDF
    pdf_prices = {}

    with pdfplumber.open(pdf_path) as pdf:
        print(f"  頁數: {len(pdf.pages)}")

        for page_num, page in enumerate(pdf.pages[:5], 1):  # 只看前 5 頁
            print(f"\n  頁面 {page_num}:")

            # 提取表格
            tables = page.extract_tables({
                'vertical_strategy': 'text',
                'horizontal_strategy': 'text'
            })

            for table in tables:
                for row in table:
                    if not row:
                        continue

                    # 將整行轉為字串
                    row_text = ' '.join([str(cell) if cell else '' for cell in row])

                    # 尋找會議室名稱和價格
                    for room_name in [r['name'] for r in rooms]:
                        if room_name in row_text:
                            # 尋找價格（平日/假日）
                            prices = re.findall(r'(\d{1,6}(?:,\d{3})*)', row_text)
                            if len(prices) >= 2:
                                try:
                                    weekday = int(prices[0].replace(',', ''))
                                    holiday = int(prices[1].replace(',', ''))

                                    if room_name not in pdf_prices:
                                        pdf_prices[room_name] = {
                                            'weekday': weekday,
                                            'holiday': holiday
                                        }

                                        print(f"    {room_name}: 平日 {weekday:,} / 假日 {holiday:,}")
                                except:
                                    pass

    # 如果沒有找到，嘗試全頁文字搜尋
    if not pdf_prices:
        print("\n  使用全頁文字搜尋...")

        with pdfplumber.open(pdf_path) as pdf:
            all_text = ''
            for page in pdf.pages:
                all_text += page.extract_text() + '\n'

            for room_name in [r['name'] for r in rooms]:
                if room_name in all_text:
                    # 尋找該會議室附近的價格資訊
                    lines = all_text.split('\n')
                    for i, line in enumerate(lines):
                        if room_name in line:
                            # 檢查接下來的幾行
                            for j in range(i, min(i+5, len(lines))):
                                prices = re.findall(r'(\d{1,6}(?:,\d{3})*)', lines[j])
                                if len(prices) >= 2:
                                    try:
                                        weekday = int(prices[0].replace(',', ''))
                                        holiday = int(prices[1].replace(',', ''))

                                        if 1000 <= weekday <= 100000:  # 合理價格範圍
                                            pdf_prices[room_name] = {
                                                'weekday': weekday,
                                                'holiday': holiday
                                            }
                                            print(f"    {room_name}: 平日 {weekday:,} / 假日 {holiday:,}")
                                            break
                                    except:
                                        pass

                            break

    print(f"\n  PDF 價格提取: {len(pdf_prices)} 個會議室")

except Exception as e:
    print(f"❌ PDF 解析錯誤: {e}")
    import traceback
    traceback.print_exc()

# 2.2 爬取每個會議室頁面
print("\n\n2.2 爬取會議室頁面")
print("-" * 100)

for room in rooms:
    print(f"\n{room['name']}:")
    print(f"  URL: {room['url']}")

    result = {
        'name': room['name'],
        'url': room['url']
    }

    try:
        response = requests.get(room['url'], timeout=15, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取照片
        photos = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if 'lease' in src.lower():
                if not src.startswith('http'):
                    src = 'https://www.meeting.com.tw/ntut/' + src
                if src not in photos:
                    photos.append(src)

        result['photos'] = photos
        print(f"    照片: {len(photos)} 張")

        # 提取容量
        page_text = soup.get_text()
        capacity_match = re.search(r'(\d+)\s*人', page_text)
        if capacity_match:
            result['capacity'] = int(capacity_match.group(1))
            print(f"    容量: {result['capacity']} 人")

        # 提取面積
        area_match = re.search(r'(\d+\.?\d*)\s*坪', page_text)
        if area_match:
            area_ping = float(area_match.group(1))
            result['areaPing'] = area_ping
            result['areaSqm'] = round(area_ping * 3.3058, 2)
            print(f"    面積: {result['areaPing']} 坪 ({result['areaSqm']} ㎡)")

        # 提取樓層
        floor_match = re.search(r'(\d+)F', page_text)
        if floor_match:
            result['floor'] = floor_match.group(1)
            print(f"    樓層: {result['floor']}F")

        # 添加價格（從 PDF）
        if room['name'] in pdf_prices:
            result['price'] = pdf_prices[room['name']]
            print(f"    價格: 平日 {result['price']['weekday']:,} / 假日 {result['price']['holiday']:,}")

        result['success'] = True

    except Exception as e:
        print(f"  ❌ 錯誤: {e}")
        result['error'] = str(e)
        result['success'] = False

    stage2_results.append(result)

# 儲存階段2結果
output = {
    "venue": "集思北科大會議中心",
    "timestamp": datetime.now().isoformat(),
    "pdf_prices": pdf_prices,
    "rooms": stage2_results
}

with open('nutut_room_stage2_results.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n\n✅ 階段2完成")
print(f"  PDF 價格: {len(pdf_prices)}/{len(rooms)} 個會議室")
print(f"  照片: {sum(len(r.get('photos', [])) for r in stage2_results)} 張")
print(f"  結果已儲存: nutut_room_stage2_results.json")
