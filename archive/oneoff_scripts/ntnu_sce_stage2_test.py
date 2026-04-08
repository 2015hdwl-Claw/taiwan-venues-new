#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
師大進修 - 階段2：測試連結並深度爬取
基於階段1技術檢測結果（發現場地租借頁面）
"""

import requests
from bs4 import BeautifulSoup
import json
import sys
import re
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("師大進修推廣學院 - 階段2：測試連結並深度爬取")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 場地租借頁面（從階段1發現）
space_url = "https://www.sce.ntnu.edu.tw/home/space/"

print("訪問場地租借頁面...")
session = requests.Session()
response = session.get(space_url, timeout=15, verify=False)
print(f"HTTP 狀態: {response.status_code}")
print(f"Cookies: {len(session.cookies)} 個")

if response.status_code != 200:
    print(f"❌ 頁面訪問失敗")
    sys.exit(1)

soup = BeautifulSoup(response.text, 'html.parser')

# 儲存頁面
page_file = f"ntnu_sce_space_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
with open(page_file, 'w', encoding='utf-8') as f:
    f.write(str(soup.prettify()))
print(f"✅ 頁面已儲存: {page_file}\n")

# 分析頁面
print("=" * 100)
print("分析頁面內容")
print("=" * 100)

page_text = soup.get_text()

# 尋找容量、面積、樓層資訊
capacity_pattern = r'(\d+)\s*[人名]'
capacities = re.findall(capacity_pattern, page_text)

area_pattern = r'(\d+\.?\d*)\s*[坪平米]'
areas = re.findall(area_pattern, page_text)

floor_pattern = r'(\d+[F樓層])|([B\d]|[地下]\d*[層樓])'
floors = re.findall(floor_pattern, page_text)

print(f"\n找到的資訊:")
if capacities:
    capacities_int = [int(c) for c in capacities]
    print(f"  容量: {len(capacities)} 處 ({min(capacities_int)}-{max(capacities_int)} 人)")
if areas:
    areas_float = [float(a) for a in areas]
    print(f"  面積: {len(areas)} 處 ({min(areas_float)}-{max(areas_float)} 坪)")
if floors:
    unique_floors = list(set([f[0] if f[0] else f[1] for f in floors]))
    print(f"  樓層: {len(unique_floors)} 種 ({', '.join(unique_floors[:5])})")

# 尋找表格
tables = soup.find_all('table')
print(f"\n表格數量: {len(tables)} 個")

if tables:
    print("\n分析表格...")
    for i, table in enumerate(tables[:3], 1):
        table_text = table.get_text()
        rows = table.find_all('tr')

        print(f"\n表格 {i}:")
        print(f"  行數: {len(rows)}")
        print(f"  文字量: {len(table_text)} 字元")

        # 檢查是否包含場地資訊
        has_venue_info = any(kw in table_text for kw in
                            ['會議室', '教室', '演講', '容量', '坪', '人'])
        print(f"  包含場地資訊: {'是' if has_venue_info else '否'}")

        if has_venue_info:
            # 提取表格資料
            table_data = []
            for row in rows:
                cells = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
                if cells:
                    table_data.append(cells)

            if table_data:
                print(f"  資料行數: {len(table_data)}")

                # 儲存表格資料
                table_file = f"ntnu_sce_table{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(table_file, 'w', encoding='utf-8') as f:
                    json.dump(table_data, f, ensure_ascii=False, indent=2)
                print(f"  ✅ 表格資料已儲存: {table_file}")

# 尋找 PDF 連結
pdf_links = []
for a in soup.find_all('a', href=True):
    href = a['href']
    if href.lower().endswith('.pdf') or 'pdf' in href.lower():
        if not href.startswith('http'):
            if href.startswith('/'):
                href = 'https://www.sce.ntnu.edu.tw' + href
            else:
                href = 'https://www.sce.ntnu.edu.tw/' + href

        text = a.get_text(strip=True)
        pdf_links.append({'text': text, 'url': href})

if pdf_links:
    print(f"\n找到 PDF: {len(pdf_links)} 個")
    for i, pdf in enumerate(pdf_links, 1):
        print(f"  {i}. {pdf['text'][:50]}")
        print(f"     {pdf['url']}")

    # 儲存 PDF 連結
    pdf_file = f"ntnu_sce_pdfs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(pdf_file, 'w', encoding='utf-8') as f:
        json.dump(pdf_links, f, ensure_ascii=False, indent=2)
    print(f"\n✅ PDF 連結已儲存: {pdf_file}")

# 尋找所有連結
all_links = []
for a in soup.find_all('a', href=True):
    href = a['href']
    text = a.get_text(strip=True)
    if len(text) > 1 and len(text) < 100:
        all_links.append({'text': text, 'href': href})

print(f"\n總連結數: {len(all_links)}")

# 尋找可能包含會議室資料的連結
venue_links = [l for l in all_links if any(kw in l['text'] for kw in
             ['會議室', '教室', '演講', '場地', '租借'])]
print(f"會議室相關連結: {len(venue_links)}")

if venue_links:
    print("\n前 5 個:")
    for link in venue_links[:5]:
        print(f"  - {link['text']}")
        print(f"    {link['href']}")

# 結果
result = {
    'venue': '師大進修推廣學院',
    'venue_id': 1493,
    'url': space_url,
    'http_status': response.status_code,
    'cookies': len(session.cookies),
    'capacities': capacities[:10] if capacities else [],
    'areas': areas[:10] if areas else [],
    'floors': list(set([f[0] if f[0] else f[1] for f in floors])) if floors else [],
    'tables_count': len(tables),
    'total_links': len(all_links),
    'venue_links': len(venue_links),
    'pdf_links': pdf_links,
    'has_data': len(capacities) > 0 or len(areas) > 0
}

result_file = f'ntnu_sce_stage2_result_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
with open(result_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"\n✅ 結果已儲存: {result_file}")

# 階段3總結
print("\n" + "=" * 100)
print("師大進修 - 階段2 總結")
print("=" * 100)

print("\n【技術檢測】")
print(f"  HTTP 狀態: {response.status_code}")
print(f"  需要 Cookies: 是 ({len(session.cookies)} 個)")

print("\n【資料發現】")
print(f"  容量資訊: {len(capacities)} 處")
print(f"  面積資訊: {len(areas)} 處")
print(f"  樓層資訊: {len(set([f[0] if f[0] else f[1] for f in floors]))} 種")
print(f"  表格數量: {len(tables)} 個")
print(f"  PDF 連結: {len(pdf_links)} 個")

print("\n【下一步建議】")
if result['has_data']:
    print("  ✅ 頁面包含場地資料")
    print("  建議：")
    print("    1. 分析表格資料提取會議室列表")
    if pdf_links:
        print(f"    2. 下載並解析 {len(pdf_links)} 個 PDF 檔案")
    print("    3. 建立完整 30 欄位資料")
else:
    print("  ⚠️  頁面資料不明確")
    print("  建議：手動檢查 HTML 檔案，尋找隱藏的場地資料")

print("\n" + "=" * 100)
print("✅ 師大進修階段2測試完成")
print("=" * 100)
