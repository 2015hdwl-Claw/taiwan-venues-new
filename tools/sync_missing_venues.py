#!/usr/bin/env python3
"""
sync_missing_venues.py - Create KB files for venues missing from ai_knowledge_base/

Reads venues.json and creates KB files for venues that don't have one yet.
Also enriches existing empty KB files with basic summary data.

Usage:
    python tools/sync_missing_venues.py [--enrich-summaries]
"""

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
VENUES_FILE = PROJECT_ROOT / "venues.json"
KB_DIR = PROJECT_ROOT / "ai_knowledge_base" / "venues"


def create_kb_from_venue(venue):
    """Convert a venues.json venue object to a KB file structure."""
    vid = venue["id"]

    # Identity
    identity = {
        "id": vid,
        "name": venue.get("name", ""),
        "nameEn": venue.get("nameEn"),
        "venueType": venue.get("venueType", ""),
        "city": venue.get("city", ""),
        "address": venue.get("address", ""),
        "url": venue.get("url"),
        "phone": venue.get("contactPhone"),
        "contactEmail": venue.get("contactEmail"),
    }

    # Summary from venues.json data
    rooms = venue.get("rooms", [])
    total_rooms = len(rooms)

    def get_room_cap(r):
        cap = r.get("capacity", 0)
        if isinstance(cap, int):
            return cap
        if isinstance(cap, dict):
            return max(cap.get("theater", 0) or 0, cap.get("classroom", 0) or 0,
                       cap.get("banquet", 0) or 0, cap.get("ushape", 0) or 0)
        return 0

    max_cap = max((get_room_cap(r) for r in rooms), default=0)
    max_cap = max(max_cap, venue.get("maxCapacityTheater", 0) or 0, venue.get("maxCapacityClassroom", 0) or 0)

    summary = None
    if total_rooms > 0 or max_cap > 0:
        price_min = venue.get("priceHalfDay")
        price_max = venue.get("priceFullDay")
        summary = {
            "shortDescription": f"{venue.get('name', '')}位於{venue.get('city', '')}，擁有{total_rooms}間會議室，最大容納{max_cap}人。",
            "totalRooms": total_rooms,
            "maxCapacity": max_cap,
            "priceRange": {
                "halfDayMin": price_min,
                "halfDayMax": None,
                "fullDayMin": None,
                "fullDayMax": price_max,
                "note": None,
            },
            "suitableEventTypes": [],
            "strengths": [],
            "weaknesses": [],
        }

    # Rooms
    kb_rooms = []
    for r in rooms:
        raw_cap = r.get("capacity", {})
        if isinstance(raw_cap, int):
            cap = {"theater": raw_cap, "classroom": None, "banquet": None, "ushape": None}
        elif isinstance(raw_cap, dict):
            cap = {
                "theater": raw_cap.get("theater"),
                "classroom": raw_cap.get("classroom"),
                "banquet": raw_cap.get("banquet"),
                "ushape": raw_cap.get("ushape"),
            }
        else:
            cap = {}
        pricing = r.get("pricing", {}) or {}
        kb_room = {
            "id": r.get("id", f"{vid}-{r.get('name', '')}"),
            "name": r.get("name", ""),
            "nameEn": r.get("nameEn"),
            "floor": r.get("floor"),
            "capacity": cap,
            "area": r.get("area"),
            "ceilingHeight": r.get("ceilingHeight"),
            "pillar": r.get("pillar"),
            "pricing": {
                "halfDay": pricing.get("halfDay"),
                "fullDay": pricing.get("fullDay"),
                "overtimePerHour": None,
                "note": pricing.get("note"),
            },
            "limitations": r.get("limitations", []),
            "loadIn": None,
            "suitableEventTypes": None,
            "equipment": r.get("equipment"),
            "breakoutRooms": None,
            "layout": None,
        }
        kb_rooms.append(kb_room)

    # Build KB structure
    kb = {
        "identity": identity,
        "summary": summary,
        "risks": None,
        "rules": None,
        "pricingTips": None,
        "seasonal": None,
        "logistics": None,
        "rooms": kb_rooms,
        "ragChunks": [],
        "inquiries": {"pending": [], "sent": []},
    }

    # If venue has risks in venues.json, copy them
    if venue.get("risks"):
        kb["risks"] = venue["risks"]

    # If venue has rules in venues.json, copy them
    if venue.get("rules"):
        kb["rules"] = venue["rules"]

    # If venue has pricingTips in venues.json
    if venue.get("pricingTips"):
        if isinstance(venue["pricingTips"], list):
            kb["pricingTips"] = {"tips": venue["pricingTips"]}
        elif isinstance(venue["pricingTips"], dict):
            kb["pricingTips"] = venue["pricingTips"]

    return kb


def enrich_summary(kb, venue):
    """Enrich an existing KB file with summary from venues.json if missing."""
    if kb.get("summary"):
        return kb

    rooms = venue.get("rooms", [])
    total_rooms = len(rooms)
    max_cap = max(
        (r.get("capacity", {}).get("theater", 0) or 0) for r in rooms
    ) if rooms else 0
    max_cap = max(max_cap, venue.get("maxCapacityTheater", 0) or 0, venue.get("maxCapacityClassroom", 0) or 0)

    kb["summary"] = {
        "shortDescription": f"{venue.get('name', '')}位於{venue.get('city', '')}，擁有{total_rooms}間會議室，最大容納{max_cap}人。",
        "totalRooms": total_rooms,
        "maxCapacity": max_cap,
        "priceRange": {
            "halfDayMin": venue.get("priceHalfDay"),
            "halfDayMax": None,
            "fullDayMin": None,
            "fullDayMax": venue.get("priceFullDay"),
            "note": None,
        },
        "suitableEventTypes": [],
        "strengths": [],
        "weaknesses": [],
    }
    return kb


def main():
    # Load venues.json
    print("Loading venues.json...")
    with open(VENUES_FILE, "r", encoding="utf-8") as f:
        venues = json.load(f)
    venues_by_id = {v["id"]: v for v in venues}
    print(f"  {len(venues)} venues loaded")

    # Get existing KB files
    kb_files = {int(f.replace(".json", "")) for f in os.listdir(KB_DIR) if f.endswith(".json")}
    print(f"  {len(kb_files)} existing KB files")

    # Find missing venues
    missing_ids = sorted(set(venues_by_id.keys()) - kb_files)
    print(f"  {len(missing_ids)} venues missing KB files")

    # Create missing KB files
    created = 0
    for vid in missing_ids:
        venue = venues_by_id[vid]
        kb = create_kb_from_venue(venue)
        output_path = KB_DIR / f"{vid}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(kb, f, ensure_ascii=False, indent=2)
        print(f"  Created: {vid} - {venue['name']}")
        created += 1

    print(f"\nCreated {created} new KB files")

    # Enrich existing KB files that lack summaries
    enriched = 0
    for vid in kb_files:
        venue = venues_by_id.get(vid)
        if not venue:
            continue
        kb_path = KB_DIR / f"{vid}.json"
        with open(kb_path, "r", encoding="utf-8") as f:
            kb = json.load(f)

        if not kb.get("summary"):
            kb = enrich_summary(kb, venue)
            with open(kb_path, "w", encoding="utf-8") as f:
                json.dump(kb, f, ensure_ascii=False, indent=2)
            enriched += 1

    if enriched:
        print(f"Enriched {enriched} KB files with summaries")

    print(f"\nTotal KB files now: {len(os.listdir(KB_DIR))}")


if __name__ == "__main__":
    main()
