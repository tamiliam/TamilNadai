"""
parse_grammar_xml.py — Step 1 of TamilNadai dataset pipeline

Parses ta_grammar.xml and extracts every <example> element with its
rule metadata into a structured JSONL file.

Usage:
    python Tamil_Nadai/tools/parse_grammar_xml.py

Output:
    Tamil_Nadai/dataset/tier1_grammar_xml.jsonl
"""

import json
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path


def extract_marker_span(example_text: str) -> tuple[str, str, list[int]]:
    """Extract the full sentence, marked text, and word-level span from an example.

    The example text contains <marker>...</marker> tags indicating the error span.
    We need to:
    1. Get the full sentence (without marker tags)
    2. Get the marked text
    3. Get the word-level span [start_word_idx, end_word_idx]
    """
    # Find marker content
    marker_match = re.search(r'<marker>(.*?)</marker>', example_text)
    if not marker_match:
        return example_text.strip(), "", []

    marked_text = marker_match.group(1)
    # Full sentence without tags
    full_sentence = re.sub(r'</?marker>', '', example_text).strip()

    # Word-level span: find the position of the marked text in the sentence
    # Split by whitespace to find word indices
    # First, find character position of marked text
    clean_before_marker = re.sub(r'</?marker>', '', example_text[:marker_match.start()]).strip()
    words_before = clean_before_marker.split() if clean_before_marker else []
    marked_words = marked_text.split()

    start_idx = len(words_before)
    end_idx = start_idx + len(marked_words)

    return full_sentence, marked_text, [start_idx, end_idx]


def extract_page_from_url(url: str) -> int:
    """Extract page number from tamilvu URL."""
    match = re.search(r'pno=(\d+)', url)
    return int(match.group(1)) if match else 0


def parse_grammar_xml(xml_path: str) -> list[dict]:
    """Parse grammar.xml and extract all examples with metadata."""

    tree = ET.parse(xml_path)
    root = tree.getroot()

    examples = []
    example_counter = 0

    for category in root.findall('.//category'):
        cat_id = category.get('id', '')
        cat_name = category.get('name', '')

        # Process rules — they can be directly under category or inside rulegroups
        # We need to handle both: <rule> directly in <category> and <rule> in <rulegroup>

        for element in category:
            if element.tag == 'rulegroup':
                rulegroup_id = element.get('id', '')
                rulegroup_name = element.get('name', '')

                for rule in element.findall('rule'):
                    rule_id = rule.get('id', '') or rulegroup_id
                    rule_name = rule.get('name', '') or rulegroup_name

                    examples.extend(
                        _process_rule(
                            rule, rule_id, rule_name,
                            rulegroup_id, rulegroup_name,
                            cat_id, cat_name, example_counter
                        )
                    )
                    example_counter += len([e for e in rule.findall('example')])

            elif element.tag == 'rule':
                rule_id = element.get('id', '')
                rule_name = element.get('name', '')

                examples.extend(
                    _process_rule(
                        element, rule_id, rule_name,
                        '', '',
                        cat_id, cat_name, example_counter
                    )
                )
                example_counter += len([e for e in element.findall('example')])

    return examples


def _process_rule(
    rule_elem,
    rule_id: str, rule_name: str,
    rulegroup_id: str, rulegroup_name: str,
    cat_id: str, cat_name: str,
    counter_start: int
) -> list[dict]:
    """Process a single <rule> element and extract its examples."""

    results = []

    # Extract rule-level metadata
    message_elem = rule_elem.find('message')
    message_text = ''
    if message_elem is not None:
        # Get full text content including nested elements
        message_text = ''.join(message_elem.itertext()).strip()

    url_elem = rule_elem.find('url')
    url = url_elem.text.strip() if url_elem is not None and url_elem.text else ''

    short_elem = rule_elem.find('short')
    short_desc = short_elem.text.strip() if short_elem is not None and short_elem.text else ''

    page_num = extract_page_from_url(url)

    # Extract pattern info for metadata
    pattern_elem = rule_elem.find('pattern')
    uses_postag = False
    postag_list = []
    if pattern_elem is not None:
        for token in pattern_elem.findall('token'):
            pt = token.get('postag', '')
            if pt:
                uses_postag = True
                postag_list.append(pt)

    # Process each example
    for i, example in enumerate(rule_elem.findall('example')):
        correction = example.get('correction', '')
        example_type = example.get('type', '')

        # Get the raw XML text of the example
        # We need to handle the <marker> child element
        raw_text = ET.tostring(example, encoding='unicode', method='xml')
        # Extract just the inner content (between <example ...> and </example>)
        inner_match = re.search(r'<example[^>]*>(.*?)</example>', raw_text, re.DOTALL)
        inner_text = inner_match.group(1) if inner_match else ''

        full_sentence, marked_text, span = extract_marker_span(inner_text)

        # Determine if this is an error example or correct example
        is_error = bool(correction) or example_type == 'incorrect'

        # Build the correct sentence
        if correction:
            # Replace the marked text with the correction
            correct_sentence = full_sentence.replace(marked_text, correction, 1)
        elif example_type == 'incorrect':
            correct_sentence = ''  # Will need to pair with next example
        else:
            correct_sentence = full_sentence  # This IS the correct sentence

        # Generate ID
        effective_rule_id = rulegroup_id or rule_id
        seq = counter_start + i + 1
        example_id = f"tn_{cat_id.lower()}_{effective_rule_id}_{seq:03d}"

        record = {
            "id": example_id,
            "source": f"tamilvu_169_p{page_num}" if page_num else "",
            "category_id": cat_id,
            "category_name": cat_name,
            "rule_id": effective_rule_id,
            "rule_name": rulegroup_name or rule_name,
            "book_page": page_num,
            "error_sentence": full_sentence if is_error else "",
            "correct_sentence": correct_sentence,
            "marked_text": marked_text,
            "correction": correction,
            "error_span": span,
            "message": message_text,
            "short_description": short_desc,
            "source_url": url,
            "origin": "grammar_xml",
            "is_error_example": is_error,
            "uses_postag": uses_postag,
            "postags": postag_list,
            "example_type": example_type if example_type else ("error" if correction else "correct")
        }
        results.append(record)

    return results


def write_jsonl(records: list[dict], output_path: str) -> None:
    """Write records to JSONL file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')


def print_summary(records: list[dict]) -> None:
    """Print extraction summary."""
    total = len(records)
    with_correction = sum(1 for r in records if r['correction'])
    without_correction = sum(1 for r in records if not r['correction'] and r['is_error_example'])
    correct_examples = sum(1 for r in records if not r['is_error_example'])

    cats = {}
    for r in records:
        cats[r['category_id']] = cats.get(r['category_id'], 0) + 1

    rules = set(r['rule_id'] for r in records)

    print(f"\n{'='*60}")
    print(f"TamilNadai — Tier 1 Extraction Summary")
    print(f"{'='*60}")
    print(f"Total examples extracted:     {total}")
    print(f"  With correction attribute:  {with_correction}")
    print(f"  Error (type='incorrect'):   {without_correction}")
    print(f"  Correct examples:           {correct_examples}")
    print(f"Unique rule IDs:              {len(rules)}")
    print(f"\nBy category:")
    for cat, count in sorted(cats.items()):
        print(f"  {cat}: {count}")
    print(f"{'='*60}\n")


def main():
    # Resolve paths relative to project root
    script_dir = Path(__file__).resolve().parent
    project_dir = script_dir.parent
    xml_path = project_dir / 'ta_grammar.xml'
    output_path = project_dir / 'dataset' / 'tier1_grammar_xml.jsonl'

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Parsing: {xml_path}")
    records = parse_grammar_xml(str(xml_path))

    print(f"Writing: {output_path}")
    write_jsonl(records, str(output_path))

    print_summary(records)

    # Quick validation
    print("Validating JSONL...")
    with open(output_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines, 1):
            try:
                obj = json.loads(line)
                assert 'id' in obj, f"Line {i}: missing 'id'"
                assert 'rule_id' in obj, f"Line {i}: missing 'rule_id'"
                assert 'error_sentence' in obj or 'correct_sentence' in obj, \
                    f"Line {i}: missing sentence fields"
            except json.JSONDecodeError as e:
                print(f"ERROR: Line {i} is not valid JSON: {e}")
                return

    print(f"Validation passed: {len(lines)} valid JSONL records.")


if __name__ == '__main__':
    main()
