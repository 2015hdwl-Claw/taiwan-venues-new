#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Three-Stage Venue Scraper - Strict Workflow
Stage 1: Technical Detection
Stage 2: Deep Scraping
Stage 3: Validation & Write
"""

import requests
from bs4 import BeautifulSoup
import json
import shutil
from datetime import datetime
import sys
import re
import warnings
warnings.filterwarnings('ignore')

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("Three-Stage Venue Scraper - Strict Workflow")
print("=" * 100)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Read venues.json
with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

# Backup
backup_file = f"venues.json.backup.threestage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
shutil.copy2('venues.json', backup_file)
print(f"Backup: {backup_file}\n")

# Low quality venues to process
target_venues = [
    (1499, '高雄國際會議中心', 'https://www.meeting.com.tw/khh/'),
    (1501, '安順文旅', 'https://www.amforahotel.com.tw/ambanew/'),
    (1502, '台灣晶豐酒店', 'https://www.chinapalace.com.tw/'),
    (1503, '裕珍花園酒店', 'https://www.yuzenhotel.com.tw/'),
    (1505, '漢來大飯店', 'https://www.hanlai-hotel.com.tw/'),
    (1526, '蓮潭國際會館', 'TBD'),
    (1529, '福客來南北樓', 'TBD'),
    (1530, '富苑喜宴會館', 'TBD'),
    (1536, '高雄國際會議中心 (ICCK)', 'https://www.icck.com.tw/'),
    (1539, '震大金鬱金香酒店', 'https://www.goldentulip-zendahotel.com/'),
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

def stage1_technical_detection(url, venue_name):
    """Stage 1: Technical Detection"""
    print("\n" + "=" * 100)
    print(f"STAGE 1: TECHNICAL DETECTION - {venue_name}")
    print("=" * 100)
    print(f"URL: {url}\n")

    detection_report = {
        'url': url,
        'venue_name': venue_name,
        'can_proceed': False,
        'http_status': None,
        'content_type': None,
        'final_url': None,
        'page_type': None,
        'js_framework': None,
        'cms_type': None,
        'data_location': [],
        'anti_scraping': None,
        'recommendation': None
    }

    if url == 'TBD' or not url:
        print("[X] URL is TBD - CANNOT PROCEED")
        detection_report['recommendation'] = 'SKIP - URL TBD'
        return detection_report

    try:
        # 1.1 HTTP Status Detection
        print("[1.1] HTTP Status Detection...")
        r = requests.get(url, timeout=15, verify=False, headers=headers, allow_redirects=True)
        detection_report['http_status'] = r.status_code
        detection_report['final_url'] = r.url
        detection_report['content_type'] = r.headers.get('Content-Type', '')

        print(f"  Status: {r.status_code}")
        print(f"  Content-Type: {detection_report['content_type']}")
        print(f"  Final URL: {r.url}")

        if r.status_code not in [200, 202]:
            print(f"  [X] HTTP {r.status_code} - Cannot proceed")
            detection_report['recommendation'] = f'SKIP - HTTP {r.status_code}'
            return detection_report

        # 1.2 Page Type Detection
        print("\n[1.2] Page Type Detection...")
        soup = BeautifulSoup(r.text, 'html.parser')

        # Check for JS frameworks
        scripts = soup.find_all('script', src=True)
        js_frameworks = []
        for script in scripts:
            src = script['src'].lower()
            if 'react' in src:
                js_frameworks.append('React')
            if 'vue' in src:
                js_frameworks.append('Vue')
            if 'angular' in src:
                js_frameworks.append('Angular')
            if 'jquery' in src:
                js_frameworks.append('jQuery')

        detection_report['js_framework'] = js_frameworks if js_frameworks else 'None detected'
        print(f"  JS Frameworks: {detection_report['js_framework']}")

        # Check if content is dynamically loaded
        page_text = soup.get_text()
        if len(page_text.strip()) < 500:
            detection_report['page_type'] = 'Dynamic JS (likely)'
            print(f"  Page Type: Dynamic JS (little content in HTML)")
        else:
            detection_report['page_type'] = 'Static HTML'
            print(f"  Page Type: Static HTML ({len(page_text)} chars)")

        # 1.3 CMS Detection
        print("\n[1.3] CMS Detection...")
        generator = soup.find('meta', {'name': 'generator'})
        if generator:
            detection_report['cms_type'] = generator.get('content', 'Unknown')
        else:
            # Check common CMS patterns
            if '/wp-content/' in r.text:
                detection_report['cms_type'] = 'WordPress'
            elif 'drupal' in r.text.lower():
                detection_report['cms_type'] = 'Drupal'
            else:
                detection_report['cms_type'] = 'Custom/Unknown'

        print(f"  CMS: {detection_report['cms_type']}")

        # 1.4 Data Location Detection
        print("\n[1.4] Data Location Detection...")

        # Check for JSON-LD
        json_ld = soup.find('script', type='application/ld+json')
        if json_ld:
            detection_report['data_location'].append('JSON-LD')
            print(f"  [V] JSON-LD found")

        # Check for embedded JSON
        if 'var' in r.text and '{' in r.text:
            detection_report['data_location'].append('Embedded JSON')
            print(f"  [V] Embedded JSON found")

        # Check for meeting/conference links
        meeting_links = soup.find_all('a', href=re.compile(r'(meeting|conference|banquet|會議|宴會|婚禮)', re.I))
        if meeting_links:
            detection_report['data_location'].append(f'Meeting links ({len(meeting_links)} found)')
            print(f"  [V] Meeting links: {len(meeting_links)}")

        # Check for PDFs
        pdf_links = soup.find_all('a', href=re.compile(r'\.pdf', re.I))
        if pdf_links:
            detection_report['data_location'].append(f'PDF files ({len(pdf_links)} found)')
            print(f"  [V] PDF links: {len(pdf_links)}")

        if not detection_report['data_location']:
            detection_report['data_location'].append('HTML content only')
            print(f"  [~] HTML content only (no structured data)")

        # 1.5 Anti-Scraping Detection
        print("\n[1.5] Anti-Scraping Detection...")

        # Check for Cloudflare
        if 'cloudflare' in r.text.lower():
            detection_report['anti_scraping'] = 'Cloudflare detected'
            print(f"  [!] Cloudflare detected")

        # Check for cookie requirements
        if 'cookie' in r.headers.get('Set-Cookie', '').lower():
            detection_report['anti_scraping'] = detection_report['anti_scraping'] + ' + Cookies' if detection_report['anti_scraping'] else 'Cookies required'
            print(f"  [!] Cookies required")

        if not detection_report['anti_scraping']:
            detection_report['anti_scraping'] = 'None detected'
            print(f"  [V] No anti-scraping detected")

        # Decision
        print("\n" + "-" * 100)
        if r.status_code == 200 and detection_report['anti_scraping'] == 'None detected':
            print("[V] CAN PROCEED TO STAGE 2")
            detection_report['can_proceed'] = True
            detection_report['recommendation'] = 'PROCEED - Static HTML scraping'
        elif r.status_code == 200 and detection_report['anti_scraping']:
            print("[~] CAN PROCEED WITH CAUTION")
            detection_report['can_proceed'] = True
            detection_report['recommendation'] = f'PROCEED - Handle {detection_report["anti_scraping"]}'
        else:
            print("[X] CANNOT PROCEED")
            detection_report['recommendation'] = 'SKIP - Technical issues'

        return detection_report

    except requests.exceptions.ConnectionError as e:
        print(f"  [X] Connection Error: {e}")
        detection_report['recommendation'] = 'SKIP - DNS/Connection failure'
        return detection_report
    except requests.exceptions.Timeout as e:
        print(f"  [X] Timeout Error: {e}")
        detection_report['recommendation'] = 'SKIP - Timeout'
        return detection_report
    except Exception as e:
        print(f"  [X] Error: {e}")
        detection_report['recommendation'] = f'SKIP - {type(e).__name__}'
        return detection_report

def stage2_deep_scraping(detection_report):
    """Stage 2: Deep Scraping based on Stage 1 findings"""
    print("\n" + "=" * 100)
    print(f"STAGE 2: DEEP SCRAPING - {detection_report['venue_name']}")
    print("=" * 100)

    if not detection_report['can_proceed']:
        print("[X] Skipping Stage 2 - Technical issues in Stage 1")
        return None

    scraped_data = {
        'venue_name': detection_report['venue_name'],
        'url': detection_report['url'],
        'success': False,
        'data': {}
    }

    try:
        url = detection_report['final_url'] or detection_report['url']

        # Level 1: Main page analysis
        print("\n[Level 1] Main Page Analysis...")
        r = requests.get(url, timeout=20, verify=False, headers=headers, allow_redirects=True)
        soup = BeautifulSoup(r.text, 'html.parser')
        page_text = soup.get_text()

        # Extract ALL links (not just common paths)
        all_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)
            if href and not href.startswith(('javascript:', 'mailto:', 'tel:')):
                # Convert relative URLs to absolute
                if not href.startswith('http'):
                    from urllib.parse import urljoin
                    href = urljoin(url, href)
                all_links.append({'href': href, 'text': text})

        print(f"  Total links found: {len(all_links)}")

        # Classify links
        meeting_links = []
        pdf_links = []
        contact_links = []

        for link in all_links:
            href_lower = link['href'].lower()
            text_lower = link['text'].lower()

            if any(kw in href_lower or kw in text_lower for kw in ['meeting', 'conference', 'banquet', '會議', '宴會', '婚禮', '活動', 'event']):
                meeting_links.append(link)
            if '.pdf' in href_lower:
                pdf_links.append(link)
            if any(kw in href_lower or kw in text_lower for kw in ['contact', 'about', '關於', '聯絡']):
                contact_links.append(link)

        print(f"  Meeting-related links: {len(meeting_links)}")
        print(f"  PDF links: {len(pdf_links)}")
        print(f"  Contact links: {len(contact_links)}")

        # Level 2: Visit meeting pages (up to 3)
        print("\n[Level 2] Meeting Page Discovery...")
        visited_pages = [url]

        for link in meeting_links[:3]:
            if link['href'] not in visited_pages:
                print(f"  Visiting: {link['text'][:50]} - {link['href']}")
                try:
                    r2 = requests.get(link['href'], timeout=15, verify=False, headers=headers)
                    if r2.status_code == 200:
                        visited_pages.append(link['href'])
                        soup2 = BeautifulSoup(r2.text, 'html.parser')
                        page_text += soup2.get_text()
                        print(f"    [V] Success - Total content: {len(page_text)} chars")
                except Exception as e:
                    print(f"    [X] Error: {e}")

        # Level 3: Extract complete data
        print("\n[Level 3] Complete Data Extraction...")

        # Extract phone
        phone = None
        phone_patterns = [
            r'0\d-\d{3,4}-\d{3,4}',
            r'\+886-[\d-]+',
            r'\+886\s?\d[\d-]{7,9}',
            r'\d{2,3}-\d{3,4}-\d{3,4}'
        ]
        for pattern in phone_patterns:
            match = re.search(pattern, page_text)
            if match:
                phone = match.group()
                break

        if phone:
            print(f"  [V] Phone: {phone}")
            scraped_data['data']['phone'] = phone

        # Extract email
        email = None
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', page_text)
        if email_match:
            email_candidate = email_match.group()
            if 'noreply' not in email_candidate.lower() and 'no-reply' not in email_candidate.lower():
                email = email_candidate
                print(f"  [V] Email: {email}")
                scraped_data['data']['email'] = email

        # Extract rooms
        rooms = re.findall(r'([^\s]{2,10}[廳室房])(?:\s|[,，.。、\n])', page_text)
        if rooms:
            unique_rooms = list(set(rooms))[:20]
            print(f"  [V] Rooms found: {len(unique_rooms)}")
            scraped_data['data']['room_names'] = unique_rooms

        # Extract capacities
        capacities = re.findall(r'(\d+)\s*[人名桌者席位]', page_text)
        if capacities:
            caps = [int(c) for c in capacities if 5 <= int(c) <= 5000]
            print(f"  [V] Capacities: {caps[:20]}")
            scraped_data['data']['capacities'] = caps

        # Extract areas
        areas = re.findall(r'(\d+|\d+\.\d+)\s*([坪平方公尺㎡㎡²])', page_text)
        if areas:
            print(f"  [V] Areas: {len(areas)} found")
            scraped_data['data']['areas'] = areas[:20]

        # Extract prices
        prices = re.findall(r'(\d+,?\d*)\s*元', page_text)
        if prices:
            print(f"  [V] Prices: {len(prices)} found")
            scraped_data['data']['prices'] = prices[:20]

        # Extract PDFs
        if pdf_links:
            pdf_urls = [link['href'] for link in pdf_links]
            print(f"  [V] PDFs: {len(pdf_urls)}")
            scraped_data['data']['pdfs'] = pdf_urls[:10]

        scraped_data['success'] = True

        print("\n[V] STAGE 2 COMPLETE")
        return scraped_data

    except Exception as e:
        print(f"[X] Error in Stage 2: {e}")
        import traceback
        traceback.print_exc()
        scraped_data['success'] = False
        return scraped_data

def stage3_validation_write(venue_id, scraped_data):
    """Stage 3: Validation & Write"""
    print("\n" + "=" * 100)
    print(f"STAGE 3: VALIDATION & WRITE - Venue ID {venue_id}")
    print("=" * 100)

    venue = next((v for v in venues if v['id'] == venue_id), None)
    if not venue:
        print("[X] Venue not found!")
        return False

    if not scraped_data or not scraped_data.get('success'):
        print("[X] No valid data to write")
        return False

    data = scraped_data['data']

    # Validation checklist
    print("\n[Validation Checklist]")

    checks = {
        'phone': False,
        'email': False,
        'rooms': False,
        'capacities': False,
        'areas': False,
        'prices': False
    }

    # Check phone
    if 'phone' in data:
        checks['phone'] = True
        venue['contact']['phone'] = data['phone']
        print(f"  [V] Phone: {data['phone']}")
    else:
        print(f"  [X] Phone: Missing")

    # Check email
    if 'email' in data:
        checks['email'] = True
        venue['contact']['email'] = data['email']
        print(f"  [V] Email: {data['email']}")
    else:
        print(f"  [X] Email: Missing")

    # Check rooms
    if 'room_names' in data and data['room_names']:
        checks['rooms'] = True
        print(f"  [V] Rooms: {len(data['room_names'])} found")
    else:
        print(f"  [X] Rooms: Missing")

    # Check capacities
    if 'capacities' in data and data['capacities']:
        checks['capacities'] = True
        print(f"  [V] Capacities: {len(data['capacities'])} found")
    else:
        print(f"  [X] Capacities: Missing")

    # Check areas
    if 'areas' in data and data['areas']:
        checks['areas'] = True
        print(f"  [V] Areas: {len(data['areas'])} found")
    else:
        print(f"  [X] Areas: Missing")

    # Check prices
    if 'prices' in data and data['prices']:
        checks['prices'] = True
        print(f"  [V] Prices: {len(data['prices'])} found")
    else:
        print(f"  [X] Prices: Missing")

    # Calculate quality score
    quality = 35
    if checks['phone']:
        quality += 10
    if checks['email']:
        quality += 10
    if checks['rooms']:
        quality += len(data.get('room_names', [])) * 3
    if checks['capacities']:
        quality += 5
    if checks['areas']:
        quality += 3
    if checks['prices']:
        quality += 10
    if 'pdfs' in data:
        quality += 5

    venue['metadata']['qualityScore'] = min(quality, 100)
    venue['metadata']['lastScrapedAt'] = datetime.now().isoformat()
    venue['metadata']['scrapeVersion'] = "V3_ThreeStage"
    venue['verified'] = False

    # Build room data if we have capacities
    if 'capacities' in data and data['capacities']:
        max_cap = max(data['capacities'])
        room_data = {
            'name': 'Meeting Room',
            'capacity': {
                'theater': max_cap,
                'banquet': int(max_cap * 0.8),
                'classroom': int(max_cap * 0.5)
            },
            'source': 'threestage_20260327'
        }

        if 'room_names' in data and data['room_names']:
            room_data['name'] = data['room_names'][0]

        venue['rooms'] = [room_data]
        venue['capacity'] = room_data['capacity']

    print(f"\n[Quality Score] {venue['metadata']['qualityScore']}")
    print("\n[V] STAGE 3 COMPLETE - Data written to venues.json")

    return True

# Execute three-stage workflow for each venue
results = {
    'processed': 0,
    'stage1_passed': 0,
    'stage2_passed': 0,
    'stage3_passed': 0,
    'failed': 0
}

for vid, name, url in target_venues:
    print("\n" + "=" * 100)
    print(f"PROCESSING: ID {vid} - {name}")
    print("=" * 100)

    # Stage 1: Technical Detection
    detection = stage1_technical_detection(url, name)
    results['processed'] += 1

    if detection['can_proceed']:
        results['stage1_passed'] += 1

        # Stage 2: Deep Scraping
        scraped = stage2_deep_scraping(detection)

        if scraped and scraped['success']:
            results['stage2_passed'] += 1

            # Stage 3: Validation & Write
            if stage3_validation_write(vid, scraped):
                results['stage3_passed'] += 1
        else:
            results['failed'] += 1
    else:
        results['failed'] += 1

    # Save after each venue
    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)

    print(f"\n[Progress: {results['processed']}/{len(target_venues)}]")

# Final summary
print("\n" + "=" * 100)
print("THREE-STAGE WORKFLOW COMPLETE")
print("=" * 100)
print(f"Processed: {results['processed']}")
print(f"Stage 1 Passed: {results['stage1_passed']}")
print(f"Stage 2 Passed: {results['stage2_passed']}")
print(f"Stage 3 Passed: {results['stage3_passed']}")
print(f"Failed: {results['failed']}")
print(f"\nBackup: {backup_file}")
print("\nDONE!")
