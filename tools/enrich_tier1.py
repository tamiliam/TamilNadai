"""
enrich_tier1.py — Step 2.4: Add taxonomy fields to Tier 1 JSONL

Reads tier1_grammar_xml.jsonl and taxonomy.json, adds category/subcategory
fields, and overwrites the JSONL with enriched records.

Usage:
    python Tamil_Nadai/tools/enrich_tier1.py
"""

import json
from pathlib import Path


def main():
    project_dir = Path(__file__).resolve().parent.parent
    jsonl_path = project_dir / 'dataset' / 'tier1_grammar_xml.jsonl'
    taxonomy_path = project_dir / 'dataset' / 'taxonomy.json'

    # Load taxonomy
    with open(taxonomy_path, 'r', encoding='utf-8') as f:
        taxonomy = json.load(f)

    rule_mappings = taxonomy['rule_mappings']

    # Load records
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        records = [json.loads(line) for line in f]

    # Enrich each record
    unmapped = set()
    for record in records:
        rule_id = record['rule_id']

        if rule_id in rule_mappings:
            mapping = rule_mappings[rule_id]
            record['category'] = mapping['category']
            record['subcategory'] = mapping.get('subcategory', '')
            record['book_rules'] = mapping.get('book_rules', [])

            # Look up the error_type from the category definition
            cat_def = taxonomy['categories'].get(mapping['category'], {})
            record['error_type'] = cat_def.get('error_type', '')

            # For correct examples, override
            if not record['is_error_example']:
                record['error_type'] = ''
        else:
            unmapped.add(rule_id)
            record['category'] = 'unknown'
            record['subcategory'] = ''
            record['book_rules'] = []
            record['error_type'] = ''

    if unmapped:
        print(f"WARNING: {len(unmapped)} unmapped rule IDs: {unmapped}")

    # Write enriched records
    with open(jsonl_path, 'w', encoding='utf-8') as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')

    # Print summary
    from collections import Counter
    cat_counts = Counter(r['category'] for r in records)
    print(f"\nEnriched {len(records)} records with taxonomy fields.")
    print(f"\nCategory distribution:")
    for cat, count in cat_counts.most_common():
        print(f"  {cat}: {count}")


if __name__ == '__main__':
    main()
