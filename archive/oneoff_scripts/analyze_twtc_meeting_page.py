#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析台北世貿中心會議室詳細頁面
ID 1049: https://www.twtc.com.tw/meeting11
"""
import requests
from bs4 import BeautifulSoup
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if sys.platform == 'win32':
    import io as sys_io
    sys.stdout = sys_io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def analyze_meeting_page():
    """分析會議室詳細頁面"""
    url = "https://www.twtc.com.tw/meeting11"

    print("="*80)
    print("台北世貿中心會議室詳細頁面分析")
    print("="*80)
    print(f"URL: {url}")
    print()

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    try:
        print("[1/4] 下載頁面...")
        response = session.get(url, timeout=15, verify=False)
        print(f"✅ HTTP {response.status_code}")

        soup = BeautifulSoup(response.text, 'html.parser')
        print()

        # 分析頁面結構
        print("[2/4] 分析頁面結構...")

        # 尋找標題
        title = soup.find('h1')
        if title:
            print(f"標題: {title.get_text().strip()}")

        # 尋找所有標題
        print("\n標題結構:")
        for i, heading in enumerate(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])[:10], 1):
            print(f"  {heading.name}: {heading.get_text().strip()[:60]}")

        print()

        # 尋找表格
        print("[3/4] 尋找資料表格...")
        tables = soup.find_all('table')
        print(f"找到 {len(tables)} 個表格")

        for i, table in enumerate(tables[:3], 1):
            print(f"\n表格 {i}:")
            rows = table.find_all('tr')
            print(f"  行數: {len(rows)}")

            # 顯示前幾行
            for j, row in enumerate(rows[:5], 1):
                cells = row.find_all(['td', 'th'])
                cell_texts = [cell.get_text().strip()[:30] for cell in cells]
                print(f"  行 {j}: {' | '.join(cell_texts)}")

        print()

        # 尋找會議室資訊
        print("[4/4] 尋找會議室資訊...")

        # 嘗試不同的選擇器
        selectors = [
            ('classroom', 'class', 'classroom'),
            ('meeting-room', 'class', 'meeting-room'),
            ('meeting', 'class', 'meeting'),
            ('room', 'class', 'room'),
            ('table', 'tag', 'table'),
        ]

        found_info = False
        for name, attr_type, attr_value in selectors:
            if attr_type == 'class':
                elements = soup.find_all(class_=attr_value)
            elif attr_type == 'tag':
                elements = soup.find_all(attr_value)

            if elements:
                print(f"\n找到 {len(elements)} 個 '{attr_value}' 元素")
                found_info = True

                # 顯示前3個元素的內容
                for elem in elements[:3]:
                    text = elem.get_text().strip()[:200]
                    print(f"  內容: {text}...")

        # 尋找包含關鍵字的段落
        print("\n尋找包含關鍵字的內容:")
        keywords = ['容量', '面積', '坪', '平方公尺', '尺寸', '租金', '設備']

        all_paragraphs = soup.find_all(['p', 'div', 'td', 'li'])
        for keyword in keywords:
            found = False
            for elem in all_paragraphs:
                text = elem.get_text()
                if keyword in text:
                    if not found:
                        print(f"\n{keyword}:")
                        found = True

                    # 清理並顯示文字
                    clean_text = ' '.join(text.split())[:100]
                    print(f"  - {clean_text}...")
                    break

        # 儲存原始HTML
        with open('twtc_meeting11.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())

        print()
        print("="*80)
        print("分析完成")
        print("="*80)
        print(f"原始HTML已儲存至: twtc_meeting11.html")

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    analyze_meeting_page()
