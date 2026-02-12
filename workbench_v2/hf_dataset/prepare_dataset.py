"""Prepare Tamil Grammar Benchmark dataset for HuggingFace upload.

Reads a JSON file (array of sentence objects) and produces:
  - sentences.csv  (main dataset)
  - rules.csv      (rule metadata)
  - sentences.jsonl (JSONL format with rule metadata)

Usage:
  python prepare_dataset.py <input.json>

The input JSON should be an array of objects with keys:
  sentence_id, rule_id, category, sentence, sentence_type,
  sentence_status, review_count, rule_title, rule_subtitle,
  rule_description, source_ref
"""

import csv
import json
import os
import sys

# Fix Windows console encoding for Tamil text
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def load_raw_data(path: str) -> list[dict]:
    """Load sentence data from a JSON file (array of objects)."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list) or not data:
        raise ValueError(f"Expected a non-empty JSON array in {path}")

    return data


def write_sentences_csv(rows: list[dict], path: str):
    """Write the main sentences dataset."""
    fieldnames = [
        "sentence_id", "rule_id", "category", "sentence",
        "sentence_type", "sentence_status", "review_count",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "sentence_id": row["sentence_id"],
                "rule_id": row["rule_id"],
                "category": row["category"],
                "sentence": row["sentence"],
                "sentence_type": row["sentence_type"],
                "sentence_status": row["sentence_status"],
                "review_count": row["review_count"],
            })
    print(f"  Wrote {len(rows)} sentences to {path}")


def write_rules_csv(rows: list[dict], path: str):
    """Write rule metadata (deduplicated)."""
    seen = set()
    rules = []
    for row in rows:
        rid = row["rule_id"]
        if rid not in seen:
            seen.add(rid)
            rules.append({
                "rule_id": rid,
                "category": row["category"],
                "title": row["rule_title"],
                "subtitle": row["rule_subtitle"],
                "description": row["rule_description"],
                "source_ref": row["source_ref"],
            })

    fieldnames = ["rule_id", "category", "title", "subtitle", "description", "source_ref"]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rules)
    print(f"  Wrote {len(rules)} rules to {path}")


def write_jsonl(rows: list[dict], path: str):
    """Write sentences as JSONL (common HF format)."""
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            record = {
                "sentence_id": row["sentence_id"],
                "rule_id": row["rule_id"],
                "category": row["category"],
                "sentence": row["sentence"],
                "sentence_type": row["sentence_type"],
                "sentence_status": row["sentence_status"],
                "review_count": row["review_count"],
                "rule_title": row["rule_title"],
                "rule_description": row["rule_description"],
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"  Wrote {len(rows)} records to {path}")


def print_stats(rows: list[dict]):
    """Print dataset statistics."""
    categories = {}
    types = {"correct": 0, "wrong": 0}
    rules = set()

    for row in rows:
        cat = row["category"]
        categories[cat] = categories.get(cat, 0) + 1
        types[row["sentence_type"]] = types.get(row["sentence_type"], 0) + 1
        rules.add(row["rule_id"])

    print(f"\n  Dataset Statistics:")
    print(f"  Total sentences: {len(rows)}")
    print(f"  Total rules:     {len(rules)}")
    print(f"  Correct:         {types.get('correct', 0)}")
    print(f"  Wrong:           {types.get('wrong', 0)}")
    print(f"\n  By category:")
    for cat, count in sorted(categories.items()):
        print(f"    {cat}: {count}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python prepare_dataset.py <input.json>")
        print("  The input file should be a JSON array of sentence objects.")
        sys.exit(1)

    input_file = sys.argv[1]
    print(f"Loading data from {input_file}...")
    rows = load_raw_data(input_file)
    print(f"  Loaded {len(rows)} rows")

    print_stats(rows)

    print("\nWriting sentences.csv...")
    write_sentences_csv(rows, os.path.join(OUTPUT_DIR, "sentences.csv"))

    print("Writing rules.csv...")
    write_rules_csv(rows, os.path.join(OUTPUT_DIR, "rules.csv"))

    print("Writing sentences.jsonl...")
    write_jsonl(rows, os.path.join(OUTPUT_DIR, "sentences.jsonl"))

    print("\nDone! Files ready in:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
