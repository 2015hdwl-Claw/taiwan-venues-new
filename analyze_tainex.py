#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢測南港展覽館首頁網頁技術
URL: https://www.tainex.com.tw/
"""
import requests
from bs4 import BeautifulSoup
import sys
import io
import urllib3
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def analyze_tainex():
    """分析南港展覽館首頁"""
    url = "https://www.tainex.com.tw/"

    print("="*80)
    print("南港展覽館首頁技術檢測")
    print("="*80)
    print(f"URL: {url}")
    print()

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    })

    try:
        # 1. 基本 HTTP 請求
        print("[1/6] 基本 HTTP 請求...")
        response = session.get(url, timeout=15, verify=False)
        print(f"    HTTP {response.status_code}")
        print(f"    內容長度: {len(response.text)} bytes")
        print(f"    Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"    Server: {response.headers.get('Server', 'N/A')}")

        # 檢查重定向
        if response.history:
            print(f"    重定向: {' -> '.join([str(r.status_code) for r in response.history])} -> {response.status_code}")

        # 2. 分析 HTML 結構
        print("\n[2/6] 分析 HTML 結構...")
        soup = BeautifulSoup(response.text, 'html.parser')

        # 標題
        title = soup.find('title')
        if title:
            print(f"    標題: {title.get_text().strip()}")

        # 檢查是否為 SPA
        body_div = soup.find('div', id='body')
        if body_div:
            print(f"    SPA 檢測: 找到 <div id='body'>")
            print(f"    內容長度: {len(body_div.get_text())} 字元")

        # 檢查 script 標籤
        scripts = soup.find_all('script')
        js_files = [s.get('src', '') for s in scripts if s.get('src')]
        inline_js = [s for s in scripts if not s.get('src')]

        print(f"    JavaScript 檔案: {len(js_files)} 個")
        print(f"    內嵌 JavaScript: {len(inline_js)} 個")

        # 顯示關鍵 JS 檔案
        for js in js_files[:5]:
            print(f"      - {js}")

        # 3. 檢測框架
        print("\n[3/6] 檢測 JavaScript 框架...")

        frameworks = {
            'React': ['react', 'react-dom', 'ReactDOM'],
            'Vue': ['vue', 'Vue', 'VueRouter'],
            'Angular': ['angular', 'ng-app', 'ng-controller'],
            'jQuery': ['jquery', 'jQuery', '$'],
            'Bootstrap': ['bootstrap'],
        }

        html_lower = response.text.lower()

        for framework, keywords in frameworks.items():
            found = [kw for kw in keywords if kw in html_lower]
            if found:
                print(f"    ✓ {framework}: {', '.join(found)}")

        # 4. 尋找 API 端點
        print("\n[4/6] 尋找 API 端點...")

        # 尋找常見的 API 模式
        api_patterns = [
            r'https?://[^\s"\']+api[^\s"\']*',
            r'/api/[^\s"\']+',
            r'fetch\([^\)]+\)',
            r'axios[^\n]+',
            r'XMLHttpRequest',
        ]

        apis_found = set()
        for pattern in api_patterns:
            matches = re.findall(pattern, response.text, re.IGNORECASE)
            apis_found.update(matches[:5])  # 最多 5 個

        if apis_found:
            print(f"    找到 {len(apis_found)} 個可能的 API:")
            for api in list(apis_found)[:5]:
                print(f"      - {api[:80]}")
        else:
            print("    未找到明顯的 API 端點")

        # 5. 尋找會議室相關連結
        print("\n[5/6] 尋找會議室相關連結...")

        meeting_keywords = ['會議室', '會議', '展覽', '場地', '租借', 'room', 'venue', 'meeting', 'exhibition']
        all_links = soup.find_all('a', href=True)

        meeting_links = []
        for a in all_links:
            href = a['href']
            text = a.get_text().strip()

            for kw in meeting_keywords:
                if kw in text.lower() or kw in href.lower():
                    if 0 < len(text) < 100:
                        meeting_links.append({
                            'text': text,
                            'url': href
                        })
                        break

        print(f"    會議室相關連結: {len(meeting_links)} 個")
        for link in meeting_links[:8]:
            url = link['url']
            if url.startswith('/'):
                url = 'https://www.tainex.com.tw' + url
            print(f"      - {link['text'][:50]}")
            print(f"        {url}")

        # 6. 檢查反爬蟲機制
        print("\n[6/6] 檢查反爬蟲機制...")

        anti_bot_checks = {
            'Cloudflare': 'cloudflare' in html_lower,
            'DataDome': 'datadome' in html_lower,
            'Akamai': 'akamai' in html_lower,
            ' honeypot': 'honeypot' in html_lower,
            '隱藏欄位': soup.find('input', type='hidden') is not None,
            'Cookie 檢查': 'set-cookie' in str(response.headers).lower(),
        }

        for check, result in anti_bot_checks.items():
            status = "⚠️" if result else "✓"
            print(f"    {status} {check}: {'發現' if result else '未發現'}")

        # 結論
        print("\n" + "="*80)
        print("【結論】")
        print("="*80)

        if body_div and len(scripts) > 5:
            print("網頁類型: JavaScript SPA (Single Page Application)")
            print("特徵:")
            print("  - 內容由 JavaScript 動態生成")
            print("  - 使用 <div id='body'> 作為容器")
            print("  - 多個 JavaScript 檔案")
            print()
            print("爬蟲策略:")
            print("  1. 使用 Playwright/Selenium 等瀏覽器自動化工具")
            print("  2. 分析 network 找到 API 端點直接調用")
            print("  3. 檢查是否有 JSON 資料來源")
        elif len(js_files) > 3:
            print("網頁類型: Dynamic (動態網頁)")
            print("爬蟲策略:")
            print("  1. 使用 Playwright 等待 JavaScript 執行")
            print("  2. 或找尋靜態資料來源")
        else:
            print("網頁類型: Static/SSR (靜態/伺服器端渲染)")
            print("爬蟲策略:")
            print("  1. 使用 requests + BeautifulSoup")
            print("  2. 直接解析 HTML 內容")

        print()
        print("下一步建議:")
        if meeting_links:
            print("  1. 深入爬取會議室連結頁面")
            print(f"  2. 嘗試: {meeting_links[0]['url']}")
        else:
            print("  1. 檢視網站地圖")
            print("  2. 檢查網站源碼中的 API 調用")

    except Exception as e:
        print(f"錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    analyze_tainex()
