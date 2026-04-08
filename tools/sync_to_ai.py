#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/sync_to_ai.py — venues.json → ai_knowledge_base/venues/*.json（單向同步）

規則：
- 永遠是 venues.json → AI 知識庫（AI 不回寫）
- 只同步 active=true 的場地
- 保留 AI 層獨有的欄位（summary, ragChunks, inquiries, seasonal, logistics, rules 結構化版）
- 新增/更新 venue 層 identity 資料
- 新增/更新 room 層基本資料（area, capacity, ceilingHeight, pillar, pricing）
- 不覆蓋 AI 層已有的 summary, ragChunks, inquiries, seasonal, logistics, rules
"""

import json
import os
import sys
import io
from datetime import date
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VENUES_FILE = PROJECT_ROOT / 'venues.json'
AI_DIR = PROJECT_ROOT / 'ai_knowledge_base' / 'venues'


def load_venues():
    with open(VENUES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_ai_venue(venue_id):
    path = AI_DIR / f'{venue_id}.json'
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def save_ai_venue(data):
    AI_DIR.mkdir(parents=True, exist_ok=True)
    path = AI_DIR / f'{data["identity"]["id"]}.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def build_identity(venue):
    return {
        'id': venue['id'],
        'name': venue.get('name', ''),
        'nameEn': venue.get('nameEn'),
        'venueType': venue.get('venueType', ''),
        'city': venue.get('city', ''),
        'address': venue.get('address', ''),
        'url': venue.get('url', ''),
        'phone': venue.get('contactPhone') or venue.get('phone'),
        'contactEmail': venue.get('contactEmail') or venue.get('email'),
    }


def build_room_knowledge(room):
    return {
        'id': room.get('id', ''),
        'name': room.get('name', ''),
        'nameEn': room.get('nameEn'),
        'floor': room.get('floor'),
        'capacity': room.get('capacity'),
        'area': room.get('area'),
        'ceilingHeight': room.get('ceilingHeight'),
        'pillar': room.get('pillar'),
        'pricing': room.get('pricing'),
        'limitations': room.get('limitations', []),
        'loadIn': room.get('loadIn'),
        'suitableEventTypes': None,
        'equipment': None,
        'breakoutRooms': None,
        'layout': room.get('shape') or room.get('layout'),
    }


def sync_venue(venue):
    vid = venue['id']
    existing = load_ai_venue(vid)

    identity = build_identity(venue)
    rooms = [build_room_knowledge(r) for r in venue.get('rooms', [])]

    if existing:
        existing['identity'] = identity
        existing['rooms'] = rooms
        # Sync knowledge fields from venues.json → AI knowledge base
        for field in ('risks', 'pricingTips', 'rules'):
            src = venue.get(field)
            existing_val = existing.get(field)
            # Overwrite if source has data and existing is empty/null
            if src and not existing_val:
                existing[field] = src
        # Sync room-level limitations and loadIn
        for room_data in rooms:
            room_id = room_data.get('id')
            for er in existing.get('rooms', []):
                if er.get('id') == room_id:
                    if room_data.get('limitations') and not er.get('limitations'):
                        er['limitations'] = room_data['limitations']
                    if room_data.get('loadIn') and not er.get('loadIn'):
                        er['loadIn'] = room_data['loadIn']
                    break
    else:
        existing = {
            'identity': identity,
            'summary': None,
            'risks': venue.get('risks'),
            'rules': None,
            'pricingTips': venue.get('pricingTips'),
            'seasonal': None,
            'logistics': None,
            'rooms': rooms,
            'ragChunks': [],
            'inquiries': {'pending': [], 'sent': []},
        }

    path = save_ai_venue(existing)
    return path


def sync_all():
    venues = load_venues()
    synced = 0
    skipped = 0

    for venue in venues:
        if venue.get('active') is False:
            skipped += 1
            continue
        path = sync_venue(venue)
        synced += 1
        print(f'  {venue["id"]:>5} {venue.get("name","")[:30]:<30} → {path.name}')

    print(f'\n[sync] {synced} venues synced, {skipped} inactive skipped')
    return synced


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Sync venues.json → AI knowledge base')
    parser.add_argument('--venue', type=int, help='Sync specific venue only')
    args = parser.parse_args()

    if args.venue:
        venues = load_venues()
        venue = next((v for v in venues if v['id'] == args.venue), None)
        if not venue:
            print(f'[error] Venue {args.venue} not found')
            sys.exit(1)
        path = sync_venue(venue)
        print(f'[sync] {venue["id"]} → {path.name}')
    else:
        sync_all()


if __name__ == '__main__':
    main()
