#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scrape Nangang Exhibition Center (Tainex) room data
URL: https://www.tainex.com.tw/venue/room-info/1/3
"""
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape_nangang():
    """爬取南港展覽館會議室資料"""
    url = "https://www.tainex.com.tw/venue/room-info/1/3"

    print("="*80)
    print("Scraping Nangang Exhibition Center (Tainex)")
    print("="*80)
    print(f"URL: {url}")
    print()

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    try:
        print("[1/4] Fetching webpage...")
        response = session.get(url, timeout=15)
        print(f"    Status: {response.status_code}")
        print(f"    Content length: {len(response.text)} bytes")
        print()

        print("[2/4] Parsing HTML...")
        soup = BeautifulSoup(response.text, 'html.parser')

        # 尋找會議室資料
        rooms = []

        # 嘗試不同的選擇器
        selectors = [
            '.room-item',
            '.venue-room',
            '.meeting-room',
            '.exhibition-hall',
            'table',
            '.room-list',
        ]

        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                print(f"    Found {len(elements)} elements with '{selector}'")

                for elem in elements[:5]:  # 只顯示前5個
                    text = elem.get_text()[:100]
                    print(f"      - {text}...")

        # 檢查是否有表格
        tables = soup.find_all('table')
        if tables:
            print(f"\n[3/4] Found {len(tables)} table(s)")
            for i, table in enumerate(tables[:2]):
                print(f"  Table {i+1}:")
                rows = table.find_all('tr')
                for j, row in enumerate(rows[:3]):
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        cell_text = ' | '.join([c.get_text().strip()[:30] for c in cells])
                        print(f"    Row {j+1}: {cell_text}")

        # 尋找會議室名稱
        print("\n[4/4] Looking for room names...")
        room_keywords = ['會議室', '展覽館', '會議廳', '宴會廳', '樓', '廳']

        for keyword in room_keywords:
            elements = soup.find_all(text=lambda text: text and keyword in text)
            if elements:
                print(f"  Found '{keyword}' in {len(elements)} places:")
                for elem in elements[:3]:
                    print(f"    - {elem.strip()[:60]}")

        # 儲存原始 HTML 供後續分析
        with open('nangang_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)

        print()
        print("[INFO] Saved raw HTML to nangang_page.html")
        print()
        print("="*80)
        print("Analysis complete")
        print("="*80)
        print()
        print("Next steps:")
        print("  1. Review nangang_page.html")
        print("  2. Identify the correct data structure")
        print("  3. Create specific parser for Nangang")

        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    scrape_nangang()
