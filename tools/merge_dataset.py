"""
merge_dataset.py — Step 5: Merge all 3 tiers into a single dataset.

Combines Tier 1 (grammar.xml), Tier 2 (book rules), and Tier 3 (correct)
into tamilnadai_v1.jsonl. Deduplicates, adds split field (80% test / 20% val),
and prints statistics.

Usage:
    python Tamil_Nadai/tools/merge_dataset.py

Output:
    Tamil_Nadai/dataset/tamilnadai_v1.jsonl
"""

import json
import sys
import hashlib
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")


def sentence_hash(record: dict) -> str:
    """Create a dedup key from error+correct sentence pair."""
    err = record.get("error_sentence", "").strip()
    cor = record.get("correct_sentence", "").strip()
    key = f"{err}||{cor}"
    return hashlib.md5(key.encode("utf-8")).hexdigest()


def main():
    project_dir = Path(__file__).resolve().parent.parent
    dataset_dir = project_dir / "dataset"

    tier1_path = dataset_dir / "tier1_grammar_xml.jsonl"
    tier2_path = dataset_dir / "tier2_book_rules.jsonl"
    tier3_path = dataset_dir / "tier3_correct.jsonl"
    output_path = dataset_dir / "tamilnadai_v1.jsonl"

    # Load all tiers
    all_records = []
    tier_counts = {}

    for label, path in [("tier1", tier1_path), ("tier2", tier2_path), ("tier3", tier3_path)]:
        if not path.exists():
            print(f"WARNING: {path} not found, skipping.")
            continue
        with open(path, "r", encoding="utf-8") as f:
            records = [json.loads(line) for line in f]
        tier_counts[label] = len(records)
        all_records.extend(records)
        print(f"Loaded {label}: {len(records)} records")

    print(f"\nTotal before dedup: {len(all_records)}")

    # Deduplicate by sentence pair
    seen_hashes = set()
    unique_records = []
    dup_count = 0

    for record in all_records:
        h = sentence_hash(record)
        if h in seen_hashes:
            dup_count += 1
            continue
        seen_hashes.add(h)
        unique_records.append(record)

    print(f"Duplicates removed: {dup_count}")
    print(f"Total after dedup: {len(unique_records)}")

    # Add split field: 80% test, 20% validation
    # Use deterministic assignment based on record index
    for i, record in enumerate(unique_records):
        record["split"] = "validation" if i % 5 == 0 else "test"

    # Renumber IDs sequentially
    for i, record in enumerate(unique_records):
        record["id"] = f"tn_{i+1:04d}"

    # Write merged dataset
    with open(output_path, "w", encoding="utf-8") as f:
        for record in unique_records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    # ========== Statistics ==========
    print(f"\n{'='*60}")
    print(f"DATASET STATISTICS — tamilnadai_v1.jsonl")
    print(f"{'='*60}")
    print(f"Total examples: {len(unique_records)}")
    print(f"  Error examples: {sum(1 for r in unique_records if r.get('is_error_example', True))}")
    print(f"  Correct examples: {sum(1 for r in unique_records if not r.get('is_error_example', True))}")

    # Split distribution
    split_counts = Counter(r["split"] for r in unique_records)
    print(f"\nSplit distribution:")
    for split, count in split_counts.most_common():
        print(f"  {split}: {count} ({count*100/len(unique_records):.1f}%)")

    # Category distribution
    cat_counts = Counter(r.get("category", "unknown") for r in unique_records)
    print(f"\nCategory distribution:")
    for cat, count in cat_counts.most_common():
        print(f"  {cat}: {count}")

    # Origin distribution
    origin_counts = Counter(r.get("origin", "unknown") for r in unique_records)
    print(f"\nOrigin (tier) distribution:")
    for origin, count in origin_counts.most_common():
        print(f"  {origin}: {count}")

    # Error type distribution
    error_types = Counter(r.get("error_type", "") for r in unique_records if r.get("error_type"))
    print(f"\nError type distribution:")
    for etype, count in error_types.most_common():
        print(f"  {etype}: {count}")

    # Needs review flag
    review_count = sum(1 for r in unique_records if r.get("needs_review"))
    print(f"\nNeeds review: {review_count} / {len(unique_records)}")

    print(f"\nOutput: {output_path}")


if __name__ == "__main__":
    main()
