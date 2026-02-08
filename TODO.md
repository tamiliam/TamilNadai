# TamilNadai — Working TODO
# Last updated: 2026-02-08

---

## Step 1: Parse grammar.xml → structured data ✅
- [x] 1.1 Write `tools/parse_grammar_xml.py` — XML parser
- [x] 1.2 Create `dataset/` folder
- [x] 1.3 Run parser → `dataset/tier1_grammar_xml.jsonl`
- [x] 1.4 Verify: 216 active examples (18 in commented-out block excluded), all fields present, valid JSON per line
- [x] 1.5 Spot-checked CAT1/CAT2/CAT3 examples against grammar.xml — all accurate
- **Result**: 216 examples, 83 unique rules (CAT1:11, CAT2:57, CAT3:15), pages 36-88, 80 use POS tags

## Step 2: Build error taxonomy ✅
- [x] 2.1 Define 12 macro categories in `dataset/taxonomy.json`
- [x] 2.2 Map all 83 grammar.xml rule IDs → categories (zero unmapped)
- [x] 2.3 Map all 174 book rules → categories (using audit catalogs)
- [x] 2.4 Enrich Tier 1 JSONL with taxonomy fields via `tools/enrich_tier1.py`
- **Result**: 6 categories used in Tier 1: sandhi_doubling (47), word_joining (74), word_separation (44), noun_postposition (22), case_marker_sandhi (16), verb_auxiliary (13)

## Step 3: Generate Tier 2 examples from book rules
- [x] 3.1 Identify ~90 unimplemented book rules from audit catalogs
- [x] 3.2 For each rule, create 2-3 example sentence pairs
- [x] 3.3 Output to `dataset/tier2_book_rules.jsonl` — 106 examples, 47 rules
- [ ] 3.4 User review of generated examples (domain expert check)

## Step 4: Curate Tier 3 correct sentences ✅
- [x] 4.1 Source ~100 well-formed Tamil sentences (100 created across 9 subcategories)
- [x] 4.2 Tricky contexts included: sandhi boundaries, ஒரு/ஓர், word-joining — all correct
- [x] 4.3 Output to `dataset/tier3_correct.jsonl` — 100 sentences
- [ ] 4.4 User review: `review/tier3_review.md`

## Step 5: Merge and deduplicate ✅
- [x] 5.1 Combine all 3 tiers into `dataset/tamilnadai_v1.jsonl`
- [x] 5.2 Deduplicate — 0 duplicates found (422 unique)
- [x] 5.3 Add `split` field — test: 337 (80%), validation: 85 (20%)
- [x] 5.4 Statistics: 422 total (318 error + 104 correct), 11 categories, 3 origins
- **Result**: 422 examples across 11 categories, 206 need expert review

## Step 6: Write evaluation script ✅
- [x] 6.1 Write `tools/evaluate.py` — scoring framework
- [x] 6.2 Implement metrics: precision, recall, F1 (detection); accuracy (correction); FPR; per-category breakdown
- [x] 6.3 Test on 20-example mock sample — verified meaningful scores
- [x] 6.4 Supports --split, --json flags, usable as library import
- **Note**: Real LLM evaluation (Claude/Gemini) deferred — requires API calls

## Step 7: Write dataset card ✅
- [x] 7.1 Write `dataset/README.md` (HuggingFace format with YAML frontmatter)
- [x] 7.2 Includes: description, statistics, category table, data format, usage examples, evaluation metrics, citation, CC BY-SA 4.0 license
- [x] 7.3 Final review — pending user check

---

## Notes
- Steps may require re-planning as new information emerges during implementation
- Tier 2 (Step 3) requires user review — cannot be fully automated
- Master plan: `master_plan.md`
