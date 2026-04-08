#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests

urls_to_try = [
    'https://www.meeting.com.tw/tc/',
    'https://www.meeting.com.tw/tc/index.php',
    'https://www.meeting.com.tw/tc/index.html',
    'https://www.meeting.com.tw/tc/taichung/',
    'https://www.meeting.com.tw/khh/',
    'https://www.meeting.com.tw/khh/index.php',
    'https://www.meeting.com.tw/khh/index.html',
    'https://www.meeting.com.tw/khh/kaohsiung/',
    'https://www.meeting.com.tw/tcc/',
    'https://www.meeting.com.tw/khc/',
]

print('Testing alternative URLs:')
print('-' * 60)

valid_urls = []

for url in urls_to_try:
    try:
        response = requests.get(url, timeout=10, verify=False)
        if response.status_code == 200:
            print(f'OK: {url}')
            valid_urls.append(url)
        else:
            print(f'HTTP {response.status_code}: {url}')
    except Exception as e:
        print(f'ERROR: {url}')

print()
print(f'Found {len(valid_urls)} valid URLs')

if valid_urls:
    print('\nValid URLs:')
    for url in valid_urls:
        print(f'  - {url}')
