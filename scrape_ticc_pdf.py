#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TICC PDF 下載與解析
"""

import requests
import pdfplumber
import json
import sys
from datetime import datetime
import re

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("TICC - PDF 下載與解析")
print("=" * 100)
print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# TICC 主頁 URL
base_url = "https://www.ticc.com.tw/"

print(f"主頁 URL: {base_url}\n")

# 從主頁開始尋找 PDF
print("步驟 1：訪問主頁，尋找價目表連結...")
try:
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin

    response = requests.get(base_url, timeout=30, verify=False)
    print(f"主頁 HTTP 狀態: {response.status_code}")

    if response.status_code != 200:
        print("❌ 主頁訪問失敗")
        sys.exit(1)

    soup = BeautifulSoup(response.text, 'html.parser')

    # 尋找價目表相關連結
    price_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True)
        if any(kw in text for kw in ['價目', '收費', '價格', '租用', '費率']):
            full_url = urljoin(base_url, href)
            price_links.append({
                'href': full_url,
                'text': text[:100]
            })

    print(f"\n找到 {len(price_links)} 個價格相關連結:")
    for link in price_links:
        print(f"  - {link['text']}")
        print(f"    {link['href']}")

    if not price_links:
        print("\n❌ 未找到價格相關連結")
        sys.exit(1)

    # 訪問第一個價格連結
    price_page_url = price_links[0]['href']
    print(f"\n步驟 2：訪問價目表頁面...")
    print(f"URL: {price_page_url}")

    response = requests.get(price_page_url, timeout=30, verify=False)
    print(f"價目表頁面 HTTP 狀態: {response.status_code}")

    if response.status_code != 200:
        print("❌ 價目表頁面訪問失敗")
        sys.exit(1)

    soup = BeautifulSoup(response.text, 'html.parser')

    # 尋找 PDF 連結
    pdf_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True)
        if '.pdf' in href.lower() or any(kw in text for kw in ['下載', '下載', 'PDF']):
            full_url = urljoin(base_url, href)
            pdf_links.append({
                'href': full_url,
                'text': text[:100]
            })

    print(f"\n找到 {len(pdf_links)} 個 PDF 連結:")
    for link in pdf_links:
        print(f"  - {link['text']}")
        print(f"    {link['href']}")

    if not pdf_links:
        print("\n❌ 未找到 PDF 連結")
        sys.exit(1)

    # 下載第一個 PDF
    pdf_url = pdf_links[0]['href']
    print(f"\n步驟 3：下載 PDF...")
    print(f"PDF URL: {pdf_url}")

    response = requests.get(pdf_url, timeout=30, verify=False)
    print(f"PDF HTTP 狀態: {response.status_code}")

    if response.status_code != 200:
        print("❌ PDF 下載失敗")
        sys.exit(1)

    # 檢查是否是 PDF
    content_type = response.headers.get('Content-Type', '')
    print(f"Content-Type: {content_type}")

    if 'pdf' not in content_type.lower():
        print("\n⚠️ 這不是 PDF 檔案")
        print(f"實際內容長度: {len(response.content)} bytes")
        # 檢查是否是 HTML
        if b'<html' in response.content[:100]:
            print("這是 HTML 頁面，不是 PDF")
            sys.exit(1)

    # 儲存 PDF
    pdf_filename = f'ticc_pricelist_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    with open(pdf_filename, 'wb') as f:
        f.write(response.content)

    print(f"✅ PDF 已儲存: {pdf_filename}")

except Exception as e:
    print(f"❌ 下載失敗: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 解析 PDF
print("\n" + "=" * 100)
print("解析 PDF")
print("=" * 100)

try:
    with pdfplumber.open(pdf_filename) as pdf:
        print(f"PDF 頁數: {len(pdf.pages)}\n")

        # 提取所有頁面的文字
        all_text = ""
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                all_text += text + "\n\n"
            print(f"頁面 {i+1}: {len(text) if text else 0} 字元")

        # 儲存文字
        text_filename = f'ticc_pricelist_text_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        with open(text_filename, 'w', encoding='utf-8') as f:
            f.write(all_text)

        print(f"\n✅ PDF 文字已儲存: {text_filename}")

        # 尋找會議室資訊
        print("\n" + "=" * 100)
        print("尋找會議室資訊")
        print("=" * 100)

        # 尋找會議室名稱模式
        room_patterns = [
            r'\d+[F樓]\s*會議室',
            r'\d+\s*會議室',
            r'國際會議廳',
            r'宴會廳',
        ]

        rooms_found = []
        for pattern in room_patterns:
            matches = re.findall(pattern, all_text)
            rooms_found.extend(matches)

        if rooms_found:
            print(f"\n找到可能的會議室: {len(set(rooms_found))} 個")
            for room in sorted(set(rooms_found)):
                print(f"  - {room}")
        else:
            print("\n⚠️ 未找到明確的會議室名稱")

        # 尋找容量資訊
        print("\n尋找容量資訊...")
        capacity_patterns = [
            r'(\d+)\s*人',
            r'容量[：:]\s*(\d+)',
        ]

        capacities = []
        for pattern in capacity_patterns:
            matches = re.findall(pattern, all_text)
            capacities.extend(matches)

        if capacities:
            print(f"找到容量資訊: {len(capacities)} 處")
            print(f"範圍: {min(int(c) for c in capacities)} - {max(int(c) for c in capacities)} 人")

        # 尋找價格資訊
        print("\n尋找價格資訊...")
        price_patterns = [
            r'(\d{2,5}[,.]?\d{0,3})\s*元',
            r'NT\$\s*(\d+[,.]?\d*)',
            r'TWD\s*(\d+[,.]?\d*)',
        ]

        prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, all_text)
            prices.extend(matches)

        if prices:
            print(f"找到價格資訊: {len(prices)} 處")

        # 嘗試提取表格
        print("\n" + "=" * 100)
        print("嘗試提取表格")
        print("=" * 100)

        for i, page in enumerate(pdf.pages[:3]):  # 只看前 3 頁
            tables = page.extract_tables()
            if tables:
                print(f"\n頁面 {i+1}: 找到 {len(tables)} 個表格")
                for j, table in enumerate(tables):
                    print(f"\n表格 {j+1}:")
                    print(f"  列數: {len(table)}")
                    if table:
                        print(f"  欄數: {len(table[0]) if table[0] else 0}")
                        # 顯示前 3 行
                        for row in table[:3]:
                            print(f"  {row}")

        # 儲存完整結果
        result = {
            'venue': 'TICC',
            'venue_id': 1448,
            'pdf_url': pdf_url,
            'pdf_file': pdf_filename,
            'text_file': text_filename,
            'total_pages': len(pdf.pages),
            'rooms_found': list(set(rooms_found)),
            'capacities': capacities[:10] if capacities else [],
            'prices': prices[:10] if prices else [],
            'timestamp': datetime.now().isoformat()
        }

        result_filename = f'ticc_pdf_result_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(result_filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 解析結果已儲存: {result_filename}")

except Exception as e:
    print(f"❌ 解析失敗: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 100)
print("✅ TICC PDF 處理完成")
print("=" * 100)
