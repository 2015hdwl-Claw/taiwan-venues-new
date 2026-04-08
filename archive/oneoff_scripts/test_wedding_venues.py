#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import sys
import io

# Fix encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def test_wedding_venue(venue_data):
    """測試單個婚宴場地"""
    vid = venue_data['id']
    name = venue_data['name']
    url = venue_data['url']
    vtype = venue_data['venueType']

    print(f'\n[婚宴場地] ID {vid}: {name}')
    print(f'URL: {url}')
    print('-'*60)

    result = {
        'id': vid,
        'name': name,
        'venueType': vtype,
        'url': url,
        'tested_at': datetime.now().isoformat()
    }

    try:
        # 測試1: 檢測網頁類型
        print('[1] 檢測網頁類型...')

        # 檢查 WordPress API
        api_url = urljoin(url, '/wp-json/wp/v2/pages')
        try:
            api_resp = requests.get(api_url, timeout=5)
            if api_resp.status_code == 200:
                print('    類型: WordPress API')
                result['pageType'] = 'WordPress API'
            else:
                print(f'    無WordPress API (status {api_resp.status_code})')
        except:
            print('    無WordPress API')

        if 'pageType' not in result:
            # 檢查靜態內容
            resp = requests.get(url, timeout=10, verify=False)
            soup = BeautifulSoup(resp.text, 'html.parser')

            text = soup.get_text().lower()

            # 婚宴關鍵字
            wedding_keywords = ['婚宴', '婚禮', '宴會', 'banquet', 'wedding']
            has_wedding = sum(1 for kw in wedding_keywords if kw in text)

            if has_wedding >= 2:
                print(f'    類型: Static/SSR (有{has_wedding}個婚宴關鍵字)')
                result['pageType'] = 'Static/SSR'
            else:
                print('    類型: 可能需要 JS 渲染')
                result['pageType'] = 'JavaScript (CSR)'

        # 測試2: 擷取基本資料
        print('[2] 擷取基本資料...')

        resp = requests.get(url, timeout=10, verify=False)
        soup = BeautifulSoup(resp.text, 'html.parser')

        # 電話
        import re
        phones = re.findall(r'0\d-\d{4}-\d{4}', soup.get_text())
        if phones:
            print(f'    電話: {phones[0]}')
            result['phone'] = phones[0]

        # Email
        emails = re.findall(r'[\w.-]+@[\w.-]+\.\w+', soup.get_text())
        if emails:
            print(f'    Email: {emails[0]}')
            result['email'] = emails[0]

        # 測試3: 尋找宴會/婚宴相關連結
        print('[3] 尋找宴會/婚宴連結...')

        banquet_keywords = ['宴會', '婚宴', '婚禮', 'banquet', 'wedding', '婚禮廳', '宴會廳']
        banquet_links = []

        for a in soup.find_all('a', href=True):
            text = a.get_text().strip().lower()
            href = a['href'].lower()

            if any(kw in text or kw in href for kw in banquet_keywords):
                full_url = urljoin(url, a['href'])
                banquet_links.append({
                    'text': a.get_text().strip()[:30],
                    'url': full_url
                })

        print(f'    找到 {len(banquet_links)} 個宴會連結')
        result['banquet_links_count'] = len(banquet_links)

        if banquet_links:
            print(f'    範例: {banquet_links[0]["text"]}: {banquet_links[0]["url"][:50]}')

        # 測試4: 統計連結數
        all_links = soup.find_all('a', href=True)
        print(f'[4] 總連結數: {len(all_links)}')
        result['total_links'] = len(all_links)

        result['success'] = True

    except Exception as e:
        print(f'    錯誤: {str(e)[:100]}')
        result['success'] = False
        result['error'] = str(e)

    return result


def main():
    # 讀取 venues.json
    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    # 找出婚宴相關場地
    wedding_venues = []
    for v in venues:
        if v.get('status') == 'discontinued':
            continue

        venue_type = v.get('venueType', '').lower()
        name = v.get('name', '').lower()

        if ('婚宴' in venue_type or 'wedding' in venue_type or
            '飯店' in venue_type or 'hotel' in venue_type or
            '宴' in name or 'banquet' in name):
            wedding_venues.append(v)

    print('='*80)
    print(f'測試婚宴場地（共 {len(wedding_venues)} 個）')
    print('='*80)

    # 測試前5個
    test_venues = wedding_venues[:5]
    results = []

    for i, venue in enumerate(test_venues, 1):
        print(f'\n[{i}/{len(test_venues)}]')
        result = test_wedding_venue(venue)
        results.append(result)

    # 儲存結果
    report = {
        'tested_at': datetime.now().isoformat(),
        'total_wedding_venues': len(wedding_venues),
        'tested_count': len(test_venues),
        'results': results
    }

    with open('wedding_venues_test.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print('\n' + '='*80)
    print(f'測試完成！共 {len(results)} 個場地')
    print('詳細結果已儲存到 wedding_venues_test.json')

    # 統計
    static = sum(1 for r in results if r.get('pageType') == 'Static/SSR')
    api_count = sum(1 for r in results if r.get('pageType') == 'WordPress API')
    js = sum(1 for r in results if r.get('pageType') == 'JavaScript (CSR)')

    print('\n統計:')
    print(f'  Static/SSR: {static}')
    print(f'  WordPress API: {api_count}')
    print(f'  JavaScript: {js}')

    # 宴會連結統計
    banquet_counts = [r.get('banquet_links_count', 0) for r in results]
    if banquet_counts:
        avg = sum(banquet_counts) / len(banquet_counts)
        print(f'\n平均宴會連結數: {avg:.1f}')


if __name__ == '__main__':
    main()
