#!/usr/bin/env python3
"""
generate_embeddings.py - Generate vector embeddings for AI knowledge base

Usage:
    python -m tools.generate_embeddings [--output embeddings.json] [--api-key KEY]

Environment:
    OPENAI_API_KEY - OpenAI API key (or use --api-key)
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional
import argparse

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def load_venues() -> list[dict]:
    """Load all venue JSON files from ai_knowledge_base/venues/"""
    venues_dir = PROJECT_ROOT / "ai_knowledge_base" / "venues"
    venues = []
    for file_path in venues_dir.glob("*.json"):
        with open(file_path, "r", encoding="utf-8") as f:
            venues.append(json.load(f))
    return venues


def create_text_chunks(venue: dict) -> list[dict]:
    """
    Convert venue knowledge into searchable text chunks.

    Each chunk contains:
    - venue_id: for reference
    - text: searchable content
    - metadata: source info (field path, confidence)
    """
    chunks = []
    venue_id = venue.get("identity", {}).get("id")
    venue_name = venue.get("identity", {}).get("name", "")

    def add_chunk(text: str, field_path: str, confidence: str = "unknown"):
        if not text or not text.strip():
            return
        chunks.append({
            "venue_id": venue_id,
            "venue_name": venue_name,
            "text": text.strip(),
            "field_path": field_path,
            "confidence": confidence
        })

    # 1. Summary chunk (for general venue queries)
    summary = venue.get("summary") or {}
    if summary.get("shortDescription"):
        text = f"【{venue_name}】{summary['shortDescription']}"
        if summary.get("strengths"):
            text += f"\n優勢：{', '.join(summary['strengths'][:3])}"
        if summary.get("weaknesses"):
            text += f"\n注意：{', '.join(summary['weaknesses'][:3])}"
        add_chunk(text, "summary", "confirmed")

    # 2. Rules chunks (catering, decoration, sound, etc.)
    rules = venue.get("rules") or {}
    for category, rule_list in rules.items():
        if not isinstance(rule_list, list):
            continue
        for i, rule in enumerate(rule_list):
            if isinstance(rule, dict) and rule.get("rule"):
                text = f"【{venue_name}】{get_category_label(category)}：{rule['rule']}"
                if rule.get("exception"):
                    text += f"（例外：{rule['exception']}）"
                if rule.get("penalty"):
                    text += f"（違規：{rule['penalty']}）"
                confidence = rule.get("confidence", "unverified")
                add_chunk(text, f"rules.{category}[{i}]", confidence)

    # 3. Risks chunk
    risks = venue.get("risks") or {}
    if isinstance(risks, dict) and risks:
        text_parts = [f"【{venue_name}】風險提示："]
        if risks.get("bookingLeadTime"):
            text_parts.append(f"預訂提前時間：{risks['bookingLeadTime']}")
        if risks.get("peakSeasons"):
            text_parts.append(f"旺季：{', '.join(risks['peakSeasons'])}")
        if risks.get("commonIssues"):
            text_parts.append(f"常見問題：{', '.join(risks['commonIssues'])}")
        if len(text_parts) > 1:
            add_chunk("\n".join(text_parts), "risks", "confirmed")

    # 4. Room chunks (limitations, loadIn)
    for room in venue.get("rooms") or []:
        room_name = room.get("name", "")
        room_id = room.get("id", "")

        # Limitations
        limitations = room.get("limitations", [])
        if limitations:
            text = f"【{venue_name} - {room_name}】限制：{'; '.join(limitations)}"
            add_chunk(text, f"rooms.{room_id}.limitations", "confirmed")

        # LoadIn
        loadin = room.get("loadIn") or {}
        if isinstance(loadin, dict) and any(loadin.values()):
            text_parts = [f"【{venue_name} - {room_name}】進撤場："]
            if loadin.get("elevatorCapacity"):
                text_parts.append(f"貨梯載重：{loadin['elevatorCapacity']}")
            if loadin.get("loadingDock"):
                text_parts.append(f"卸貨區：{loadin['loadingDock']}")
            if loadin.get("setupDayBefore"):
                text_parts.append("可前一天進場布置")
            if loadin.get("loadInTime") or loadin.get("loadOutTime"):
                text_parts.append(f"進場{loadin.get('loadInTime', '?')} / 撤場{loadin.get('loadOutTime', '?')}")
            add_chunk("\n".join(text_parts), f"rooms.{room_id}.loadIn", "confirmed")

        # Equipment
        equipment = room.get("equipmentDetails", [])
        for eq in equipment:
            if eq.get("spec"):
                text = f"【{venue_name} - {room_name}】{eq.get('name', '設備')}：{eq['spec']}"
                if eq.get("externalAllowed") is not None:
                    text += f"（{'可' if eq['externalAllowed'] else '不可'}自帶）"
                add_chunk(text, f"rooms.{room_id}.equipment", "confirmed")

    # 5. Pricing tips
    pricing_tips = venue.get("pricingTips") or {}
    if isinstance(pricing_tips, dict) and pricing_tips:
        text_parts = [f"【{venue_name}】價格提示："]
        for key, value in pricing_tips.items():
            if value and key not in ["source", "verifiedAt", "expiresAt", "confidence"]:
                text_parts.append(f"{get_pricing_label(key)}：{value}")
        if len(text_parts) > 1:
            add_chunk("\n".join(text_parts), "pricingTips", "confirmed")

    return chunks


def get_category_label(category: str) -> str:
    """Convert category key to Chinese label"""
    labels = {
        "catering": "餐飲規定",
        "decoration": "佈置規定",
        "sound": "音響規定",
        "loadIn": "進撤場規定",
        "cancellation": "取消政策",
        "insurance": "保險規定",
        "pricing": "價格規定",
        "other": "其他規定"
    }
    return labels.get(category, category)


def get_pricing_label(key: str) -> str:
    """Convert pricing key to Chinese label"""
    labels = {
        "depositNote": "訂金說明",
        "overtimeNote": "超時費用",
        "holidayNote": "假日費用",
        "discountNote": "折扣說明",
        "cateringNote": "餐飲費用"
    }
    return labels.get(key, key)


def generate_embeddings_openai(chunks: list[dict], api_key: str) -> list[dict]:
    """Generate embeddings using OpenAI text-embedding-3-small"""
    try:
        from openai import OpenAI
    except ImportError:
        print("Error: openai package not installed. Run: pip install openai")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    embeddings = []
    batch_size = 100  # OpenAI API limit

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        texts = [c["text"] for c in batch]

        print(f"  Generating embeddings for batch {i//batch_size + 1} ({len(batch)} chunks)...")

        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=texts,
            encoding_format="float"
        )

        for j, chunk in enumerate(batch):
            embeddings.append({
                **chunk,
                "embedding": response.data[j].embedding
            })

    return embeddings


def main():
    parser = argparse.ArgumentParser(description="Generate embeddings for AI knowledge base")
    parser.add_argument("--output", "-o", default="ai_knowledge_base/embeddings.json",
                        help="Output file path")
    parser.add_argument("--api-key", "-k", default=None,
                        help="OpenAI API key (or set OPENAI_API_KEY env var)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Only create chunks, don't generate embeddings")
    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key and not args.dry_run:
        print("Error: OpenAI API key required. Set OPENAI_API_KEY or use --api-key")
        sys.exit(1)

    # Load venues
    print("Loading venues...")
    venues = load_venues()
    print(f"  Found {len(venues)} venues")

    # Create chunks
    print("Creating text chunks...")
    all_chunks = []
    for venue in venues:
        chunks = create_text_chunks(venue)
        all_chunks.extend(chunks)
    print(f"  Created {len(all_chunks)} chunks")

    if args.dry_run:
        # Save chunks without embeddings
        output_path = PROJECT_ROOT / "ai_knowledge_base" / "chunks_preview.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(all_chunks, f, ensure_ascii=False, indent=2)
        print(f"Dry run complete. Chunks saved to {output_path}")
        return

    # Generate embeddings
    print("Generating embeddings...")
    embeddings = generate_embeddings_openai(all_chunks, api_key)

    # Save
    output_path = PROJECT_ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "model": "text-embedding-3-small",
            "generatedAt": __import__('datetime').datetime.now().isoformat(),
            "totalChunks": len(embeddings),
            "embeddings": embeddings
        }, f, ensure_ascii=False)

    print(f"Done! Saved {len(embeddings)} embeddings to {output_path}")


if __name__ == "__main__":
    main()
