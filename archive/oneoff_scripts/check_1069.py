#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

with open('venues.json', encoding='utf-8') as f:
    venues = json.load(f)

venue = next((v for v in venues if v['id'] == 1069), None)
if venue:
    print(f"Name: {venue.get('name')}")
    print(f"URL: {venue.get('url')}")
    print(f"Address: {venue.get('address')}")
    print(f"Rooms: {len(venue.get('rooms', []))}")
else:
    print("Venue 1069 not found")
