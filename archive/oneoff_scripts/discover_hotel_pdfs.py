#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Discover PDF links on hotel websites"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

HOTELS_TO_CHECK = [
    {"id": 1048, "name": "老爺大酒店", "url": "https://www.ile-hotel.com"},
    {"id": 1059, "name": "友春大飯店", "url": "https://www.youchun-hotel.com"},
    {"id": 1073, "name": "子皮大飯店", "url": "https://www.zibei-hotel.com"},
    {"id": 1080, "name": "康華大飯店", "url": "https://www.kanghua-hotel.com"},
    {"id": 1084, "name": "寒舍大飯店", "url": "https://www.ching-tai.com"},
    {"id": 1092, "name": "第一飯店", "url": "https://www.firsthotel.com"},
]

async def check_hotel_pdfs(session, hotel_info):
    """Check if hotel website has PDF links"""
    hotel_id = hotel_info["id"]
    name = hotel_info["name"]
    url = hotel_info["url"]

    print(f"\nChecking: {name} (ID: {hotel_id})")
    print(f"URL: {url}")

    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
            if response.status != 200:
                print(f"  [ERROR] HTTP {response.status}")
                return {"hotel": hotel_info, "pdfs": [], "error": f"HTTP {response.status}"}

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            # Find PDF links
            pdf_links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                text = a.get_text().strip()

                # Check if PDF
                if href.lower().endswith('.pdf') or '.pdf' in href.lower():
                    full_url = urljoin(url, href)

                    # Check for meeting/banquet/wedding related PDFs
                    context = 'unknown'
                    text_lower = text.lower()
                    if any(kw in text_lower for kw in ['會議', 'meeting', 'banquet', '婚宴', '宴會', '價目', '收費']):
                        context = 'meeting_related'

                    pdf_links.append({
                        'url': full_url,
                        'text': text,
                        'context': context
                    })

            # Filter for meeting-related PDFs
            meeting_pdfs = [p for p in pdf_links if p['context'] == 'meeting_related']

            print(f"  Found {len(pdf_links)} PDF(s) total")
            print(f"  Meeting-related: {len(meeting_pdfs)}")

            if meeting_pdfs:
                print(f"  [FOUND] Meeting PDFs:")
                for pdf in meeting_pdfs[:3]:
                    print(f"    - {pdf['text'][:50]}")
                    print(f"      {pdf['url'][:80]}")

            return {"hotel": hotel_info, "pdfs": meeting_pdfs}

    except Exception as e:
        print(f"  [ERROR] {e}")
        return {"hotel": hotel_info, "pdfs": [], "error": str(e)}

async def main():
    """Main function"""
    print("="*80)
    print("Hotel PDF Discovery")
    print("="*80)

    async with aiohttp.ClientSession() as session:
        tasks = [check_hotel_pdfs(session, hotel) for hotel in HOTELS_TO_CHECK]
        results = await asyncio.gather(*tasks)

    # Summary
    print("\n" + "="*80)
    print("Summary")
    print("="*80)

    with_pdf = [r for r in results if r.get('pdfs')]
    without_pdf = [r for r in results if not r.get('pdfs')]

    print(f"\nWith Meeting PDFs: {len(with_pdf)}")
    for r in with_pdf:
        print(f"  - {r['hotel']['name']}: {len(r['pdfs'])} PDF(s)")

    print(f"\nWithout Meeting PDFs: {len(without_pdf)}")
    for r in without_pdf:
        print(f"  - {r['hotel']['name']}")

    # Generate download script
    if with_pdf:
        print("\n" + "="*80)
        print("Generating download script...")
        print("="*80)

        with open('download_hotel_pdfs.py', 'w', encoding='utf-8') as f:
            f.write('#!/usr/bin/env python3\n')
            f.write('# -*- coding: utf-8 -*-\n')
            f.write('"""Download hotel PDFs"""\n')
            f.write('import requests\n\n')

            f.write('HOTEL_PDFS = [\n')
            for r in with_pdf:
                for pdf in r['pdfs']:
                    f.write(f"    {{\n")
                    f.write(f"        \"venue_id\": {r['hotel']['id']},\n")
                    f.write(f"        \"name\": \"{r['hotel']['name']}\",\n")
                    f.write(f"        \"url\": \"{pdf['url']}\",\n")
                    f.write(f"        \"filename\": \"hotel_{r['hotel']['id']}_{{filename}}.pdf\"\n")
                    f.write(f"    }},\n")
            f.write(']\n\n')

            # Add download function
            f.write('''def download_pdf(pdf_info):
    """Download single PDF"""
    url = pdf_info["url"]
    filename = pdf_info["filename"]

    print(f"Downloading: {filename}")

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"  [OK] Size: {len(response.content):,} bytes")
            return True
        else:
            print(f"  [ERROR] HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

def main():
    import shutil
    from datetime import datetime as dt

    print("="*80)
    print("Download Hotel PDFs")
    print("="*80)
    print()

    # Create backup
    backup_name = f"venues.json.backup.hotel_pdfs_{dt.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy('venues.json', backup_name)
    print(f"Backup: {backup_name}")
    print()

    # Download PDFs
    downloaded = []
    for pdf_info in HOTEL_PDFS:
        success = download_pdf(pdf_info)
        if success:
            downloaded.append(pdf_info)
        print()

    print(f"Downloaded: {len(downloaded)}/{len(HOTEL_PDFS)} PDFs")

if __name__ == '__main__':
    main()
''')

        print("[OK] Generated: download_hotel_pdfs.py")

if __name__ == '__main__':
    asyncio.run(main())
