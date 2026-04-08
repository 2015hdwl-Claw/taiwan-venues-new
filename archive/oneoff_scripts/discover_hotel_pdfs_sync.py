#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Discover PDF links on hotel websites (sync version)"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

HOTELS_TO_CHECK = [
    {"id": 1048, "name": "Old Hotel", "url": "https://www.ile-hotel.com"},
    {"id": 1059, "name": "Youchun Hotel", "url": "https://www.youchun-hotel.com"},
    {"id": 1073, "name": "Zibei Hotel", "url": "https://www.zibei-hotel.com"},
    {"id": 1080, "name": "Kanghua Hotel", "url": "https://www.kanghua-hotel.com"},
    {"id": 1084, "name": "Ching Tai Hotel", "url": "https://www.ching-tai.com"},
    {"id": 1092, "name": "First Hotel", "url": "https://www.firsthotel.com"},
]

def check_hotel_pdfs(hotel_info):
    """Check if hotel website has PDF links"""
    hotel_id = hotel_info["id"]
    url = hotel_info["url"]

    print(f"\nChecking ID {hotel_id}: {url}")

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code != 200:
            print(f"  [ERROR] HTTP {response.status_code}")
            return {"hotel": hotel_info, "pdfs": [], "error": f"HTTP {response.status_code}"}

        soup = BeautifulSoup(response.text, 'html.parser')

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
                if any(kw in text_lower for kw in ['meeting', 'banquet', 'wedding', 'menu', 'price']):
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

def main():
    """Main function"""
    print("="*80)
    print("Hotel PDF Discovery")
    print("="*80)

    results = []
    for hotel in HOTELS_TO_CHECK:
        result = check_hotel_pdfs(hotel)
        results.append(result)

    # Summary
    print("\n" + "="*80)
    print("Summary")
    print("="*80)

    with_pdf = [r for r in results if r.get('pdfs')]
    without_pdf = [r for r in results if not r.get('pdfs')]

    print(f"\nWith Meeting PDFs: {len(with_pdf)}")
    for r in with_pdf:
        print(f"  - ID {r['hotel']['id']}: {len(r['pdfs'])} PDF(s)")

    print(f"\nWithout Meeting PDFs: {len(without_pdf)}")
    for r in without_pdf:
        print(f"  - ID {r['hotel']['id']}")

    # Generate list for manual processing
    print("\n" + "="*80)
    print("Hotels for Manual Processing (No PDF Found):")
    print("="*80)
    for r in without_pdf:
        hid = r['hotel']['id']
        url = r['hotel']['url']
        print(f"{hid}: {url}")

if __name__ == '__main__':
    main()
