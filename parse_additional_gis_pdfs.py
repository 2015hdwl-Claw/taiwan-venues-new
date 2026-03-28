#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下載並解析額外的集思 PDF
"""
import asyncio
import requests
import PyPDF2
import re
import json
from datetime import datetime


# 更新的 PDF 連結
ADDITIONAL_PDFS = [
    {
        "venue_id": 1498,
        "name": "集思烏日會議中心(WURI)",
        "url": "https://www.meeting.com.tw/xinwuri/download/%E5%8F%B0%E4%B8%AD%E6%96%B0%E7%83%8F%E6%97%A5_%E5%A0%B4%E5%9C%B0%E7%A7%9F%E5%80%9F%E7%94%B3%E8%AB%8B%E8%A1%A8_20260102.pdf",
        "filename": "gis_wuri_2026_correct.pdf"
    },
    {
        "venue_id": 1495,
        "name": "集思北科技會議中心(Tech)",
        "url": "https://www.meeting.com.tw/ntut/download/%E5%8C%97%E7%A7%91%E5%A4%A7_%E5%A0%B4%E5%9C%B0%E7%A7%9F%E7%94%A8%E7%94%B3%E8%AB%8B%E8%A1%A8_20250401.pdf",
        "filename": "gis_ntut_2025_correct.pdf"
    },
    {
        "venue_id": 1496,
        "name": "集思竹科會議中心(HSPH)",
        "url": "https://www.meeting.com.tw/hsp/download/%E7%AB%B9%E7%A7%91-%E5%A0%B4%E5%9C%B0%E7%A7%9F%E7%94%A8%E7%94%B3%E8%AB%8B%E8%A1%A8-20250402.pdf",
        "filename": "gis_tc_2025_correct.pdf"
    },
]


def download_pdf(pdf_info):
    """Download single PDF"""
    url = pdf_info["url"]
    filename = pdf_info["filename"]

    print(f"Downloading: {filename}")

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 200:
            content = response.content

            with open(filename, 'wb') as f:
                f.write(content)

            print(f"  [OK] Size: {len(content):,} bytes")
            return True
        else:
            print(f"  [ERROR] HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def parse_table_format_pdf(text, venue_id):
    """Parse table format PDF (like MOTC)"""
    rooms = []

    lines = text.split('\n')

    for i, line in enumerate(lines):
        line = line.strip()

        # Look for lines with room numbers and info
        # Pattern: "201  會議室  容納人數  63  坪數  63  樓層  2樓"
        if re.match(r'^\d+', line) and '會議室' in line:
            parts = line.split()
            if len(parts) >= 6:
                room_num = parts[0]
                capacity = None
                area = None
                floor = None

                # Find capacity
                for j, part in enumerate(parts):
                    if part.isdigit() and j > 0:
                        # Check if this is capacity (usually < 500)
                        val = int(part)
                        if val < 500:
                            capacity = val

                # Find area
                for j, part in enumerate(parts):
                    if re.search(r'\d+', part) and '坪' in parts[min(j+1, len(parts)-1)] if j+1 < len(parts) else False:
                        area_match = re.search(r'(\d+(?:\.\d+)?)', part)
                        if area_match:
                            area = float(area_match.group(1))
                            break

                # Find floor
                for part in parts:
                    if '樓' in part or 'F' in part:
                        floor = part
                        break

                if capacity and area:
                    rooms.append({
                        'id': f"{venue_id}-{room_num}",
                        'name': f"{room_num}會議室",
                        'nameEn': f"Room {room_num}",
                        'area': area,
                        'areaUnit': '坪',
                        'floor': floor,
                        'capacity': {'standard': capacity},
                        'source': 'gis_official_pdf'
                    })

    return rooms


def parse_list_format_pdf(text, venue_id):
    """Parse list format PDF"""
    rooms = []

    lines = text.split('\n')

    for line in lines:
        line = line.strip()

        # Look for lines with room info
        # Pattern: "國際會議廳    容納人數    400人    坪數    253.6坪"
        if '會議廳' in line or '會議室' in line:
            # Extract room name
            room_name_match = re.match(r'^([\u4e00-\u9fff]+(?:廳|室))', line)
            if room_name_match:
                room_name = room_name_match.group(1)

                # Extract capacity
                cap_match = re.search(r'(\d+)\s*人', line)
                capacity = int(cap_match.group(1)) if cap_match else None

                # Extract area
                area_match = re.search(r'([\d.]+)\s*坪', line)
                area = float(area_match.group(1)) if area_match else None

                if capacity and area:
                    rooms.append({
                        'id': f"{venue_id}-{room_name}",
                        'name': room_name,
                        'nameEn': room_name,
                        'area': area,
                        'areaUnit': '坪',
                        'capacity': {'standard': capacity},
                        'source': 'gis_official_pdf'
                    })

    return rooms


def parse_pdf(pdf_info):
    """Parse single PDF"""
    filename = pdf_info["filename"]
    venue_id = pdf_info["venue_id"]

    print()
    print(f"Parsing: {filename}")

    try:
        with open(filename, 'rb') as file:
            reader = PyPDF2.PdfReader(file)

            print(f"  Pages: {len(reader.pages)}")

            # Extract all text
            all_text = ""
            for page in reader.pages:
                text = page.extract_text()
                all_text += text + "\n"

            # Save text
            text_filename = filename.replace('.pdf', '_text.txt')
            with open(text_filename, 'w', encoding='utf-8') as f:
                f.write(all_text)

            print(f"  [OK] Saved text")

            # Try different parsing methods
            rooms = parse_table_format_pdf(all_text, venue_id)

            if not rooms:
                rooms = parse_list_format_pdf(all_text, venue_id)

            print(f"  [OK] Found {len(rooms)} rooms")

            return rooms

    except Exception as e:
        print(f"  [ERROR] {e}")
        return []


def main():
    print("="*80)
    print("Download and Parse Additional GIS PDFs")
    print("="*80)
    print()

    # Download PDFs
    print("Step 1: Download PDFs")
    print("-"*80)

    downloaded = []
    for pdf_info in ADDITIONAL_PDFS:
        success = download_pdf(pdf_info)
        if success:
            downloaded.append(pdf_info)
        print()

    print(f"Downloaded: {len(downloaded)}/{len(ADDITIONAL_PDFS)} PDFs")
    print()

    # Parse PDFs
    print("Step 2: Parse PDFs")
    print("-"*80)

    all_results = []

    for pdf_info in downloaded:
        rooms = parse_pdf(pdf_info)

        if rooms:
            all_results.append({
                'venue_id': pdf_info['venue_id'],
                'venue_name': pdf_info['name'],
                'filename': pdf_info['filename'],
                'rooms': rooms,
                'total': len(rooms)
            })

        print()

    # Update venues.json
    print("Step 3: Update venues.json")
    print("-"*80)

    with open('venues.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)

    updated_count = 0

    for result in all_results:
        venue_id = result['venue_id']
        rooms = result['rooms']
        venue_name = result['venue_name']

        for venue in venues:
            if venue.get('id') == venue_id:
                venue['rooms'] = rooms

                # Calculate max capacity
                if rooms:
                    max_cap = max([r['capacity']['standard'] for r in rooms])
                    venue['capacity'] = {'standard': max_cap}

                # Update metadata
                venue['metadata'] = {
                    'lastScrapedAt': datetime.now().isoformat(),
                    'scrapeVersion': 'GIS_PDF_Official',
                    'scrapeConfidenceScore': 100,
                    'totalRooms': len(rooms),
                    'source': 'gis_official_pdf'
                }

                updated_count += 1
                print(f"  [OK] Updated: {venue_name} ({len(rooms)} rooms)")
                break

    # Save
    with open('venues.json', 'w', encoding='utf-8') as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)

    print()
    print(f"Updated: {updated_count} venues")
    print()

    # Summary
    print("="*80)
    print("Summary")
    print("="*80)
    print()

    total_rooms = 0
    for result in all_results:
        venue_name = result['venue_name']
        count = result['total']
        total_rooms += count

        print(f"{venue_name}: {count} rooms")

        for room in result['rooms'][:5]:
            cap = room['capacity']['standard']
            area = room['area']
            print(f"  - {room['name']}: {cap} people, {area} ping")

        if count > 5:
            print(f"  ... and {count - 5} more")

        print()

    print(f"Total: {total_rooms} rooms added")


if __name__ == '__main__':
    main()
