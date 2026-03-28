#!/usr/bin/env python3
"""
會議室資料分析工具
分析場地官網的會議室資訊結構
"""
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

def analyze_venue_meeting_rooms(venue_url, venue_id):
    """分析場地的會議室資訊"""

    print(f'分析場地 ID {venue_id}')
    print(f'URL: {venue_url}')
    print('='*60)

    try:
        response = requests.get(venue_url, timeout=15, verify=False)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. 尋找會議室相關連結
        meeting_keywords = ['meeting', '會議', 'banquet', '宴會', 'conference', '會議室', '場地']
        all_links = soup.find_all('a', href=True)

        meeting_links = []
        for link in all_links:
            text = link.get_text().strip().lower()
            href = link['href'].lower()

            if any(kw in text or kw in href for kw in meeting_keywords):
                full_url = urljoin(venue_url, link['href'])
                meeting_links.append({
                    'text': link.get_text().strip(),
                    'url': full_url
                })

        print(f'找到 {len(meeting_links)} 個會議相關連結')

        # 顯示前5個連結
        for i, link in enumerate(meeting_links[:5], 1):
            print(f'{i}. {link["text"][:50]}')
            print(f'   {link["url"]}')

        # 2. 抓取第一個會議室頁面
        if meeting_links:
            meeting_url = meeting_links[0]['url']
            print(f'\n深入分析: {meeting_url}')

            try:
                meeting_response = requests.get(meeting_url, timeout=15, verify=False)
                meeting_soup = BeautifulSoup(meeting_response.text, 'html.parser')

                # 尋找會議室資訊
                # 常見的結構：
                # - 表格
                # - 列表
                # - 卡片

                rooms_found = []

                # 方法1: 尋找包含 "會議室" 或 "Room" 的標題
                for heading in meeting_soup.find_all(['h1', 'h2', 'h3', 'h4']):
                    text = heading.get_text().strip()
                    if any(kw in text for kw in ['會議室', 'Room', '宴會廳', 'Hall']):
                        print(f'\n找到標題: {text}')

                        # 找這個標題後面的內容
                        next_elem = heading.find_next()
                        if next_elem:
                            content = next_elem.get_text().strip()[:200]
                            print(f'內容: {content}...')

            except Exception as e:
                print(f'抓取會議室頁面失敗: {e}')

        return {
            'venue_id': venue_id,
            'url': venue_url,
            'meeting_links_count': len(meeting_links),
            'meeting_links': meeting_links[:10]
        }

    except Exception as e:
        print(f'分析失敗: {e}')
        return None

# 測試一個場地
if __name__ == '__main__':
    # 讀取 venues.json
    with open('venues.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 找一個有 URL 的場地
    test_venue = None
    for venue in data:
        if venue.get('url') and venue.get('status') != 'discontinued':
            test_venue = venue
            break

    if test_venue:
        analyze_venue_meeting_rooms(test_venue['url'], test_venue['id'])
