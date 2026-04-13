#!/usr/bin/env python3
"""
generate_embeddings_hf.py - Generate vector embeddings using HuggingFace API

Uses BAAI/bge-small-zh-v1.5 (512-dim, optimized for Chinese text).
Reads chunks_preview.json, generates embeddings, saves to embeddings.json.

Usage:
    python tools/generate_embeddings_hf.py

Environment:
    HF_API_KEY - HuggingFace API token (required)
"""

import json
import os
import sys
import time
import statistics
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
MODEL = "BAAI/bge-small-zh-v1.5"
HF_URL = f"https://router.huggingface.co/hf-inference/models/{MODEL}"


def mean_pool(embeddings):
    """Mean-pool across token dimension: [seq_len, dim] -> [dim]"""
    if not embeddings or not embeddings[0]:
        return []
    dim = len(embeddings[0])
    pooled = [0.0] * dim
    for token_vec in embeddings:
        for i in range(dim):
            pooled[i] += token_vec[i]
    n = len(embeddings)
    return [v / n for v in pooled]


def embed_batch(texts, api_key):
    """Call HF API and return pooled embeddings."""
    import requests

    r = requests.post(
        HF_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={"inputs": texts},
        timeout=60
    )

    if r.status_code != 200:
        raise Exception(f"HF API {r.status_code}: {r.text[:200]}")

    data = r.json()
    # data shape: [batch_size, seq_len, hidden_dim]
    return [mean_pool(item) for item in data]


def main():
    api_key = os.environ.get("HF_API_KEY")
    if not api_key:
        print("Error: HF_API_KEY not set")
        sys.exit(1)

    # Load chunks
    chunks_path = PROJECT_ROOT / "ai_knowledge_base" / "chunks_preview.json"
    print(f"Loading chunks from {chunks_path}...")
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    print(f"  Found {len(chunks)} chunks")

    # Generate embeddings in batches
    embeddings = []
    batch_size = 20  # Conservative for HF free tier
    failed = 0

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        texts = [c["text"] for c in batch]
        batch_num = i // batch_size + 1
        total = (len(chunks) + batch_size - 1) // batch_size

        print(f"  Batch {batch_num}/{total} ({len(batch)} chunks)...", end=" ", flush=True)

        for attempt in range(3):
            try:
                vectors = embed_batch(texts, api_key)
                for j, chunk in enumerate(batch):
                    embeddings.append({
                        **chunk,
                        "embedding": vectors[j]
                    })
                print(f"OK")
                break
            except Exception as e:
                if attempt < 2:
                    wait = (attempt + 1) * 10
                    print(f"Retry ({e}) wait {wait}s...", end=" ", flush=True)
                    time.sleep(wait)
                else:
                    print(f"FAILED: {e}")
                    failed += len(batch)

        # Rate limit
        if i + batch_size < len(chunks):
            time.sleep(1)

    if failed > 0:
        print(f"\nWarning: {failed} chunks failed")

    if not embeddings:
        print("No embeddings generated. Exiting.")
        sys.exit(1)

    # Save
    output_path = PROJECT_ROOT / "ai_knowledge_base" / "embeddings.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "model": MODEL,
            "provider": "huggingface",
            "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "totalChunks": len(embeddings),
            "embeddingDim": len(embeddings[0]["embedding"]) if embeddings else 0,
            "embeddings": embeddings
        }, f, ensure_ascii=False)

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"\nDone! {len(embeddings)} embeddings saved to {output_path} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
