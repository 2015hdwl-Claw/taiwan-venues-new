#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
專門腳本：深度抓取剩餘 3 家飯店的場地資料
"""

import json
import re
import sys
from datetime import datetime

# Windows UTF-8 相容
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

import requests
from bs4 import BeautifulSoup

# 飯店特定的場地頁面 URL
HOTEL_URLS = {
    1069: {  # 台北國賓大飯店
        "name": "台北國賓大飯店",
        "urls": [
            "https://www.ambassador-hotels.com/tc/taipei/occasions",
            "https://www.ambassador-hotels.com/tc/taipei/occasions/meetings"
        ]
    },
    1086: {  # 台北晶華酒店
        "name": "台北晶華酒店",
        "urls": [
            "https://www.regenttaiwan.com/occasions",
            "https://www.regenttaiwan.com/occasions/meetings-events"
        ]
    },
    1090: {  # 茹曦酒店
        "name": "茹曦酒店",
        "urls": [
            "https://www.theillumehotel.com/zh/meetings-events/",
            "https://www.theillumehotel.com/zh/meetings-events/ballroom/"
        ]
    }
}


def scrape_venue_page(url: str) -> dict:
    """深度抓取單一頁面的場地資訊"""
    print(f"\n  抓取: {url[:60]}...")

    try:
        resp = requests.get(url, timeout=20, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        resp.raise_for_status()

        soup = BeautifulSoup(resp.content, 'html.parser')

        # 移除不需要的元素
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()

        # 提取文字
        text = soup.get_text(separator='\n', strip=True)

        # 尋找場地相關資訊
        venues = []
        lines = text.split('\n')

        for i, line in enumerate(lines):
            line_clean = line.strip()

            # 尋找包含場地資訊的行
            if any(kw in line_clean for kw in ['坪', '平方', '公尺', '人', '宴會廳', '會議室', '容量']):
                # 收集前後文
                context = []
                for j in range(max(0, i-2), min(len(lines), i+3)):
                    context_line = lines[j].strip()
                    if context_line and len(context_line) < 100:
                        context.append(context_line)

                if context:
                    venues.append(' | '.join(context))

        return {
            'url': url,
            'text_length': len(text),
            'venues': list(set(venues))  # 去重
        }

    except Exception as e:
        print(f"    ❌ 錯誤: {e}")
        return None


def extract_room_info(text: str) -> list:
    """從文字中提取場地資訊"""
    rooms = []

    # 尋找場地名稱和規格的模式
    patterns = [
        r'([^、\n]{2,10}廳)[^\n]*?(\d+)[^\n]*?坪',
        r'([^、\n]{2,10}廳)[^\n]*?(\d+)[^\n]*?平方',
        r'([^、\n]{2,10}室)[^\n]*?(\d+)[^\n]*?坪',
        r'([^、\n]{2,10}會議室)[^\n]*?(\d+)[^\n]*?人',
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            name = match.group(1)
            spec = match.group(2)
            rooms.append({
                'name': name,
                'spec': spec
            })

    return rooms


def main():
    """主程式"""

    # 讀取 venues.json
    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    print("="*70)
    print("深度抓取 3 家飯店的場地資料")
    print("="*70)

    all_results = {}

    # 抓取每家飯店
    for hotel_id, info in HOTEL_URLS.items():
        print(f"\n{'='*70}")
        print(f"[{hotel_id}] {info['name']}")
        print(f"{'='*70}")

        all_results[hotel_id] = {
            'name': info['name'],
            'pages': [],
            'all_text': ''
        }

        # 抓取所有 URL
        for url in info['urls']:
            result = scrape_venue_page(url)
            if result:
                all_results[hotel_id]['pages'].append(result)
                all_results[hotel_id]['all_text'] += result['text_length'] * ' ' + '\n'.join(result['venues'])

        print(f"\n  ✅ 完成: {len(all_results[hotel_id]['pages'])} 個頁面")
        print(f"     總字元: {len(all_results[hotel_id]['all_text'])}")

        # 顯示找到的場地資訊
        if all_results[hotel_id]['all_text']:
            print(f"\n  場地資訊預覽:")
            for page in all_results[hotel_id]['pages']:
                for venue_info in page['venues'][:5]:
                    print(f"    - {venue_info[:80]}")

    # 儲存結果
    output_file = f'deep_scrape_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*70}")
    print(f"📁 結果已儲存: {output_file}")
    print(f"{'='*70}")

    return all_results


if __name__ == '__main__':
    main()
