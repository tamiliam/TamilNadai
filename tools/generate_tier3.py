"""
generate_tier3.py — Step 4: Curate Tier 3 correct sentences.

Creates ~100 well-formed Tamil sentences that do NOT contain any grammar
errors according to the 174 book rules. These test false-positive rates:
can a model correctly identify that NO correction is needed?

Best practice: include "tricky" contexts (sandhi boundaries, ஒரு/ஓர்,
word-joining points) where the sentence IS correct.

Usage:
    python Tamil_Nadai/tools/generate_tier3.py

Output:
    Tamil_Nadai/dataset/tier3_correct.jsonl
"""

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# ========================================================================
# CORRECT SENTENCES — organized by the category they could be confused with
# ========================================================================

TIER3_DATA = [

    # ================================================================
    # GROUP 1: Correct sandhi doubling (vallinam properly doubled)
    # These test that models don't "un-double" correct forms.
    # ================================================================

    # Correct: இ/அ/எ-series demonstrative adverbs + doubled consonant
    {"sentence": "அவன் அப்படிச் செய்வான் என்று எதிர்பார்க்கவில்லை.",
     "category_tested": "sandhi_doubling", "note": "அப்படி + ச் correct"},
    {"sentence": "இப்படிப் பேசுவது நல்லதல்ல.",
     "category_tested": "sandhi_doubling", "note": "இப்படி + ப் correct"},
    {"sentence": "எப்படிச் சொன்னாலும் கேட்கமாட்டான்.",
     "category_tested": "sandhi_doubling", "note": "எப்படி + ச் correct"},

    # Correct: Adjective prefix + doubled consonant
    {"sentence": "திருக்குறள் இன்றும் பொருத்தமானது.",
     "category_tested": "sandhi_doubling", "note": "திரு + க்குறள் correct"},
    {"sentence": "புதுக்கோட்டையில் கோயில் திருவிழா நடைபெற்றது.",
     "category_tested": "sandhi_doubling", "note": "புது + க்கோட்டை correct"},
    {"sentence": "முழுப்பக்கமும் படித்துவிட்டேன்.",
     "category_tested": "sandhi_doubling", "note": "முழு + ப்பக்கம் correct"},

    # Correct: எட்டு/பத்து + doubled
    {"sentence": "எட்டுத் திசைகளிலும் புகழ் பரவியது.",
     "category_tested": "sandhi_doubling", "note": "எட்டு + த் correct"},
    {"sentence": "பத்துப்பாட்டு சங்க இலக்கியமாகும்.",
     "category_tested": "sandhi_doubling", "note": "பத்து + ப் correct"},

    # Correct: எல்லா/அனைத்து + doubled
    {"sentence": "எல்லாக் குழந்தைகளுக்கும் கல்வி அவசியம்.",
     "category_tested": "sandhi_doubling", "note": "எல்லா + க் correct"},
    {"sentence": "அனைத்துப் பள்ளிகளிலும் விழா நடைபெற்றது.",
     "category_tested": "sandhi_doubling", "note": "அனைத்து + ப் correct"},

    # Correct: மெல்ல/உரக்க + doubled
    {"sentence": "மெல்லப் பேசினாள் அவள்.",
     "category_tested": "sandhi_doubling", "note": "மெல்ல + ப் correct"},
    {"sentence": "உரக்கச் சொன்னார் ஆசிரியர்.",
     "category_tested": "sandhi_doubling", "note": "உரக்க + ச் correct"},

    # Correct: கீழ்/மேல் compound
    {"sentence": "கீழ்க்காணும் விவரங்களைப் படியுங்கள்.",
     "category_tested": "sandhi_doubling", "note": "கீழ் + க் correct"},

    # Correct: Direction words + doubled
    {"sentence": "கிழக்குப் பகுதியில் மழை பெய்தது.",
     "category_tested": "sandhi_doubling", "note": "கிழக்கு + ப் correct"},

    # Correct: ஈறுகெட்ட எதிர்மறை + doubled
    {"sentence": "படாத் துன்பம் அனுபவித்தான்.",
     "category_tested": "sandhi_doubling", "note": "படா + த் correct"},
    {"sentence": "காணாக் காட்சியைக் கண்டோம்.",
     "category_tested": "sandhi_doubling", "note": "காணா + க் correct"},

    # Correct: Metaphor + doubled
    {"sentence": "வாழ்க்கைப் படகு கரை சேரும்.",
     "category_tested": "sandhi_doubling", "note": "வாழ்க்கை + ப் correct"},

    # ================================================================
    # GROUP 2: Correct non-doubling (vallinam properly NOT doubled)
    # These test that models don't incorrectly add doubling.
    # ================================================================

    # Correct: Demonstrative PRONOUNS (don't double — Rule 94)
    {"sentence": "அது கனமானது.",
     "category_tested": "sandhi_no_doubling", "note": "அது + க — no doubling"},
    {"sentence": "இது செய்வதற்கு எளிதானது.",
     "category_tested": "sandhi_no_doubling", "note": "இது + ச — no doubling"},

    # Correct: Interrogative pronouns (don't double — Rule 95)
    {"sentence": "எது சிறந்தது என்று தெரியவில்லை.",
     "category_tested": "sandhi_no_doubling", "note": "எது + ச — no doubling"},

    # Correct: Nominative subject (don't double — Rule 96)
    {"sentence": "குதிரை கனைத்தது.",
     "category_tested": "sandhi_no_doubling", "note": "குதிரை + க — no doubling"},
    {"sentence": "கிளி கொஞ்சியது.",
     "category_tested": "sandhi_no_doubling", "note": "கிளி + க — no doubling"},
    {"sentence": "தாமரை பூத்தது.",
     "category_tested": "sandhi_no_doubling", "note": "தாமரை + ப — no doubling"},

    # Correct: Participial adjective (don't double — Rule 100)
    {"sentence": "ஓடிய குதிரை திரும்பி வந்தது.",
     "category_tested": "sandhi_no_doubling", "note": "ஓடிய + க — no doubling"},
    {"sentence": "படித்த பெண் சிறந்த தொழிலாளி.",
     "category_tested": "sandhi_no_doubling", "note": "படித்த + ப — no doubling"},
    {"sentence": "சென்ற தமிழன் வெற்றி பெற்றான்.",
     "category_tested": "sandhi_no_doubling", "note": "சென்ற + த — no doubling"},

    # Correct: Optative verb (don't double — Rule 104)
    {"sentence": "வாழ்க தமிழ்!",
     "category_tested": "sandhi_no_doubling", "note": "வாழ்க + த — no doubling"},

    # Correct: Quantity words (don't double — Rules 106-107)
    {"sentence": "அத்தனை புத்தகங்களையும் படித்துவிட்டான்.",
     "category_tested": "sandhi_no_doubling", "note": "அத்தனை + ப — no doubling"},
    {"sentence": "எவ்வளவு கொடுத்தாலும் போதாது.",
     "category_tested": "sandhi_no_doubling", "note": "எவ்வளவு + க — no doubling"},

    # Correct: Numerals other than 8/10 (don't double — Rule 109)
    {"sentence": "மூன்று கனிகள் வாங்கினேன்.",
     "category_tested": "sandhi_no_doubling", "note": "மூன்று + க — no doubling"},
    {"sentence": "ஐந்து பழங்கள் சாப்பிட்டான்.",
     "category_tested": "sandhi_no_doubling", "note": "ஐந்து + ப — no doubling"},
    {"sentence": "ஏழு கடல்களைக் கடந்தான்.",
     "category_tested": "sandhi_no_doubling", "note": "ஏழு + க — no doubling"},

    # Correct: Coordinative compound (don't double — Rule 111)
    {"sentence": "தாய் தந்தை வந்தனர்.",
     "category_tested": "sandhi_no_doubling", "note": "coordinative — no doubling"},
    {"sentence": "செடி கொடி வளர்ந்தன.",
     "category_tested": "sandhi_no_doubling", "note": "coordinative — no doubling"},

    # Correct: Temporal words (don't double — Rule 112)
    {"sentence": "அன்று கேட்டதை இன்று செய்தான்.",
     "category_tested": "sandhi_no_doubling", "note": "அன்று/இன்று — no doubling"},

    # Correct: Manner words (don't double — Rule 113)
    {"sentence": "அவ்வாறு கூறினார்.",
     "category_tested": "sandhi_no_doubling", "note": "அவ்வாறு + க — no doubling"},

    # Correct: Human nouns (don't double — Rule 119)
    {"sentence": "ஆசிரியர் கல்வி கற்பித்தார்.",
     "category_tested": "sandhi_no_doubling", "note": "ஆசிரியர் + க — no doubling"},

    # Correct: Negative participial (don't double — Rule 121)
    {"sentence": "பார்க்காத பயிர் வாடியது.",
     "category_tested": "sandhi_no_doubling", "note": "negative participial — no doubling"},

    # Correct: Size adjectives (don't double — Rule 122)
    {"sentence": "சிறிய கண்ணாடி போதும்.",
     "category_tested": "sandhi_no_doubling", "note": "சிறிய + க — no doubling"},
    {"sentence": "பெரிய பானையில் தண்ணீர் நிரம்பியது.",
     "category_tested": "sandhi_no_doubling", "note": "பெரிய + ப — no doubling"},

    # Correct: Reduplicated words (don't double — Rule 124)
    {"sentence": "பாம்பு பாம்பு என்று கத்தினான்.",
     "category_tested": "sandhi_no_doubling", "note": "reduplicated — no doubling"},

    # Correct: Quality adjectives (don't double — Rule 127)
    {"sentence": "நல்ல பையன் என்று அழைத்தார்.",
     "category_tested": "sandhi_no_doubling", "note": "நல்ல + ப — no doubling"},
    {"sentence": "தீய பழக்கங்களைத் தவிர்க்க வேண்டும்.",
     "category_tested": "sandhi_no_doubling", "note": "தீய + ப — no doubling"},

    # Correct: Kinship terms (don't double — Rule 128)
    {"sentence": "தம்பி பார்த்ததும் ஓடி வந்தான்.",
     "category_tested": "sandhi_no_doubling", "note": "தம்பி + ப — no doubling"},

    # ================================================================
    # GROUP 3: Correct ஒரு/ஓர் usage
    # ================================================================

    # ஒரு before consonant
    {"sentence": "ஒரு மரத்தின் கீழ் அமர்ந்தான்.",
     "category_tested": "article_usage", "note": "ஒரு + consonant correct"},
    {"sentence": "ஒரு குழந்தை சிரித்தது.",
     "category_tested": "article_usage", "note": "ஒரு + consonant correct"},
    {"sentence": "ஒரு நாள் புரட்சி வரும்.",
     "category_tested": "article_usage", "note": "ஒரு + consonant correct"},

    # ஓர் before vowel
    {"sentence": "ஓர் ஆடு மேய்ந்துகொண்டிருந்தது.",
     "category_tested": "article_usage", "note": "ஓர் + vowel correct"},
    {"sentence": "ஓர் ஊரில் ஒரு ராஜா இருந்தான்.",
     "category_tested": "article_usage", "note": "ஓர் + vowel, ஒரு + consonant"},
    {"sentence": "ஓர் இரவில் நிகழ்ந்தது.",
     "category_tested": "article_usage", "note": "ஓர் + vowel correct"},

    # ================================================================
    # GROUP 4: Correct word joining
    # ================================================================

    {"sentence": "அவர் வேலைக்குச் சென்றார்.",
     "category_tested": "word_joining", "note": "case marker joined correctly"},
    {"sentence": "மாணவர்களுக்குப் புத்தகங்கள் வழங்கப்பட்டன.",
     "category_tested": "word_joining", "note": "dative case correct"},
    {"sentence": "அவன் வீட்டிற்குச் சென்றான்.",
     "category_tested": "word_joining", "note": "case marker correct"},
    {"sentence": "கடைக்குப் போனான்.",
     "category_tested": "word_joining", "note": "dative + sandhi correct"},
    {"sentence": "ஆற்றங்கரையில் அமர்ந்தான்.",
     "category_tested": "word_joining", "note": "compound noun joined correct"},

    # ================================================================
    # GROUP 5: Correct word separation
    # ================================================================

    {"sentence": "வடை அல்லது முறுக்கு வாங்கி வா.",
     "category_tested": "word_separation", "note": "அல்லது separated correctly"},
    {"sentence": "அவன் என்னிடம் கேட்டான்.",
     "category_tested": "word_separation", "note": "postposition correct"},
    {"sentence": "மேசையின் மேல் புத்தகம் இருந்தது.",
     "category_tested": "word_separation", "note": "postposition separated correctly"},

    # ================================================================
    # GROUP 6: Correct number agreement
    # ================================================================

    {"sentence": "ஒவ்வொரு மாணவரும் தேர்வில் பங்கேற்றார்.",
     "category_tested": "number_agreement", "note": "ஒவ்வொரு + singular correct"},
    {"sentence": "எல்லா மாணவர்களும் தேர்வில் பங்கேற்றனர்.",
     "category_tested": "number_agreement", "note": "எல்லா + plural correct"},
    {"sentence": "எந்தப் புத்தகமும் எடுக்கலாம்.",
     "category_tested": "number_agreement", "note": "எந்த + singular correct"},

    # ================================================================
    # GROUP 7: Correct noun + postposition
    # ================================================================

    {"sentence": "அவர் பற்றிய செய்தி வந்தது.",
     "category_tested": "noun_postposition", "note": "postposition correct"},
    {"sentence": "மழையினால் வெள்ளம் ஏற்பட்டது.",
     "category_tested": "noun_postposition", "note": "instrumental case correct"},
    {"sentence": "வீட்டுக்கு அருகில் பூங்கா இருக்கிறது.",
     "category_tested": "noun_postposition", "note": "அருகில் separated correct"},

    # ================================================================
    # GROUP 8: Correct verb + auxiliary
    # ================================================================

    {"sentence": "அவன் படித்துக்கொண்டிருக்கிறான்.",
     "category_tested": "verb_auxiliary", "note": "auxiliary joined correctly"},
    {"sentence": "மழை பெய்துவிட்டது.",
     "category_tested": "verb_auxiliary", "note": "auxiliary joined correctly"},
    {"sentence": "அவள் பாடிக்கொண்டிருந்தாள்.",
     "category_tested": "verb_auxiliary", "note": "auxiliary joined correctly"},

    # ================================================================
    # GROUP 9: General correct sentences (no specific trap)
    # ================================================================

    {"sentence": "காலையில் சூரியன் எழுந்தது.",
     "category_tested": "general", "note": "simple correct sentence"},
    {"sentence": "குழந்தைகள் பூங்காவில் விளையாடினர்.",
     "category_tested": "general", "note": "simple correct sentence"},
    {"sentence": "நூலகத்தில் புத்தகங்கள் நிறைய இருக்கின்றன.",
     "category_tested": "general", "note": "simple correct sentence"},
    {"sentence": "தமிழ் மொழி மிகப் பழமையானது.",
     "category_tested": "general", "note": "மிக + ப் sandhi correct"},
    {"sentence": "கடலில் மீன்கள் நீந்தின.",
     "category_tested": "general", "note": "simple correct sentence"},
    {"sentence": "வானத்தில் நிலவு ஒளிர்ந்தது.",
     "category_tested": "general", "note": "simple correct sentence"},
    {"sentence": "பள்ளிக்கூடத்தில் ஆசிரியர் பாடம் நடத்தினார்.",
     "category_tested": "general", "note": "compound noun + sandhi correct"},
    {"sentence": "சிறுவன் மரத்தின் மேல் ஏறினான்.",
     "category_tested": "general", "note": "simple correct sentence"},
    {"sentence": "விவசாயி வயலில் நெல் அறுவடை செய்தார்.",
     "category_tested": "general", "note": "simple correct sentence"},
    {"sentence": "அரசு மருத்துவமனையில் சிகிச்சை பெற்றான்.",
     "category_tested": "general", "note": "simple correct sentence"},
    {"sentence": "நீதிமன்றத்தில் வழக்கு நடைபெற்றது.",
     "category_tested": "general", "note": "simple correct sentence"},
    {"sentence": "பேருந்தில் இடம் இல்லாமல் நின்றான்.",
     "category_tested": "general", "note": "simple correct sentence"},
    {"sentence": "கணினியில் வேலை செய்வது கடினமல்ல.",
     "category_tested": "general", "note": "simple correct sentence"},
    {"sentence": "தமிழ்நாட்டில் பொங்கல் பெரிய திருநாள்.",
     "category_tested": "general", "note": "simple correct sentence"},
    {"sentence": "அறிவியல் கண்டுபிடிப்புகள் மனித வாழ்க்கையை மாற்றின.",
     "category_tested": "general", "note": "simple correct sentence"},
    {"sentence": "இலக்கியம் சமூகத்தின் கண்ணாடி.",
     "category_tested": "general", "note": "simple correct sentence"},
    {"sentence": "கலைஞர்கள் தங்கள் படைப்புகளால் புகழ் பெற்றனர்.",
     "category_tested": "general", "note": "simple correct sentence"},
    {"sentence": "தொல்காப்பியம் தமிழின் மிகப் பழமையான இலக்கண நூல்.",
     "category_tested": "general", "note": "மிக + ப் sandhi correct"},
    {"sentence": "சங்க காலத்தில் தமிழ் இலக்கியம் சிறப்புற்று விளங்கியது.",
     "category_tested": "general", "note": "simple correct sentence"},
    {"sentence": "வள்ளுவரின் குறள் உலகப் பொதுமறை என்று போற்றப்படுகிறது.",
     "category_tested": "general", "note": "simple correct sentence"},

    # Additional correct sentences to reach ~100
    {"sentence": "நிறையக் கற்றவன் நிறையப் பேசுவான்.",
     "category_tested": "sandhi_doubling", "note": "நிறைய + க்/ப் both correct"},
    {"sentence": "இன்றிச் செய்ய முடியாது.",
     "category_tested": "sandhi_doubling", "note": "இன்றி + ச் correct"},
    {"sentence": "அவ்வகைச் செடிகள் இப்பகுதியில் வளரும்.",
     "category_tested": "sandhi_doubling", "note": "அவ்வகை + ச் correct"},
    {"sentence": "இவ்வாறு கூறினார் தலைவர்.",
     "category_tested": "sandhi_no_doubling", "note": "இவ்வாறு + க — no doubling"},
    {"sentence": "அவன் ஒரு செல்லாத காசு.",
     "category_tested": "sandhi_no_doubling", "note": "செல்லாத + க — no doubling"},
    {"sentence": "அரிய காட்சிகள் நிறைந்த காடு.",
     "category_tested": "sandhi_no_doubling", "note": "அரிய + க — no doubling"},
    {"sentence": "தங்கை கூப்பிட்டதும் தம்பி ஓடிவந்தான்.",
     "category_tested": "sandhi_no_doubling", "note": "kinship terms — no doubling"},
    {"sentence": "நாட்டுப்பற்று உள்ளவனே நல்லவன்.",
     "category_tested": "sandhi_doubling", "note": "நாட்டு + ப் correct compound"},
    {"sentence": "ஒன்று கூடுவோம் ஒருமையுடன்.",
     "category_tested": "sandhi_no_doubling", "note": "ஒன்று + க — no doubling"},
    {"sentence": "மழைக்காலத்தில் ஆறுகள் நிறைந்து ஓடின.",
     "category_tested": "general", "note": "simple correct sentence"},
    {"sentence": "பலாப்பழம் சுவையானது.",
     "category_tested": "sandhi_doubling", "note": "பலா + ப் correct compound"},
    {"sentence": "சின்னக்குடை ஒன்று கொண்டு வா.",
     "category_tested": "sandhi_doubling", "note": "சின்ன + க் correct compound"},
    {"sentence": "எந்த நாட்டுக்கும் செல்லலாம்.",
     "category_tested": "number_agreement", "note": "எந்த + singular correct"},
]


def build_records(data: list[dict]) -> list[dict]:
    """Convert raw data into JSONL records."""
    records = []

    for i, item in enumerate(data):
        record = {
            "id": f"tn_t3_{i+1:03d}",
            "source": "",
            "category": "correct_sentence",
            "subcategory": item["category_tested"],
            "rule_id": "",
            "rule_name": "",
            "book_page": 0,
            "book_rules": [],
            "error_sentence": "",
            "correct_sentence": item["sentence"],
            "marked_text": "",
            "correction": "",
            "error_span": [],
            "message": "",
            "short_description": item["note"],
            "source_url": "",
            "origin": "curated_correct",
            "is_error_example": False,
            "uses_postag": False,
            "postags": [],
            "example_type": "correct",
            "error_type": "",
            "difficulty": "",
            "needs_review": True,
        }
        records.append(record)

    return records


def main():
    project_dir = Path(__file__).resolve().parent.parent
    output_path = project_dir / "dataset" / "tier3_correct.jsonl"

    records = build_records(TIER3_DATA)

    with open(output_path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    # Summary
    from collections import Counter
    cats = Counter(r["subcategory"] for r in records)

    print(f"Tier 3 generation complete.")
    print(f"Total correct sentences: {len(records)}")
    print(f"\nBy category tested:")
    for cat, count in cats.most_common():
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    main()
