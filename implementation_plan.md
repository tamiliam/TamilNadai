# Implement Remaining Tamil Grammar Rules + Adversarial Review

## Context

The audit (`.tmp/audit_report.md`) found that 83 of ~88 machine-implementable rules are already in `ta_grammar.xml`. Of those 83, all are correct. **15 rules remain to implement** (originally 17, but Rule 92 `விட/கூட` is already in `Ends_in_A_3`, and Rule 61 is a simple expansion of that same rule).

The commented-out block at lines 2066-2111 was an earlier attempt at some of these — it has bugs (wrong message text, deprecated example format). We'll replace it with correct rules.

---

## What We're Building

### 15 Changes to `ta_grammar.xml`

| # | Book Rule | ID | Type | Batch |
|---|-----------|-----|------|-------|
| 1 | 57: அப்படி/இப்படி/எப்படி | `appadi_ippadi_eppadi` | New rulegroup (4 sub-rules) | 1 |
| 2 | 58: அவ்வகை/இவ்வகை/எவ்வகை | `avvagai_ivvagai_evvagai` | New rulegroup (4 sub-rules) | 1 |
| 3 | 59: இனி/தனி | `ini_thani` | New rulegroup (4 sub-rules) | 1 |
| 4 | 60: அன்றி/இன்றி | `andri_indri` | New rulegroup (4 sub-rules) | 1 |
| 5 | 62: முழு/திரு/புது/அரை/பாதி | `muzhu_thiru_puthu_arai_paadhi` | New rulegroup (4 sub-rules) | 1 |
| 6 | 63: எட்டு/பத்து | `ettu_pathu` | New rulegroup (4 sub-rules) | 1 |
| 7 | 69: ஆய்/போய் | `aay_pooy` | New rulegroup (4 sub-rules) | 2 |
| 8 | 80: கிழக்கு/மேற்கு/தெற்கு/வடக்கு | `thisai_peyargal` | New rulegroup (4 sub-rules) | 2 |
| 9 | 87: மெல்ல/உரக்க/நிறம்ப/நிறைய | `mella_urakka` | New rulegroup (4 sub-rules) | 2 |
| 10 | 88: எல்லா/அனைத்து | `ellaa_anaithu` | New rulegroup (4 sub-rules) | 2 |
| 11 | 61: நடு/பொது (expand) | Modify `Ends_in_A_3` | Add to existing regex | 3 |
| 12 | 53: ஒரு vs ஓர் | `oru_oor` | New rulegroup (2 sub-rules) | 4 |
| 13 | 5-03: ஒவ்வொரு + singular | `ovvoru_singular` | New rule (warning only) | 4 |
| 14 | 5-04: எல்லா + plural | `ellaa_plural` | New rule (warning only) | 4 |
| 15 | 6-19: அல்லது separate | `allathu_separate` | New rule (CAT2-style) | 4 |

**Estimated ~600 new lines**, bringing `ta_grammar.xml` from 2,282 to ~2,880 lines.

---

## Implementation Strategy

### Step 1: Build Test Suite First (TDD)

Write `tools/test_tamil_rules.py` — a Python regex tester that simulates LanguageTool's two-token matching. For each of the 15 rules, define test cases in 5 categories:

| Category | Purpose | Example |
|----------|---------|---------|
| **True Positive** | Wrong text that SHOULD trigger | `அப்படி கூறினான்` |
| **True Negative** | Correct text that should NOT trigger | `அப்படிக் கூறினான்` |
| **Non-vallinam** | Next word starts with non-vallinam consonant | `அப்படி மாறியது` (ம is not vallinam) |
| **Adversarial** | Looks similar but shouldn't trigger | `அப்படியே கொடு` (different token) |
| **Interaction** | Tests against existing rules for double-flagging | `கிழக்கு கோட்டை` (could hit both `thisai_peyargal` AND existing `Ends_in_U`) |

All tests written BEFORE any XML — test-driven.

### Step 2: Python Generator for Batch 1-2 (10 templated rules)

Write `tools/generate_sandhi_xml.py` that takes a structured word list and produces valid XML rulegroups following the exact template of `angu_ingu_engu` (lines 2023-2064). This eliminates copy-paste errors across 40 nearly-identical XML blocks.

Template per vallinam consonant:
```xml
<rule>
  <pattern>
    <token regexp='yes'>{TRIGGER_WORDS}</token>
    <token regexp='yes'>{CONSONANT}[ா-ௌ]?(([க-ஹ][ா-்]?)*)?</token>
  </pattern>
  <message>{MESSAGE}: <suggestion>\1{CONSONANT}் \2</suggestion></message>
  <url>http://www.tamilvu.org/slet/lA100/lA100pd3.jsp?bookid=169&amp;pno={PAGE}</url>
  <short>ஒற்றுப் பிழை</short>
  <example correction="{CORRECT}">{CONTEXT}<marker>{WRONG}</marker>{AFTER}</example>
</rule>
```

### Step 3: Hand-craft Batch 3-4 (5 special rules)

These have unique patterns:
- **Rule 61**: Just add `நடு|பொது` to the existing `Ends_in_A_3` token regex (line 1685)
- **Rule 53**: Two rules — `ஒரு` + vowel-starting word → suggest `ஓர்`; `ஓர்` + consonant-starting word → suggest `ஒரு`
- **Rules 5-03/5-04**: Warning-only rules (no auto-correction — the fix requires changing the noun form, not just adding a consonant)
- **Rule 6-19**: CAT2-style separation rule — flag `அல்லது` joined to adjacent words

### Step 4: Insert into grammar.xml

- Batch 1-2: Insert new rulegroups inside `<category id="CAT3">`, replacing the commented-out block (lines 2066-2111)
- Batch 3: Modify `Ends_in_A_3` regex at line 1685
- Batch 4: Rules 53, 5-03, 5-04 go into CAT3; Rule 6-19 goes into CAT2

---

## Adversarial Review Process

### Tier 1: Python Regex Tests (automated, fast)

The test script tokenises Tamil text on whitespace and applies each rule's regex. Validates:
- All true positives match
- All true negatives don't match
- Suggestion output produces correct Tamil
- No rule triggers on text that another existing rule already covers

### Tier 2: LanguageTool CLI (ground truth)

Download LanguageTool 6.x (~200MB, free). Run each test case through the real Java engine:
```
java -jar languagetool-commandline.jar -l ta -e RULE_ID < test_input.txt
```
This catches any Python-vs-Java regex differences.

### Tier 3: Corpus Smoke Test

Run the full grammar against a Tamil text sample (e.g., a Tamil Wikipedia article). Check:
- No rule fires on >5% of sentences (would indicate false-positive flood)
- New rules fire at reasonable rates
- No double-flagging with existing rules

### Key Interaction Risks to Test

| New Rule | Existing Rule | Risk | Resolution |
|----------|---------------|------|------------|
| `mella_urakka` (மெல்ல) | `Ends_in_A_2` (VP POS tag) | Double-flag if POS tagger tags மெல்ல as VP | Add only `நிறம்ப\|நிறைய` if overlap confirmed |
| `thisai_peyargal` (கிழக்கு) | `Ends_in_U` (NNA/NNU POS tag) | Double-flag if POS tagger tags கிழக்கு as NNA | Remove from new rule if overlap confirmed |
| `ellaa_anaithu` (அனைத்து) | `Ends_in_U` (NNA/NNU POS tag) | Same as above | Same resolution |
| `Ends_in_A_3` expansion (நடு) | `Ends_in_U` (NNA/NNU POS tag) | நடு could match both | Test; if POS tagger doesn't tag நடு as NNA, no conflict |

---

## Batch Schedule

### Batch 1 (Low Risk) — Rules 57, 58, 59, 60, 62, 63
Six pure word-list sandhi rules. No ambiguity, no POS dependencies, no overlap risk. These are the "quick wins" from the audit.

### Batch 2 (Low-Medium Risk) — Rules 69, 80, 87, 88
Four sandhi rules with minor structural variations:
- Rule 69: `ஆய்/போய்` end in ய் not a vowel — verify suggestion format
- Rule 80: Direction words end in உ — check overlap with `Ends_in_U`
- Rule 87: Adverbs end in அ — check overlap with `Ends_in_A_2`
- Rule 88: `அனைத்து` ends in உ — check overlap with `Ends_in_U`

### Batch 3 (Medium Risk) — Rule 61 expansion
Modifies existing `Ends_in_A_3` regex. Small change but touches working code. Run full existing test suite before and after.

### Batch 4 (Medium-High Risk) — Rules 53, 5-03, 5-04, 6-19
Novel pattern types that don't follow the standard 4-vallinam template:
- Rule 53 needs vowel/consonant detection
- Rules 5-03/5-04 need plural detection (warning only, no auto-fix)
- Rule 6-19 needs joined-word detection (single-token matching)

---

## Files Modified/Created

| File | Action |
|------|--------|
| `Tamil_Nadai/ta_grammar.xml` | Modified — add ~600 lines of new rules |
| `Tamil_Nadai/tools/generate_sandhi_xml.py` | Created — Python generator for templated rules |
| `Tamil_Nadai/tools/test_tamil_rules.py` | Created — adversarial test framework |
| `Tamil_Nadai/test_cases.json` | Created — all test cases for 15 rules |
| `Tamil_Nadai/audit_report.md` | Updated — reflect new coverage (~82%) |

---

## Verification

1. **Before each batch**: Run existing LanguageTool rule tests (the `<example>` elements in grammar.xml serve as built-in tests — LanguageTool validates them on load)
2. **After each batch**: Run full test suite (Python Tier 1 + LanguageTool CLI Tier 2)
3. **After all batches**: Corpus smoke test, interaction audit, update audit report
4. **Final check**: Load grammar.xml in LanguageTool — all `<example>` elements must validate (LanguageTool rejects files with broken examples)
