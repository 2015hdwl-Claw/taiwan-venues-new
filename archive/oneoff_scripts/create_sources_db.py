#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create sources.json from existing venues.json
"""
import json
from datetime import datetime

print("="*80)
print("Create Source Database")
print("="*80)
print()

# Load existing venues
with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

print(f"Loaded {len(venues)} venues from venues.json")
print()

# Define regions
REGIONS = [
    {
        "id": "TW-TPE",
        "name": "台北市",
        "nameEn": "Taipei City",
        "country": "台灣",
        "countryCode": "TW"
    },
    {
        "id": "TW-TPQ",
        "name": "新北市",
        "nameEn": "New Taipei City",
        "country": "台灣",
        "countryCode": "TW"
    },
    {
        "id": "TW-TYN",
        "name": "台南市",
        "nameEn": "Tainan City",
        "country": "台灣",
        "countryCode": "TW"
    },
    {
        "id": "TW-KHH",
        "name": "高雄市",
        "nameEn": "Kaohsiung City",
        "country": "台灣",
        "countryCode": "TW"
    },
    {
        "id": "TW-TXG",
        "name": "台中市",
        "nameEn": "Taichung City",
        "country": "台灣",
        "countryCode": "TW"
    },
    {
        "id": "TW-HSZ",
        "name": "新竹市",
        "nameEn": "Hsinchu City",
        "country": "台灣",
        "countryCode": "TW"
    },
    {
        "id": "TW-HCU",
        "name": "新竹縣",
        "nameEn": "Hsinchu County",
        "country": "台灣",
        "countryCode": "TW"
    },
    {
        "id": "TW-NAN",
        "name": "南投縣",
        "nameEn": "Nantou County",
        "country": "台灣",
        "countryCode": "TW"
    }
]

# Define venue types
VENUE_TYPES = [
    {
        "id": "conference_center",
        "name": "會議中心",
        "nameEn": "Conference Center",
        "priority": 1
    },
    {
        "id": "hotel",
        "name": "飯店場地",
        "nameEn": "Hotel Venue",
        "priority": 2
    },
    {
        "id": "wedding",
        "name": "婚宴場地",
        "nameEn": "Wedding Venue",
        "priority": 3
    },
    {
        "id": "exhibition",
        "name": "展演場地",
        "nameEn": "Exhibition Venue",
        "priority": 4
    },
    {
        "id": "sports",
        "name": "運動場地",
        "nameEn": "Sports Venue",
        "priority": 5
    }
]

# Define web tech types
WEB_TECH_TYPES = [
    {
        "id": "static",
        "name": "Static HTML",
        "recommendedScraper": "requests + BeautifulSoup"
    },
    {
        "id": "wordpress",
        "name": "WordPress",
        "recommendedScraper": "scraper_wordpress_ticc.py"
    },
    {
        "id": "javascript",
        "name": "JavaScript Heavy",
        "recommendedScraper": "Playwright"
    },
    {
        "id": "unknown",
        "name": "Unknown",
        "recommendedScraper": "deep_scraper_v2.py (auto-detect)"
    }
]

# Build sources list
sources = []

for venue in venues:
    vid = venue.get('id')
    name = venue.get('name')
    url = venue.get('url')
    vtype = venue.get('venueType', '')

    # Map venue type
    venue_type_id = "conference_center"
    if '飯店' in vtype or 'hotel' in vtype.lower():
        venue_type_id = "hotel"
    elif '婚宴' in vtype:
        venue_type_id = "wedding"
    elif '展演' in vtype:
        venue_type_id = "exhibition"
    elif '運動' in vtype:
        venue_type_id = "sports"

    # Determine region from city
    city = venue.get('city', '')
    region_id = "TW-TPE"  # Default
    if '台北' in city:
        region_id = "TW-TPE"
    elif '新北' in city:
        region_id = "TW-TPQ"
    elif '台南' in city:
        region_id = "TW-TYN"
    elif '高雄' in city:
        region_id = "TW-KHH"
    elif '台中' in city:
        region_id = "TW-TXG"
    elif '新竹' in city:
        if '市' in city:
            region_id = "TW-HSZ"
        else:
            region_id = "TW-HCU"
    elif '南投' in city:
        region_id = "TW-NAN"

    # Determine web tech
    metadata = venue.get('metadata', {})
    web_tech = "unknown"
    if 'meeting.com.tw' in url:
        web_tech = "static"
    elif 'ticc.com.tw' in url:
        web_tech = "wordpress"

    # Determine priority
    priority = 3  # Default
    if '集思' in name or 'TICC' in name or '台大' in name:
        priority = 1
    elif '國際' in name:
        priority = 2

    # Determine status
    has_rooms = len(venue.get('rooms', [])) > 0

    sources.append({
        "id": vid,
        "name": name,
        "nameEn": "",  # Could be added later
        "regionId": region_id,
        "venueTypeId": venue_type_id,
        "url": url,
        "webTech": web_tech,
        "priority": priority,
        "status": "active" if has_rooms else "pending",
        "notes": f"Has {len(venue.get('rooms', []))} rooms" if has_rooms else "Needs scraping",
        "lastChecked": datetime.now().isoformat(),
        "lastScraped": metadata.get('lastScrapedAt'),
        "scrapeVersion": metadata.get('scrapeVersion'),
        "scrapeResult": "success" if has_rooms else "pending"
    })

# Create sources.json structure
sources_json = {
    "version": "1.0",
    "lastUpdated": datetime.now().isoformat(),
    "regions": REGIONS,
    "venueTypes": VENUE_TYPES,
    "webTechTypes": WEB_TECH_TYPES,
    "sources": sources
}

# Save
with open('sources.json', 'w', encoding='utf-8') as f:
    json.dump(sources_json, f, ensure_ascii=False, indent=2)

print("[OK] Created sources.json")
print()

# Summary
print("="*80)
print("Summary")
print("="*80)
print()
print(f"Total sources: {len(sources)}")
print()

print("By status:")
status_count = {}
for s in sources:
    status = s['status']
    status_count[status] = status_count.get(status, 0) + 1

for status, count in status_count.items():
    print(f"  {status}: {count}")
print()

print("By venue type:")
type_count = {}
for s in sources:
    vtype = s['venueTypeId']
    type_count[vtype] = type_count.get(vtype, 0) + 1

for vtype, count in sorted(type_count.items()):
    print(f"  {vtype}: {count}")
print()

print("By priority:")
priority_count = {}
for s in sources:
    priority = s['priority']
    priority_count[priority] = priority_count.get(priority, 0) + 1

for priority in sorted(priority_count.keys()):
    count = priority_count[priority]
    print(f"  Priority {priority}: {count}")

print()
print("File: sources.json")
print("="*80)
