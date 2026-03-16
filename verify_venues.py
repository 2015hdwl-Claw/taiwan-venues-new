#!/usr/bin/env python3
"""
台北市飯店會議室資訊驗證腳本
批次訪問飯店官網，確認會議室資訊
"""

import json
import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, urlparse

# 設定
REQUEST_TIMEOUT = 15
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def load_venues():
    """載入 venues.json"""
    with open('venues.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_venues(venues):
    """儲存 venues.json"""
    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)

def get_taipei_hotels(venues):
    """篩選台北市飯店場地"""
    return [v for v in venues if v.get('city') == '台北市' and v.get('venueType') == '飯店場地']

def fetch_page(url):
    """獲取網頁內容"""
    headers = {'User-Agent': USER_AGENT}
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, verify=False)
        response.encoding = 'utf-8'
        return response.text
    except Exception as e:
        print(f"  ❌ 獲取失敗: {e}")
        return None

def extract_meeting_info(html, base_url):
    """從網頁中提取會議室資訊"""
    if not html:
        return None
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # 尋找會議室相關的關鍵字
    keywords = ['會議', '宴會', 'ballroom', 'meeting', 'conference', 'banquet']
    
    # 提取所有連結
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text().lower()
        if any(kw in text or kw in href.lower() for kw in keywords):
            full_url = urljoin(base_url, href)
            links.append(full_url)
    
    return links

def main():
    print("=== 台北市飯店會議室資訊驗證 ===\n")
    
    # 載入資料
    venues = load_venues()
    taipei_hotels = get_taipei_hotels(venues)
    
    print(f"找到 {len(taipei_hotels)} 個台北市飯店場地\n")
    
    results = []
    
    for i, hotel in enumerate(taipei_hotels, 1):
        print(f"[{i}/{len(taipei_hotels)}] {hotel['name']}")
        print(f"  官網: {hotel.get('url', '無')}")
        
        url = hotel.get('url')
        if not url:
            print("  ⚠️ 無官網 URL\n")
            continue
        
        # 訪問官網
        html = fetch_page(url)
        if html:
            # 提取會議室相關連結
            meeting_links = extract_meeting_info(html, url)
            if meeting_links:
                print(f"  ✓ 找到 {len(meeting_links)} 個會議相關連結")
                results.append({
                    'name': hotel['name'],
                    'url': url,
                    'meeting_links': meeting_links[:5]  # 只取前 5 個
                })
            else:
                print("  ⚠️ 未找到會議室相關連結")
        
        time.sleep(1)  # 避免過度請求
        print()
    
    # 儲存結果
    with open('venue_verification_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n驗證完成！結果已儲存到 venue_verification_results.json")
    print(f"總計處理: {len(taipei_hotels)} 個飯店")
    print(f"找到會議室資訊: {len(results)} 個")

if __name__ == '__main__':
    main()
