#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json

# 測試多個無頁面場地
test_venues = [
    (1083, 'https://www.citizenm.com/hotels/asia/taipei/taipei-north-gate', 'citizenM'),
    (1086, 'https://www.regenttaiwan.com/', 'Regent Taipei'),
    (1103, 'https://www.taipeimarriott.com.tw/', 'Marriott Taipei'),
    (1495, 'https://www.meeting.com.tw/', '集思北科'),
    (1034, 'https://nuzone.stpi.narl.org.tw/', 'NUZONE'),
]

print('=== 測試多個無頁面場地 ===\n')

results = []

for venue_id, url, name in test_venues:
    print(f'[{name}] (ID: {venue_id})')
    print(f'URL: {url}')

    try:
        resp = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        soup = BeautifulSoup(resp.text, 'html.parser')
        all_links = soup.find_all('a', href=True)

        # 找 nav/footer
        nav = soup.find('nav')
        footer = soup.find('footer')

        print(f'  狀態: {resp.status_code}')
        print(f'  重定向: {resp.url}')
        print(f'  總連結: {len(all_links)}')
        print(f'  有<nav>: {"Yes" if nav else "No"}')
        print(f'  有<footer>: {"Yes" if footer else "No"}')

        # 找會議相關
        meeting_keywords = ['meeting', '會議', 'banquet', '宴會', 'conference', 'mice', 'events']
        meeting_links = []
        for a in all_links:
            text = a.get_text().lower()
            href = a.get('href', '')
            if any(kw in text or kw in href for kw in meeting_keywords):
                meeting_links.append((a.get_text().strip()[:50], href))

        print(f'  會議連結: {len(meeting_links)}')

        if len(meeting_links) > 0:
            print(f'  ✅ 找到會議資訊!')
            results.append((venue_id, name, 'SUCCESS', len(meeting_links)))
        else:
            print(f'  ❌ 無會議資訊')
            results.append((venue_id, name, 'FAIL', 0))

    except Exception as e:
        print(f'  ❌ Error: {str(e)[:50]}')
        results.append((venue_id, name, 'ERROR', 0))

    print()

print('=== 總結 ===')
success = sum(1 for r in results if r[2] == 'SUCCESS')
print(f'成功: {success}/{len(results)}')

print('\n成功場地:')
for r in results:
    if r[2] == 'SUCCESS':
        print(f'  ID {r[0]}: {r[1]} - {r[3]} 會議連結')

print('\n失敗場地:')
for r in results:
    if r[2] != 'SUCCESS':
        print(f'  ID {r[0]}: {r[1]} - {r[2]}')
