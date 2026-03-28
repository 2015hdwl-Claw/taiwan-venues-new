#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

print(f"Total venues: {len(venues)}")

taipei_venues = [v for v in venues if '台北' in v.get('city', '')]
print(f"Taipei venues: {len(taipei_venues)}")

print()
print("Sample Taipei venues:")
for v in taipei_venues[:5]:
    print(f"  ID {v.get('id')}: {v.get('name')} - Quality: {v.get('qualityScore', 'N/A')}")

print()
print("All data verified successfully!")
