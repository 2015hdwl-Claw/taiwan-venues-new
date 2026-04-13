#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下載並解析 1532 的規則文檔
"""

import sys
import os

# Windows UTF-8 輸出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright

VENUE_ID = 1532
URL = 'https://www.tcwtc.com.tw/conference-rules.html'


def main():
    print(f'=== 爬取: {URL} ===')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()

        page.goto(URL, wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(10000)

        # 取得頁面 HTML
        html = page.content()
        text = page.evaluate('() => document.body.innerText')

        # 儲存 HTML 和文字
        with open(f'venue_{VENUE_ID}_rules.html', 'w', encoding='utf-8') as f:
            f.write(html)

        with open(f'venue_{VENUE_ID}_rules.txt', 'w', encoding='utf-8') as f:
            f.write(text)

        print(f'HTML 長度: {len(html)}')
        print(f'文字長度: {len(text)}')
        print(f'\\n已儲存至 venue_{VENUE_ID}_rules.html 和 venue_{VENUE_ID}_rules.txt')

        # 顯示前 500 字
        print(f'\\n頁面內容預覽:')
        print(text[:500])

        # 找連結
        links = page.locator('a')
        for i in range(min(10, links.count())):
            try:
                href = links.nth(i).get_attribute('href') or ''
                link_text = links.nth(i).evaluate('el => el.textContent') or ''
                if href and ('.doc' in href or '.pdf' in href):
                    print(f'  文檔連結: {link_text[:80]} - {href[:100]}')
            except:
                pass

        context.close()
        browser.close()


if __name__ == '__main__':
    main()
