#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
豪景大酒店 - 階段2：深度爬蟲（完整版）
三級爬取：主頁 → 會議頁 → 詳情頁
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import sys
import warnings
warnings.filterwarnings('ignore')

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("豪景大酒店 - 階段2：深度爬蟲（完整版）")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8'
}

base_url = 'https://www.riverview.com.tw'

# 2.1 第一級：主頁分析
print("2.1 第一級：主頁分析")
print("-" * 100)

try:
    response = requests.get(base_url, timeout=15, verify=False, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 尋找會議服務連結
    meeting_service_link = None
    for link in soup.find_all('a', href=True):
        if '會議服務' in link.get_text():
            meeting_service_link = link['href']
            break

    if meeting_service_link:
        print(f"✓ 發現會議服務連結: {meeting_service_link}")
    else:
        print("✗ 未發現會議服務連結")

except Exception as e:
    print(f"✗ 錯誤: {e}")

# 2.2 第二級：會議服務頁面發現
print("\n2.2 第二級：會議服務頁面分析")
print("-" * 100)

meeting_url = f"{base_url}/會議服務/"
print(f"訪問: {meeting_url}")

try:
    response = requests.get(meeting_url, timeout=15, verify=False, headers=headers)
    print(f"HTTP Status: {response.status_code}")

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()

        # 顯示頁面內容（前3000字）
        print("\n頁面內容（前3000字）:")
        print("=" * 100)
        print(page_text[:3000])

        # 尋找所有會議室名稱
        print("\n" + "=" * 100)
        print("提取會議室資訊:")
        print("=" * 100)

        # 尋找表格或列表
        tables = soup.find_all('table')
        print(f"\n發現 {len(tables)} 個表格")

        for i, table in enumerate(tables):
            print(f"\n表格 {i+1} 內容:")
            rows = table.find_all('tr')
            for row in rows[:10]:
                cells = row.find_all(['td', 'th'])
                if cells:
                    row_text = ' | '.join([cell.get_text(strip=True)[:30] for cell in cells])
                    print(f"  {row_text}")

        # 尋找列表
        lists = soup.find_all(['ul', 'ol'])
        print(f"\n發現 {len(lists)} 個列表")

        # 尋找包含會議室資訊的段落
        print("\n尋找關鍵段落:")
        for tag in soup.find_all(['div', 'p', 'section', 'h1', 'h2', 'h3', 'h4']):
            text = tag.get_text(strip=True)
            if any(keyword in text for keyword in ['廳', '坪', '人', '容量', '面積', '樓']) and 10 < len(text) < 200:
                print(f"  {text[:100]}")

        # 提取數字資訊
        print("\n提取數字資訊:")
        capacities = re.findall(r'(\d+)\s*[人名桌者]', page_text)
        areas = re.findall(r'(\d+|\d+\.\d+)\s*[坪平方公尺㎡]', page_text)
        floors = re.findall(r'([1-9B][F樓層])', page_text)

        print(f"容量數字: {capacities[:20] if capacities else '未找到'}")
        print(f"面積數字: {areas[:20] if areas else '未找到'}")
        print(f"樓層數字: {floors[:20] if floors else '未找到'}")

except Exception as e:
    print(f"✗ 錯誤: {e}")
    import traceback
    traceback.print_exc()

# 2.3 第三級：嘗試其他可能的路徑
print("\n2.3 第三級：嘗試其他路徑")
print("-" * 100)

other_urls = [
    f"{base_url}/meeting/",
    f"{base_url}/banquet/",
    f"{base_url}/conference/",
    f"{base_url}/facility/",
    f"{base_url}/facilities/",
    f"{base_url}/room/meeting"
]

for url in other_urls:
    print(f"\n嘗試: {url}")
    try:
        r = requests.get(url, timeout=10, verify=False, headers=headers)
        if r.status_code == 200:
            print(f"  ✓ 200 OK")
            # 檢查是否有會議室資訊
            if '會議' in r.text or '宴會' in r.text:
                print(f"  ✓ 包含會議/宴會內容")
        else:
            print(f"  ✗ {r.status_code}")
    except Exception as e:
        print(f"  ✗ 錯誤: {e}")

# 2.4 提取聯絡資訊
print("\n2.4 提取聯絡資訊")
print("-" * 100)

contact_url = f"{base_url}/contact/"
print(f"訪問聯絡頁面: {contact_url}")

try:
    r = requests.get(contact_url, timeout=15, verify=False, headers=headers)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        page_text = soup.get_text()

        # 提取電話
        phones = re.findall(r'0\d[\d-]{7,9}', page_text)
        print(f"電話: {phones}")

        # 提取Email
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', page_text)
        valid_emails = [e for e in emails if 'no-reply' not in e.lower() and 'noreply' not in e.lower()]
        print(f"Email: {valid_emails}")

        # 提取傳真
        faxes = re.findall(r'傳真[：:]\s*(0\d[\d-]{7,9})', page_text)
        if faxes:
            print(f"傳真: {faxes}")

except Exception as e:
    print(f"✗ 錯誤: {e}")

# 儲存階段2結果
stage2_result = {
    "venue": "豪景大酒店",
    "venue_id": 1126,
    "timestamp": datetime.now().isoformat(),
    "meeting_service_page": meeting_url,
    "meeting_page_status": response.status_code if 'response' in locals() else None,
    "phones": phones if 'phones' in locals() else [],
    "emails": valid_emails if 'valid_emails' in locals() else [],
    "note": "完整三級爬取完成"
}

with open('riverview_stage2_results.json', 'w', encoding='utf-8') as f:
    json.dump(stage2_result, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 100)
print("階段2完成")
print("=" * 100)
print(f"結果已儲存: riverview_stage2_results.json")
