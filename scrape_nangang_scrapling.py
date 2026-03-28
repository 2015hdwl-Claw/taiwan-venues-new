#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 Scrapling 爬取南港展覽館（正確版本）
"""
from scrapling import Fetcher
import json
from datetime import datetime


def scrape_with_scrapling():
    """使用 Scrapling 的 impersonate 功能"""
    url = "https://www.tainex.com.tw/venue/room-info/1/3"

    print("="*80)
    print("Scrapling 爬蟲 - 南港展覽館")
    print("="*80)
    print(f"URL: {url}")
    print()

    print("[1/4] 建立 Fetcher（模擬 Chrome 瀏覽器）...")

    fetcher = Fetcher()

    print("[2/4] 發送請求（使用 impersonate）...")

    try:
        response = fetcher.get(
            url,
            # Scrapling 的關鍵參數
            impersonate="chrome120",  # 模擬 Chrome 120
            stealthy_headers=True,     # 使用真實瀏覽器 headers
            timeout=30,
            retries=3,
            retry_delay=2,
        )

        print(f"    HTTP 狀態: {response.status}")
        print(f"    內容長度: {len(response.text)} bytes")

        # 檢查是否被阻擋
        if 'blocked' in response.text.lower() or 'access denied' in response.text.lower():
            print("    ✗ 被阻擋（Access Denied）")
            return False
        elif 'challenge' in response.text.lower() or 'captcha' in response.text.lower():
            print("    ⚠️ 需要驗證（Cloudflare Challenge）")
            return False
        elif len(response.text) < 5000:
            print("    ⚠️ 內容太短，可能是錯誤頁面")
            return False
        else:
            print("    ✓ 成功！")

        print()
        print("[3/4] 分析內容...")

        # 使用 BeautifulSoup 解析
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # 標題
        title = soup.find('title')
        if title:
            print(f"    頁面標題: {title.get_text().strip()}")

        # 檢查關鍵字
        keywords = ['會議室', '展覽', '場地', '樓', '廳']
        text = soup.get_text()
        found = [kw for kw in keywords if kw in text]

        if found:
            print(f"    找到關鍵字: {', '.join(found)}")
        else:
            print("    未找到會議室關鍵字")

        # 尋找表格
        tables = soup.find_all('table')
        if tables:
            print(f"    找到 {len(tables)} 個表格")

            for i, table in enumerate(tables[:2]):
                rows = table.find_all('tr')
                print(f"      表格 {i+1}: {len(rows)} 行")

                # 顯示前幾行
                for row in rows[:3]:
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        row_text = ' | '.join([c.get_text().strip()[:30] for c in cells])
                        print(f"        {row_text}")

        # 尋找會議室相關連結
        links = soup.find_all('a', href=True)
        venue_links = []

        for a in links:
            href = a.get('href', '')
            text = a.get_text().strip()

            if any(kw in text.lower() or kw in href.lower() for kw in ['room', 'venue', '會議', '展覽']):
                if 0 < len(text) < 100 and text not in [l['text'] for l in venue_links]:
                    venue_links.append({'text': text, 'url': href})

        print(f"    相關連結: {len(venue_links)} 個")

        if venue_links:
            for link in venue_links[:5]:
                print(f"      - {link['text'][:50]}")
                print(f"        {link['url']}")

        print()
        print("[4/4] 儲存結果...")

        # 儲存 HTML
        with open('nangang_scrapling_success.html', 'w', encoding='utf-8') as f:
            f.write(response.text)

        print("    已儲存: nangang_scrapling_success.html")

        # 儲存 JSON 報告
        report = {
            'url': url,
            'status_code': response.status,
            'content_length': len(response.text),
            'success': True,
            'found_keywords': found,
            'tables_count': len(tables),
            'links_count': len(venue_links),
            'timestamp': datetime.now().isoformat()
        }

        with open('nangang_scrapling_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print("    已儲存: nangang_scrapling_report.json")

        return True

    except Exception as e:
        print(f"    錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_homepage_first():
    """先測試首頁"""
    print()
    print("="*80)
    print("先測試首頁（通常保護較鬆）")
    print("="*80)

    fetcher = Fetcher()

    try:
        response = fetcher.get(
            "https://www.tainex.com.tw/",
            impersonate="chrome120",
            stealthy_headers=True,
            timeout=30,
        )

        print(f"HTTP {response.status}")
        print(f"內容長度: {len(response.text)} bytes")

        if 'blocked' not in response.text.lower():
            print("✓ 首頁可訪問！")

            # 尋找會議室相關連結
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            links = soup.find_all('a', href=True)
            meeting_links = []

            for a in links:
                href = a.get('href', '')
                text = a.get_text().strip()

                if any(kw in text.lower() or kw in href.lower() for kw in ['room', 'venue', '會議', '展覽', '樓']):
                    if 0 < len(text) < 100:
                        meeting_links.append({'text': text, 'url': href})

            print(f"找到 {len(meeting_links)} 個會議室相關連結")

            if meeting_links:
                print("\n相關連結:")
                for link in meeting_links[:8]:
                    url = link['url']
                    if url.startswith('/'):
                        url = 'https://www.tainex.com.tw' + url
                    print(f"  - {link['text'][:60]}")
                    print(f"    {url}")

            return True
        else:
            print("✗ 首頁也被阻擋")
            return False

    except Exception as e:
        print(f"錯誤: {e}")
        return False


def main():
    print("="*80)
    print("Scrapling v0.4.2 測試")
    print("="*80)
    print()
    print("Scrapling 優勢:")
    print("  - 使用 curl_cffi（比 requests 更底層）")
    print("  - impersonate 模擬真實瀏覽器")
    print("  - stealthy_headers 自動生成真實 headers")
    print("  - 不易被檢測")
    print()

    # 先測試首頁
    homepage_ok = test_homepage_first()

    if homepage_ok:
        print()
        print("首頁成功，嘗試會議室頁面...")
        print()
        success = scrape_with_scrapling()

        if success:
            print()
            print("="*80)
            print("【成功】Scrapling 突破了 Cloudflare！")
            print("="*80)
            print()
            print("下一步:")
            print("  1. 查看 nangang_scrapling_success.html")
            print("  2. 檢查是否有會議室資料")
            print("  3. 如果有資料，提取並更新到 venues.json")
        else:
            print()
            print("="*80)
            print("【部分成功】")
            print("="*80)
            print()
            print("首頁可訪問，但會議室頁面仍有困難")
            print("建議:")
            print("  1. 從首頁找到的連結逐一測試")
            print("  2. 手動訪問會議室頁面")
    else:
        print()
        print("="*80)
        print("【失敗】")
        print("="*80)
        print()
        print("Scrapling 也無法突破")
        print("建議回歸手動輸入或聯繫場地")


if __name__ == '__main__':
    main()
