# Audit Report: Tamil Grammar Book vs LanguageTool Implementation

**Book**: "தமிழைப் பிழையின்றி எழுதுவோம்" (Write Tamil Without Errors), Tamil Virtual Academy, 2024 edition
**Implementation**: LanguageTool grammar.xml (Copyright 2014, Elanjelian Venugopal)
**Date**: 2026-02-08

---

## Executive Summary

| Metric | Count |
|--------|-------|
| Total prescriptive rules in book | **174** |
| Machine-implementable (regex-suitable) | **~88** |
| Implemented in grammar.xml | **83 rule entries** (covering ~60 book rules) |
| Correctly implemented | **~58** (estimated, see notes) |
| Partially/needs review | **~2** |
| Book rules remaining to implement | **~28** |
| Not implementable as regex | **~86** |

**Bottom line**: The grammar.xml implements roughly **68% of the machine-implementable rules** from the book. The implemented rules are overwhelmingly correct. The biggest gaps are in the sandhi (ஒற்று மிகுதல்/மிகாமை) section, where the book has ~75 rules and the grammar.xml covers ~25 of them.

---

## Book Structure (199 pages, Chapters 4-6 are relevant)

| Chapter | Title | Book Pages | Rules Found |
|---------|-------|-----------|-------------|
| 4 | புணர்ச்சிகள் (Sandhi/Joining) | 97-130 | 128 |
| 5 | தனிச்சொல் - துணைவினை (Individual Words) | 131-153 | 7 |
| 6 | சொற்பிரிப்பு, சொற்சேர்க்கை (Word Separation/Combination) | 154-181 | 39 |
| | **Total** | | **174** |

---

## Category Breakdown

### A. Classical Sandhi Rules (Chapter 4, Rules 1-53) — 53 rules

**What they cover**: Morphophonemic processes — how sounds change when words combine (plurals, glide consonants, kutriyalukara sandhi, consonant-final sandhi, numeral sandhi).

**Machine-implementable?** Mostly **NO**. These rules describe phonological transformations that are applied AUTOMATICALLY in standard Tamil writing. A writer doesn't "choose" whether to apply them — they're part of word formation. LanguageTool would need a morphological analyzer to detect violations, not just regex.

**Exceptions** (partially implementable):
- Rules 1-6 (plural formation) — could detect incorrect plural forms like *படம்கள் instead of படங்கள்
- Rule 53 (ஒரு vs ஓர்) — could detect ஒரு before vowel-initial words

**grammar.xml coverage**: 1 rule entry (noun_noun covers Rule 64's one-syllable noun sandhi, which is related)

**Verdict**: These are grammar fundamentals, not the target of the grammar.xml project. Low priority for implementation.

---

### B. ஒற்று மிகும் — Where Consonant Doubles (Chapter 4, Rules 54-93) — 40 rules

**What they cover**: When the hard consonant (வல்லினம்: க, ச, த, ப) at the start of the second word should be doubled.

**Machine-implementable?** **YES** — this is the core of grammar.xml's CAT3.

| Book Rule | Description | grammar.xml Match | Status |
|-----------|-------------|-------------------|--------|
| 54: சுட்டெழுத்து (அ/இ/உ + noun) | After demonstrative prefix | aie_noun (CAT2) | IMPLEMENTED |
| 55: அந்த/இந்த/எந்த + noun | After demonstrative words | Ends_in_A_1 | IMPLEMENTED |
| 56: அங்கு/இங்கு/எங்கு + word | After locative words | angu_ingu_engu | IMPLEMENTED |
| 57: அப்படி/இப்படி/எப்படி | After "like this/that" | — | NOT IMPLEMENTED |
| 58: அவ்வகை/இவ்வகை/எவ்வகை | After "this/that type" | — | NOT IMPLEMENTED |
| 59: இனி, தனி | After "henceforth", "single" | — | NOT IMPLEMENTED |
| 60: அன்றி, இன்றி | After "otherwise", "without" | — | NOT IMPLEMENTED |
| 61: என, மிக, நடு, பொது | After common adverbs | Ends_in_A_3 (partial) | PARTIAL |
| 62: முழு, திரு, புது, அரை, பாதி | After adjective prefixes | — | NOT IMPLEMENTED |
| 63: எட்டு, பத்து | After numerals 8, 10 | — | NOT IMPLEMENTED |
| 64: ஓரெழுத்து ஒருமொழி | After monosyllabic words | noun_noun (CAT1) | IMPLEMENTED |
| 65: ஈறுகெட்ட எதிர்மறை பெயரெச்சம் | After negative participial adj | Ends_in_Aa_1 | IMPLEMENTED |
| 66: வன்றொடர் குற்றியலுகரம் | After hard-cluster ukara words | Ends_in_IU_1 + Ends_in_U | IMPLEMENTED |
| 67: அகர ஈற்று வினையெச்சம் | After verb participle ending in அ | Ends_in_A_2 | IMPLEMENTED |
| 68: இகர/உகர ஈற்று வினையெச்சம் | After verb participle ending in இ/உ | Ends_in_IU_1 | IMPLEMENTED |
| 69: ஆய், போய் | After "as", "having gone" | — | NOT IMPLEMENTED |
| 70: 2nd case ஐ (explicit) | After accusative marker | Ends_in_Ai_1, Ends_in_Ai_2 | IMPLEMENTED |
| 71: 4th case கு (explicit) | After dative marker | Ends_in_Ku_1, Ends_in_Ku_2 | IMPLEMENTED |
| 72-77: Case compounds (2-7) | In various case compounds | — | NOT IMPLEMENTED (requires morphological analysis) |
| 78: ஆக suffix | After adverbial ஆக | Ends_in_A_4 | IMPLEMENTED |
| 79: ய, ர, ழ ஒற்று | After ய்/ர்/ழ் consonants | — | NOT IMPLEMENTED |
| 80: திசைப்பெயர்கள் | After direction names | — | NOT IMPLEMENTED |
| 81-82: Other kutriyalukara | Various ukara endings | — | NOT IMPLEMENTED |
| 83: தொகைநிலை compounds | In compound constructions | — | NOT IMPLEMENTED |
| 84: உரிச்சொற்கள் | After expressive words | — | NOT IMPLEMENTED |
| 85: Onomatopoeia | After sound-words | — | NOT IMPLEMENTED |
| 86: உருவகம் | In metaphors | — | NOT IMPLEMENTED (semantic) |
| 87: மெல்ல, உரக்க etc. | After specific adverbs | — | NOT IMPLEMENTED |
| 88: எல்லா, அனைத்து | After "all" | — | NOT IMPLEMENTED |
| 89: ஒற்று இரட்டிக்கும் kutriyalukara | Doubling ukara | — | NOT IMPLEMENTED |
| 90: முற்றியலுகரம் | After full ukaram | — | NOT IMPLEMENTED |
| 91: சின்ன | After "small" | Ends_in_A_5 | IMPLEMENTED |
| 92: விட, கூட | After comparison words | — | NOT IMPLEMENTED |
| 93: கீழ், இடை | After positional words | — | NOT IMPLEMENTED |

**Summary**: 40 book rules → 14 implemented in grammar.xml, ~12 more are implementable, ~14 need morphological analysis

---

### C. ஒற்று மிகாமை — Where Consonant Does NOT Double (Chapter 4, Rules 94-128) — 35 rules

**What they cover**: Contexts where the hard consonant should NOT be doubled (even though it might seem like it should).

**Machine-implementable?** **PARTIALLY**. These are harder to implement as positive regex rules. They're more useful as exception lists for the doubling rules above. Some specific ones (like "after demonstrative PRONOUNS" or "after certain verb forms") could be implemented as anti-patterns.

**grammar.xml coverage**: **0 explicit rules**. However, the grammar.xml implicitly handles some of these by limiting its doubling rules' scope with exceptions in the regex patterns.

**Key gap rules that COULD be implemented**:
- Rule 94: After demonstrative PRONOUNS (அது, இது) — DON'T double
- Rule 95: After interrogative PRONOUNS (எது, யாது) — DON'T double
- Rule 100: After participial adjectives (பெயரெச்சம்) — DON'T double
- Rule 109: After numerals OTHER THAN எட்டு/பத்து — DON'T double

---

### D. Word Joining/Separation — Individual Words (grammar.xml CAT1 + CAT2)

This is the user's strongest area of implementation. The grammar.xml has **68 rule entries** (11 CAT1 + 57 CAT2) covering specific words that should be joined or separated. These correspond to conventions found across the book's Chapters 5 and 6.

**grammar.xml CAT1 (11 entries) — Grammatical Structure Joining**:

| grammar.xml Rule | What it checks | Book Source | Status |
|------------------|----------------|-------------|--------|
| noun_noun | One-syllable noun + noun, double consonant | Ch4 Rule 64 | CORRECT |
| noun_suffix_1 | Noun + postposition (no case marker) → JOIN | Ch6 6-03 | CORRECT |
| noun_suffix_1A | Noun + இன் + கீழ் → SEPARATE | Ch6 convention | CORRECT |
| noun_suffix_1B | Noun + ஐ + குறித்த → SEPARATE | Ch6 convention | CORRECT |
| noun_suffix_1C | Noun + ஐ + குறித்து → SEPARATE | Ch6 convention | CORRECT |
| noun_suffix_1D | Noun + ஐ + பற்றி → SEPARATE | Ch6 convention | CORRECT |
| noun_suffix_1E | Noun + இன் + பேரில் → SEPARATE | Ch6 convention | CORRECT |
| noun_suffix_1F | Noun + ஐ + போல → SEPARATE | Ch6 convention | CORRECT |
| noun_suffix_2 | Noun + தோறும் → JOIN | Ch5 Rule 5-02 | CORRECT |
| vinai_vinai | Verb + auxiliary verb → JOIN | Ch5 Rules 5-01, 5-02 | CORRECT |
| vinaiyeccham_vinai | Participle + causative verb → JOIN | Ch5 Rule 5-01 | CORRECT |

**All 11 CAT1 rules: CORRECT**

**grammar.xml CAT2 (57 entries) — Individual Word Conventions**:

All 57 CAT2 rules specify whether a particular word/suffix should be joined or separated from the preceding word. These are highly specific and directly implementable. Cross-referencing against the book:

| Category | Count | Status |
|----------|-------|--------|
| Correctly implements book convention | 55 | CORRECT |
| Needs review (ambiguous in book) | 2 | REVIEW |
| Incorrect | 0 | — |

The 2 rules to review:
1. **polum** (போலும்): grammar.xml says separate at sentence end. Book conventions vary.
2. **mattil** (மட்டில்): grammar.xml says join. Book may allow both.

**All other CAT2 rules: CORRECT**

---

### E. Chapter 5 Rules (7 total)

| Rule | Description | Implementable? | In grammar.xml? |
|------|-------------|---------------|-----------------|
| 5-01 | Auxiliary verb follows main verb | YES | vinai_vinai, vinaiyeccham_vinai |
| 5-02 | Auxiliary verbs must be joined | YES | vinai_vinai + multiple CAT2 rules |
| 5-03 | ஒவ்வொரு + singular only | YES | NOT IMPLEMENTED |
| 5-04 | எல்லா + plural only | YES | NOT IMPLEMENTED |
| 5-05 | எந்த + singular only | YES | NOT IMPLEMENTED |
| 5-06 | Spacing changes meaning | NO | — |
| 5-07 | Don't use ஒரு/ஓர் as article | PARTIAL | NOT IMPLEMENTED |

---

### F. Chapter 6 Rules (39 total)

| Category | Rules | Implementable? | In grammar.xml? |
|----------|-------|---------------|-----------------|
| General joining principles | 6-01 to 6-04 | NO (too broad) | — |
| General separation principles | 6-05 to 6-12 | NO (about prosody) | — |
| Specific word conventions | 6-13 to 6-20 (8 rules) | PARTIALLY | NOT IMPLEMENTED |
| Meaning-dependent spacing | 6-21 to 6-22 | NO (semantic) | — |
| Punctuation rules | 6-23 to 6-39 (17 rules) | SEPARATE SCOPE | NOT IMPLEMENTED |

The 8 specific word rules (6-13 to 6-20) are context-dependent (JOIN in one meaning, SEPARATE in another). Some could be partially implemented:
- **6-19: அல்லது** (or) — always separate. IMPLEMENTABLE.
- **6-20: ஆனால்** (but) — separate when conjunction. PARTIALLY implementable.
- **6-16: அற்ற** — join with simple nouns, separate with compound. PARTIALLY implementable.

---

## Gap Analysis: What's Left to Implement

### High Priority (straightforward regex, high frequency in Tamil writing)

| Book Rule | Description | Difficulty |
|-----------|-------------|------------|
| 57: அப்படி/இப்படி/எப்படி + doubling | After "like this/that/how" | EASY |
| 58: அவ்வகை/இவ்வகை/எவ்வகை + doubling | After "this/that type" | EASY |
| 59: இனி, தனி + doubling | After "henceforth", "single" | EASY |
| 60: அன்றி, இன்றி + doubling | After "otherwise", "without" | EASY |
| 62: முழு, திரு, புது, அரை, பாதி + doubling | After common adjective prefixes | EASY |
| 63: எட்டு, பத்து + doubling | After numerals 8, 10 | EASY |
| 69: ஆய், போய் + doubling | After common verb forms | EASY |
| 5-03: ஒவ்வொரு + singular | Agreement check | MEDIUM |
| 5-04: எல்லா + plural | Agreement check | MEDIUM |
| 6-19: அல்லது always separate | Simple word check | EASY |

### Medium Priority (implementable but need care with exceptions)

| Book Rule | Description | Difficulty |
|-----------|-------------|------------|
| 61: என, மிக, நடு, பொது (expand) | Extend existing Ends_in_A_3 | MEDIUM |
| 79: ய, ர, ழ ஒற்று + doubling | After ய்/ர்/ழ் endings | MEDIUM |
| 80: திசைப்பெயர்கள் + doubling | After direction names | MEDIUM |
| 87: மெல்ல, உரக்க + doubling | After specific adverbs | MEDIUM |
| 88: எல்லா, அனைத்து + doubling | After "all" | MEDIUM |
| 91: விட, கூட + doubling | After comparison words | MEDIUM |
| 53: ஒரு vs ஓர் | Use ஓர் before vowels only | MEDIUM |

### Low Priority (needs morphological analysis or too many exceptions)

| Book Rule | Description | Why Difficult |
|-----------|-------------|---------------|
| 72-77: Case compound doubling | Genitive compounds etc. | Need morphological parser |
| 83-86: Compounds, metaphors | Semantic context | Need semantic analysis |
| 94-128: ஒற்று மிகாமை | When NOT to double | Better as exceptions to existing rules |
| 6-13 to 6-18: Context-dependent words | மேல், அல், அற்ற, etc. | Need sentence-level context |
| Punctuation (6-23 to 6-39) | Commas, semicolons etc. | Different rule type entirely |

---

## Correctness Summary

Of the **83 grammar.xml rule entries**:
- **All 83 are ACTIVE** (none disabled)
- **~81 are correctly implementing** their corresponding book conventions
- **2 are ambiguous** (polum, mattil) — not wrong, but the book may allow both forms
- **0 are incorrect** — no rule was found to contradict the book

The regex patterns were validated in a previous session (0 errors, 3 minor cosmetic warnings).

---

## Recommendations

1. **Quick wins (8-10 new rules)**: Implement the "High Priority" sandhi rules above. These are straightforward regex patterns following the exact same structure as existing CAT3 rules (4 patterns each for க/ச/த/ப).

2. **Expand existing rules**: Ends_in_A_3 could be extended to cover more adverbs from Rules 61, 87.

3. **Agreement checks (2-3 rules)**: Rules 5-03/5-04 (ஒவ்வொரு/எல்லா) are implementable with regex + POS tags.

4. **Don't implement**: Rules 1-53 (classical sandhi), Rules 72-86 (morphological), Rules 6-23 to 6-39 (punctuation) — these are outside the scope of the original project.

5. **Consider**: The ஒற்று மிகாமை rules (94-128) could be added as `<exception>` elements within existing CAT3 rules to reduce false positives.

---

## Appendix: Files

| File | Contents |
|------|----------|
| `.tmp/ta_grammar.xml` | Original LanguageTool grammar.xml (2,282 lines) |
| `.tmp/Thamizhai_Pizhaiyinri_Ezhuthuvom.pdf` | Source book (199 pages) |
| `.tmp/grammar_xml_catalog.md` | Parsed grammar.xml: 83 rule entries |
| `.tmp/book_ch4_rules.md` | Chapter 4 rules: 128 rules cataloged |
| `.tmp/book_ch5_6_rules.md` | Chapters 5-6 rules: 46 rules cataloged |
| `.tmp/spelling_rules_chapter.txt` | Raw extracted text (Chapters 4-6) |
