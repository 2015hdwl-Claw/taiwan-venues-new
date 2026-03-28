#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集思台中新烏日會議中心 - 三階段完整流程
階段2：深度爬蟲（基於階段1結果）
"""

import requests
from bs4 import BeautifulSoup
import json
import sys
import re
from datetime import datetime
from urllib.parse import urljoin

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

venue_id = 1498
venue_name = "集思台中新烏日會議中心(WURI)"

print("=" * 100)
print(f"{venue_name} - 階段2：深度爬蟲")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 讀取階段1結果
stage1_files = [f for f in __import__('os').listdir('.') if f.startswith(f'{venue_name}_stage1_') and f.endswith('.json')]
if not stage1_files:
    print(f"❌ 找不到階段1結果檔案")
    sys.exit(1)

with open(stage1_files[-1], encoding='utf-8') as f:
    stage1 = json.load(f)

base_url = stage1['url']
print(f"基礎 URL: {base_url}\n")

# 根據階段1結果：動態渲染，但先嘗試直接爬取
# 如果失敗，則建議使用 Selenium

session = requests.Session()

# 2.1 第一級：主頁分析
print("2.1 主頁分析...")
response = session.get(base_url, timeout=15, verify=False)
soup = BeautifulSoup(response.text, 'html.parser')

# 儲存主頁
homepage_file = f'{venue_name}_homepage_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
with open(homepage_file, 'w', encoding='utf-8') as f:
    f.write(str(soup.prettify()))
print(f"✅ 主頁已儲存: {homepage_file}")

# 尋找會議室相關連結
meeting_links = []
for a in soup.find_all('a', href=True):
    href = a['href']
    text = a.get_text(strip=True)

    if any(kw in text.lower() or kw in href.lower() for kw in
           ['會議', '場地', '空間', '場地租借', '會議室', 'room', 'space', 'venue', 'meeting']):
        # 轉換為完整 URL
        if not href.startswith('http'):
            if href.startswith('/'):
                href = urljoin(base_url, href)
            else:
                href = urljoin(base_url, '/' + href)

        meeting_links.append({
            'text': text,
            'href': href
        })

print(f"找到會議相關連結: {len(meeting_links)} 個")

# 去重
seen_urls = set()
unique_links = []
for link in meeting_links:
    if link['href'] not in seen_urls:
        seen_urls.add(link['href'])
        unique_links.append(link)

print(f"去重後: {len(unique_links)} 個")

# 顯示前 10 個
for i, link in enumerate(unique_links[:10], 1):
    print(f"  {i}. {link['text'][:60]}")
    print(f"     {link['href']}")

# 2.2 第二級：測試會議室連結
print("\n2.2 測試會議室連結...")
working_links = []
failed_links = []

for i, link in enumerate(unique_links[:15], 1):  # 限制測試前15個
    print(f"\n測試 {i}/{min(15, len(unique_links))}: {link['text'][:50]}")
    print(f"  URL: {link['href']}")

    try:
        test_response = session.get(link['href'], timeout=10, verify=False)
        print(f"  HTTP: {test_response.status_code}")

        if test_response.status_code == 200:
            test_soup = BeautifulSoup(test_response.text, 'html.parser')
            page_text = test_soup.get_text()

            # 檢查是否包含場地資訊
            has_data = any(kw in page_text for kw in ['坪', '人', '容量', '面積', '租金', '費用', '會議室', '場地'])

            if has_data:
                print(f"  ✅ 包含場地資料")
                working_links.append({**link, 'has_data': True})

                # 儲存前 5 個有資料的頁面
                if len([l for l in working_links if l.get('has_data')]) <= 5:
                    page_file = f'{venue_name}_page{i}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
                    with open(page_file, 'w', encoding='utf-8') as f:
                        f.write(str(test_soup.prettify()))
                    print(f"  💾 已儲存: {page_file}")
            else:
                print(f"  ⚠️  可能不是場地頁面")
                working_links.append({**link, 'has_data': False})
        else:
            print(f"  ❌ 不可用")
            failed_links.append({**link, 'status': test_response.status_code})

    except Exception as e:
        print(f"  ❌ 錯誤: {e}")
        failed_links.append({**link, 'error': str(e)})

    # 延遲
    import time
    time.sleep(0.5)

# 2.3 第三級：提取場地資料
print("\n" + "=" * 100)
print("2.3 提取場地資料")
print("=" * 100)

all_rooms = []

# 從所有頁面提取會議室資料
processed_urls = [link['href'] for link in working_links if link.get('has_data')]

print(f"\n有資料的頁面: {len(processed_urls)} 個")

for url in processed_urls:
    print(f"\n處理頁面: {url}")

    try:
        response = session.get(url, timeout=10, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()

        # 尋找會議室名稱
        # 模式：可能是標題或特殊格式
        room_patterns = [
            r'(\d+F樓\s*[^\n]{1,20})',  # 1F 會議室
            r'([^\n]{2,20}(?:會議室|會議廳|廳|空間))',  # XX會議室
        ]

        for pattern in room_patterns:
            matches = re.findall(pattern, page_text)
            if matches:
                for match in matches[:5]:  # 最多取5個
                    room = {
                        'name': match.strip(),
                        'source': url
                    }
                    all_rooms.append(room)
                    print(f"  找到: {match.strip()}")

        # 尋找容量
        capacity_pattern = r'(\d+)\s*[人名]'
        capacities = re.findall(capacity_pattern, page_text)

        if capacities:
            print(f"  容量: {', '.join(capacities[:5])}")

        # 尋找坪數
        area_pattern = r'(\d+\.?\d*)\s*[坪平米]'
        areas = re.findall(area_pattern, page_text)

        if areas:
            print(f"  面積: {', '.join(areas[:5])}")

        # 尋找價格
        price_pattern = r'(\d{2,6}[,.]?\d{0,3})\s*元'
        prices = re.findall(price_pattern, page_text)

        if prices:
            # 清理並轉換
            valid_prices = []
            for p in prices:
                try:
                    price = int(p.replace(',', ''))
                    if 1000 <= price <= 500000:
                        valid_prices.append(price)
                except:
                    pass

            if valid_prices:
                print(f"  價格: {', '.join([str(p) for p in valid_prices[:5]])}")

    except Exception as e:
        print(f"  ❌ 錯誤: {e}")

# 去重會議室
seen_rooms = set()
unique_rooms = []
for room in all_rooms:
    if room['name'] not in seen_rooms:
        seen_rooms.add(room['name'])
        unique_rooms.append(room)

# 檢查是否有 PDF
print("\n" + "=" * 100)
print("2.4 檢查 PDF 連結")
print("=" * 100)

pdf_links = []
for link in unique_links:
    href = link['href']
    if '.pdf' in href.lower():
        pdf_links.append(link)

print(f"找到 PDF 連結: {len(pdf_links)} 個")
for pdf in pdf_links:
    print(f"  - {pdf['text']}")
    print(f"    {pdf['href']}")

# 儲存階段2結果
stage2_result = {
    "venue": venue_name,
    "venue_id": venue_id,
    "stage2": {
        "homepage_links": len(unique_links),
        "working_links": len(working_links),
        "failed_links": len(failed_links),
        "data_sources": len(processed_urls),
        "total_rooms_found": len(unique_rooms),
        "rooms": unique_rooms,
        "pdf_links": pdf_links
    },
    "timestamp": datetime.now().isoformat()
}

result_file = f'{venue_name}_stage2_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
with open(result_file, 'w', encoding='utf-8') as f:
    json.dump(stage2_result, f, ensure_ascii=False, indent=2)

print(f"\n✅ 階段2結果已儲存: {result_file}")

# 階段2 總結
print("\n" + "=" * 100)
print("階段2 總結")
print("=" * 100)

print(f"\n鏈結測試:")
print(f"  測試鏈結: {len(unique_links)} 個")
print(f"  可用鏈結: {len(working_links)} 個")
print(f"  有資料鏈結: {len([l for l in working_links if l.get('has_data')])} 個")

print(f"\n會議室發現:")
print(f"  總會議室: {len(unique_rooms)} 個")

print(f"\nPDF 連結:")
print(f"  數量: {len(pdf_links)} 個")

print(f"\n下一步建議:")
if len(unique_rooms) == 0 and len(pdf_links) == 0:
    print(f"  ⚠️  未找到會議室資料或 PDF")
    print(f"  建議：")
    print(f"    1. 手動檢查保存的 HTML 檔案")
    print(f"    2. 使用瀏覽器開發者工具")
    print(f"    3. 可能需要使用 Selenium 爬取動態內容")
elif len(pdf_links) > 0:
    print(f"  ✅ 找到 {len(pdf_links)} 個 PDF 連結")
    print(f"  建議：下載並解析 PDF 獲取完整場地資料")
elif len(unique_rooms) < 5:
    print(f"  ⚠️  會議室資料較少")
    print(f"  建議：手動檢查是否有其他隱藏的會議室頁面或 PDF")
else:
    print(f"  ✅ 找到 {len(unique_rooms)} 個會議室")
    print(f"  建議：進入階段3，驗證並提取完整 30 欄位資料")

print("\n" + "=" * 100)
print(f"✅ {venue_name} 階段2完成")
print("=" * 100)
