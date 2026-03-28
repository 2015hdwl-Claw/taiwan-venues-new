#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 3 Quality Booster - Enhance Rooms and Price Data

Goal: Boost quality score from 42.6 → 65+
- Extract complete room details (capacity, area, equipment)
- Extract price data from HTML
- Mark venues with PDF price lists

Strategy:
1. Test 5 Taipei venues
2. Measure quality improvement
3. Scale to all 41 Taipei venues
"""
import sys
import io
import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin
from datetime import datetime
from pathlib import Path

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class QualityBooster:
    """Boost venue quality by extracting missing room and price data"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def calculate_room_quality(self, room):
        """Calculate quality score for a single room"""
        score = 0
        max_score = 100

        # Name (required)
        if room.get('name'):
            score += 10

        # Capacity (20 points)
        if room.get('capacity'):
            if isinstance(room['capacity'], dict):
                # Multiple layout types
                score += 20
            elif isinstance(room['capacity'], (int, float)):
                score += 15

        # Area (15 points)
        if room.get('area'):
            score += 15

        # Price (30 points) - most valuable
        if room.get('price'):
            if isinstance(room['price'], dict):
                score += 30
            elif room.get('priceHalfDay') or room.get('priceFullDay'):
                score += 20

        # Equipment (10 points)
        if room.get('equipment'):
            score += 10

        # Images (10 points)
        if room.get('images'):
            score += 10

        # Description (5 points)
        if room.get('description'):
            score += 5

        return score

    def calculate_venue_quality(self, venue):
        """Calculate overall venue quality score"""
        rooms = venue.get('rooms', [])

        if not rooms:
            return 0

        # Average room quality
        room_scores = [self.calculate_room_quality(room) for room in rooms]
        avg_room_score = sum(room_scores) / len(room_scores)

        # Bonus for having many rooms
        room_count_bonus = min(len(rooms) * 2, 20)

        # Contact info bonus (already 100% from Phase 2)
        contact_bonus = 10

        # Transportation bonus
        transport_bonus = 0
        if venue.get('traffic'):
            transport_bonus = 10

        total_score = avg_room_score + room_count_bonus + contact_bonus + transport_bonus
        return min(int(total_score), 100)

    def extract_price_from_html(self, soup):
        """Extract price information from HTML"""
        price_data = {
            'hasPriceInfo': False,
            'priceInHTML': False,
            'hasPDF': False,
            'pdfUrls': [],
            'extractedPrices': {}
        }

        page_text = soup.get_text()

        # Check for PDF links
        pdf_links = soup.find_all('a', href=re.compile(r'\.pdf$', re.I))
        if pdf_links:
            price_data['hasPDF'] = True
            for link in pdf_links:
                href = link.get('href', '')
                text = link.get_text().lower()
                # Check if PDF might be a price list
                if any(kw in href.lower() or kw in text for kw in ['價格', '價目', '收費', 'rate', 'price', '費率']):
                    full_url = urljoin(str(soup.base.get('href', '')), href) if soup.base else href
                    price_data['pdfUrls'].append(full_url)

        # Extract price from text
        price_patterns = [
            (r'平日[：:]\s*NT\$?\s*([\d,]+)', 'weekday'),
            (r'假日[：:]\s*NT\$?\s*([\d,]+)', 'holiday'),
            (r'週一至週五[：:]\s*NT\$?\s*([\d,]+)', 'weekday'),
            (r'週末[：:]\s*NT\$?\s*([\d,]+)', 'holiday'),
            (r'全日[：:]\s*NT\$?\s*([\d,]+)', 'full_day'),
            (r'半日[：:]\s*NT\$?\s*([\d,]+)', 'half_day'),
            (r'小時[：:]\s*NT\$?\s*([\d,]+)', 'hourly'),
        ]

        for pattern, key in price_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                try:
                    price_value = int(matches[0].replace(',', ''))
                    price_data['extractedPrices'][key] = price_value
                    price_data['priceInHTML'] = True
                    price_data['hasPriceInfo'] = True
                except ValueError:
                    continue

        return price_data

    def enhance_room_capacity(self, room, page_text):
        """Enhance room with multiple capacity layouts"""
        existing_capacity = room.get('capacity')

        if not existing_capacity:
            return room

        # If already a dict, keep it
        if isinstance(existing_capacity, dict):
            return room

        # If single number, try to extract more layouts
        if isinstance(existing_capacity, (int, float)):
            capacity_dict = {'theater': existing_capacity}

            # Try to find other layouts
            layout_patterns = {
                'classroom': r'教室式[：:]\s*(\d+)',
                'banquet': r'宴會式[：:]\s*(\d+)',
                'discussion': r'討論式[：:]\s*(\d+)',
                'u-shape': r'U型[：:]\s*(\d+)',
            }

            for layout, pattern in layout_patterns.items():
                match = re.search(pattern, page_text)
                if match:
                    try:
                        capacity_dict[layout] = int(match.group(1))
                    except ValueError:
                        continue

            room['capacity'] = capacity_dict

        return room

    def process_venue(self, venue):
        """Process a single venue to enhance quality"""
        venue_id = venue.get('id')
        venue_url = venue.get('url')

        if not venue_url:
            return {
                'success': False,
                'id': venue_id,
                'error': 'No URL'
            }

        try:
            # Fetch page
            response = self.session.get(venue_url, timeout=10, verify=False)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text()

            # Calculate current quality
            current_quality = self.calculate_venue_quality(venue)

            # Extract price data
            price_data = self.extract_price_from_html(soup)

            # Enhance existing rooms
            rooms = venue.get('rooms', [])
            enhanced_rooms = []

            for room in rooms:
                enhanced_room = self.enhance_room_capacity(room, page_text)
                enhanced_rooms.append(enhanced_room)

            # Update venue with enhanced data
            result = {
                'success': True,
                'id': venue_id,
                'currentQuality': current_quality,
                'rooms': enhanced_rooms,
                'priceData': price_data
            }

            # Calculate new quality
            test_venue = venue.copy()
            test_venue['rooms'] = enhanced_rooms
            new_quality = self.calculate_venue_quality(test_venue)

            result['newQuality'] = new_quality
            result['qualityImprovement'] = new_quality - current_quality

            return result

        except Exception as e:
            return {
                'success': False,
                'id': venue_id,
                'error': str(e)
            }


def main():
    """Main execution"""
    print('='*70)
    print('Phase 3 Quality Booster - Room & Price Enhancement')
    print('='*70)

    # Load venues
    with open('venues.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Find Taipei venues
    taipei_venues = [
        v for v in data
        if v.get('city') == '台北市' and v.get('status') != 'discontinued'
    ]

    print(f'\nTotal Taipei venues: {len(taipei_venues)}')

    # Select test sample
    test_venues = taipei_venues[:5]
    print(f'Testing with {len(test_venues)} venues\n')

    booster = QualityBooster()

    results = []
    total_improvement = 0

    for i, venue in enumerate(test_venues, 1):
        venue_id = venue['id']
        venue_name = venue.get('name', 'Unknown')

        print(f'[{i}/{len(test_venues)}] ID: {venue_id} - {venue_name[:30]}...')

        result = booster.process_venue(venue)
        results.append(result)

        if result['success']:
            improvement = result['qualityImprovement']
            total_improvement += improvement

            status = '✓' if improvement > 0 else '→'
            print(f'  {status} Quality: {result["currentQuality"]} → {result["newQuality"]} (+{improvement})')

            if result['priceData']['hasPriceInfo']:
                if result['priceData']['priceInHTML']:
                    print(f'    💰 Price found in HTML')
                if result['priceData']['hasPDF']:
                    print(f'    📄 {len(result["priceData"]["pdfUrls"])} PDF price list(s)')
        else:
            print(f'  ✗ Error: {result.get("error", "Unknown")}')

        print()

    # Summary
    print('='*70)
    print('Summary')
    print('='*70)

    successful = sum(1 for r in results if r['success'])
    avg_improvement = total_improvement / len(test_venues) if test_venues else 0

    print(f'Venues processed: {len(test_venues)}')
    print(f'Successful: {successful}')
    print(f'Average quality improvement: +{avg_improvement:.1f} points')

    # Calculate quality distribution
    current_scores = [r['currentQuality'] for r in results if r['success']]
    new_scores = [r['newQuality'] for r in results if r['success']]

    if current_scores:
        print(f'\nQuality Distribution:')
        print(f'  Before - Min: {min(current_scores)}, Max: {max(current_scores)}, Avg: {sum(current_scores)/len(current_scores):.1f}')
        print(f'  After  - Min: {min(new_scores)}, Max: {max(new_scores)}, Avg: {sum(new_scores)/len(new_scores):.1f}')

    # Save results
    output_file = f'phase3_enhancement_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f'\nResults saved to {output_file}')

    # Predict full-scale impact
    if avg_improvement > 0:
        print(f'\n📊 Prediction for all {len(taipei_venues)} Taipei venues:')
        print(f'   Expected average quality: {42.6 + avg_improvement:.1f}')
        print(f'   Quality score target: 65+')
        print(f'   Gap remaining: {max(0, 65 - (42.6 + avg_improvement)):.1f} points')


if __name__ == '__main__':
    main()
