#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

total = len(venues)
taipei = [v for v in venues if '台北' in v.get('city', '')]

# Check phone coverage
has_phone = 0
has_email = 0
has_contact_phone = 0
has_contact_email = 0

for v in taipei:
    # Check contact.phone field
    if v.get('contact', {}).get('phone'):
        has_contact_phone += 1
    # Check contactPhone field
    if v.get('contactPhone'):
        has_contact_phone += 1
    # Check any phone field
    if v.get('contact', {}).get('phone') or v.get('contactPhone'):
        has_phone += 1
    # Check email
    if v.get('contact', {}).get('email') or v.get('contactEmail'):
        has_email += 1

print("="*60)
print("Taipei Venues Contact Coverage")
print("="*60)
print()
print(f"Total Taipei venues: {len(taipei)}")
print()
print(f"Phone coverage (any field): {has_phone}/{len(taipei)} ({has_phone/len(taipei)*100:.1f}%)")
print(f"Email coverage (any field): {has_email}/{len(taipei)} ({has_email/len(taipei)*100:.1f}%)")
print()
print(f"contact.phone field: {has_contact_phone}/{len(taipei)}")
print(f"contactPhone field: {has_contact_phone}/{len(taipei)}")
print(f"contact.email field: {sum(1 for v in taipei if v.get('contact', {}).get('email'))}/{len(taipei)}")
print(f"contactEmail field: {sum(1 for v in taipei if v.get('contactEmail'))}/{len(taipei)}")
