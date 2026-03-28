#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json

# 抓取台北萬豪的會議室頁面
url = 'https://www.taipeimarriott.com.tw/websev?cat=page&id=39'

print(f'抓取: {url}')
response = requests.get(url, timeout=15, verify=False)
print(f'Status: {response.status_code}')

soup = BeautifulSoup(response.text, 'html.parser')

# 尋找會議室資訊
print('\n=== 會議室標題 ===')
for h2 in soup.find_all('h2'):
    print(f'  {h2.get_text().strip()[:80]}')

print('\n=== 會議室表格 ===')
tables = soup.find_all('table')
print(f'找到 {len(tables)} 個表格')

for i, table in enumerate(tables[:3]):
    print(f'\n表格 {i+1}:')
    rows = table.find_all('tr')
    for row in rows[:5]:
        cells = [cell.get_text().strip() for cell in row.find_all(['td', 'th'])]
        print(f'  {" | ".join(cells[:3])}')

print('\n=== 會議室卡片/列表 ===')
# 尋找包含 "廳" 的元素
for elem in soup.find_all(['div', 'li'], class_=True):
    text = elem.get_text().strip()
    if '廳' in text and len(text) < 100:
        print(f'  {text[:80]}')

print('\n=== 所有文字內容 (前2000字) ===')
text = soup.get_text()
print(text[:2000])
