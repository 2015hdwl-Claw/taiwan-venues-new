#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import requests
import re
from bs4 import BeautifulSoup
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Load venues
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

taipei_venues = [v for v in venues if '台北' in v.get('city', '')][:5]

print(f"Testing {len(taipei_venues)} Taipei venues")
print("="*60)

phone_patterns = [
    r'0\d[\d-]{7,9}',
    r'\+886-[\d-]+',
    r'\+886\s?\d[\d-]{7,9}',
]

email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
spam_keywords = ['no-reply', 'noreply', 'donotreply', '@spam', '@test', '@example']

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})

for venue in taipei_venues:
    venue_id = venue.get('id')
    venue_name = venue.get('name')
    url = venue.get('url')
    
    print(f"\n[{venue_id}] {venue_name}")
    
    try:
        response = session.get(url, timeout=10, verify=False)
        response.raise_for_status()
        
        phones = []
        for pattern in phone_patterns:
            matches = re.findall(pattern, response.text)
            valid_phones = [m for m in matches if len(re.sub(r'[\D]', '', m)) >= 7]
            phones.extend(valid_phones)
        
        phones = list(set(phones))[:5]
        
        email_matches = email_pattern.findall(response.text)
        emails = []
        for email in email_matches:
            if not any(spam in email.lower() for spam in spam_keywords):
                emails.append(email)
        
        emails = list(set(emails))[:5]
        
        current_phone = venue.get('contactPhone') or venue.get('contact', {}).get('phone')
        current_email = venue.get('contactEmail') or venue.get('contact', {}).get('email')
        
        print(f"Current phone: {current_phone or '(none)'}")
        print(f"Current email: {current_email or '(none)'}")
        print(f"Found phones: {phones[:3] if phones else '(none)'}")
        print(f"Found emails: {emails[:3] if emails else '(none)'}")
        
        if (not current_phone and phones) or (not current_email and emails):
            print("[OK] Can supplement contact info")
        
    except Exception as e:
        print(f"[ERROR] {str(e)[:50]}")

print()
print("="*60)
print("Test complete")
