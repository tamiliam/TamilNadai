# TamilNadai Coverage Map

**Primary Source**: தமிழ் நடைக் கையேடு (Tamil Writing Style Guide)
**Publisher**: Tamil Virtual Academy (tamilvu.org, bookid=169)
**Pages**: 36-88 (53 pages)
**Total Rules**: 161 (per author's count)

**Secondary Source**: தமிழைப் பிழையின்றி எழுதுவோம் (Write Tamil Without Errors)
**Publisher**: Tamil Virtual Academy, 2024 edition
**Pages**: 97-181 (Chapters 4-6)
**Total Rules**: 174 (overlaps significantly with primary; numbering differs)

**Implementation**: LanguageTool grammar.xml (Copyright 2014, Elanjelian Venugopal)
**Rule entries**: 83 rule groups (all ACTIVE, ~81 correct, 2 ambiguous, 0 incorrect)

---

## Summary

| Category | Tamil Name | Book Rules | grammar.xml Groups | Dataset Examples | Status |
|----------|-----------|------------|-------------------|------------------|--------|
| 1. Grammar structure | இலக்கண அமைப்பில் சொற்கள் | 13 | 11 | ~96 (Tier 1) | Good coverage |
| 2. Individual words | தனித் சொற்களை எழுதும் முறை | 112 | 57 | ~74 (Tier 1) + ~7 (Tier 2) | Partial — many are narrow word-specific rules |
| 3. Sandhi | சந்தி | 36 | 15 | ~46 (Tier 1) + ~99 (Tier 2) | Core covered; gaps in ஒற்று மிகாமை |
| **Total** | | **161** | **83** | **422** | |

### Coverage at a Glance

| Status | Count | Description |
|--------|-------|-------------|
| `covered` | ~68 | In grammar.xml with examples in dataset |
| `tier2_draft` | ~40 | In Tier 2 (from secondary book), needs review |
| `pending` | ~28 | Identified as implementable, no examples yet |
| `cannot_test` | ~25 | Requires morphological/semantic analysis, beyond regex |
| **Total** | **~161** | |

---

## Category 1: இலக்கண அமைப்பில் சொற்கள் (Grammar Structure)
**Pages 36-43 | 13 rules | grammar.xml: CAT1 (11 groups)**

These rules define how words combine according to grammatical structure — noun+noun compounds, noun+postposition, verb+auxiliary, participle+causative.

### Covered by grammar.xml

| # | Book Rule | grammar.xml ID | Page | Description | Examples |
|---|-----------|---------------|------|-------------|----------|
| 1 | 1.1 | noun_noun | 36 | ஓரெழுத்துப் பெயர் + பெயர் (monosyllabic noun compounds) | 4 |
| 2 | 1.5 (group) | noun_suffix_1 | 39 | பெயர் + இடைச்சொல் (noun + postposition, no case marker → join) | 2 |
| 3 | 1.5a | noun_suffix_1A | 39 | பெயர் + இன் + கீழ் (with case marker → separate) | 1 |
| 4 | 1.5b | noun_suffix_1B | 39 | பெயர் + ஐ + குறித்த → separate | 1 |
| 5 | 1.5c | noun_suffix_1C | 39 | பெயர் + ஐ + குறித்து → separate | 1 |
| 6 | 1.5d | noun_suffix_1D | 39 | பெயர் + ஐ + பற்றி/பற்றிய → separate | 10 |
| 7 | 1.5e | noun_suffix_1E | 65 | பெயர் + இன் + பேரில் → separate | 1 |
| 8 | 1.5f | noun_suffix_1F | 67 | பெயர் + ஐ + போல/போல் → separate | 6 |
| 9 | 1.6 | noun_suffix_2 | — | பெயர் + தோறும் → join | 2 |
| 10 | 1.8 | vinai_vinai | 40 | வினை + துணை வினை (verb + auxiliary → join) | 8 |
| 11 | 1.9 | vinaiyeccham_vinai | 41 | வினையெச்சம் + காரண வினை (participle + causative → join) | 5 |

### NOT in grammar.xml (from uncovered pages)

| # | Book Rule | Page | Description | Implementable? | Status |
|---|-----------|------|-------------|----------------|--------|
| 12 | 1.1.4 | 37 | Consonant transformations in compounding (ம் → ங், ந்) | No — morphophonemic | `cannot_test` |
| 13 | 1.2 | 37 | Compound noun formation rules | Partial | `pending` |
| 14 | 1.3 | 38 | Adjective + noun compound words | Partial — limited patterns | `pending` |
| 15 | 1.4 | 38 | When adjective+noun should be joined vs separated | Yes — specific patterns | `pending` |
| 16 | 1.10 | 42 | Verbal participle combinations (join/separate) | Yes — pattern-based | `pending` |
| 17 | 1.11 | 42 | Reduplicated words → join; similar-meaning → separate | Partial — needs word list | `pending` |
| 18 | 1.12 | 43 | Compound words with markers (ஆகிய etc.) | Yes — specific patterns | `pending` |
| 19 | 1.13 | 43 | Conjunctions (உம், ஆவது) joining rules | Yes — specific patterns | `pending` |

**Note**: Rules 1.1.4அ/ஆ, 1.2.1, 1.4.1அ/ஆ, 1.10.1, 1.11.1/2, 1.12.1(அ)/(ஆ), 1.13.1 are sub-rules of the main 13. The grammar.xml covers rules 1.1, 1.5, 1.6, 1.8, 1.9 well. Rules 1.2, 1.3, 1.4, 1.7, 1.10, 1.11, 1.12, 1.13 are the gaps.

---

## Category 2: தனித் சொற்களை எழுதும் முறை (Individual Word Conventions)
**Pages 44-73 | 112 rules | grammar.xml: CAT2 (57 groups)**

These rules specify whether specific words/postpositions should be joined to or separated from the preceding word. Each rule is a narrow convention for one word or word family. The book organises them alphabetically by the Tamil word.

### Covered by grammar.xml (57 rule groups)

The grammar.xml has 57 CAT2 entries covering individual word conventions. All 57 are correct implementations of the primary book's conventions.

**Rule groups with multiple sub-rules (higher coverage):**

| grammar.xml ID | Page | Word/Pattern | Sub-rules | Examples |
|---------------|------|-------------|-----------|----------|
| aie_noun | 44 | அ/இ/எ + பெயர் (demonstrative prefix) | 12 | 12 |
| pin2 | 65 | பின்/பின்னர்/பின்பு/பின்னே/பின்னால் | 9 | 9 |
| uLLa | 53 | உள்ள | 6 | 6 |
| vazhiyaaka | 72 | வழியாக | 5 | 5 |
| pothu | 66 | போது/பொழுது | 4 | 4 |
| idayil | 50 | இடையில்/இடையே | 4 | 4 |
| illaamal2 | 50 | இல்லாமல் | 3 | 3 |
| irunthu | 50 | இருந்து | 3 | 4 |
| vENdum | 73 | வேண்டும்/வேண்டாம் | 3 | 3 |
| vERu | 73 | வேறு + ஒரு/பல/சில etc. | 3 | 3 |
| mun2 | 70 | முன்/முன்பு/முன்னே | 6 | 6 |

**Rule groups with single pattern (narrow):**

| grammar.xml ID | Page | Word | Join/Separate |
|---------------|------|------|---------------|
| aakaadhu | 47 | ஆகாது | Separate |
| illaamal | 50 | மட்டும் + இல்லாமல் | Separate |
| illai | 50 | இல்லை | Separate |
| illai2 | 51 | இல்லை (after participle) | Separate |
| indRi | 51 | இன்றி | Separate |
| udan | 51 | உடன் | Separate |
| uNdu / uNdu2 | 52 | உண்டு | Separate |
| uriya | 52 | உரிய | Separate |
| uudaaga | 53 | ஊடே/ஊடாக | Join |
| enRu | 55 | என்று | Separate |
| ena | 56 | என | Separate |
| YEn | 57 | ஏன் | Separate |
| ERRa | 57 | ஏற்ற | Separate |
| oru | 58 | ஒரு | Separate |
| ozhiya | 58 | ஒழிய | Separate |
| kaattilum | 59 | காட்டிலும் | Separate |
| kuudaadhu | 60 | கூடாது | Separate |
| kuudiya | 60 | கூடிய | Separate |
| kuudum | 61 | கூடும் | Separate |
| thakka | 61 | தக்க | Separate |
| thagaadha | 61 | தகாத | Separate |
| thaguntha | 62 | தகுந்த | Separate |
| piRagu / piRagu2 | 64 | பிறகு | Separate |
| pin | 65 | பின் (after participle) | Separate |
| puthithil | 65 | புதிதில் | Separate |
| poorvamaaka | 66 | பூர்வமாக | Join |
| pothilum | 66 | போதிலும் | Separate |
| polum | 67 | போலும் | Separate |
| pondRa | 67 | போன்ற | Separate |
| pondRu | 67 | போன்று | Separate |
| mattil | 66 | மட்டில் | Join |
| mattum | 68 | மட்டும் | Separate |
| mayam | 68 | மயம்/மயமாக | Join |
| maattu | 68 | மாட்டு | Separate |
| maathiraththil | 69 | மாத்திரத்தில் | Separate |
| mugamaaga | 69 | முகமாக | Separate |
| mudiyum | 69 | முடியும்/முடியாது | Separate |
| vannam | 71 | வண்ணம் | Separate |
| varai | 72 | வரை/வரைக்கும் | Separate |
| vaakkil | 72 | வாக்கில் | Separate |
| vida | 72 | விட | Separate |
| vegu | 73 | வெகு | Join |
| valadhu | 49 | இடது/வலது | Separate |

### NOT in grammar.xml (from uncovered pages)

| Book Rule(s) | Page | Word(s) | Description | Status |
|-------------|------|---------|-------------|--------|
| 2.4-2.7 | 45 | அல்ல, அல்லது, அல்லவா, அல்லாமல் | Joining/separation patterns | `pending` |
| 2.8-2.9 | 46 | அளவு, அளி | Various usage patterns | `pending` |
| 2.14-2.16 | 48 | ஆயிற்றே, ஆயினும், ஆனால் | Conjunction conventions | `pending` |
| 2.33-2.35 | 54 | எங்கும், எதிர், எல்லாம் | Individual word conventions | `pending` |
| 2.62-2.66 | 63 | தொட்டு, தோறும், நடு, நடுவில், நெடு | Individual word conventions | `pending` |

**Estimated gap**: The primary book lists 112 individual word rules (2.1 through 2.112). The grammar.xml covers ~57 of these. The 5 uncovered pages above account for ~17 rules. The remaining ~38 rules are on pages covered by grammar.xml (meaning grammar.xml implements them for common words, but some less-common words on the same pages may lack coverage).

**Note on ambiguous rules**: `polum` and `mattil` are flagged as needing review — the book may allow both joined and separated forms.

---

## Category 3: சந்தி (Sandhi — Consonant Doubling)
**Pages 74-88 | 36 rules | grammar.xml: CAT3 (15 groups)**

This is the most complex section. It covers when வல்லினம் (hard consonants: க, ச, த, ப) should or should not be doubled at word boundaries.

### Book Structure (Primary Source)

The sandhi section has two major divisions:

**A. ஒற்று மிகுதல் — Where consonant DOUBLES (pages 74-87)**
Organised by the final vowel of the first word:

| Final Vowel | Pages | Sub-rules | grammar.xml Coverage |
|-------------|-------|-----------|---------------------|
| Introduction/methodology | 74-76 | — | Not applicable |
| 1. அ ending | 77-78 | 7 | 5 groups (Ends_in_A_1 to _5) on p.77; p.78 sub-rules NOT covered |
| 2. ஆ ending | 79 | 4 | 1 group (Ends_in_Aa_1) |
| 3. இ ending | 80 | 4 | 2 groups (Ends_in_I_1, _2) |
| 3b. இ or உ ending | 80 | 4 | 1 group (Ends_in_IU_1) |
| 4. ஈ ending | 81 | — | NOT covered |
| 5. உ ending | 82, 84-85 | 4+ | 1 group (Ends_in_U, p.82); p.84-85 NOT in grammar.xml |
| 6. ஊ ending | 85 | — | NOT covered |
| 7. ஏ ending | 86 | — | NOT covered |
| 8. ஐ ending | 86-87 | 4+ | 2 groups (Ends_in_Ai_1 p.80, Ends_in_Ai_2 p.87) |
| 4th case marker கு | 88 | 4 | 2 groups (Ends_in_Ku_1, _2) |
| Locative அங்கு/இங்கு/எங்கு | 83 | 4 | 1 group (angu_ingu_engu) |

**B. ஒற்று மிகாமை — Where consonant does NOT double (pages 87-88)**

The primary book has a shorter section on non-doubling rules. The grammar.xml handles these implicitly through regex pattern scoping (exceptions built into the doubling rules).

### Covered by grammar.xml (15 groups)

| # | grammar.xml ID | Page | Pattern | Sub-rules |
|---|---------------|------|---------|-----------|
| 1 | Ends_in_A_1 | 77 | அந்த/இந்த/எந்த + பெயர் | 4 |
| 2 | Ends_in_A_2 | 77 | Verb participle ending in அ | 4 |
| 3 | Ends_in_A_3 | 77 | என, மிக, நடு, பொது + word | 4 |
| 4 | Ends_in_A_4 | 77 | ஆக + வினை | 4 |
| 5 | Ends_in_A_5 | 77 | சின்ன + பெயர் | 3 |
| 6 | Ends_in_Aa_1 | 79 | Negative participial adj + noun | 4 |
| 7 | Ends_in_I_1 | 80 | பற்றி + வினை | 4 |
| 8 | Ends_in_I_2 | 80 | மாதிரி + பெயர் | 4 |
| 9 | Ends_in_IU_1 | 80 | இ/உ ending + word | 4 |
| 10 | Ends_in_U | 82 | உ ending noun + noun | 4 |
| 11 | angu_ingu_engu | 83 | அங்கு/இங்கு/எங்கு + word | 4 |
| 12 | Ends_in_Ai_1 | 80 | 2nd case ஐ (singular) | 4 |
| 13 | Ends_in_Ai_2 | 87 | 2nd case ஐ (plural) | 4 |
| 14 | Ends_in_Ku_1 | 88 | 4th case கு (singular) | 4 |
| 15 | Ends_in_Ku_2 | 88 | 4th case கு (plural) | 4 |

### NOT in grammar.xml (from uncovered pages)

| Rule Area | Pages | Description | Implementable? | Status |
|-----------|-------|-------------|----------------|--------|
| Sandhi methodology | 74-76 | Introduction, list-based approach, gemination exceptions | Not a rule | `out_of_scope` |
| Gemination exceptions | 76 | Quotes, parentheses, abbreviations block doubling | Yes | `pending` |
| Final அ — extended | 78 | 7 sub-rules for அ-ending words (reduplication, udambadumei) | Partial | `pending` |
| Final ஈ | 81 | Words ending in long ஈ vowel — doubling patterns | Yes | `pending` |
| Final உ — extended | 84-85 | Detailed sub-rules A-D for உ-ending words, கள் compounds | Yes | `tier2_draft` |
| Final ஊ | 85 | Words ending in long ஊ — doubling patterns | Yes | `pending` |
| Final ஏ | 86 | Words ending in ஏ (உள்ளே, வெளியே etc.) — ய் insertion | Yes | `pending` |
| Final ஐ — extended | 86 | Extended ஐ rules (single-letter words, compounds) | Yes | `tier2_draft` |

### Tier 2 Coverage (from secondary book)

The Tier 2 examples in `generate_tier2.py` use rule numbers from the **secondary book** (தமிழைப் பிழையின்றி எழுதுவோம்). These correspond to sandhi rules but use different numbering:

| Tier 2 Rule Range | Secondary Book | Primary Book Equivalent | Count |
|-------------------|---------------|------------------------|-------|
| book_053 | Rule 53 (p.82) | ஒரு vs ஓர் | 2 |
| book_057 — book_069 | Rules 57-69 (p.83) | ஒற்று மிகும் — specific patterns | 18 |
| book_079 — book_096 | Rules 79-96 (p.84) | ஒற்று மிகும்/மிகாமை patterns | 38 |
| book_100 — book_113 | Rules 100-113 (p.85) | ஒற்று மிகாமை patterns | 24 |
| book_119 — book_128 | Rules 119-128 (p.86) | ஒற்று மிகாமை patterns | 18 |
| book_5_03 — book_5_07 | Ch.5 Rules 3-7 | Number agreement / articles | 6 |
| book_6_19 — book_6_20 | Ch.6 Rules 19-20 | அல்லது / ஆனால் separation | 4 |

**Total Tier 2 examples**: 106 (from 47 unique secondary-book rules)

**Important**: These secondary-book rule numbers do NOT directly map to primary-book rule numbers. The content overlaps but numbering differs. Each Tier 2 example needs individual verification against the primary source.

---

## Gap Analysis

### High Priority — Straightforward to implement

These rules from the primary book are well-defined, high-frequency, and regex-implementable:

| # | Primary Book Area | Page | Description | Difficulty |
|---|------------------|------|-------------|------------|
| 1 | Cat 3: Final ஈ | 81 | Words ending in ஈ — doubling rules | Easy |
| 2 | Cat 3: Final ஊ | 85 | Words ending in ஊ — doubling rules | Easy |
| 3 | Cat 3: Final ஏ | 86 | Words ending in ஏ — ய் insertion, doubling | Easy |
| 4 | Cat 3: Gemination exceptions | 76 | Block doubling after quotes/parentheses | Easy |
| 5 | Cat 2: அல்ல/அல்லது | 45 | Always separate when conjunction | Easy |
| 6 | Cat 2: ஆனால் | 48 | Separate when used as conjunction | Easy |
| 7 | Cat 2: ஆயினும் | 48 | Joining convention | Easy |
| 8 | Cat 2: எங்கும்/எதிர் | 54 | Individual word conventions | Easy |
| 9 | Cat 2: தொட்டு/நடு/நெடு | 63 | Individual word conventions | Easy |
| 10 | Cat 1: Reduplicated words | 42 | Join reduplicated, separate similar-meaning | Medium |

### Medium Priority — Implementable with care

| # | Primary Book Area | Description | Difficulty |
|---|------------------|-------------|------------|
| 1 | Cat 3: Final அ extended | Additional அ-ending patterns (p.78) | Medium |
| 2 | Cat 3: Final உ extended | Detailed உ sub-rules (p.84-85) | Medium |
| 3 | Cat 1: Adjective+noun | When to join vs separate (p.38) | Medium |
| 4 | Cat 1: Verbal participles | Specific combination rules (p.42) | Medium |
| 5 | Cat 1: Compounds with markers | ஆகிய, உம், ஆவது patterns (p.43) | Medium |
| 6 | Cat 2: அளவு/அளி | Multiple usage patterns (p.46) | Medium |

### Cannot Test (requires capabilities beyond regex)

| # | Area | Description | Why |
|---|------|-------------|-----|
| 1 | Cat 1: Morphophonemic compounding | Consonant transformations (ம் → ங்) | Needs morphological analyzer |
| 2 | Cat 3: Case compound doubling | Genitive, instrumental compounds | Needs POS tagging |
| 3 | Cat 3: Semantic compounds | Metaphors, expressive words | Needs semantic analysis |
| 4 | Cat 2: Context-dependent words | மேல், அல், அற்ற etc. | Join/separate depends on meaning |
| 5 | General: Punctuation rules | 17 rules about commas, semicolons | Different rule category entirely |

---

## Two-Book Reconciliation

### The Issue

The project has two Tamil Virtual Academy books as sources:

1. **தமிழ் நடைக் கையேடு** (bookid=169) — the PRIMARY and AUTHORITATIVE source
   - All grammar.xml `<url>` tags point to this book
   - 161 rules in 3 categories (user's confirmed count)
   - The user authored the grammar.xml rules based on this book

2. **தமிழைப் பிழையின்றி எழுதுவோம்** — SECONDARY reference
   - The audit catalogs (`audit/book_ch4_rules.md`, `audit/book_ch5_6_rules.md`) were built from this book
   - 174 rules in 3 chapters
   - The Tier 2 examples use THIS book's rule numbers (book_057, book_084, etc.)

### What Needs Reconciliation

1. **Tier 2 rule numbers**: The 47 unique `book_XXX` IDs in `generate_tier2.py` reference the secondary book. Each needs to be mapped to the primary book's rule number (or flagged if no direct equivalent exists).

2. **Rule counts**: 161 vs 174. The secondary book likely added ~13 rules not in the primary edition. These may still be valid Tamil conventions but aren't in the primary source.

3. **Content overlap**: The actual grammar rules are the same Tamil language conventions. The difference is in organization and numbering. Most Tier 2 examples will be linguistically correct regardless of which numbering system is used.

### Recommended Resolution

- Keep all Tier 2 examples that are linguistically correct (expert review in Step 9)
- Add a `primary_book_ref` field to reconciled examples
- Flag examples where the secondary book has a rule but the primary book doesn't
- The coverage map above uses the primary book's structure as the organizing principle

---

## Files

| File | Description |
|------|-------------|
| `audit/coverage_map.md` | This file |
| `audit/audit_report.md` | Cross-reference with secondary book (174 rules) |
| `audit/grammar_xml_catalog.md` | All 83 grammar.xml rule groups |
| `.tmp/grammar_xml_rules.json` | Machine-readable grammar.xml extraction |
| `dataset/tier1_grammar_xml.jsonl` | 216 examples from grammar.xml |
| `dataset/tier2_book_rules.jsonl` | 106 examples from secondary book rules |
| `dataset/tier3_correct.jsonl` | 100 correct sentences |
| `dataset/tamilnadai_v1.jsonl` | 422 merged examples |

---

## Next Steps

1. **Expert review** (Step 9): User reviews `review/tier2_review.md` and `review/tier3_review.md`
2. **Fill gaps** (Step 10): Add examples for high-priority gaps listed above
3. **Reconcile Tier 2 numbering**: Map secondary book numbers to primary book where possible
4. **LLM evaluation** (Step 11): Run benchmark against Claude/Gemini/GPT
5. **Publish** (Step 12): HuggingFace + GitHub
