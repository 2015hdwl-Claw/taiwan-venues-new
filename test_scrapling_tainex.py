#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 Scrapling 測試南港展覽館爬蟲
Scrapling 宣稱是不可檢測的爬蟲框架
"""
from scrapling import Fetcher
import json
from datetime import datetime


def test_scrapling():
    """測試 Scrapling 是否能突破 Cloudflare"""
    url = "https://www.tainex.com.tw/venue/room-info/1/3"

    print("="*80)
    print("Scrapling 測試 - 南港展覽館")
    print("="*80)
    print(f"URL: {url}")
    print()

    print("[1/4] 建立 Fetcher...")
    # Scrapling 使用 Fetcher 類別
    fetcher = Fetcher()

    print("[2/4] 發送請求...")

    try:
        # 使用 Scrapling 的 auto_playwright 功能
        # 它會自動使用瀏覽器如果需要
        response = fetcher.get(
            url,
            # Scrapling 的參數
            auto_playwright=True,  # 自動使用 Playwright 如果被阻擋
            headless=False,  # 非無頭模式（更容易繞過）
            timeout=30000,
        )

        print(f"    狀態碼: {response.status}")
        print(f"    內容長度: {len(response.text)} bytes")

        # 檢查是否被阻擋
        if 'blocked' in response.text.lower():
            print("    ✗ 仍然被阻擋")
            return False
        elif 'challenge' in response.text.lower() or 'captcha' in response.text.lower():
            print("    ⚠️ 需要驗證（Cloudflare Challenge）")
            return False
        else:
            print("    ✓ 成功！")

        print()
        print("[3/4] 分析內容...")

        # 檢查是否有會議室資料
        keywords = ['會議室', '展覽', '場地', '樓', '廳', 'room', 'venue']
        found_keywords = [kw for kw in keywords if kw in response.text]

        if found_keywords:
            print(f"    找到關鍵字: {', '.join(found_keywords)}")
        else:
            print("    未找到會議室相關關鍵字")

        # 嘗試解析 HTML
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # 尋找標題
        title = soup.find('title')
        if title:
            print(f"    頁面標題: {title.get_text().strip()}")

        # 尋找連結
        links = soup.find_all('a', href=True)
        print(f"    連結數量: {len(links)}")

        # 尋找會議室相關連結
        meeting_links = []
        for a in links:
            href = a.get('href', '')
            text = a.get_text().strip()

            for kw in keywords:
                if kw in text.lower() or kw in href.lower():
                    if 0 < len(text) < 100:
                        meeting_links.append({
                            'text': text,
                            'url': href
                        })
                        break

        print(f"    會議室連結: {len(meeting_links)} 個")

        if meeting_links:
            print()
            print("    前 5 個相關連結:")
            for link in meeting_links[:5]:
                print(f"      - {link['text'][:50]}")
                if link['url'].startswith('/'):
                    print(f"        {link['url']}")

        print()
        print("[4/4] 儲存結果...")

        # 儲存 HTML
        with open('nangang_scrapling.html', 'w', encoding='utf-8') as f:
            f.write(response.text)

        print("    已儲存: nangang_scrapling.html")

        return True

    except Exception as e:
        print(f"    錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_alternative_approach():
    """測試替代方法"""
    print()
    print("="*80)
    print("測試 Scrapling 替代方法")
    print("="*80)
    print()

    from scrapling import Fetcher

    # 測試首頁
    print("[1/2] 測試首頁...")
    fetcher = Fetcher()

    try:
        response = fetcher.get(
            "https://www.tainex.com.tw/",
            auto_playwright=True,
            headless=False,
            timeout=30000,
        )

        if 'blocked' not in response.text.lower():
            print("    ✓ 首頁可訪問！")

            # 尋找會議室相關連結
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            links = soup.find_all('a', href=True)
            venue_links = []

            for a in links:
                href = a.get('href', '')
                text = a.get_text().strip()

                # 尋找可能包含會議室資料的連結
                if any(kw in text.lower() or kw in href.lower() for kw in ['venue', 'room', '會議', '展覽', '樓']):
                    if 0 < len(text) < 100:
                        # 轉換為完整 URL
                        if href.startswith('/'):
                            href = 'https://www.tainex.com.tw' + href

                        venue_links.append({
                            'text': text,
                            'url': href
                        })

            print(f"    找到 {len(venue_links)} 個可能相關的連結")

            # 顯示前 10 個
            for link in venue_links[:10]:
                print(f"      - {link['text'][:50]}")
                print(f"        {link['url']}")

            # 建議下一步
            if venue_links:
                print()
                print("[2/2] 建議下一步:")
                print("    手動訪問這些連結:")
                for link in venue_links[:3]:
                    print(f"      - {link['url']}")

        else:
            print("    ✗ 首頁也被阻擋")

    except Exception as e:
        print(f"    錯誤: {e}")


def main():
    print("="*80)
    print("Scrapling 爬蟲測試")
    print("="*80)
    print()
    print("Scrapling 特點:")
    print("  - 宣稱是不可檢測的 (Undetectable)")
    print("  - 自動使用 Playwright 當需要時")
    print("  - 內建反反爬蟲機制")
    print()

    # 測試主要 URL
    success = test_scrapling()

    if success:
        print()
        print("="*80)
        print("【成功】Scrapling 突破了 Cloudflare！")
        print("="*80)
        print()
        print("下一步:")
        print("  1. 查看 nangang_scrapling.html")
        print("  2. 提取會議室資料")
        print("  3. 更新到 venues.json")
    else:
        print()
        print("="*80)
        print("【失敗】Scrapling 無法突破")
        print("="*80)
        print()
        test_alternative_approach()


if __name__ == '__main__':
    main()
