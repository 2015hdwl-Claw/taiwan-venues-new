#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mega50宴會廳 - PDF 提取
"""

import requests
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
print("Mega50宴會廳 - PDF 提取")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取 venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# 備份
backup_file = f"venues.json.backup.mega50_pdf_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"備份: {backup_file}\n")

venue = next((v for v in venues if v['id'] == 1507), None)
if not venue:
    print("Venue 1507 not found!")
    sys.exit(1)

# 下載活力會議專案PDF
pdf_url = 'https://www.mega50.com.tw/mega4850-mgr/fileman/users/restaurantImage/2026活力會議專案.pdf'

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

        # 提取關鍵資訊
        print(f"\n{'=' * 100}")
        print("關鍵資訊提取")
        print("=" * 100)

        # 提取會議室名稱
        room_patterns = [
            r'([^\s]{2,10}[廳室房])(?:\s|[,，.。、\n])',
            r'(宴會廳|會議室|鼎鼎)'
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
            # 清理價格
            clean_prices = []
            for p in prices:
                p_clean = p.replace(',', '').replace('NT', '').replace('$', '').strip()
                try:
                    if int(p_clean) > 100:  # 過濾掉小額
                        clean_prices.append(int(p_clean))
                except:
                    pass
            print(f"價格: {clean_prices[:20]}")

        # 提取樓層
        floor = re.findall(r'(\d+)樓', all_text)
        if floor:
            print(f"樓層: {floor}")

except Exception as e:
    print(f"❌ PDF 解析失敗: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 更新場地資料
print(f"\n{'=' * 100}")
print("更新 venues.json")
print("=" * 100)

# 根據提取的資料建立會議室清單
rooms_data = []

# 根據文字資料建立會議室
main_room = {
    'name': '鼎鼎宴會廳',
    'nameEn': 'Mega50 Banquet Hall',
    'capacity': {},
    'source': 'pdf_20260327'
}

# 容量分析 - 從文字中提取
if '40桌' in all_text or '40 桌' in all_text:
    main_room['capacity']['banquet'] = 400  # 40桌 = 400人

# 從capacity列表中尋找合理容量
for cap in capacities:
    cap_int = int(cap)
    if 200 <= cap_int <= 600:
        main_room['capacity']['theater'] = cap_int
        break

# 提取樓層
if floor:
    main_room['floor'] = int(floor[0])

rooms_data.append(main_room)

# 計算場地總面積（如果找到）
if areas:
    for area_val, area_unit in areas:
        if '坪' in area_unit:
            try:
                area_val_float = float(area_val)
                if 100 <= area_val_float <= 1000:
                    main_room['areaPing'] = area_val_float
                    # 轉換為平方公尺
                    main_room['areaSqm'] = round(area_val_float * 3.3058, 2)
                    break
            except:
                pass

# 提取價格資訊
price_data = {}
for price in prices:
    price_clean = price.replace(',', '').replace('NT', '').replace('$', '').strip()
    try:
        price_int = int(price_clean)
        if price_int >= 10000:  # 場地租金通常 > 10000
            # 根據金額判斷是半天或全天
            if price_int < 30000:
                price_data['halfDay'] = price_int
            elif price_int < 50000:
                price_data['fullDay'] = price_int
            else:
                price_data['fullDay'] = price_int
            break
    except:
        pass

if price_data:
    main_room['price'] = price_data

# 更新場地資料
venue['rooms'] = rooms_data

# 總容量
total_capacity = 0
if rooms_data:
    for room in rooms_data:
        if room.get('capacity'):
            # 使用劇院型或宴會型作為主要容量
            total_capacity = max(total_capacity,
                               room['capacity'].get('theater', 0),
                               room['capacity'].get('banquet', 0))

venue['capacity'] = {'theater': total_capacity} if total_capacity else {}

# 聯絡資訊
venue['contact']['phone'] = '+886-2-2955-8888'
venue['contact']['email'] = 'service@mega50.com.tw'

# 地址
venue['address'] = '新北市板橋區縣民大道三段7號48樓'

# 其他資訊
venue['verified'] = False

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
        if room.get('price'):
            quality_score += 10

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
    print(f"  - {room['name']}:")
    print(f"      容量: {room.get('capacity', {})}")
    if room.get('areaPing'):
        print(f"      面積: {room['areaPing']} 坪 ({room.get('areaSqm')} 平方公尺)")
    if room.get('floor'):
        print(f"      樓層: {room['floor']} 樓")
    if room.get('price'):
        print(f"      價格: {room['price']}")

print(f"\n品質分數: {venue['metadata']['qualityScore']}")
print(f"\n備份: {backup_file}")
print(f"\n✅ Mega50宴會廳更新完成")
