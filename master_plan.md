# TamilNadai — Master Plan
# தமிழ் இலக்கணத் தரவுத்தொகுப்பு — முதன்மைத் திட்டம்

## Context

Between 2004-2014, Elanjelian Venugopal created one of the most comprehensive machine-readable descriptions of Tamil writing conventions: 83 LanguageTool grammar rules, a 14,399-word POS-tagged dictionary, and a 46-tag POS system — all based on the Tamil Virtual Academy's "தமிழ் நடைக் கையேடு" (2004/2007).

An audit against the source book found 174 prescriptive rules total, of which ~88 are machine-testable. The existing grammar.xml covers ~60 of these with 234 test examples.

**The problem:** Writing more regex rules has diminishing returns. But the linguistic knowledge encoded in these rules is permanently valuable — and rare. Tamil has only 65 sentences in the IndicGEC benchmark. LLMs consistently fail on exactly the prescriptive conventions these rules test (sandhi doubling, word joining, ஒரு/ஓர்).

**The pivot:** Instead of extending LanguageTool XML, repackage this knowledge as a **gold-standard Tamil grammar evaluation dataset** — publishable on HuggingFace, usable immediately to test LLMs.

---

## What We're Building

A structured dataset called **TamilNadai** containing:

1. **~500 sentence pairs** (erroneous → corrected), covering all 174 book rules
2. **Error taxonomy** mapping rules to 12-15 macro categories
3. **Rich metadata** per example (source URL, error type, POS tags, explanation)
4. **JSONL format** for easy consumption by LLMs and evaluation frameworks
5. **Dataset card** (HuggingFace-compatible README)
6. **Evaluation script** to test any model against the benchmark

---

## Dataset Structure

### Each example (JSONL record):

```json
{
  "id": "tn_cat3_057_ka_001",
  "source": "tamilvu_169_p83",
  "category": "sandhi_doubling",
  "subcategory": "demonstrative_adverb",
  "rule_id": "appadi_ippadi_eppadi",
  "book_rule": 57,
  "error_sentence": "அப்படி கூறினான்.",
  "correct_sentence": "அப்படிக் கூறினான்.",
  "error_span": [0, 2],
  "error_type": "missing_vallinam_doubling",
  "explanation_ta": "அப்படி, இப்படி, எப்படி பின்பு ஒற்று மிகும்",
  "explanation_en": "Hard consonant doubles after appadi/ippadi/eppadi",
  "source_url": "http://www.tamilvu.org/slet/lA100/lA100pd3.jsp?bookid=169&pno=83",
  "origin": "grammar_xml",
  "difficulty": "easy"
}
```

### Error Taxonomy (12 macro categories):

| ID | Category | Tamil | Book Rules | Est. Examples |
|----|----------|-------|------------|---------------|
| 1 | `sandhi_doubling` | ஒற்று மிகுதல் | 54-93 | ~160 |
| 2 | `sandhi_no_doubling` | ஒற்று மிகாமை | 94-128 | ~70 |
| 3 | `word_joining` | சேர்த்து எழுதுதல் | CAT1 rules | ~50 |
| 4 | `word_separation` | பிரித்து எழுதுதல் | CAT2 rules | ~60 |
| 5 | `noun_postposition` | பெயர் + இடைச்சொல் | 1.1-1.3 | ~30 |
| 6 | `verb_auxiliary` | வினை + துணைவினை | 5-01, 5-02 | ~30 |
| 7 | `number_agreement` | எண் ஒப்புமை | 5-03, 5-04 | ~20 |
| 8 | `article_usage` | ஒரு/ஓர் | 53 | ~15 |
| 9 | `case_marker_sandhi` | வேற்றுமை உருபு | 70-77 | ~30 |
| 10 | `classical_sandhi` | மரபுப் புணர்ச்சி | 1-53 | ~20 |
| 11 | `specific_words` | தனிச்சொல் வழக்கு | Ch 5-6 | ~30 |
| 12 | `correct_sentence` | பிழையற்ற வாக்கியம் | — | ~100 |

**Target: ~500 examples** (400 erroneous + 100 correct = 80/20 split)

---

## Data Sources (3 tiers)

### Tier 1: Extract from grammar.xml (234 examples)
- Parse all `<example>` elements with their `correction` attributes and `<marker>` spans
- Extract rule ID, category, URL, message
- Automated, high confidence

### Tier 2: Generate from book rules (200-250 new examples)
- For each of the ~90 unimplemented book rules, create 2-3 example sentences
- Use examples from the book catalog files (`book_ch4_rules.md`, `book_ch5_6_rules.md`)
- Supplement with realistic Tamil sentences
- **Requires user review** — user is the domain expert

### Tier 3: Correct sentences (100 examples)
- Tamil sentences that do NOT violate any rule
- Sourced from correctly-written Tamil text
- Important for measuring false-positive rates of models being evaluated

---

## Implementation Steps

### Step 1: Parse grammar.xml → structured data
- Python script reads `ta_grammar.xml`
- Extracts every `<example>` with its rule metadata
- Outputs to `Tamil_Nadai/dataset/tier1_grammar_xml.jsonl`
- **Automated, no manual work**

### Step 2: Build error taxonomy
- Map 83 rule IDs → 12 macro categories (table above)
- Map 174 book rules → same taxonomy
- Output: `Tamil_Nadai/dataset/taxonomy.json`

### Step 3: Generate Tier 2 examples from book rules
- For each unimplemented book rule in `book_ch4_rules.md` and `book_ch5_6_rules.md`:
  - Use the book's own examples where available
  - Create realistic sentence context around them
- Output: `Tamil_Nadai/dataset/tier2_book_rules.jsonl`
- **User reviews and corrects these**

### Step 4: Curate Tier 3 correct sentences
- Extract well-formed Tamil sentences from the source book or Tamil Wikipedia
- Verify none trigger any of the 174 rules
- Output: `Tamil_Nadai/dataset/tier3_correct.jsonl`

### Step 5: Merge and deduplicate
- Combine all 3 tiers into `Tamil_Nadai/dataset/tamilnadai_v1.jsonl`
- Add `split` field: 80% test / 20% validation
- Generate statistics

### Step 6: Write evaluation script
- `Tamil_Nadai/tools/evaluate.py`
- Takes a model's corrections and scores against gold standard
- Metrics: precision, recall, F1 (detection); sentence-level accuracy (correction)
- Can test any LLM via API or local model

### Step 7: Write dataset card
- `Tamil_Nadai/dataset/README.md` (HuggingFace format)
- Description, statistics, citation, usage examples, license

---

## Files Created

| File | Purpose |
|------|---------|
| `tools/parse_grammar_xml.py` | Step 1: XML → JSONL extractor |
| `dataset/taxonomy.json` | Step 2: Error type definitions |
| `dataset/tier1_grammar_xml.jsonl` | Step 1 output: 234 existing examples |
| `dataset/tier2_book_rules.jsonl` | Step 3 output: ~250 new examples |
| `dataset/tier3_correct.jsonl` | Step 4 output: ~100 correct sentences |
| `dataset/tamilnadai_v1.jsonl` | Step 5: Merged final dataset |
| `tools/evaluate.py` | Step 6: Evaluation script |
| `dataset/README.md` | Step 7: Dataset card |

**No existing files are modified.** All output goes into `dataset/` and `tools/`.

---

## Source Materials (in `Tamil_Nadai/`)

| File | Description |
|------|-------------|
| `ta_grammar.xml` | Original LanguageTool grammar (83 rules, 234 examples) |
| `source/tamil_nadai_kaiyedu.txt` | Primary source: TVA book (140 pages) |
| `source/Thamizhai_Pizhaiyinri_Ezhuthuvom.pdf` | Secondary source (199 pages) |
| `source/tamil-style-guide.md` | 55-rule digest |
| `audit/audit_report.md` | Audit: 174 book rules vs 83 implemented |
| `audit/grammar_xml_catalog.md` | All 83 grammar.xml rules cataloged |
| `audit/book_ch4_rules.md` | Chapter 4: 128 sandhi rules |
| `audit/book_ch5_6_rules.md` | Chapters 5-6: 46 rules |
| `languagetool/resource/tagset.txt` | 46-tag POS system |
| `languagetool/solthiruthi2/` | Hunspell dictionary (14,399 roots) |

---

## Why This Matters

- **Tamil has only 65 sentences** in the IndicGEC benchmark
- **500 expert-annotated examples** with source references would be the **largest prescriptive Tamil grammar evaluation set**
- Every example traces to a specific page in an authoritative Tamil Virtual Academy publication
- The 12-category taxonomy covers conventions that LLMs systematically get wrong
- Immediately usable to benchmark Claude, Gemini, GPT, and any future Tamil NLP model
