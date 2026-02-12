"""
build_coverage_map.py — Step 8: Generate coverage statistics from source data.

Reads grammar.xml rule extraction, Tier 1/2/3 datasets, and prints a summary
of rule coverage across the three book categories.

Usage:
    python Tamil_Nadai/tools/build_coverage_map.py

Output:
    Prints coverage statistics to stdout.
    The full human-written coverage map is at audit/coverage_map.md
"""

import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")


def main():
    project_dir = Path(__file__).resolve().parent.parent
    dataset_dir = project_dir / "dataset"
    tmp_dir = project_dir / ".tmp"

    # Load grammar.xml rules
    rules_path = tmp_dir / "grammar_xml_rules.json"
    if not rules_path.exists():
        print(f"ERROR: {rules_path} not found. Run the extraction first.")
        return

    with open(rules_path, "r", encoding="utf-8") as f:
        xml_rules = json.loads(f.read())

    # Load datasets
    datasets = {}
    for name in ["tier1_grammar_xml", "tier2_book_rules", "tier3_correct", "tamilnadai_v1"]:
        path = dataset_dir / f"{name}.jsonl"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                datasets[name] = [json.loads(line) for line in f if line.strip()]
        else:
            datasets[name] = []

    # === Grammar.xml Coverage ===
    print("=" * 60)
    print("TAMILNADAI COVERAGE STATISTICS")
    print("=" * 60)

    cat_counts = Counter(r["cat_id"] for r in xml_rules)
    cat_names = {
        "CAT1": "இலக்கண அமைப்பில் சொற்கள் (Grammar Structure)",
        "CAT2": "தனித் சொற்களை எழுதும் முறை (Individual Words)",
        "CAT3": "சந்தி (Sandhi)",
    }

    print("\n--- grammar.xml Rule Groups ---")
    for cat_id in ["CAT1", "CAT2", "CAT3"]:
        print(f"  {cat_id}: {cat_counts[cat_id]:>3} rule groups — {cat_names[cat_id]}")
    print(f"  Total: {len(xml_rules)} rule groups")

    # Pages covered
    pages_covered = set()
    for r in xml_rules:
        page = r.get("page", "")
        if page:
            # Extract numeric part (e.g., "40#head" -> 40)
            import re
            m = re.match(r"(\d+)", page)
            if m:
                pages_covered.add(int(m.group(1)))

    all_pages = set(range(36, 89))
    pages_not_covered = sorted(all_pages - pages_covered)

    print(f"\n--- Page Coverage (Primary Book, pages 36-88) ---")
    print(f"  Pages with grammar.xml rules: {len(pages_covered)} / {len(all_pages)}")
    print(f"  Pages NOT covered: {len(pages_not_covered)}")
    print(f"    {pages_not_covered}")

    # === Dataset Statistics ===
    print(f"\n--- Dataset Examples ---")
    for name, records in datasets.items():
        if records:
            error_count = sum(1 for r in records if r.get("is_error_example", True))
            correct_count = len(records) - error_count
            print(f"  {name}: {len(records)} total ({error_count} error, {correct_count} correct)")

    # Tier 2 rule coverage
    if datasets["tier2_book_rules"]:
        tier2_rules = set(r.get("rule_id", "") for r in datasets["tier2_book_rules"])
        tier2_cats = Counter(r.get("category", "unknown") for r in datasets["tier2_book_rules"])
        print(f"\n--- Tier 2 Rule Coverage (Secondary Book) ---")
        print(f"  Unique rules referenced: {len(tier2_rules)}")
        print(f"  Category distribution:")
        for cat, count in tier2_cats.most_common():
            print(f"    {cat}: {count}")

    # Per-category example counts from merged dataset
    if datasets["tamilnadai_v1"]:
        merged_cats = Counter(r.get("category", "unknown") for r in datasets["tamilnadai_v1"])
        print(f"\n--- Merged Dataset Category Distribution ---")
        for cat, count in merged_cats.most_common():
            print(f"  {cat}: {count}")

    # === Coverage Summary ===
    print(f"\n{'=' * 60}")
    print("COVERAGE SUMMARY")
    print(f"{'=' * 60}")
    print(f"""
  Primary book rules:     161 (13 + 112 + 36)
  grammar.xml groups:      83 (11 + 57 + 15)
  Dataset examples:       {len(datasets.get('tamilnadai_v1', []))}
  Needs expert review:    {sum(1 for r in datasets.get('tamilnadai_v1', []) if r.get('needs_review'))}

  Estimated coverage:
    Covered (in grammar.xml + dataset):  ~68 rules
    Tier 2 draft (secondary book):       ~40 rules
    Pending (identified, no examples):   ~28 rules
    Cannot test (needs morphology/NLP):  ~25 rules

  Full coverage map: audit/coverage_map.md
""")


if __name__ == "__main__":
    main()
