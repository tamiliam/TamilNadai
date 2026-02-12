---
license: cc-by-sa-4.0
language:
- ta
task_categories:
- text-classification
- text2text-generation
tags:
- tamil
- grammar
- writing-conventions
- benchmark
- llm-evaluation
- spell-check
- sandhi
pretty_name: Tamil Grammar Benchmark
size_categories:
- n<1K
---

# Tamil Grammar Benchmark

A curated dataset of Tamil sentences annotated for **writing convention correctness**, designed to benchmark how well LLMs understand Tamil grammar rules — particularly word joining, sandhi (vallinam doubling), and individual word conventions.

## Dataset Description

This benchmark is derived from the **Tamil Nadai (தமிழ் நடை) Workbench**, a collaborative platform where Tamil language experts review and validate grammar rules based on the authoritative **Tamil Virtual University Style Guide** (*தமிழ் நடைக் கையேடு*, Book 169, published by tamilvu.org).

Each sentence is labelled as either **correct** (follows the writing convention) or **wrong** (violates it), and is linked to a specific grammar rule with a full description.

### Source Authority

The rules originate from the **Tamil Virtual University (தமிழ் இணையக் கல்விக்கழகம்)** style guide, considered the standard reference for modern Tamil writing conventions. The dataset was curated by Tamil language experts with decades of experience in Tamil localisation (Mozilla, OpenOffice, LibreOffice) and grammar tooling (LanguageTool Tamil rules).

## Dataset Structure

### Files

| File | Description |
|------|-------------|
| `sentences.csv` | Main dataset — one row per sentence with labels |
| `sentences.jsonl` | Same data in JSONL format (includes rule metadata) |
| `rules.csv` | Rule definitions and descriptions (109 rules) |

### Schema: sentences.csv

| Column | Type | Description |
|--------|------|-------------|
| `sentence_id` | string | Unique sentence identifier (e.g., SEN-00001) |
| `rule_id` | string | Grammar rule this sentence tests (e.g., 1.1.1) |
| `category` | string | Rule category (Tamil) |
| `sentence` | string | The Tamil sentence or phrase |
| `sentence_type` | string | `correct` or `wrong` |
| `sentence_status` | string | Review status (pending, review_1_done, accepted) |
| `review_count` | int | Number of expert reviews completed |

### Schema: rules.csv

| Column | Type | Description |
|--------|------|-------------|
| `rule_id` | string | Rule identifier matching the style guide numbering |
| `category` | string | One of three categories (see below) |
| `title` | string | Rule title (Tamil) |
| `subtitle` | string | Rule subtitle (Tamil, optional) |
| `description` | string | Full rule description (Tamil) |
| `source_ref` | string | Page reference in the style guide |

## Categories

| Category (Tamil) | Category (English) | Sentences | Description |
|---|---|---|---|
| இலக்கண அமைப்பில் சொற்கள் | Grammar Structure | 73 | Word joining rules based on grammatical structure |
| தனிச் சொற்களை எழுதும் முறை | Individual Words | 126 | Conventions for writing specific words |
| சந்தி | Sandhi | 142 | Vallinam consonant doubling rules |

## Statistics

- **341 sentences** across **109 rules**
- **324 correct** sentences (95.0%)
- **17 wrong** sentences (5.0%)
- **3 categories** covering the major domains of Tamil writing conventions

### Known Limitations

- The dataset is **imbalanced** — only 5% of sentences are labelled as `wrong`. This reflects the early stage of data collection (wrong sentences require more careful curation). More wrong sentences will be added in future versions.
- Not all sentences have been expert-reviewed yet. The `sentence_status` and `review_count` fields indicate review progress. Filter to `sentence_status = "accepted"` for fully validated sentences.
- Sentences range from single words/phrases to short sentences. Complex multi-clause sentences are not yet represented.

## Intended Use

### Benchmarking LLMs on Tamil Grammar

Send each sentence to an LLM with a prompt like:

> "You are a Tamil language expert. The following Tamil sentence may contain a writing convention error (such as incorrect word joining, missing sandhi doubling, or wrong usage). If there is an error, return ONLY the corrected sentence. If the sentence is already correct, return it unchanged. Return ONLY the Tamil sentence — no explanation, no quotes, no other text."

Then score the response:

| Sentence Type | Model Behaviour | Outcome |
|---|---|---|
| wrong | Changed to exact correct form | True Positive |
| wrong | Changed, but not to correct form | Partial |
| wrong | Left unchanged | False Negative |
| correct | Left unchanged | True Negative |
| correct | Changed | False Positive |

### Key Metrics

- **Detection Rate**: % of wrong sentences where the model made any change
- **Correction Accuracy**: % of wrong sentences fixed to the exact correct form
- **Preservation Rate**: % of correct sentences left unchanged (100 − False Positive Rate)

## Evaluation Results (Baseline)

Results from running Gemini 2.0 Flash on all 341 sentences (February 2026):

| Metric | Score |
|--------|-------|
| Detection Rate | 88.2% |
| Correction Accuracy | 41.2% |
| Preservation Rate | 57.4% |

## Citation

If you use this dataset, please cite:

```bibtex
@dataset{tamil_grammar_benchmark_2026,
  title={Tamil Grammar Benchmark},
  author={Tamil Nadai Workbench Contributors},
  year={2026},
  url={https://tamilnadai-90344691621.asia-southeast1.run.app},
  note={Based on Tamil Virtual University Style Guide (Book 169)}
}
```

## Licence

This dataset is released under **CC BY-SA 4.0**. The underlying grammar rules are from the Tamil Virtual University's publicly available style guide.

## Links

- **Tamil Nadai Workbench**: [tamilnadai-90344691621.asia-southeast1.run.app](https://tamilnadai-90344691621.asia-southeast1.run.app)
- **Tamil Virtual University**: [tamilvu.org](https://www.tamilvu.org)
