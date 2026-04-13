#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度爬取 1532 新北市工商展覽中心的規則頁面
"""

import sys
import json
import re
import os
from bs4 import BeautifulSoup

# Windows UTF-8 輸出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 專案根目錄
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PRO_ROOT)
sys.path.insert(0, PROJECT_ROOT)

VENUE_ID = 1532
VENUES_FILE = os.path.join(PROJECT_ROOT, 'venues.json')


def render_page_with_playwright(url):
    """使用 Playwright 渲染頁面"""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(5000)
        html = page.content()
        browser.close()
        return html


def extract_text_from_html(html):
    """從 HTML 中提取有意義的文字"""
    soup = BeautifulSoup(html, 'html.parser')

    # 移除 script 和 style
    for script in soup(['script', 'style', 'noscript']):
        script.decompose()

    # 取得所有文字
    text = soup.get_text(separator='\n')

    # 清理文字
    lines = []
    for line in text.split('\n'):
        line = line.strip()
        if len(line) >= 5 and len(line) <= 200:
            # 過濾掉純符號或數字的行
            if not re.match(r'^[\W\d_]+$', line):
                lines.append(line)

    return lines


def main():
    urls = [
        'https://www.tcwtc.com.tw/conference-rules.html',
        'https://www.tcwtc.com.tw/how-to-rent-conference-oom.html',
        'https://www.tcwtc.com.tw/conference-room-fee.html',
        'https://www.tcwtc.com.tw/venue-operation-project.html',
    ]

    all_content = []

    for url in urls:
        print(f'=== 爬取: {url} ===')
        try:
            html = render_page_with_playwright(url)
            lines = extract_text_from_html(html)

            print(f'  提取 {len(lines)} 行文字')
            all_content.extend(lines)

        except Exception as e:
            print(f'  [錯誤] {e}')

    # 分析並分類規則
    rules = {
        'catering': [],
        'decoration': [],
        'sound': [],
        'loadIn': [],
        'cancellation': [],
        'payment': [],
        'general': []
    }

    for line in all_content:
        if any(kw in line for kw in ['餐飲', '食物', '外燴', '自備', '廚房', '冰箱', '火', '烹飪']):
            if line not in rules['catering']:
                rules['catering'].append(line)
        elif any(kw in line for kw in ['裝潢', '佈置', '裝飾', '膠帶', '釘子', '海報', '噴漆', '牆面']):
            if line not in rules['decoration']:
                rules['decoration'].append(line)
        elif any(kw in line for kw in ['音量', '噪音', '分貝', '擴音', '音響']):
            if line not in rules['sound']:
                rules['sound'].append(line)
        elif any(kw in line for kw in ['進場', '搬運', '貨梯', '車輛', '動線', '装卸']):
            if line not in rules['loadIn']:
                rules['loadIn'].append(line)
        elif any(kw in line for kw in ['取消', '延期', '退費', '保證金', '訂金']):
            if line not in rules['cancellation']:
                rules['cancellation'].append(line)
        elif any(kw in line for kw in ['付款', '匯款', '定金', '尾款', '繳費']):
            if line not in rules['payment']:
                rules['payment'].append(line)
        else:
            # 一般規則
            if any(kw in line for kw in ['禁止', '不得', '需', '應', '必須', '規定', '注意']):
                if line not in rules['general'] and len(rules['general']) < 20:
                    rules['general'].append(line)

    # 輸出結果
    print('\n=== 規則分析結果 ===')
    for key, value in rules.items():
        if value:
            print(f'\n{key} ({len(value)} 條):')
            for rule in value[:3]:
                print(f'  - {rule}')

    # 儲存結果
    output_file = os.path.join(PROJECT_ROOT, f'venue_{VENUE_ID}_rules.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(rules, f, ensure_ascii=False, indent=2)

    print(f'\n[完成] 規則已儲存至 {output_file}')


if __name__ == '__main__':
    main()
