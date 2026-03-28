#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract meeting page content for 茹曦酒店
"""

import requests
from bs4 import BeautifulSoup
import sys
import re

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

url = 'https://www.theillumehotel.com/zh/meeting'
print(f"Fetching: {url}\n")

response = requests.get(url, timeout=15, verify=False)
soup = BeautifulSoup(response.text, 'html.parser')

print("Title:", soup.title.string if soup.title else "No title")
print("\n" + "=" * 100 + "\n")

# Get page text
page_text = soup.get_text()

# Print first 5000 chars
print(page_text[:5000])

print("\n" + "=" * 100 + "\n")

# Look for room names
room_patterns = [
    r'會議室[：:\s]*([^\n]+)',
    r'宴會廳[：:\s]*([^\n]+)',
    r'Room[：:\s]*([^\n]+)',
]

for pattern in room_patterns:
    matches = re.findall(pattern, page_text)
    if matches:
        print(f"Pattern '{pattern}' matches:")
        for m in matches[:10]:
            print(f"  - {m.strip()}")
