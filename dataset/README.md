---
language:
  - ta
license: cc-by-sa-4.0
task_categories:
  - text2text-generation
tags:
  - grammar-correction
  - Tamil
  - evaluation
  - prescriptive-grammar
  - sandhi
  - GEC
pretty_name: TamilNadai
size_categories:
  - n<1K
---

# TamilNadai — Tamil Grammar Evaluation Dataset

## Dataset Description

**TamilNadai** (தமிழ் நடை) is a gold-standard evaluation dataset for Tamil prescriptive grammar correction. It contains **422 expert-annotated examples** covering writing conventions prescribed by the Tamil Virtual Academy's *தமிழ் நடைக் கையேடு* (Tamil Writing Style Guide, 2004/2007).

The dataset tests whether language models can:
1. **Detect** prescriptive grammar errors in Tamil text
2. **Correct** them according to established conventions
3. **Avoid false positives** on grammatically correct sentences

### Why This Dataset

- Tamil has only **65 sentences** in the IndicGEC benchmark, the largest Indian language GEC dataset
- LLMs consistently fail on exactly the prescriptive conventions this dataset tests (sandhi doubling, word joining, ஒரு/ஓர்)
- Every example traces to a specific page in an authoritative Tamil Virtual Academy publication
- The 11-category taxonomy covers conventions that LLMs systematically get wrong

### Source Authority

All rules derive from: **தமிழ் நடைக் கையேடு** (Tamil Writing Style Guide)
- Publisher: Tamil Virtual Academy (தமிழ் இணையக் கல்விக்கழகம்)
- Book ID: 169
- URL pattern: `http://www.tamilvu.org/slet/lA100/lA100pd3.jsp?bookid=169&pno={page}`
- Total prescriptive rules cataloged: **174** (128 sandhi + 7 syntax + 39 word conventions)

## Dataset Statistics

| Metric | Count |
|--------|-------|
| Total examples | 422 |
| Error examples | 318 |
| Correct examples | 104 |
| Unique error categories | 11 |
| Test split | 337 (80%) |
| Validation split | 85 (20%) |

### Category Distribution

| Category | Tamil Name | Examples | Error Type |
|----------|-----------|----------|------------|
| `correct_sentence` | பிழையற்ற வாக்கியம் | 100 | — |
| `sandhi_doubling` | ஒற்று மிகுதல் | 96 | missing_vallinam_doubling |
| `word_joining` | சேர்த்து எழுதுதல் | 74 | incorrect_separation |
| `word_separation` | பிரித்து எழுதுதல் | 46 | incorrect_joining |
| `sandhi_no_doubling` | ஒற்று மிகாமை | 43 | unnecessary_vallinam_doubling |
| `noun_postposition` | பெயர் + இடைச்சொல் | 22 | noun_postposition_spacing |
| `case_marker_sandhi` | வேற்றுமை உருபு | 16 | case_marker_doubling |
| `verb_auxiliary` | வினை + துணைவினை | 13 | verb_auxiliary_separation |
| `number_agreement` | எண் ஒப்புமை | 6 | number_agreement_error |
| `article_usage` | ஒரு/ஓர் பயன்பாடு | 5 | article_form_error |
| `specific_words` | தனிச்சொல் வழக்கு | 1 | specific_word_convention |

### Data Sources (3 Tiers)

| Tier | Source | Examples |
|------|--------|----------|
| Tier 1 | Extracted from LanguageTool grammar.xml (83 rules) | 216 |
| Tier 2 | Generated from unimplemented book rules (47 rules) | 106 |
| Tier 3 | Curated correct sentences (false-positive testing) | 100 |

## Data Format

Each line in the JSONL file is a JSON object:

```json
{
  "id": "tn_0001",
  "source": "tamilvu_169_p83",
  "category": "sandhi_doubling",
  "subcategory": "demonstrative_adverb",
  "rule_id": "appadi_ippadi_eppadi",
  "rule_name": "அப்படி/இப்படி/எப்படி பின் ஒற்று மிகுதல்",
  "book_page": 83,
  "book_rules": [57],
  "error_sentence": "அவன் அப்படி செய்தான்.",
  "correct_sentence": "அவன் அப்படிச் செய்தான்.",
  "marked_text": "அப்படி செய்தான்",
  "correction": "அப்படிச் செய்தான்",
  "error_span": [6, 22],
  "error_type": "missing_vallinam_doubling",
  "origin": "grammar_xml",
  "is_error_example": true,
  "split": "test"
}
```

### Key Fields

| Field | Description |
|-------|-------------|
| `error_sentence` | Sentence containing the grammar error (empty for correct examples) |
| `correct_sentence` | The grammatically correct version |
| `category` | One of 11 error categories (or `correct_sentence`) |
| `error_type` | Specific error classification |
| `marked_text` | The erroneous span within the sentence |
| `correction` | The corrected span |
| `origin` | Data source: `grammar_xml`, `book_rule`, or `curated_correct` |
| `split` | `test` (80%) or `validation` (20%) |
| `is_error_example` | `true` for error examples, `false` for correct sentences |

## Usage

### Loading the Dataset

```python
import json

with open("tamilnadai_v1.jsonl", "r", encoding="utf-8") as f:
    dataset = [json.loads(line) for line in f]

# Filter by split
test_set = [r for r in dataset if r["split"] == "test"]
val_set = [r for r in dataset if r["split"] == "validation"]

# Filter error examples only
errors = [r for r in dataset if r["is_error_example"]]
```

### Running Evaluation

```bash
# Generate predictions JSONL with format: {"id": "tn_0001", "model_output": "corrected text"}
python tools/evaluate.py --gold dataset/tamilnadai_v1.jsonl --predictions my_predictions.jsonl

# Evaluate only test split
python tools/evaluate.py --gold dataset/tamilnadai_v1.jsonl --predictions my_predictions.jsonl --split test

# Output as JSON
python tools/evaluate.py --gold dataset/tamilnadai_v1.jsonl --predictions my_predictions.jsonl --json
```

### Evaluation Metrics

| Metric | Description |
|--------|-------------|
| **Precision** | Of sentences flagged as errors, how many truly are? |
| **Recall** | Of actual errors, how many were detected? |
| **F1** | Harmonic mean of precision and recall |
| **Correction Accuracy** | Of detected errors, how many corrections match exactly? |
| **False Positive Rate** | Of correct sentences, how many were incorrectly flagged? |

## Limitations

- Dataset focuses on **prescriptive** conventions from one authoritative source; spoken Tamil and regional variations may differ
- Tier 2 examples (106) were generated using the book's own examples and placed in sentence context — they await expert review
- Some error categories have fewer examples (article_usage: 5, specific_words: 1)
- The dataset tests **writing conventions**, not semantic or stylistic quality

## Citation

```bibtex
@dataset{tamilnadai2026,
  title={TamilNadai: A Tamil Grammar Evaluation Dataset},
  author={Venugopal, Elanjelian},
  year={2026},
  note={Based on Tamil Virtual Academy's Tamil Writing Style Guide (2004/2007)},
  url={https://github.com/tamiliam/TamilNadai}
}
```

## License

This dataset is released under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

The underlying grammar rules derive from the Tamil Virtual Academy's publicly available style guide.

## Acknowledgments

- **Tamil Virtual Academy** (தமிழ் இணையக் கல்விக்கழகம்) for the source material
- The original LanguageTool grammar rules (2004-2014) that encoded these conventions in machine-readable form
- POS dictionary (14,399 entries, 46 tags) developed as part of the LanguageTool Tamil module
