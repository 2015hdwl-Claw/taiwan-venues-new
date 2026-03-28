#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analyze venue website structure to create targeted scrapers"""

import sys
import io
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def analyze_venue_structure(url, venue_name):
    """Analyze a venue's website structure"""

    print(f'\n{"=" * 80}')
    print(f'Analyzing: {venue_name}')
    print(f'URL: {url}')
    print('=' * 80)

    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Find all links that might be room/hall pages
        print('\n[1] Finding room/hall links...')
        room_links = []

        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            text = link.get_text(strip=True)

            # Look for venue-specific keywords
            hall_keywords = ['廳', 'hall', 'banquet', '宴會', '會議', 'meeting']
            if any(kw in href or kw in text.lower() for kw in hall_keywords):
                if len(text) > 2 and len(text) < 50:
                    room_links.append({
                        'text': text,
                        'href': link['href']
                    })

        # Remove duplicates and limit
        seen = set()
        unique_links = []
        for link in room_links:
            key = (link['text'], link['href'])
            if key not in seen:
                seen.add(key)
                unique_links.append(link)

        print(f'  Found {len(unique_links)} potential room/hall links:')
        for i, link in enumerate(unique_links[:10], 1):
            print(f'  {i}. {link["text"]}')
            print(f'     URL: {link["href"]}')

        # 2. Sample first room page
        if unique_links:
            print('\n[2] Analyzing first room page...')
            from urllib.parse import urljoin
            first_room_url = urljoin(url, unique_links[0]['href'])

            try:
                room_response = requests.get(first_room_url, timeout=15)
                room_soup = BeautifulSoup(room_response.text, 'html.parser')

                # Look for structured data patterns
                print(f'  Title: {room_soup.title.get_text(strip=True) if room_soup.title else "N/A"}')

                # Check for JSON-LD
                json_ld = room_soup.find('script', type='application/ld+json')
                if json_ld:
                    print('  ✅ Has JSON-LD structured data')

                # Look for common data patterns
                page_text = room_soup.get_text()[:5000]  # First 5000 chars
                print(f'  Page text sample: {page_text[:200]}...')

                # Check for price patterns
                if 'NT$' in page_text or '元' in page_text or '價格' in page_text:
                    print('  ✅ Contains price information')

                # Check for capacity
                if '人' in page_text or '容量' in page_text or '桌' in page_text:
                    print('  ✅ Contains capacity information')

                # Check for dimensions
                if '坪' in page_text or '㎡' in page_text or '平米' in page_text:
                    print('  ✅ Contains area information')

                # Find images
                images = room_soup.find_all('img', src=True)
                print(f'  Found {len(images)} images')

            except Exception as e:
                print(f'  Error analyzing room page: {e}')

        return unique_links[:10]

    except Exception as e:
        print(f'Error: {e}')
        return []


def main():
    print('=' * 80)
    print('Venue Structure Analysis')
    print('=' * 80)

    # Analyze 青青婚宴會館
    qingqing_links = analyze_venue_structure(
        'https://www.77-67.com/',
        '青青婚宴會館'
    )

    # Analyze 台北世貿中心
    twtc_links = analyze_venue_structure(
        'https://www.twtc.com.tw/',
        '台北世貿中心'
    )

    print('\n' + '=' * 80)
    print('Analysis Complete')
    print('=' * 80)
    print(f'青青婚宴會館: {len(qingqing_links)} room links found')
    print(f'台北世貿中心: {len(twtc_links)} room links found')


if __name__ == '__main__':
    main()
