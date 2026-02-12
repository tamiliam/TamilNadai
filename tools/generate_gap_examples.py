"""
generate_gap_examples.py — Step 10: Fill coverage gaps.

Creates examples for rules identified in audit/coverage_map.md as NOT covered
by grammar.xml (Tier 1) or existing Tier 2 examples.

All rule references are to the PRIMARY source:
  தமிழ் நடைக் கையேடு (bookid=169), pages 36-88.

Usage:
    python Tamil_Nadai/tools/generate_gap_examples.py

Output:
    Tamil_Nadai/dataset/tier2_primary_gaps.jsonl
"""

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# ============================================================
# Category 1 Gaps: இலக்கண அமைப்பில் சொற்கள் (pp.37-43)
# ============================================================

CAT1_GAPS = [
    # --- Rule 1.3: Adjective + noun compound words (p.38) ---
    # When an adjective forms a compound with a noun, they join
    {
        "rule_id": "primary_1.3",
        "rule_name": "பெயரடை + பெயர் சேர்த்து எழுதுதல்",
        "category": "word_joining",
        "book_page": 38,
        "error_sentence": "நல் எண்ணம் வேண்டும்.",
        "correct_sentence": "நல்லெண்ணம் வேண்டும்.",
        "short_description": "adjective + noun compound must join",
    },
    {
        "rule_id": "primary_1.3",
        "rule_name": "பெயரடை + பெயர் சேர்த்து எழுதுதல்",
        "category": "word_joining",
        "book_page": 38,
        "error_sentence": "இனிய சொல் பேசு.",
        "correct_sentence": "இனியசொல் பேசு.",
        "short_description": "adjective + noun compound must join",
    },

    # --- Rule 1.4: When adjective+noun should be SEPARATED (p.38) ---
    # When case marker is present, separate
    {
        "rule_id": "primary_1.4",
        "rule_name": "பெயரடை + உருபு + பெயர் பிரித்து எழுதுதல்",
        "category": "word_separation",
        "book_page": 38,
        "error_sentence": "பெரியதொரு மாற்றம் வேண்டும்.",
        "correct_sentence": "பெரிய ஒரு மாற்றம் வேண்டும்.",
        "short_description": "adjective with separate noun — keep space",
    },

    # --- Rule 1.10: Verbal participle combinations (p.42) ---
    {
        "rule_id": "primary_1.10",
        "rule_name": "வினையெச்சத் தொடர்கள்",
        "category": "word_joining",
        "book_page": 42,
        "error_sentence": "ஓடி வந்தான்.",
        "correct_sentence": "ஓடிவந்தான்.",
        "short_description": "verbal participle + verb → join",
    },
    {
        "rule_id": "primary_1.10",
        "rule_name": "வினையெச்சத் தொடர்கள்",
        "category": "word_joining",
        "book_page": 42,
        "error_sentence": "படித்து முடித்தான்.",
        "correct_sentence": "படித்துமுடித்தான்.",
        "short_description": "verbal participle + completion verb → join",
    },

    # --- Rule 1.11: Reduplicated words join; similar-meaning separate (p.42) ---
    {
        "rule_id": "primary_1.11a",
        "rule_name": "அடுக்குச்சொல் சேர்த்து எழுதுதல்",
        "category": "word_joining",
        "book_page": 42,
        "error_sentence": "மெல்ல மெல்ல வந்தான்.",
        "correct_sentence": "மெல்லமெல்ல வந்தான்.",
        "short_description": "reduplicated word → join",
    },
    {
        "rule_id": "primary_1.11a",
        "rule_name": "அடுக்குச்சொல் சேர்த்து எழுதுதல்",
        "category": "word_joining",
        "book_page": 42,
        "error_sentence": "சிறிது சிறிதாக வளர்ந்தது.",
        "correct_sentence": "சிறிதுசிறிதாக வளர்ந்தது.",
        "short_description": "reduplicated word → join",
    },
    {
        "rule_id": "primary_1.11b",
        "rule_name": "ஒருபொருட்சொல் பிரித்து எழுதுதல்",
        "category": "word_separation",
        "book_page": 42,
        "error_sentence": "கட்டுக்கோப்பாக இருக்க வேண்டும்.",
        "correct_sentence": "கட்டுக் கோப்பாக இருக்க வேண்டும்.",
        "short_description": "similar-meaning pair → separate",
    },

    # --- Rule 1.12: Compounds with ஆகிய, ஆன (p.43) ---
    {
        "rule_id": "primary_1.12",
        "rule_name": "ஆகிய/ஆன தொடர்கள்",
        "category": "word_separation",
        "book_page": 43,
        "error_sentence": "அழகான குழந்தை.",
        "correct_sentence": "அழகான குழந்தை.",
        "short_description": "ஆன as suffix — keep joined (no error here, control)",
        "is_error_example": False,
    },

    # --- Rule 1.13: Conjunctions உம், ஆவது (p.43) ---
    {
        "rule_id": "primary_1.13",
        "rule_name": "உம்/ஆவது இணைப்புச் சொல்",
        "category": "word_joining",
        "book_page": 43,
        "error_sentence": "அவன் ஆவது வரவேண்டும்.",
        "correct_sentence": "அவனாவது வரவேண்டும்.",
        "short_description": "ஆவது joins with preceding word",
    },
    {
        "rule_id": "primary_1.13",
        "rule_name": "உம்/ஆவது இணைப்புச் சொல்",
        "category": "word_joining",
        "book_page": 43,
        "error_sentence": "நீ ஆவது சொல்.",
        "correct_sentence": "நீயாவது சொல்.",
        "short_description": "ஆவது joins with preceding word",
    },
]

# ============================================================
# Category 2 Gaps: தனித் சொற்களை எழுதும் முறை (pp.45-63)
# ============================================================

CAT2_GAPS = [
    # --- Rules 2.4-2.7: அல்ல, அல்லது, அல்லவா, அல்லாமல் (p.45) ---
    {
        "rule_id": "primary_2.4",
        "rule_name": "அல்ல பிரித்து எழுதுதல்",
        "category": "word_separation",
        "book_page": 45,
        "error_sentence": "இது நல்லதல்ல.",
        "correct_sentence": "இது நல்லது அல்ல.",
        "short_description": "அல்ல must be written separately",
    },
    {
        "rule_id": "primary_2.4",
        "rule_name": "அல்ல பிரித்து எழுதுதல்",
        "category": "word_separation",
        "book_page": 45,
        "error_sentence": "அவன் வரவில்லையல்ல?",
        "correct_sentence": "அவன் வரவில்லை அல்ல?",
        "short_description": "அல்ல as negation — separate",
    },
    {
        "rule_id": "primary_2.5",
        "rule_name": "அல்லது பிரித்து எழுதுதல்",
        "category": "word_separation",
        "book_page": 45,
        "error_sentence": "தேநீரல்லது காபி வேண்டுமா?",
        "correct_sentence": "தேநீர் அல்லது காபி வேண்டுமா?",
        "short_description": "அல்லது as conjunction — separate",
    },
    {
        "rule_id": "primary_2.6",
        "rule_name": "அல்லவா பிரித்து எழுதுதல்",
        "category": "word_separation",
        "book_page": 45,
        "error_sentence": "நீ வருவாயல்லவா?",
        "correct_sentence": "நீ வருவாய் அல்லவா?",
        "short_description": "அல்லவா rhetorical question — separate",
    },
    {
        "rule_id": "primary_2.7",
        "rule_name": "அல்லாமல் பிரித்து எழுதுதல்",
        "category": "word_separation",
        "book_page": 45,
        "error_sentence": "படிப்பதல்லாமல் விளையாடவும் வேண்டும்.",
        "correct_sentence": "படிப்பது அல்லாமல் விளையாடவும் வேண்டும்.",
        "short_description": "அல்லாமல் — separate",
    },

    # --- Rules 2.8-2.9: அளவு, அளி (p.46) ---
    {
        "rule_id": "primary_2.8",
        "rule_name": "அளவு — சேர்த்து/பிரித்து",
        "category": "word_joining",
        "book_page": 46,
        "error_sentence": "கொஞ்ச அளவு நீர் கொடு.",
        "correct_sentence": "கொஞ்சவளவு நீர் கொடு.",
        "short_description": "அளவு joins with measure word",
    },
    {
        "rule_id": "primary_2.8",
        "rule_name": "அளவு — சேர்த்து/பிரித்து",
        "category": "word_separation",
        "book_page": 46,
        "error_sentence": "முடிந்தவளவு செய்.",
        "correct_sentence": "முடிந்த அளவு செய்.",
        "short_description": "அளவு after participle — separate",
    },

    # --- Rules 2.14-2.16: ஆயிற்றே, ஆயினும், ஆனால் (p.48) ---
    {
        "rule_id": "primary_2.15",
        "rule_name": "ஆயினும் பிரித்து எழுதுதல்",
        "category": "word_separation",
        "book_page": 48,
        "error_sentence": "மழை பெய்தாலும்கூட ஆயினும் வருவேன்.",
        "correct_sentence": "மழை பெய்தாலும் ஆயினும் வருவேன்.",
        "short_description": "ஆயினும் as conjunction — separate",
    },
    {
        "rule_id": "primary_2.16",
        "rule_name": "ஆனால் பிரித்து எழுதுதல்",
        "category": "word_separation",
        "book_page": 48,
        "error_sentence": "படித்தான்ஆனால் தேர்வில் தோற்றான்.",
        "correct_sentence": "படித்தான். ஆனால் தேர்வில் தோற்றான்.",
        "short_description": "ஆனால் as conjunction — separate, new sentence",
    },

    # --- Rules 2.33-2.35: எங்கும், எதிர், எல்லாம் (p.54) ---
    {
        "rule_id": "primary_2.33",
        "rule_name": "எங்கும் சேர்த்து எழுதுதல்",
        "category": "word_joining",
        "book_page": 54,
        "error_sentence": "நாடு எங்கும் விழா நடந்தது.",
        "correct_sentence": "நாடெங்கும் விழா நடந்தது.",
        "short_description": "எங்கும் joins with preceding noun",
    },
    {
        "rule_id": "primary_2.34",
        "rule_name": "எதிர் சேர்த்து/பிரித்து",
        "category": "word_separation",
        "book_page": 54,
        "error_sentence": "வீட்டுக்கெதிர் கடை இருக்கிறது.",
        "correct_sentence": "வீட்டுக்கு எதிர் கடை இருக்கிறது.",
        "short_description": "எதிர் after case marker — separate",
    },
    {
        "rule_id": "primary_2.35",
        "rule_name": "எல்லாம் சேர்த்து/பிரித்து",
        "category": "word_joining",
        "book_page": 54,
        "error_sentence": "அது எல்லாம் தெரியும்.",
        "correct_sentence": "அதெல்லாம் தெரியும்.",
        "short_description": "எல்லாம் joins with pronoun",
    },
    {
        "rule_id": "primary_2.35",
        "rule_name": "எல்லாம் சேர்த்து/பிரித்து",
        "category": "word_separation",
        "book_page": 54,
        "error_sentence": "பணத்தையெல்லாம் செலவழித்தான்.",
        "correct_sentence": "பணத்தை எல்லாம் செலவழித்தான்.",
        "short_description": "எல்லாம் after case marker — separate",
    },

    # --- Rules 2.62-2.66: தொட்டு, தோறும், நடு, நடுவில், நெடு (p.63) ---
    {
        "rule_id": "primary_2.62",
        "rule_name": "தொட்டு சேர்த்து/பிரித்து",
        "category": "word_joining",
        "book_page": 63,
        "error_sentence": "காலை தொட்டு மழை பெய்கிறது.",
        "correct_sentence": "காலைதொட்டு மழை பெய்கிறது.",
        "short_description": "தொட்டு joins with time noun",
    },
    {
        "rule_id": "primary_2.63",
        "rule_name": "தோறும் சேர்த்து எழுதுதல்",
        "category": "word_joining",
        "book_page": 63,
        "error_sentence": "நாள் தோறும் பயிற்சி செய்.",
        "correct_sentence": "நாள்தோறும் பயிற்சி செய்.",
        "short_description": "தோறும் joins with preceding noun",
    },
    {
        "rule_id": "primary_2.64",
        "rule_name": "நடு சேர்த்து/பிரித்து",
        "category": "word_joining",
        "book_page": 63,
        "error_sentence": "நடு வீதியில் நின்றான்.",
        "correct_sentence": "நடுவீதியில் நின்றான்.",
        "short_description": "நடு as prefix — joins with noun",
    },
    {
        "rule_id": "primary_2.65",
        "rule_name": "நடுவில் சேர்த்து/பிரித்து",
        "category": "word_separation",
        "book_page": 63,
        "error_sentence": "கூட்டத்தின்நடுவில் பேசினார்.",
        "correct_sentence": "கூட்டத்தின் நடுவில் பேசினார்.",
        "short_description": "நடுவில் after case marker — separate",
    },
    {
        "rule_id": "primary_2.66",
        "rule_name": "நெடு சேர்த்து எழுதுதல்",
        "category": "word_joining",
        "book_page": 63,
        "error_sentence": "நெடு நாள் பழகியவன்.",
        "correct_sentence": "நெடுநாள் பழகியவன்.",
        "short_description": "நெடு as prefix — joins with noun",
    },
]

# ============================================================
# Category 3 Gaps: சந்தி — Uncovered final vowels (pp.76-86)
# ============================================================

CAT3_GAPS = [
    # --- Gemination exceptions: quotes, parentheses (p.76) ---
    {
        "rule_id": "primary_3.exception",
        "rule_name": "மேற்கோள்/அடைப்புக்குறி பின் ஒற்று மிகாமை",
        "category": "sandhi_no_doubling",
        "book_page": 76,
        "error_sentence": "'நல்லது'க் கூறினான்.",
        "correct_sentence": "'நல்லது' கூறினான்.",
        "short_description": "no doubling after closing quote",
    },
    {
        "rule_id": "primary_3.exception",
        "rule_name": "மேற்கோள்/அடைப்புக்குறி பின் ஒற்று மிகாமை",
        "category": "sandhi_no_doubling",
        "book_page": 76,
        "error_sentence": "(அவன்)க் கூறினான்.",
        "correct_sentence": "(அவன்) கூறினான்.",
        "short_description": "no doubling after closing parenthesis",
    },

    # --- Final அ extended rules (p.78) ---
    # Reduplication with அ-ending: ஒற்று doubles in reduplicated forms
    {
        "rule_id": "primary_3.a_extended",
        "rule_name": "அகர ஈற்றின் நீட்சி விதிகள்",
        "category": "sandhi_doubling",
        "book_page": 78,
        "error_sentence": "ஒவ்வொரு கணமும் முக்கியம்.",
        "correct_sentence": "ஒவ்வொருக் கணமும் முக்கியம்.",
        "short_description": "ஒவ்வொரு (a-ending) + க doubles — but see note",
        "needs_review": True,
    },

    # --- Final ஈ: Words ending in long ஈ (p.81) ---
    {
        "rule_id": "primary_3.ee",
        "rule_name": "ஈகார ஈற்றுச் சொல் பின் ஒற்று மிகுதல்",
        "category": "sandhi_doubling",
        "book_page": 81,
        "error_sentence": "தரணி கூத்தாடியது.",
        "correct_sentence": "தரணிக் கூத்தாடியது.",
        "short_description": "ஈ-ending + க doubles",
        "needs_review": True,
    },
    {
        "rule_id": "primary_3.ee",
        "rule_name": "ஈகார ஈற்றுச் சொல் பின் ஒற்று மிகுதல்",
        "category": "sandhi_doubling",
        "book_page": 81,
        "error_sentence": "வாழையிலை தட்டு வாங்கினான்.",
        "correct_sentence": "வாழையிலைத் தட்டு வாங்கினான்.",
        "short_description": "ஐ-ending compound + த doubles",
        "needs_review": True,
    },

    # --- Final ஊ: Words ending in long ஊ (p.85) ---
    {
        "rule_id": "primary_3.oo",
        "rule_name": "ஊகார ஈற்றுச் சொல் பின் ஒற்று மிகுதல்",
        "category": "sandhi_doubling",
        "book_page": 85,
        "error_sentence": "பூ கொடி அழகாக இருந்தது.",
        "correct_sentence": "பூக்கொடி அழகாக இருந்தது.",
        "short_description": "ஊ-ending (பூ) + க doubles in compound",
    },
    {
        "rule_id": "primary_3.oo",
        "rule_name": "ஊகார ஈற்றுச் சொல் பின் ஒற்று மிகுதல்",
        "category": "sandhi_doubling",
        "book_page": 85,
        "error_sentence": "தூ சுற்றம் என்பார்.",
        "correct_sentence": "தூச்சுற்றம் என்பார்.",
        "short_description": "ஊ-ending (தூ monosyllabic) + ச doubles",
    },

    # --- Final ஏ: Words ending in ஏ (p.86) ---
    {
        "rule_id": "primary_3.ae",
        "rule_name": "ஏகார ஈற்றுச் சொல் பின் விதிகள்",
        "category": "word_joining",
        "book_page": 86,
        "error_sentence": "கீழே இருந்து எடு.",
        "correct_sentence": "கீழேயிருந்து எடு.",
        "short_description": "ஏ-ending + இருந்து → ய் insertion, join",
    },
    {
        "rule_id": "primary_3.ae",
        "rule_name": "ஏகார ஈற்றுச் சொல் பின் விதிகள்",
        "category": "word_joining",
        "book_page": 86,
        "error_sentence": "வெளியே இருந்து பார்.",
        "correct_sentence": "வெளியேயிருந்து பார்.",
        "short_description": "ஏ-ending + இருந்து → ய் insertion, join",
    },

    # --- Final ஐ extended: single-letter words, descriptive compounds (p.86) ---
    {
        "rule_id": "primary_3.ai_ext",
        "rule_name": "ஐகார ஈற்று — ஓரெழுத்து/தொகை",
        "category": "sandhi_doubling",
        "book_page": 86,
        "error_sentence": "கை துண்டு எடு.",
        "correct_sentence": "கைத்துண்டு எடு.",
        "short_description": "ஐ-ending monosyllable (கை) + த doubles, compound joins",
    },
    {
        "rule_id": "primary_3.ai_ext",
        "rule_name": "ஐகார ஈற்று — ஓரெழுத்து/தொகை",
        "category": "sandhi_doubling",
        "book_page": 86,
        "error_sentence": "பச்சை கிளி அழகாக இருந்தது.",
        "correct_sentence": "பச்சைக் கிளி அழகாக இருந்தது.",
        "short_description": "descriptive ஐ-ending + க doubles",
    },
    {
        "rule_id": "primary_3.ai_ext",
        "rule_name": "ஐகார ஈற்று — ஓரெழுத்து/தொகை",
        "category": "sandhi_doubling",
        "book_page": 86,
        "error_sentence": "குதிரை குளம்பு ஒலித்தது.",
        "correct_sentence": "குதிரைக் குளம்பு ஒலித்தது.",
        "short_description": "relationship ஐ-ending + க doubles",
    },
]


def build_records(data: list[dict], origin: str) -> list[dict]:
    """Convert raw data into JSONL records."""
    records = []
    for i, item in enumerate(data):
        record = {
            "id": f"gap_{origin}_{i+1:03d}",
            "rule_id": item["rule_id"],
            "rule_name": item["rule_name"],
            "category": item["category"],
            "error_sentence": item.get("error_sentence", ""),
            "correct_sentence": item["correct_sentence"],
            "short_description": item["short_description"],
            "is_error_example": item.get("is_error_example", True),
            "origin": "tier2_primary_gaps",
            "book_page": item.get("book_page", 0),
            "book_source": "primary (bookid=169)",
            "needs_review": item.get("needs_review", True),
        }
        records.append(record)
    return records


def validate(records: list[dict]) -> int:
    """Check for common errors."""
    issues = 0
    for r in records:
        if r["is_error_example"]:
            err = r["error_sentence"].strip()
            cor = r["correct_sentence"].strip()
            if err == cor:
                print(f"  BUG: {r['id']} error == correct: {err}")
                issues += 1
            if not err or not cor:
                print(f"  BUG: {r['id']} missing sentence")
                issues += 1
    return issues


def main():
    project_dir = Path(__file__).resolve().parent.parent
    dataset_dir = project_dir / "dataset"

    all_data = CAT1_GAPS + CAT2_GAPS + CAT3_GAPS
    records = build_records(all_data, "pg")

    issues = validate(records)
    if issues:
        print(f"\nFOUND {issues} issues — fix before proceeding!")
        return

    out_path = dataset_dir / "tier2_primary_gaps.jsonl"
    with open(out_path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Stats
    error_count = sum(1 for r in records if r["is_error_example"])
    correct_count = len(records) - error_count
    unique_rules = set(r["rule_id"] for r in records)
    cats = {}
    for r in records:
        cats[r["category"]] = cats.get(r["category"], 0) + 1

    print(f"Generated {len(records)} gap-filling examples")
    print(f"  Error examples: {error_count}")
    print(f"  Correct examples: {correct_count}")
    print(f"  Unique rules: {len(unique_rules)}")
    print(f"  Categories: {cats}")
    print(f"  Needs review: {sum(1 for r in records if r.get('needs_review'))}")
    print(f"\nOutput: {out_path}")


if __name__ == "__main__":
    main()
