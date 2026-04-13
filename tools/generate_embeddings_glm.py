#!/usr/bin/env python3
"""
generate_embeddings_glm.py - Generate vector embeddings using GLM (智譜) API

Reads chunks_preview.json, generates embeddings via GLM embedding-3,
and saves to ai_knowledge_base/embeddings.json.

Usage:
    python tools/generate_embeddings_glm.py

Environment:
    CLASSIFIER_API_KEY - GLM API key (required)
    CLASSIFIER_BASE_URL - GLM API base URL (default: https://open.bigmodel.cn/api/paas/v4/)
"""

import json
import os
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def main():
    api_key = os.environ.get("CLASSIFIER_API_KEY")
    if not api_key:
        print("Error: CLASSIFIER_API_KEY not set")
        sys.exit(1)

    base_url = os.environ.get("CLASSIFIER_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/")

    # Load chunks
    chunks_path = PROJECT_ROOT / "ai_knowledge_base" / "chunks_preview.json"
    print(f"Loading chunks from {chunks_path}...")
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    print(f"  Found {len(chunks)} chunks")

    # Generate embeddings via OpenAI-compatible format
    try:
        from openai import OpenAI
    except ImportError:
        print("Error: openai package not installed. Run: pip install openai")
        sys.exit(1)

    client = OpenAI(api_key=api_key, base_url=base_url)

    embeddings = []
    batch_size = 50  # Conservative batch size for GLM API
    failed_batches = 0

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        texts = [c["text"] for c in batch]

        print(f"  Batch {i // batch_size + 1}/{(len(chunks) + batch_size - 1) // batch_size} ({len(batch)} chunks)...", end=" ", flush=True)

        for attempt in range(3):
            try:
                response = client.embeddings.create(
                    model="embedding-3",
                    input=texts
                )

                for j, chunk in enumerate(batch):
                    embeddings.append({
                        **chunk,
                        "embedding": response.data[j].embedding
                    })

                print(f"OK ({len(response.data)} embeddings)")
                break

            except Exception as e:
                if attempt < 2:
                    wait = (attempt + 1) * 5
                    print(f"Retry {attempt + 1} ({e}), waiting {wait}s...", end=" ", flush=True)
                    time.sleep(wait)
                else:
                    print(f"FAILED: {e}")
                    failed_batches += 1

        # Rate limit: small pause between batches
        if i + batch_size < len(chunks):
            time.sleep(0.5)

    if failed_batches > 0:
        print(f"\nWarning: {failed_batches} batches failed")
        if len(embeddings) == 0:
            print("No embeddings generated. Exiting.")
            sys.exit(1)

    # Save
    output_path = PROJECT_ROOT / "ai_knowledge_base" / "embeddings.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "model": "embedding-3",
            "provider": "glm",
            "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "totalChunks": len(embeddings),
            "embeddings": embeddings
        }, f, ensure_ascii=False)

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"\nDone! Saved {len(embeddings)} embeddings to {output_path} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
