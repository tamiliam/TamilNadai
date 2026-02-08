"""Generate review file for Tier 3 correct sentences."""

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")


def main():
    project_dir = Path(__file__).resolve().parent.parent
    jsonl_path = project_dir / "dataset" / "tier3_correct.jsonl"
    out_path = project_dir / "review" / "tier3_review.md"

    with open(jsonl_path, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f]

    lines = [
        "# Tier 3 Correct Sentences — Expert Review",
        f"# Total: {len(records)} sentences",
        "# Instructions: Confirm each sentence has NO grammar errors per the 174 book rules.",
        "",
        "---",
    ]

    current_sub = ""
    num = 0

    for i, r in enumerate(records):
        sub = r["subcategory"]
        if sub != current_sub:
            current_sub = sub
            lines.append("")
            lines.append(f"## {sub}")
            lines.append("")
            lines.append("| # | Correct Sentence | Note | OK? |")
            lines.append("|---|-----------------|------|-----|")

        num += 1
        lines.append(f"| {num} | {r['correct_sentence']} | {r['short_description']} | |")

        if i + 1 >= len(records) or records[i + 1]["subcategory"] != current_sub:
            lines.append("")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Written {num} sentences to {out_path}")


if __name__ == "__main__":
    main()
