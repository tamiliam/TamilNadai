#!/usr/bin/env python3
"""Extract rules and examples from Tamil Nadai book pages into CSV files.

Source: தமிழ் நடைக் கையேடு (Tamil Virtual University, 2007)
Book ID: 169, Pages 36-101

Outputs:
  source/data/tamilnadai.csv — All 204 rules (23 CAT1 + 140 CAT2 + 36 CAT3 + 5 exceptions)
  source/data/sentences.csv  — All example sentences/phrases

Usage:
  python tools/extract_book_data.py
"""

import csv
import json
import re
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
PAGES_DIR = PROJECT_DIR / ".tmp" / "book_pages"
OUTPUT_DIR = PROJECT_DIR / "source" / "data"
RULE_MAP = PROJECT_DIR / "docs" / "complete_rule_map.md"

# Tamil Unicode helpers
TAMIL_CHAR = r"[\u0B80-\u0BFF]"
TAMIL_WORD = r"[\u0B80-\u0BFF\u200C\u200D]+"  # includes ZWJ/ZWNJ

# Category names in Tamil
CAT1_NAME = "இலக்கண அமைப்பில் சொற்கள்"
CAT2_NAME = "தனிச் சொற்களை எழுதும் முறை"
CAT3_NAME = "சந்தி"

# CAT1 section headings (rule prefix → section title)
CAT1_SECTIONS = {
    "1.1": "பெயர் + பெயர்",
    "1.2": "பெயர் + பெயர் (உடம்படுமெய்)",
    "1.3": "-அம் ஏற்ற பெயர் + பெயர்",
    "1.4": "பெயரடை + பெயர்",
    "1.5": "பெயர் + இடைச்சொல்",
    "1.6": "பெயர் + வினை",
    "1.7": "வினையடி + பெயர்",
    "1.8": "வினை + வினை",
    "1.9": "செ(ய்)ய வினையெச்சம் + வினை",
    "1.10": "வினையெச்சம் + வினை",
    "1.11": "இரட்டைச் சொற்கள்",
    "1.12": "முன்னும் பின்னும் வரும் சொற்கள்",
    "1.13": "இடைச்சொல் ஏற்கும் சொற்கள்",
}

# CAT3 rule number → final letter mapping
CAT3_LETTERS = {
    1: "அ", 2: "ஆ", 3: "இ", 4: "ஈ", 5: "உ", 6: "ஊ",
    7: "ஏ", 8: "ஐ", 9: "ஓ/ஔ",
    10: "க்", 11: "கு", 12: "ங்", 13: "ச்", 14: "சு",
    15: "ட்", 16: "டு", 17: "ண்", 18: "ணு",
    19: "த்", 20: "து", 21: "பு",
    22: "ம்", 23: "ய்", 24: "ர்", 25: "ரு",
    26: "ல்", 27: "லு", 28: "ழ்", 29: "ழு",
    30: "ள்", 31: "ளு", 32: "ன்", 33: "னு",
    34: "ஜ்", 35: "ஷ்", 36: "ஸ்",
}

# Cross-reference rules in CAT3 (rule_num: target_letter)
CAT3_CROSSREFS = {14: "உ", 16: "உ", 18: "உ", 20: "உ", 21: "உ",
                   25: "உ", 27: "உ", 29: "உ", 31: "உ", 33: "உ"}


# ============================================================
# Step 1: Parse complete_rule_map.md for rule metadata
# ============================================================

def parse_rule_map() -> list[dict]:
    """Parse complete_rule_map.md to get all rule metadata.

    Returns list of dicts with keys:
        rule_id, category, title, subtitle, description
    """
    text = RULE_MAP.read_text(encoding="utf-8")
    rules = []

    # Find CAT1 table rows
    in_cat1 = False
    in_cat2 = False
    in_cat3 = False

    for line in text.splitlines():
        line = line.strip()

        # Detect section boundaries
        if "## 1. இலக்கண அமைப்பில் சொற்கள்" in line:
            in_cat1, in_cat2, in_cat3 = True, False, False
            continue
        elif "## 2. தனிச் சொற்களை எழுதும் முறை" in line:
            in_cat1, in_cat2, in_cat3 = False, True, False
            continue
        elif "## 3. சந்தி" in line:
            in_cat1, in_cat2, in_cat3 = False, False, True
            continue
        elif line.startswith("## ") or line.startswith("**CAT"):
            if line.startswith("**CAT"):
                pass  # Summary lines, don't change section
            elif line.startswith("## Summary") or line.startswith("---"):
                in_cat1 = in_cat2 = in_cat3 = False
            continue

        # Skip non-table lines
        if not line.startswith("|") or line.startswith("|-"):
            continue

        # Parse table cells
        cells = [c.strip() for c in line.split("|")]
        # Remove empty first/last cells from leading/trailing |
        cells = [c for c in cells if c]

        if len(cells) < 3:
            continue

        # Skip header rows
        if cells[0] == "No":
            continue

        try:
            int(cells[0])
        except ValueError:
            continue

        if in_cat1 and len(cells) >= 4:
            rule_id = cells[1]
            description = cells[2]
            # Determine section heading
            section_key = ".".join(rule_id.rstrip("அஆஇஈ").split(".")[:2])
            title = CAT1_SECTIONS.get(section_key, "")
            rules.append({
                "rule_id": rule_id,
                "category": CAT1_NAME,
                "title": title,
                "subtitle": "",
                "description": description,
            })

        elif in_cat2 and len(cells) >= 5:
            rule_id = cells[1]
            word = cells[2]
            description = cells[3]
            rules.append({
                "rule_id": rule_id,
                "category": CAT2_NAME,
                "title": word,
                "subtitle": "",
                "description": description,
            })

        elif in_cat3 and len(cells) >= 5:
            rule_id = cells[1]
            final_letter = cells[2]
            description = cells[3]
            rules.append({
                "rule_id": rule_id,
                "category": CAT3_NAME,
                "title": final_letter,
                "subtitle": "",
                "description": description,
            })

    return rules


# ============================================================
# Step 2: Read book pages
# ============================================================

def read_page(page_num: int) -> str:
    """Read a single book page file. Returns empty string if not found."""
    path = PAGES_DIR / f"page_{page_num:03d}.txt"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def read_pages(start: int, end: int) -> str:
    """Read a range of pages and concatenate them."""
    texts = []
    for n in range(start, end + 1):
        text = read_page(n)
        if text:
            texts.append(text)
    return "\n".join(texts)


# ============================================================
# Step 3: Extract examples from book pages
# ============================================================

def clean_line(line: str) -> str:
    """Remove excessive whitespace from OCR'd text while preserving Tamil."""
    # Replace multiple spaces/tabs with single space
    return re.sub(r"[ \t]+", " ", line).strip()


def is_tamil_text(text: str) -> bool:
    """Check if text contains Tamil characters."""
    return bool(re.search(TAMIL_CHAR, text))


def _is_description_text(line: str) -> bool:
    """Check if a line is likely description/explanation text, not an example.

    Uses both exact keywords and stem matching (strip trailing virama ்)
    to handle Tamil morphological inflections like தொடங்கும் → தொடங்குமானால்.
    """
    DESC_KEYWORDS = [
        "வேண்டும்", "எழுதப்பட", "வரும்போது", "இருக்கும்",
        "போன்று", "தொடங்கும்", "முடியும்", "சொல்லின்",
        "இரட்டிக்கும்", "மிகும்போது", "எழுதலாம்",
        "சேர்த்து எழுத", "இடம்விட்டு எழுத", "எ-டு", "இவ்வாறு",
        "பயன்படுத்த", "பொருளில்", "வருகிற", "அடுத்து வரும்",
        "சொற்கள்", "விகுதி", "உருபு",
        "பெயர்ச்சொல்", "வினைச்சொல்", "வினையெச்ச",
        "பெயரடை", "வினையடி", "தொகை", "இலக்கண",
        "மாற்றம்", "ஏற்கும்போது", "மறையும்", "மறைந்து",
        "தவிர்க்க", "எழுதப்படுகின்றன", "எழுதப்படுகிறது",
        "என்னும்", "ஆகிய", "என்ற பொருளில்",
        "பின்வரும்", "மேலே", "குறிப்பிட", "அமையும்",
        "அகராதியில்", "க்ரியா", "தனித்தே",
        "சொல்லோடு", "சொல்லுடன்", "சொல்லுக்கு",
        "சொல்லைச்", "பொதுவாக", "இடைச்சொல்",
        "தொடரும்", "அசை", "உயிரெழுத்து", "மெய்யெழுத்து",
        "குறில்", "நெடில்", "ஒற்று", "மிகும்", "மிகாது",
        "வருவதில்லை", "காணப்படுகிறது", "என்பது",
        "போன்ற", "என்பதை", "இருந்தால்",
        "பெரும்பாலும்", "தரப்பட்ட", "கூறிய",
        # Additional keywords to catch remaining description fragments
        "சொல்லால்", "சொல்லை", "எழுத்தாக", "வேறொரு",
        "உடம்படுமெய்", "எழுதுவது", "ஓரசை", "ஈரசை",
        "வல்லெழுத்து", "இடைநிலை", "மாறும்", "ஏற்கும்",
        "நிலையில்", "இரண்டு", "இரட்டிக்க",
    ]
    VIRAMA = "\u0BCD"  # Tamil virama ்

    for kw in DESC_KEYWORDS:
        if kw in line:
            return True
        # Stem matching: strip trailing virama and check
        # This handles inflections like தொடங்கும் matching தொடங்குமானால்
        if kw.endswith(VIRAMA):
            stem = kw[:-1]
            if stem in line:
                return True
    return False


def extract_cat1_examples(pages_text: str) -> dict[str, list[str]]:
    """Extract examples from CAT1 pages (36-43).

    Strategy: description text is filtered by keyword detection.
    Short Tamil-only lines without description keywords are treated as examples.

    Returns {rule_id: [list of example strings]}.
    """
    examples: dict[str, list[str]] = {}
    current_rule = None

    # Rule header: 1.X.Y or 1.X.Yஅ/ஆ (also handles 1.7.2.1)
    rule_header_re = re.compile(
        r"^(1\.\d+(?:\.\d+)*[அஆ]?)\s+",
    )
    # Section header: --- 1.X or 1.X (not a rule)
    section_header_re = re.compile(
        r"^(?:---\s*)?(1\.\d+)\s+[^\d]",
    )
    # Compound with breakdown: word (part + part) or word(part+part)
    # Also handles space-separated: word (part part)
    compound_re = re.compile(
        rf"({TAMIL_WORD})\s*\(\s*({TAMIL_WORD})\s*[\+\s]\s*({TAMIL_WORD})\s*\)",
    )
    # Sandhi equation: word+word=result
    equation_re = re.compile(
        rf"({TAMIL_WORD})\+({TAMIL_WORD})=({TAMIL_WORD})",
    )
    # (அ)/(ஆ)/(இ)/(ஈ) sentence
    sentence_label_re = re.compile(
        r"^\([\u0B85-\u0B88]\)\s+(.+)",
    )

    for raw_line in pages_text.splitlines():
        line = clean_line(raw_line)
        if not line:
            continue

        # Skip page headers and markdown
        if line.startswith("#") or line.startswith("[Page") or line.startswith("=="):
            continue

        # Check for rule header
        m = rule_header_re.match(line)
        if m:
            rid = m.group(1)
            if rid.count(".") >= 2 or any(c in rid for c in "அஆ"):
                current_rule = rid
                if current_rule not in examples:
                    examples[current_rule] = []
                continue

        # Section header (1.X level) — skip
        m = section_header_re.match(line)
        if m and m.group(1).count(".") == 1:
            continue

        if not current_rule:
            continue

        # --- Known example patterns (always extract) ---

        # Compound words with breakdown
        found = False
        for m in compound_re.finditer(line):
            examples[current_rule].append(m.group(1))
            found = True
        if found:
            continue

        # Equations (word+word=result)
        for m in equation_re.finditer(line):
            examples[current_rule].append(m.group(3))
            found = True
        if found:
            continue

        # Labeled sentences
        m = sentence_label_re.match(line)
        if m:
            examples[current_rule].append(m.group(1).strip())
            continue

        # --- Standalone word/phrase examples ---
        # Filter: must be short Tamil text, not description, not cross-ref
        if (
            is_tamil_text(line)
            and not line.startswith("(")
            and not re.match(r"^\d", line)
            and not re.match(r"^---", line)
            and "காண்க" not in line
            and "எ-டு" not in line
            and not _is_description_text(line)
        ):
            # Strip trailing parenthetical notes: "word (note about...)"
            clean = re.sub(r"\s*\([^)]*$", "", line).strip()
            if not clean:
                clean = line
            words = clean.split()
            if len(words) <= 3 and len(clean) < 50:
                examples[current_rule].append(clean)

    return examples


def extract_cat2_examples(pages_text: str, known_rule_ids: set[str] = None) -> dict[str, list[str]]:
    """Extract examples from CAT2 pages (44-73).

    Strategy: description text is filtered by keyword detection.
    Labeled sentences (அ)/(ஆ)/(இ)/(ஈ) are always extracted.
    Short Tamil-only lines without description keywords are treated as examples.

    known_rule_ids: set of valid rule IDs from rule_map, used to resolve
    ambiguous headers like "2.4 அ" → "2.4அ" vs "2.1 அ" → "2.1".

    Returns {rule_id: [list of example strings]}.
    """
    examples: dict[str, list[str]] = {}
    current_rule = None
    continuation = False  # True if previous line started a multi-line sentence

    if known_rule_ids is None:
        known_rule_ids = set()

    # Rule header: 2.X or 2.Xஅ/ஆ or "2.X அ/ஆ" (space-separated)
    rule_header_re = re.compile(
        r"^(2\.\d+)\s*([அஆ])?\s+",
    )
    # (அ)/(ஆ)/(இ)/(ஈ) sentence
    sentence_label_re = re.compile(
        r"^\([\u0B85-\u0B88]\)\s+(.+)",
    )

    for raw_line in pages_text.splitlines():
        line = clean_line(raw_line)
        if not line:
            continuation = False
            continue

        # Skip page headers and markdown
        if line.startswith("#") or line.startswith("[Page") or line.startswith("=="):
            continuation = False
            continue

        # Check for rule header
        m = rule_header_re.match(line)
        if m:
            base_num = m.group(1)     # e.g. "2.4"
            suffix_char = m.group(2)  # e.g. "அ" or None

            # Resolve rule ID: try with suffix first, then without
            if suffix_char and f"{base_num}{suffix_char}" in known_rule_ids:
                current_rule = f"{base_num}{suffix_char}"
            else:
                current_rule = base_num

            if current_rule not in examples:
                examples[current_rule] = []
            continuation = False
            continue

        if not current_rule:
            continue

        # Handle continuation of multi-line sentence
        if continuation and is_tamil_text(line) and not line.startswith("("):
            if examples[current_rule]:
                prev = examples[current_rule][-1]
                examples[current_rule][-1] = prev + " " + line
            continuation = not line.rstrip().endswith(".")
            continue

        # Labeled sentences: (அ), (ஆ), (இ), (ஈ) — always extract
        m = sentence_label_re.match(line)
        if m:
            sentence = m.group(1).strip()
            examples[current_rule].append(sentence)
            continuation = not sentence.rstrip().endswith(".")
            continue

        # Skip cross-references, sub-points, parenthesized notes
        if "காண்க" in line:
            continue
        if re.match(r"^\d+\.\s", line):
            continue
        if line.startswith("(") and not sentence_label_re.match(line):
            continue

        # --- Standalone word/phrase examples ---
        # Filter: must be short Tamil text, not description
        if (
            is_tamil_text(line)
            and not re.match(r"^\d", line)
            and not line.startswith("---")
            and not _is_description_text(line)
        ):
            words = line.split()
            if len(words) <= 3 and len(line) < 50:
                examples[current_rule].append(line)

        continuation = False

    return examples


def extract_cat3_examples(pages_text: str) -> dict[str, list[str]]:
    """Extract examples from CAT3 pages (77-101).

    Handles:
    - Split rule headers: "N" on one line, ". முதல்..." on next (OCR artifact)
    - Multi-line equations: "word+word=" on one line, result on next
    - Variant results: "result1/result2"

    Returns {rule_id: [list of example strings]}.
    rule_id is in 3.N format (e.g., "3.1", "3.22").
    """
    examples: dict[str, list[str]] = {}
    current_rule_num = None

    # Cross-reference: "காண்க:" or "காண்க :"
    crossref_re = re.compile(r"காண்க\s*:")
    # Sandhi equation: word+word=result (result may be empty if on next line)
    equation_re = re.compile(
        rf"({TAMIL_WORD}(?:\([^)]*\))?)\s*\+\s*({TAMIL_WORD})\s*=\s*(.*)"
    )

    # Pre-process: join split rule headers and multi-line equations
    raw_lines = pages_text.splitlines()
    lines = []
    i = 0
    while i < len(raw_lines):
        line = clean_line(raw_lines[i])
        if not line:
            lines.append("")
            i += 1
            continue

        # Join split headers: "N" alone followed by ". முதல்..."
        if re.match(r"^\d{1,2}$", line):
            num = int(line)
            if 1 <= num <= 36 and i + 1 < len(raw_lines):
                next_line = clean_line(raw_lines[i + 1])
                if next_line.startswith(". ") or next_line.startswith("."):
                    line = line + next_line  # e.g., "2" + ". முதல்..." → "2. முதல்..."
                    i += 1  # skip next line

        # Join multi-line equations: "word+word=" alone, result on next line
        if re.search(r"=\s*$", line) and re.search(r"\+", line):
            if i + 1 < len(raw_lines):
                next_line = clean_line(raw_lines[i + 1])
                if next_line and is_tamil_text(next_line) and "+" not in next_line:
                    line = line + next_line
                    i += 1  # skip next line

        lines.append(line)
        i += 1

    # Rule header: "N. முதல் சொல்லின்" or "N." on its own line
    rule_header_re = re.compile(r"^(\d+)\.\s*(?:முதல்\s+சொல்லின்|$)")

    for line in lines:
        if not line:
            continue

        # Skip page headers and markdown
        if line.startswith("#") or line.startswith("[Page") or line.startswith("=="):
            continue

        # Check for rule header
        m = rule_header_re.match(line)
        if m:
            num = int(m.group(1))
            if 1 <= num <= 36:
                current_rule_num = num
                rule_id = f"3.{num}"
                if rule_id not in examples:
                    examples[rule_id] = []

                # Check if this is a cross-reference rule
                rest = line[m.end():]
                if crossref_re.search(rest):
                    pass
                continue

        if current_rule_num is None:
            continue

        rule_id = f"3.{current_rule_num}"

        # Check for cross-reference on its own line
        if crossref_re.search(line):
            continue

        # Extract sandhi equations
        for m in equation_re.finditer(line):
            result_str = m.group(3).strip()
            if not result_str:
                continue  # No result even after joining
            # Handle variants separated by /
            variants = [v.strip() for v in result_str.split("/")]
            for variant in variants:
                # Clean up: extract Tamil phrase from result
                clean = re.match(rf"({TAMIL_WORD}(?:\s+{TAMIL_WORD})*)", variant)
                if clean:
                    examples[rule_id].append(clean.group(1))

    return examples


def extract_exception_rules(pages_text: str) -> list[dict]:
    """Extract the 5 exception rules from pages 75-76.

    Returns list of dicts with:
        rule_id, description, examples
    """
    exceptions = []

    # The exceptions are numbered (1) through (5)
    # Split text by these markers
    exception_re = re.compile(r"\((\d)\)\s+(.+?)(?=\(\d\)\s|\Z)", re.DOTALL)

    for m in exception_re.finditer(pages_text):
        num = int(m.group(1))
        if num < 1 or num > 5:
            continue

        block = m.group(2)
        rule_id = f"3.0.{num}"

        # Extract the description (first sentence/paragraph)
        lines = [clean_line(l) for l in block.splitlines() if clean_line(l)]
        description_lines = []
        example_lines = []
        in_examples = False

        for line in lines:
            if not line or line.startswith("#") or line.startswith("[Page"):
                continue
            # Once we see Tamil-heavy text after description, it's an example
            if not in_examples:
                description_lines.append(line)
                # Heuristic: description ends when we see a line that looks like
                # an example (e.g., starts with Tamil text that's a sentence)
                if line.rstrip().endswith(".") or line.rstrip().endswith(":"):
                    in_examples = True
            else:
                if is_tamil_text(line) and len(line) > 5:
                    example_lines.append(line)

        desc = " ".join(description_lines[:3])  # First few description lines
        exs = [l for l in example_lines if len(l) > 3]

        exceptions.append({
            "rule_id": rule_id,
            "category": CAT3_NAME,
            "title": "சந்தி விதிவிலக்கு",
            "subtitle": f"விதிவிலக்கு {num}",
            "description": desc[:300],  # Truncate if too long
            "examples": exs[:10],
        })

    return exceptions


# ============================================================
# Step 4: Build and write CSV files
# ============================================================

def _strip_trailing_examples(description: str) -> str:
    """Remove trailing parenthetical examples from rule descriptions.

    e.g. "சேர்த்தே எழுதப்படுகிறது (அக்காலத்தில், அச்சமயம்)"
      → "சேர்த்தே எழுதப்படுகிறது"

    These examples are redundant since they're already in sentences.csv.
    """
    return re.sub(r"\s*\([^()]+\)\s*$", "", description).strip()


def main():
    print("=" * 60)
    print("TamilNadai Book Data Extraction")
    print("=" * 60)

    # --- Parse rule metadata ---
    print("\n1. Parsing rule metadata from complete_rule_map.md...")
    rules = parse_rule_map()
    print(f"   Found {len(rules)} rules from rule map")

    cat_counts = {}
    for r in rules:
        cat = r["category"]
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    for cat, count in cat_counts.items():
        print(f"   - {cat}: {count}")

    # --- Read book pages ---
    print("\n2. Reading book pages...")
    cat1_text = read_pages(36, 43)
    cat2_text = read_pages(44, 73)
    cat3_text = read_pages(77, 101)
    exception_text = read_pages(75, 76)
    print(f"   CAT1 text: {len(cat1_text)} chars")
    print(f"   CAT2 text: {len(cat2_text)} chars")
    print(f"   CAT3 text: {len(cat3_text)} chars")

    # --- Extract examples ---
    print("\n3. Extracting examples...")

    cat1_examples = extract_cat1_examples(cat1_text)
    cat1_total = sum(len(v) for v in cat1_examples.values())
    print(f"   CAT1: {cat1_total} examples across {len(cat1_examples)} rules")

    known_rule_ids = {r["rule_id"] for r in rules}
    cat2_examples = extract_cat2_examples(cat2_text, known_rule_ids)
    cat2_total = sum(len(v) for v in cat2_examples.values())
    print(f"   CAT2: {cat2_total} examples across {len(cat2_examples)} rules")

    cat3_examples = extract_cat3_examples(cat3_text)
    cat3_total = sum(len(v) for v in cat3_examples.values())
    print(f"   CAT3: {cat3_total} examples across {len(cat3_examples)} rules")

    exception_rules = extract_exception_rules(exception_text)
    exc_total = sum(len(e["examples"]) for e in exception_rules)
    print(f"   Exceptions: {exc_total} examples across {len(exception_rules)} rules")

    # --- Merge all examples ---
    all_examples: dict[str, list[str]] = {}
    for d in [cat1_examples, cat2_examples, cat3_examples]:
        for rule_id, exs in d.items():
            all_examples.setdefault(rule_id, []).extend(exs)
    for exc in exception_rules:
        all_examples.setdefault(exc["rule_id"], []).extend(exc["examples"])

    # Deduplicate examples per rule
    for rule_id in all_examples:
        seen = set()
        deduped = []
        for ex in all_examples[rule_id]:
            ex_clean = ex.strip()
            if ex_clean and ex_clean not in seen:
                seen.add(ex_clean)
                deduped.append(ex_clean)
        all_examples[rule_id] = deduped

    # --- Build sentences.csv ---
    print("\n4. Building sentences.csv...")
    sentences = []  # (sentence_id, sentence)
    sentence_id_counter = 1
    rule_sentence_map: dict[str, list[str]] = {}  # rule_id -> [sentence_ids]

    for rule_id in sorted(all_examples.keys(), key=_sort_rule_id):
        rule_sentence_map[rule_id] = []
        # Skip first 2 examples (they go into example_1/example_2 columns)
        for example in all_examples[rule_id][2:10]:  # Examples 3-10 only
            sid = f"SEN-{sentence_id_counter:05d}"
            sentences.append((sid, example))
            rule_sentence_map[rule_id].append(sid)
            sentence_id_counter += 1

    print(f"   Total sentences: {len(sentences)}")

    # --- Build tamilnadai.csv ---
    print("\n5. Building tamilnadai.csv...")

    # Combine rule metadata with examples
    csv_rows = []

    # Add main rules
    for rule in rules:
        rid = rule["rule_id"]
        sids = rule_sentence_map.get(rid, [])
        exs = all_examples.get(rid, [])

        csv_rows.append({
            "rule_id": rid,
            "category": rule["category"],
            "rule": rid,
            "title": rule["title"],
            "subtitle": rule["subtitle"],
            "description": _strip_trailing_examples(rule["description"]),
            "example_1": exs[0] if len(exs) >= 1 else "",
            "example_2": exs[1] if len(exs) >= 2 else "",
            "correct_sentences_json": json.dumps(sids, ensure_ascii=False) if sids else "[]",
            "correct_sentences_count": len(sids),
            "wrong_sentences_json": "[]",
            "wrong_sentences_count": 0,
            "reviewer_one_acceptance_count": 0,
            "reviewer_two_acceptance_count": 0,
            "done": "FALSE",
        })

    # Add exception rules
    for exc in exception_rules:
        rid = exc["rule_id"]
        sids = rule_sentence_map.get(rid, [])
        exs = exc.get("examples", [])

        csv_rows.append({
            "rule_id": rid,
            "category": exc["category"],
            "rule": rid,
            "title": exc["title"],
            "subtitle": exc["subtitle"],
            "description": exc["description"],
            "example_1": exs[0] if len(exs) >= 1 else "",
            "example_2": exs[1] if len(exs) >= 2 else "",
            "correct_sentences_json": json.dumps(sids, ensure_ascii=False) if sids else "[]",
            "correct_sentences_count": len(sids),
            "wrong_sentences_json": "[]",
            "wrong_sentences_count": 0,
            "reviewer_one_acceptance_count": 0,
            "reviewer_two_acceptance_count": 0,
            "done": "FALSE",
        })

    # Sort rows by rule_id
    csv_rows.sort(key=lambda r: _sort_rule_id(r["rule_id"]))

    print(f"   Total rules: {len(csv_rows)}")

    # --- Write CSVs ---
    print("\n6. Writing CSV files...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Write sentences.csv
    sentences_path = OUTPUT_DIR / "sentences.csv"
    with open(sentences_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["sentence_id", "sentence"])
        for sid, sentence in sentences:
            writer.writerow([sid, sentence])
    print(f"   Wrote {len(sentences)} rows to {sentences_path}")

    # Write tamilnadai.csv
    rules_path = OUTPUT_DIR / "tamilnadai.csv"
    fieldnames = [
        "rule_id", "category", "rule", "title", "subtitle", "description",
        "example_1", "example_2",
        "correct_sentences_json", "correct_sentences_count",
        "wrong_sentences_json", "wrong_sentences_count",
        "reviewer_one_acceptance_count", "reviewer_two_acceptance_count",
        "done",
    ]
    with open(rules_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)
    print(f"   Wrote {len(csv_rows)} rows to {rules_path}")

    # --- Summary ---
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    rules_with_examples = sum(1 for r in csv_rows if r["correct_sentences_count"] > 0)
    rules_without = sum(1 for r in csv_rows if r["correct_sentences_count"] == 0)

    print(f"Total rules:            {len(csv_rows)}")
    print(f"Rules with examples:    {rules_with_examples}")
    print(f"Rules without examples: {rules_without}")
    print(f"Total sentences:        {len(sentences)}")

    # Per-category breakdown
    print("\nPer-category:")
    for cat_name in [CAT1_NAME, CAT2_NAME, CAT3_NAME]:
        cat_rules = [r for r in csv_rows if r["category"] == cat_name]
        cat_with = sum(1 for r in cat_rules if r["correct_sentences_count"] > 0)
        cat_sents = sum(r["correct_sentences_count"] for r in cat_rules)
        print(f"  {cat_name}:")
        print(f"    Rules: {len(cat_rules)} ({cat_with} with examples)")
        print(f"    Sentences: {cat_sents}")

    # List rules without examples
    if rules_without > 0:
        print(f"\nRules with 0 examples ({rules_without}):")
        for r in csv_rows:
            if r["correct_sentences_count"] == 0:
                print(f"  {r['rule_id']:10s} — {r['description'][:60]}")


def _sort_rule_id(rule_id: str) -> tuple:
    """Sort key for rule IDs like 1.1.1, 2.4அ, 3.0.1, 3.22."""
    # Strip Tamil suffixes for numeric sorting
    clean = rule_id.rstrip("அஆஇஈ")
    suffix = rule_id[len(clean):]
    suffix_order = {"": 0, "அ": 1, "ஆ": 2, "இ": 3, "ஈ": 4}

    parts = clean.split(".")
    nums = []
    for p in parts:
        try:
            nums.append(int(p))
        except ValueError:
            nums.append(0)

    # Pad to 4 parts
    while len(nums) < 4:
        nums.append(0)

    return (*nums, suffix_order.get(suffix, 9))


if __name__ == "__main__":
    main()
