"""
make_review.py — Create a human-readable review file from Tier 2 JSONL.

Usage:
    python Tamil_Nadai/tools/make_review.py
"""

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

CAT_TAMIL = {
    "sandhi_doubling": "ஒற்று மிகுதல்",
    "sandhi_no_doubling": "ஒற்று மிகாமை",
    "number_agreement": "எண் ஒப்புமை",
    "article_usage": "ஒரு/ஓர் பயன்பாடு",
    "word_separation": "பிரித்து எழுதுதல்",
    "specific_words": "தனிச்சொல் வழக்கு",
}


def main():
    project_dir = Path(__file__).resolve().parent.parent
    jsonl_path = project_dir / "dataset" / "tier2_book_rules.jsonl"
    out_path = project_dir / "review" / "tier2_review.md"

    with open(jsonl_path, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f]

    unique_rules = set(r["rule_id"] for r in records)

    lines = [
        "# Tier 2 Examples — Expert Review",
        "# TamilNadai Dataset",
        f"# Total: {len(records)} examples from {len(unique_rules)} rules",
        "# Instructions: Check each pair. Write OK or your correction in the Notes column.",
        "",
        "---",
    ]

    current_cat = ""
    current_rule = ""
    num = 0

    for i, r in enumerate(records):
        if r["category"] != current_cat:
            current_cat = r["category"]
            cat_ta = CAT_TAMIL.get(current_cat, current_cat)
            lines.append("")
            lines.append(f"## {current_cat} — {cat_ta}")
            lines.append("")

        if r["rule_id"] != current_rule:
            current_rule = r["rule_id"]
            page = f" (p.{r['book_page']})" if r["book_page"] else ""
            lines.append(f"### Rule {r['rule_id']}{page}: {r['rule_name']}")
            lines.append("")
            lines.append("| # | பிழை (Error) | திருத்தம் (Correct) | OK? | Notes |")
            lines.append("|---|--------------|---------------------|-----|-------|")

        num += 1
        lines.append(
            f"| {num} | {r['error_sentence']} | {r['correct_sentence']} | | |"
        )

        # Blank line after last example in a rule group
        if i + 1 >= len(records) or records[i + 1]["rule_id"] != current_rule:
            lines.append("")

    content = "\n".join(lines) + "\n"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Review file: {out_path}")
    print(f"Written {num} examples across {len(unique_rules)} rules")


if __name__ == "__main__":
    main()
