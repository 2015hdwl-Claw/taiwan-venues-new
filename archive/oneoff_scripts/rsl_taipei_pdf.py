#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
瓢山林台北中和飯店 - PDF 提取
"""

import requests
from bs4 import BeautifulSoup
import json
import shutil
from datetime import datetime
import sys
import re
import pdfplumber
import warnings
warnings.filterwarnings('ignore')

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("瓢山林台北中和飯店 - PDF 提取")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 備份
backup_file = f"venues.json.backup.rsl_taipei_pdf_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"備份: {backup_file}\n")

venue = next((v for v in venues if v['id'] == 1506), None)
if not venue:
    print("Venue 1506 not found!")
    sys.exit(1)

pdf_url = 'https://taipei.rslhotel.com/upload/download_files/twl_download_25d10_j9n2aheprr.pdf'

print(f"PDF URL: {pdf_url}\n")

# 下載 PDF
print("下載 PDF...")
try:
    response = requests.get(pdf_url, timeout=30, verify=False)
    print(f"HTTP 狀態: {response.status_code}")

    if response.status_code != 200:
        print("❌ 無法下載 PDF")
        sys.exit(1)

    # 保存到臨時檔案
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(response.content)
        pdf_path = tmp_file.name

    print(f"PDF 大小: {len(response.content):,} bytes")
    print(f"儲存: {pdf_path}\n")

except Exception as e:
    print(f"❌ 下載失敗: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 解析 PDF
print("=" * 100)
print("解析 PDF")
print("=" * 100)

try:
    with pdfplumber.open(pdf_path) as pdf:
        print(f"總頁數: {len(pdf.pages)}\n")

        all_text = ""
        all_tables = []

        for i, page in enumerate(pdf.pages):
            print(f"頁面 {i+1}/{len(pdf.pages)}")

            # 提取文字
            text = page.extract_text()
            if text:
                all_text += text + "\n"
                print(f"  文字長度: {len(text)}")

            # 提取表格
            tables = page.extract_tables()
            if tables:
                for j, table in enumerate(tables):
                    all_tables.append({
                        'page': i+1,
                        'table': table,
                        'rows': len(table),
                        'cols': len(table[0]) if table else 0
                    })
                print(f"  表格數量: {len(tables)}")

        # 顯示完整文字
        print(f"\n{'=' * 100}")
        print("PDF 完整文字")
        print("=" * 100)
        print(all_text)

        # 顯示表格資料
        if all_tables:
            print(f"\n{'=' * 100}")
            print("PDF 表格資料")
            print("=" * 100)

            for table_info in all_tables:
                print(f"\n頁面 {table_info['page']}, 表格 {table_info['rows']}x{table_info['cols']}:")
                table = table_info['table']
                for row_idx, row in enumerate(table):
                    print(f"  Row {row_idx}: {row}")

        # 提取會議室資訊
        print(f"\n{'=' * 100}")
        print("關鍵資訊提取")
        print("=" * 100)

        # 提取會議室名稱
        room_patterns = [
            r'([^\s]{2,10}[廳室房])(?:\s|[,，.。、\n])',
            r'(宴會廳|貴賓廳|會議室)'
        ]

        rooms_found = []
        for pattern in room_patterns:
            matches = re.findall(pattern, all_text)
            if matches:
                rooms_found.extend(matches)

        if rooms_found:
            unique_rooms = list(set(rooms_found))
            print(f"會議室: {unique_rooms}")

        # 提取容量
        capacities = re.findall(r'(\d+)\s*[人名桌者席位]', all_text)
        if capacities:
            caps = [int(c) for c in capacities if 5 <= int(c) <= 2000]
            print(f"容量: {caps[:20]}")

        # 提取面積
        areas = re.findall(r'(\d+|\d+\.\d+)\s*([坪平方公尺㎡㎡²])', all_text)
        if areas:
            print(f"面積: {areas[:20]}")

        # 提取價格
        prices = re.findall(r'(\d+,?\d*)\s*元', all_text)
        if prices:
            print(f"價格: {prices[:20]}")

except Exception as e:
    print(f"❌ PDF 解析失敗: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 更新場地資料
print(f"\n{'=' * 100}")
print("更新 venues.json")
print("=" * 100)

# 根據 PDF 表格資料建立完整會議室清單
rooms_data = []

# 從頁面3的表格提取完整資料
for table_info in all_tables:
    if table_info['page'] == 3 and table_info['cols'] >= 10:
        table = table_info['table']
        # 跳過標題列
        for row in table[2:]:
            if not row or not row[0]:
                continue

            room_name = row[0].strip()
            if not room_name or '場地' in room_name:
                continue

            # 提取面積資料（坪）
            area_ping = None
            if row[1]:
                try:
                    area_ping = int(str(row[1]).strip().replace(',', ''))
                except:
                    pass

            # 提取面積資料（平方公尺）
            area_sqm = None
            if row[2]:
                try:
                    area_sqm = int(str(row[2]).strip().replace(',', ''))
                except:
                    pass

            # 提取高度（公尺）
            height_m = None
            if row[4]:
                try:
                    height_m = float(str(row[4]).strip())
                except:
                    pass

            # 提取容量
            capacity = {}
            if row[6]:  # Banquet
                try:
                    capacity['banquet'] = int(str(row[6]).strip().replace(',', '').replace('-', '0'))
                except:
                    pass
            if row[7]:  # Reception
                try:
                    capacity['reception'] = int(str(row[7]).strip().replace(',', '').replace('-', '0'))
                except:
                    pass
            if row[8]:  # Classroom
                try:
                    capacity['classroom'] = int(str(row[8]).strip().replace(',', '').replace('-', '0'))
                except:
                    pass
            if row[9]:  # Theater
                try:
                    capacity['theater'] = int(str(row[9]).strip().replace(',', '').replace('-', '0'))
                except:
                    pass
            if row[10]:  # Hollow Square
                try:
                    capacity['hollowSquare'] = int(str(row[10]).strip().replace(',', '').replace('-', '0'))
                except:
                    pass

            # 建立會議室物件
            room_obj = {
                'name': room_name,
                'capacity': capacity,
                'source': 'pdf_20260327'
            }

            if area_ping:
                room_obj['areaPing'] = area_ping
            if area_sqm:
                room_obj['areaSqm'] = area_sqm
            if height_m:
                room_obj['dimensions'] = {'height': height_m}

            rooms_data.append(room_obj)

# 從頁面3的租金表格提取價格
price_table = None
for table_info in all_tables:
    if table_info['page'] == 3 and table_info['cols'] == 4:
        price_table = table_info['table']
        break

if price_table and rooms_data:
    # 對照會議室名稱添加價格
    for i, row in enumerate(price_table[1:]):  # 跳過標題
        if not row or not row[0]:
            continue

        room_name = row[0].strip().replace('\n', ' ')
        if i-1 < len(rooms_data):
            # 尋找對應的會議室
            for room in rooms_data:
                if room_name in room['name'] or room['name'] in room_name:
                    # 提取價格
                    price = {}
                    if row[1]:  # 08:00-12:00 or 13:00-17:00
                        try:
                            price['halfDay'] = int(str(row[1]).strip().replace(',', ''))
                        except:
                            pass
                    if row[2]:  # 08:00-17:00
                        try:
                            price['fullDay'] = int(str(row[2]).strip().replace(',', ''))
                        except:
                            pass
                    if row[3]:  # 17:00-22:00
                        try:
                            price['evening'] = int(str(row[3]).strip().replace(',', ''))
                        except:
                            pass

                    if price:
                        room['price'] = price
                    break

# 更新場地資料
venue['rooms'] = rooms_data
venue['capacity'] = {
    'theater': sum([r.get('capacity', {}).get('theater', 0) for r in rooms_data])
}
venue['contact']['phone'] = '+886-2-2226-6688'
venue['contact']['email'] = 'rsl.tp@rslhotels.com.tw'
venue['verified'] = False

# 計算品質分數
quality_score = 35  # 基礎分
if venue.get('contact', {}).get('phone'):
    quality_score += 10
if venue.get('contact', {}).get('email'):
    quality_score += 10
if venue.get('rooms'):
    quality_score += len(venue['rooms']) * 2
    for room in venue['rooms']:
        if room.get('capacity'):
            quality_score += 5
        if room.get('areaSqm') or room.get('areaPing'):
            quality_score += 5

venue['metadata']['qualityScore'] = min(quality_score, 100)
venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
venue['metadata']['scrapeVersion'] = "V3_PDF"
venue['metadata']['pdfUrl'] = pdf_url
venue['metadata']['totalRooms'] = len(rooms_data)

# 儲存
with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print(f"\n會議室數量: {len(rooms_data)}")
for room in rooms_data:
    print(f"  - {room['name']}: 容量 {room.get('capacity', {}).get('theater', 'N/A')}")

print(f"\n品質分數: {venue['metadata']['qualityScore']}")
print(f"\n備份: {backup_file}")
print(f"\n✅ 瓢山林台北中和飯店更新完成")
