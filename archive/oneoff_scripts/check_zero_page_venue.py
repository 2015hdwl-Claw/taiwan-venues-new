#!/usr/bin/env python3
import json

with open('venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 檢查一個無頁面場地
venue = next((v for v in data if v['id'] == 1082), None)

if venue:
    print(f'Venue ID: {venue["id"]}')
    print(f'Name: {venue["name"]}')
    print(f'URL: {venue.get("url", "N/A")}')
    print(f'V4 pagesDiscovered: {venue.get("metadata", {}).get("pagesDiscovered", 0)}')
    print(f'Verified: {venue.get("verified", False)}')
    print(f'Status: {venue.get("status", "N/A")}')
