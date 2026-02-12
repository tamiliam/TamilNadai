"""One-time migration: load tamilnadai.csv + sentences.csv into Django DB.

Usage:
    cd workbench_v2
    python ../tools/migrate_csv_to_db.py

This script:
  1. Creates the Source record for Book 169
  2. Loads 204 rules from tamilnadai.csv
  3. Loads 334 sentences from sentences.csv, linking each to its rule
  4. Prints summary stats
"""

import csv
import json
import os
import sys
from pathlib import Path

# Setup Django
WORKBENCH_DIR = Path(__file__).resolve().parent.parent / "workbench_v2"
sys.path.insert(0, str(WORKBENCH_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from core.models import Source, Rule, Sentence


DATA_DIR = Path(__file__).resolve().parent.parent / "source" / "data"
RULES_CSV = DATA_DIR / "tamilnadai.csv"
SENTENCES_CSV = DATA_DIR / "sentences.csv"

# Book 169 base URL for page links
TAMILVU_BASE = "https://www.tamilvu.org/library/l4100/html/l4100ind.htm"


def create_source():
    """Create or get the Book 169 source record."""
    source, created = Source.objects.get_or_create(
        source_id="tamilvu_169",
        defaults={
            "name": "தமிழ் நடைக் கையேடு (Book 169)",
            "author": "Tamil Virtual Academy",
            "year": 2004,
            "url": TAMILVU_BASE,
            "notes": "Primary source — Tamil Virtual University style guide",
        },
    )
    action = "Created" if created else "Already exists"
    print(f"  Source: {source.name} — {action}")
    return source


def load_rules(source):
    """Load rules from tamilnadai.csv."""
    created_count = 0
    skipped_count = 0

    with open(RULES_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rule_id = row["rule_id"].strip()
            if not rule_id:
                continue

            if Rule.objects.filter(rule_id=rule_id).exists():
                skipped_count += 1
                continue

            # Build source reference
            source_ref = f"{source.name}"
            source_url = ""

            Rule.objects.create(
                rule_id=rule_id,
                category=row.get("category", "").strip(),
                title=row.get("title", "").strip(),
                subtitle=row.get("subtitle", "").strip(),
                description=row.get("description", "").strip(),
                example_1=row.get("example_1", "").strip(),
                example_2=row.get("example_2", "").strip(),
                source=source,
                source_ref=source_ref,
                source_url=source_url,
                is_active=True,
            )
            created_count += 1

    print(f"  Rules: {created_count} created, {skipped_count} skipped (already exist)")
    return created_count


def load_sentences():
    """Load sentences from sentences.csv, linking to rules via tamilnadai.csv."""
    # First build the mapping: sentence_id -> rule_id
    sentence_rule_map = {}
    with open(RULES_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rule_id = row["rule_id"].strip()
            if not rule_id:
                continue

            # Parse correct_sentences_json
            correct_json = row.get("correct_sentences_json", "").strip()
            if correct_json:
                try:
                    sentence_ids = json.loads(correct_json)
                    for sid in sentence_ids:
                        sentence_rule_map[sid] = (rule_id, "correct")
                except json.JSONDecodeError:
                    pass

            # Parse wrong_sentences_json
            wrong_json = row.get("wrong_sentences_json", "").strip()
            if wrong_json:
                try:
                    sentence_ids = json.loads(wrong_json)
                    for sid in sentence_ids:
                        sentence_rule_map[sid] = (rule_id, "wrong")
                except json.JSONDecodeError:
                    pass

    # Now load sentences
    created_count = 0
    skipped_count = 0
    orphaned = 0

    with open(SENTENCES_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = row["sentence_id"].strip()
            text = row["sentence"].strip()

            if not sid or not text:
                continue

            if Sentence.objects.filter(sentence_id=sid).exists():
                skipped_count += 1
                continue

            if sid not in sentence_rule_map:
                orphaned += 1
                continue

            rule_id, sentence_type = sentence_rule_map[sid]

            try:
                rule = Rule.objects.get(rule_id=rule_id)
            except Rule.DoesNotExist:
                orphaned += 1
                continue

            Sentence.objects.create(
                sentence_id=sid,
                rule=rule,
                sentence=text,
                sentence_type=sentence_type,
                source="book",
                status="pending",
                review_count=0,
            )
            created_count += 1

    print(f"  Sentences: {created_count} created, {skipped_count} skipped, {orphaned} orphaned")
    return created_count


def print_stats():
    """Print summary statistics."""
    total_rules = Rule.objects.count()
    total_sentences = Sentence.objects.count()
    correct = Sentence.objects.filter(sentence_type="correct").count()
    wrong = Sentence.objects.filter(sentence_type="wrong").count()

    print(f"\n  Database totals:")
    print(f"    Rules:     {total_rules}")
    print(f"    Sentences: {total_sentences} (correct: {correct}, wrong: {wrong})")


def main():
    print("=== Tamil Nadai CSV to DB Migration ===\n")

    print("1. Creating source...")
    source = create_source()

    print("\n2. Loading rules...")
    load_rules(source)

    print("\n3. Loading sentences...")
    load_sentences()

    print_stats()
    print("\n=== Done ===")


if __name__ == "__main__":
    main()
