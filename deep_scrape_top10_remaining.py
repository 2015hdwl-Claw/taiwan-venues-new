#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deep scrape remaining Top 10 venues

Target venues:
1. 青青婚宴會館 (ID: 1129) - Scrape detail pages
2. 台北世貿中心 (ID: 1049) - Scrape detail pages

Uses new deep scraping methodology:
- Check for JavaScript variables (priority 1)
- Check for JSON-LD (priority 2)
- Check for detail pages (priority 3)
"""

import sys
import io
import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, urlparse

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class DeepScraper:
    """Enhanced scraper with JavaScript variable extraction"""

    def __init__(self, venue_id, venue_name, venue_url):
        self.venue_id = venue_id
        self.venue_name = venue_name
        self.venue_url = venue_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def check_data_sources(self, url):
        """Check all possible data sources"""
        sources = {
            'javascript_variables': [],
            'json_ld': False,
            'detail_pages': []
        }

        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')

            # 1. Check JavaScript variables
            js_patterns = [
                r'var\s+(room_data|venue_data|event_data|space_data|meeting_data)\s*=',
                r'const\s+(room_data|venue_data|event_data|space_data|meeting_data)\s*=',
            ]

            for pattern in js_patterns:
                matches = re.findall(pattern, html_content)
                if matches:
                    sources['javascript_variables'].extend(matches)

            sources['javascript_variables'] = list(set(sources['javascript_variables']))

            # 2. Check JSON-LD
            if '<script type="application/ld+json">' in html_content:
                sources['json_ld'] = True

            # 3. Check detail pages
            detail_keywords = ['detail', 'banquet', 'hall', 'room', 'space']
            for link in soup.find_all('a', href=True):
                href = link['href'].lower()
                text = link.get_text(strip=True)
                if any(kw in href for kw in detail_keywords) and len(text) > 2:
                    full_url = urljoin(url, link['href'])
                    sources['detail_pages'].append({
                        'url': full_url,
                        'text': text[:50]
                    })
                    if len(sources['detail_pages']) >= 10:
                        break

        except Exception as e:
            print(f"Error checking data sources: {e}")

        return sources

    def extract_from_js_variable(self, html_content, var_name):
        """Extract data from JavaScript variable"""
        pattern = rf'{var_name}\s*=\s*(\[.*?\]);'
        match = re.search(pattern, html_content, re.DOTALL)

        if match:
            try:
                json_str = match.group(1)
                data = json.loads(json_str)
                return data
            except:
                pass
        return None

    def scrape_detail_page(self, detail_url):
        """Scrape a single detail page"""
        try:
            response = self.session.get(detail_url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            room_data = {
                'name': soup.title.get_text(strip=True) if soup.title else '',
                'capacity': self.extract_capacity(soup),
                'area': self.extract_area(soup),
                'equipment': self.extract_equipment(soup),
                'price': self.extract_price(soup),
                'description': self.extract_description(soup),
                'images': self.extract_images(soup, detail_url)
            }

            return room_data
        except Exception as e:
            print(f"  Error scraping {detail_url}: {e}")
            return None

    def extract_capacity(self, soup):
        """Extract capacity from page"""
        # Try multiple patterns
        patterns = [
            r'容量[：:]\s*(\d+)',
            r'人數[：:]\s*(\d+)',
            r'(\d+)\s*人',
            r'capacity[：:]\s*(\d+)',
        ]

        page_text = soup.get_text()
        for pattern in patterns:
            match = re.search(pattern, page_text)
            if match:
                return int(match.group(1))

        return None

    def extract_area(self, soup):
        """Extract area from page"""
        patterns = [
            r'面積[：:]\s*(\d+\.?\d*)\s*(坪|平方米|㎡)',
            r'(\d+\.?\d*)\s*坪',
        ]

        page_text = soup.get_text()
        for pattern in patterns:
            match = re.search(pattern, page_text)
            if match:
                return float(match.group(1))

        return None

    def extract_equipment(self, soup):
        """Extract equipment list"""
        # Look for equipment/facility sections
        equipment_sections = soup.find_all(['div', 'section'],
                                          class_=re.compile(r'equip|facility|設備', re.I))
        if equipment_sections:
            return equipment_sections[0].get_text(strip=True)

        # Fallback to keyword search
        page_text = soup.get_text()
        keywords = ['投影', '音響', '麥克風', '投影機', 'screen', 'projector', 'microphone']
        found = [kw for kw in keywords if kw in page_text]
        return ', '.join(found) if found else None

    def extract_price(self, soup):
        """Extract price information"""
        patterns = [
            r'NT\$?\s*([\d,]+)',
            r'TWD\s*([\d,]+)',
            r'([\d,]+)\s*元',
        ]

        page_text = soup.get_text()
        for pattern in patterns:
            match = re.search(pattern, page_text)
            if match:
                price_str = match.group(1).replace(',', '')
                try:
                    return int(price_str)
                except:
                    pass

        return None

    def extract_description(self, soup):
        """Extract description"""
        # Look for meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', '')

        # Fallback to first paragraph
        p = soup.find('p')
        if p:
            return p.get_text(strip=True)[:200]

        return ''

    def extract_images(self, soup, base_url):
        """Extract room images"""
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            if any(kw in src.lower() for kw in ['room', 'hall', 'banquet', '會議', '宴會']):
                full_url = urljoin(base_url, src)
                images.append(full_url)
                if len(images) >= 5:
                    break
        return images

    def scrape(self):
        """Main scraping method"""
        print(f'\n{"=" * 80}')
        print(f'Scraping: {self.venue_name} (ID: {self.venue_id})')
        print(f'URL: {self.venue_url}')
        print('=' * 80)

        # Step 1: Check data sources
        print('\n[1/4] Checking data sources...')
        sources = self.check_data_sources(self.venue_url)

        if sources['javascript_variables']:
            print(f"  Found JavaScript variables: {', '.join(sources['javascript_variables'])}")
            print("  RECOMMENDATION: Extract JavaScript variables (fastest, most accurate)")

        if sources['json_ld']:
            print("  Found JSON-LD structured data")

        if sources['detail_pages']:
            print(f"  Found {len(sources['detail_pages'])} detail pages")

        # Step 2: Try to extract from JS variables first (priority 1)
        rooms = []
        if sources['javascript_variables']:
            print('\n[2/4] Attempting JavaScript variable extraction...')
            try:
                response = self.session.get(self.venue_url, timeout=15)
                html_content = response.text

                for var_name in sources['javascript_variables'][:1]:  # Try first one
                    data = self.extract_from_js_variable(html_content, var_name)
                    if data:
                        print(f"  Successfully extracted from {var_name}")
                        print(f"  Data type: {type(data).__name__}, length: {len(data) if isinstance(data, (list, dict)) else 'N/A'}")
                        # Process the data (venue-specific handling)
                        rooms = self.process_js_data(data)
                        if rooms:
                            break
            except Exception as e:
                print(f"  JS extraction failed: {e}")

        # Step 3: Fallback to detail page scraping
        if not rooms and sources['detail_pages']:
            print(f'\n[2/4] Scraping {len(sources["detail_pages"])} detail pages...')
            for i, detail in enumerate(sources['detail_pages'][:5], 1):  # Max 5 pages
                print(f"  [{i}/{min(5, len(sources["detail_pages"]))}] {detail['text']}")
                room_data = self.scrape_detail_page(detail['url'])
                if room_data:
                    rooms.append(room_data)

        # Step 4: Return results
        print(f'\n[3/4] Results:')
        print(f'  Total rooms extracted: {len(rooms)}')

        if rooms:
            for i, room in enumerate(rooms[:5], 1):  # Show first 5
                cap = room.get('capacity') or 'N/A'
                area = room.get('area') or 'N/A'
                price = room.get('price') or 'N/A'
                print(f'  {i}. {room.get("name", "Unknown")}: {cap} people / {area} ping / NT${price}')

        return rooms

    def process_js_data(self, data):
        """Process JavaScript variable data (override per venue)"""
        # Default implementation - can be overridden
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'rooms' in data:
            return data['rooms']
        return []


def scrape_qingqing():
    """Scrape 青青婚宴會館 (ID: 1129)"""
    scraper = DeepScraper(
        venue_id=1129,
        venue_name='青青婚宴會館',
        venue_url='https://www.77-67.com/'
    )
    return scraper.scrape()


def scrape_twtc():
    """Scrape 台北世貿中心 (ID: 1049)"""
    scraper = DeepScraper(
        venue_id=1049,
        venue_name='台北世貿中心',
        venue_url='https://www.twtc.com.tw/'
    )
    return scraper.scrape()


def main():
    """Main execution"""
    print('=' * 80)
    print('Deep Scraping - Top 10 Remaining Venues')
    print('=' * 80)

    # Load venues.json
    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    results = {}

    # Scrape 青青婚宴會館
    print('\n' + '=' * 80)
    print('VENUE 1/2: 青青婚宴會館 (ID: 1129)')
    print('=' * 80)
    qingqing_rooms = scrape_qingqing()
    results[1129] = qingqing_rooms

    # Scrape 台北世貿中心
    print('\n' + '=' * 80)
    print('VENUE 2/2: 台北世貿中心 (ID: 1049)')
    print('=' * 80)
    twtc_rooms = scrape_twtc()
    results[1049] = twtc_rooms

    # Summary
    print('\n' + '=' * 80)
    print('SUMMARY')
    print('=' * 80)
    print(f'青青婚宴會館 (1129): {len(qingqing_rooms)} rooms extracted')
    print(f'台北世貿中心 (1049): {len(twtc_rooms)} rooms extracted')
    print(f'\nTotal: {len(qingqing_rooms) + len(twtc_rooms)} rooms')

    return results


if __name__ == '__main__':
    main()
