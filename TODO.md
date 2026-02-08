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
- [ ] 3.1 Identify ~90 unimplemented book rules from audit catalogs
- [ ] 3.2 For each rule, create 2-3 example sentence pairs
- [ ] 3.3 Output to `dataset/tier2_book_rules.jsonl`
- [ ] 3.4 User review of generated examples (domain expert check)

## Step 4: Curate Tier 3 correct sentences
- [ ] 4.1 Source ~100 well-formed Tamil sentences
- [ ] 4.2 Verify none trigger any of the 174 rules
- [ ] 4.3 Output to `dataset/tier3_correct.jsonl`

## Step 5: Merge and deduplicate
- [ ] 5.1 Combine all 3 tiers into `dataset/tamilnadai_v1.jsonl`
- [ ] 5.2 Deduplicate
- [ ] 5.3 Add `split` field (80% test / 20% validation)
- [ ] 5.4 Generate and review statistics (total count, category distribution)

## Step 6: Write evaluation script
- [ ] 6.1 Write `tools/evaluate.py` — scoring framework
- [ ] 6.2 Implement metrics: precision, recall, F1 (detection); accuracy (correction)
- [ ] 6.3 Test on 20-example sample against Claude/Gemini
- [ ] 6.4 Verify meaningful scores are produced

## Step 7: Write dataset card
- [ ] 7.1 Write `dataset/README.md` (HuggingFace format)
- [ ] 7.2 Include: description, statistics, citation, usage examples, license
- [ ] 7.3 Final review

---

## Notes
- Steps may require re-planning as new information emerges during implementation
- Tier 2 (Step 3) requires user review — cannot be fully automated
- Master plan: `master_plan.md`
