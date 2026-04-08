#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys
import io
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

print("="*60)
print("Standardizing venue field names")
print("="*60)
print()

updated_count = 0
phone_migrated = 0
email_migrated = 0

for venue in venues:
    changes = []
    
    if 'contact' not in venue:
        venue['contact'] = {}
    
    if 'contactPhone' in venue:
        old_phone = venue['contactPhone']
        if not venue['contact'].get('phone'):
            venue['contact']['phone'] = old_phone
            changes.append('phone')
            phone_migrated += 1
        del venue['contactPhone']
    
    if 'contactEmail' in venue:
        old_email = venue['contactEmail']
        if not venue['contact'].get('email'):
            venue['contact']['email'] = old_email
            changes.append('email')
            email_migrated += 1
        del venue['contactEmail']
    
    if 'metadata' not in venue:
        venue['metadata'] = {}
    
    if changes:
        venue['metadata']['fieldsStandardized'] = changes
        venue['metadata']['fieldsStandardizedAt'] = datetime.now().isoformat()
        updated_count += 1
        print(f"[{venue.get('id')}] Updated: {', '.join(changes)}")

print()
print("="*60)
print("Summary")
print("="*60)
print(f"Total venues: {len(venues)}")
print(f"Updated: {updated_count}")
print(f"Phone fields migrated: {phone_migrated}")
print(f"Email fields migrated: {email_migrated}")
print()

with open('venues.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, ensure_ascii=False, indent=2)

print("Saved to venues.json")
