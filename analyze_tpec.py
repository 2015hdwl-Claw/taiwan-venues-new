#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢測南港展覽館網頁技術
"""
import requests
from bs4 import BeautifulSoup
import sys
import io
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def analyze_tpec():
    """分析南港展覽館"""
    url = "https://www.tcec.com.tw/"

    print("="*80)
    print("南港展覽館網頁技術檢測")
    print("="*80)
    print(f"URL: {url}")
    print()

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    try:
        # 1. 基本 HTTP 請求
        print("[1/5] 基本 HTTP 請求...")
        response = session.get(url, timeout=15, verify=False)
        print(f"    HTTP {response.status_code}")
        print(f"    內容長度: {len(response.text)} bytes")

        # 2. 分析 HTML
        print("[2/5] 分析 HTML 結構...")
        soup = BeautifulSoup(response.text, 'html.parser')

        # 標題
        title = soup.find('title')
        if title:
            print(f"    標題: {title.get_text().strip()}")

        # 尋導列
        nav = soup.find('nav')
        if nav:
            print(f"    導航列: 有")
            nav_links = nav.find_all('a', href=True)[:5]
            for a in nav_links:
                print(f"      - {a.get_text().strip()[:40]}")
        else:
            print("    導航列: 無")

        # 3. 檢測 JavaScript
        print("[3/5] 檢測 JavaScript...")
        scripts = soup.find_all('script')
        js_libs = []

        for script in scripts:
            src = script.get('src', '')
            if src:
                js_libs.append(src)
            else:
                content = script.get_text()[:100]
                if 'react' in content.lower() or 'vue' in content.lower():
                    js_libs.append('inline: ' + content[:30])

        print(f"    JS 數量: {len(scripts)}")
        if js_libs:
            for lib in js_libs[:5]:
                print(f"      - {lib[:60]}")

        # 4. 尋找會議室相關連結
        print("[4/5] 尋找會議室相關連結...")
        meeting_keywords = ['會議', 'meeting', '場地', '空間', 'space', 'room', 'venue']
        all_links = soup.find_all('a', href=True)

        meeting_links = []
        for a in all_links:
            text = a.get_text().strip()
            href = a['href']

            if any(kw in text.lower() or kw in href.lower() for kw in meeting_keywords):
                if 0 < len(text) < 80:
                    meeting_links.append({
                        'text': text,
                        'url': href
                    })

        print(f"    會議室連結: {len(meeting_links)} 個")
        for link in meeting_links[:5]:
            print(f"      - {link['text'][:50]}")

        # 5. 尋找 PDF
        print("[5/5] 尋找 PDF...")
        pdf_links = []
        for a in all_links:
            href = a['href'].lower()
            if href.endswith('.pdf'):
                pdf_links.append(a['href'])

        print(f"    PDF 連結: {len(pdf_links)} 個")
        for pdf in pdf_links[:3]:
            print(f"      - {pdf}")

        # 結論
        print()
        print("="*80)
        print("【結論】")
        print("="*80)

        if len(scripts) > 10:
            print("網頁類型: 可能是 JavaScript SPA")
            print("建議: 使用 Playwright 或 Selenium")
        elif nav and len(meeting_links) > 0:
            print("網頁類型: Static/SSR")
            print("建議: 使用 requests + BeautifulSoup")
        else:
            print("網頁類型: Static/SSR (簡單)")

        print()
        print("下一步:")
        if meeting_links:
            print("  1. 深入爬取會議室連結頁面")
        else:
            print("  1. 檢視網站地圖")
            print("  2. 手動尋找會議室頁面")

    except Exception as e:
        print(f"錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    analyze_tpec()
