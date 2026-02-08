"""
generate_tier2.py — Step 3: Generate Tier 2 examples from book rules

Creates example sentence pairs for the ~90 book rules NOT covered by
grammar.xml. Uses the book's own examples wherever possible.

Usage:
    python Tamil_Nadai/tools/generate_tier2.py

Output:
    Tamil_Nadai/dataset/tier2_book_rules.jsonl
"""

import json
from pathlib import Path

# ========================================================================
# DATA: Each entry is a dict with rule metadata and example pairs.
# Examples use the book's own words/phrases, placed in sentence context.
#
# For sandhi_doubling: error = missing doubled consonant
# For sandhi_no_doubling: error = incorrectly adding doubled consonant
# For number_agreement: error = wrong singular/plural
# For article_usage: error = wrong ஒரு/ஓர் form
# ========================================================================

TIER2_DATA = [

    # ================================================================
    # GROUP A: SANDHI DOUBLING — Unimplemented rules 57-69, 79-93
    # ================================================================

    # Rule 57: அப்படி/இப்படி/எப்படி + vallinam doubles
    {
        "rule_id": "book_057", "book_rule": 57, "book_page": 83,
        "category": "sandhi_doubling", "subcategory": "demonstrative_adverb",
        "rule_name_ta": "அப்படி/இப்படி/எப்படி பின் ஒற்று மிகுதல்",
        "examples": [
            {"error": "அவன் அப்படி செய்தான்.", "correct": "அவன் அப்படிச் செய்தான்.",
             "marked": "அப்படி செய்தான்", "correction": "அப்படிச் செய்தான்"},
            {"error": "இப்படி சொல்லாதே.", "correct": "இப்படிச் சொல்லாதே.",
             "marked": "இப்படி சொல்லாதே", "correction": "இப்படிச் சொல்லாதே"},
            {"error": "எப்படி பேசினான் தெரியுமா?", "correct": "எப்படிப் பேசினான் தெரியுமா?",
             "marked": "எப்படி பேசினான்", "correction": "எப்படிப் பேசினான்"},
        ]
    },

    # Rule 58: அவ்வகை/இவ்வகை/எவ்வகை + vallinam doubles
    {
        "rule_id": "book_058", "book_rule": 58, "book_page": 83,
        "category": "sandhi_doubling", "subcategory": "demonstrative_type",
        "rule_name_ta": "அவ்வகை/இவ்வகை/எவ்வகை பின் ஒற்று மிகுதல்",
        "examples": [
            {"error": "அவ்வகை செடி இங்கு வளராது.", "correct": "அவ்வகைச் செடி இங்கு வளராது.",
             "marked": "அவ்வகை செடி", "correction": "அவ்வகைச் செடி"},
            {"error": "இவ்வகை பூக்கள் அரிதானவை.", "correct": "இவ்வகைப் பூக்கள் அரிதானவை.",
             "marked": "இவ்வகை பூக்கள்", "correction": "இவ்வகைப் பூக்கள்"},
            {"error": "எவ்வகை துணி வேண்டும்?", "correct": "எவ்வகைத் துணி வேண்டும்?",
             "marked": "எவ்வகை துணி", "correction": "எவ்வகைத் துணி"},
        ]
    },

    # Rule 59: இனி/தனி + vallinam doubles
    {
        "rule_id": "book_059", "book_rule": 59, "book_page": 83,
        "category": "sandhi_doubling", "subcategory": "adverb",
        "rule_name_ta": "இனி/தனி பின் ஒற்று மிகுதல்",
        "examples": [
            {"error": "இனி காண்போம்.", "correct": "இனிக் காண்போம்.",
             "marked": "இனி காண்போம்", "correction": "இனிக் காண்போம்"},
            {"error": "இது ஒரு தனி சொல்.", "correct": "இது ஒரு தனிச்சொல்.",
             "marked": "தனி சொல்", "correction": "தனிச்சொல்"},
        ]
    },

    # Rule 60: அன்றி/இன்றி + vallinam doubles
    {
        "rule_id": "book_060", "book_rule": 60, "book_page": 83,
        "category": "sandhi_doubling", "subcategory": "conjunction",
        "rule_name_ta": "அன்றி/இன்றி பின் ஒற்று மிகுதல்",
        "examples": [
            {"error": "தடையின்றி செல்லலாம்.", "correct": "தடையின்றிச் செல்லலாம்.",
             "marked": "தடையின்றி செல்லலாம்", "correction": "தடையின்றிச் செல்லலாம்"},
            {"error": "அந்த மாணவனன்றி பிற மாணவர் பேசக்கூடாது.", "correct": "அந்த மாணவனன்றிப் பிற மாணவர் பேசக்கூடாது.",
             "marked": "மாணவனன்றி பிற", "correction": "மாணவனன்றிப் பிற"},
        ]
    },

    # Rule 62: முழு/திரு/புது/அரை/பாதி + vallinam doubles
    {
        "rule_id": "book_062", "book_rule": 62, "book_page": 83,
        "category": "sandhi_doubling", "subcategory": "adjective_prefix",
        "rule_name_ta": "முழு/திரு/புது/அரை/பாதி பின் ஒற்று மிகுதல்",
        "examples": [
            {"error": "முழு பக்கம் படித்தேன்.", "correct": "முழுப்பக்கம் படித்தேன்.",
             "marked": "முழு பக்கம்", "correction": "முழுப்பக்கம்"},
            {"error": "திரு குறள் படிப்போம்.", "correct": "திருக்குறள் படிப்போம்.",
             "marked": "திரு குறள்", "correction": "திருக்குறள்"},
            {"error": "புது கண்ணாடி வாங்கினேன்.", "correct": "புதுக்கண்ணாடி வாங்கினேன்.",
             "marked": "புது கண்ணாடி", "correction": "புதுக்கண்ணாடி"},
            {"error": "அரை பங்கு கொடு.", "correct": "அரைப்பங்கு கொடு.",
             "marked": "அரை பங்கு", "correction": "அரைப்பங்கு"},
        ]
    },

    # Rule 63: எட்டு/பத்து + vallinam doubles
    {
        "rule_id": "book_063", "book_rule": 63, "book_page": 83,
        "category": "sandhi_doubling", "subcategory": "numeral",
        "rule_name_ta": "எட்டு/பத்து பின் ஒற்று மிகுதல்",
        "examples": [
            {"error": "எட்டு தொகை நூல்களைப் படிப்போம்.", "correct": "எட்டுத் தொகை நூல்களைப் படிப்போம்.",
             "marked": "எட்டு தொகை", "correction": "எட்டுத் தொகை"},
            {"error": "பத்து பாட்டு கற்றேன்.", "correct": "பத்துப்பாட்டு கற்றேன்.",
             "marked": "பத்து பாட்டு", "correction": "பத்துப்பாட்டு"},
        ]
    },

    # Rule 69: ஆய்/போய் + vallinam doubles
    {
        "rule_id": "book_069", "book_rule": 69, "book_page": 83,
        "category": "sandhi_doubling", "subcategory": "verb_form",
        "rule_name_ta": "ஆய்/போய் பின் ஒற்று மிகுதல்",
        "examples": [
            {"error": "ஒழுங்காய் படி.", "correct": "ஒழுங்காய்ப் படி.",
             "marked": "ஒழுங்காய் படி", "correction": "ஒழுங்காய்ப் படி"},
            {"error": "மகிழ்ச்சியாய் பேசினாள்.", "correct": "மகிழ்ச்சியாய்ப் பேசினாள்.",
             "marked": "மகிழ்ச்சியாய் பேசினாள்", "correction": "மகிழ்ச்சியாய்ப் பேசினாள்"},
            {"error": "போய் தேடு.", "correct": "போய்த் தேடு.",
             "marked": "போய் தேடு", "correction": "போய்த் தேடு"},
        ]
    },

    # Rule 79: ய/ர/ழ ஒற்று + vallinam doubles
    {
        "rule_id": "book_079", "book_rule": 79, "book_page": 84,
        "category": "sandhi_doubling", "subcategory": "consonant_ending",
        "rule_name_ta": "ய/ர/ழ ஒற்றுப் பின் ஒற்று மிகுதல்",
        "examples": [
            {"error": "வாழ்கை நீண்டது.", "correct": "வாழ்க்கை நீண்டது.",
             "marked": "வாழ்கை", "correction": "வாழ்க்கை"},
            {"error": "பாய்சல் வேகமானது.", "correct": "பாய்ச்சல் வேகமானது.",
             "marked": "பாய்சல்", "correction": "பாய்ச்சல்"},
            {"error": "அவள் வாழ்தினாள்.", "correct": "அவள் வாழ்த்தினாள்.",
             "marked": "வாழ்தினாள்", "correction": "வாழ்த்தினாள்"},
        ]
    },

    # Rule 80: திசைப்பெயர்கள் + vallinam doubles
    {
        "rule_id": "book_080", "book_rule": 80, "book_page": 84,
        "category": "sandhi_doubling", "subcategory": "direction_words",
        "rule_name_ta": "திசைப்பெயர்கள் பின் ஒற்று மிகுதல்",
        "examples": [
            {"error": "கிழக்கு பக்கம் திரும்பு.", "correct": "கிழக்குப் பக்கம் திரும்பு.",
             "marked": "கிழக்கு பக்கம்", "correction": "கிழக்குப் பக்கம்"},
            {"error": "மேற்கு தொடர்ச்சி மலை அழகானது.", "correct": "மேற்குத் தொடர்ச்சி மலை அழகானது.",
             "marked": "மேற்கு தொடர்ச்சி", "correction": "மேற்குத் தொடர்ச்சி"},
        ]
    },

    # Rule 81-82: மென்றொடர்/உயிர்த்தொடர் குற்றியலுகரம்
    {
        "rule_id": "book_081", "book_rule": 81, "book_page": 84,
        "category": "sandhi_doubling", "subcategory": "kutriyalukara",
        "rule_name_ta": "மென்றொடர்/உயிர்த்தொடர் குற்றியலுகரம் பின் ஒற்று மிகுதல்",
        "examples": [
            {"error": "நண்டு கூட்டம் பெரிதாக இருந்தது.", "correct": "நண்டுக் கூட்டம் பெரிதாக இருந்தது.",
             "marked": "நண்டு கூட்டம்", "correction": "நண்டுக் கூட்டம்"},
            {"error": "பங்கு சந்தை இன்று சரிந்தது.", "correct": "பங்குச் சந்தை இன்று சரிந்தது.",
             "marked": "பங்கு சந்தை", "correction": "பங்குச் சந்தை"},
            {"error": "அரசு பள்ளி நல்ல பள்ளி.", "correct": "அரசுப்பள்ளி நல்ல பள்ளி.",
             "marked": "அரசு பள்ளி", "correction": "அரசுப்பள்ளி"},
        ]
    },

    # Rule 83: தொகைநிலைத் தொடர்கள்
    {
        "rule_id": "book_083", "book_rule": 83, "book_page": 84,
        "category": "sandhi_doubling", "subcategory": "compound_noun",
        "rule_name_ta": "தொகைநிலைத் தொடர்கள் பின் ஒற்று மிகுதல்",
        "examples": [
            {"error": "சிறப்பு புடவை வாங்கினாள்.", "correct": "சிறப்புப் புடவை வாங்கினாள்.",
             "marked": "சிறப்பு புடவை", "correction": "சிறப்புப் புடவை"},
            {"error": "முல்லை காடு பசுமையானது.", "correct": "முல்லைக்காடு பசுமையானது.",
             "marked": "முல்லை காடு", "correction": "முல்லைக்காடு"},
        ]
    },

    # Rule 84: உரிச்சொற்கள்
    {
        "rule_id": "book_084", "book_rule": 84, "book_page": 84,
        "category": "sandhi_doubling", "subcategory": "expressive_word",
        "rule_name_ta": "உரிச்சொற்கள் பின் ஒற்று மிகுதல்",
        "examples": [
            {"error": "அவர் சால பேசினார்.", "correct": "அவர் சாலப் பேசினார்.",
             "marked": "சால பேசினார்", "correction": "சாலப் பேசினார்"},
            {"error": "தட கை யானை.", "correct": "தடக்கை யானை.",
             "marked": "தட கை", "correction": "தடக்கை"},
        ]
    },

    # Rule 85: ஆகாரச்சொல் (onomatopoeia after short vowel)
    {
        "rule_id": "book_085", "book_rule": 85, "book_page": 84,
        "category": "sandhi_doubling", "subcategory": "onomatopoeia",
        "rule_name_ta": "ஆகாரச்சொல் பின் ஒற்று மிகுதல்",
        "examples": [
            {"error": "நிலா பாட்டு கேட்டோம்.", "correct": "நிலாப்பாட்டு கேட்டோம்.",
             "marked": "நிலா பாட்டு", "correction": "நிலாப்பாட்டு"},
            {"error": "பலா பழம் சுவையானது.", "correct": "பலாப்பழம் சுவையானது.",
             "marked": "பலா பழம்", "correction": "பலாப்பழம்"},
        ]
    },

    # Rule 86: உருவகம் (metaphors)
    {
        "rule_id": "book_086", "book_rule": 86, "book_page": 84,
        "category": "sandhi_doubling", "subcategory": "metaphor",
        "rule_name_ta": "உருவகம் பின் ஒற்று மிகுதல்",
        "examples": [
            {"error": "வாழ்க்கை படகு கரை சேரும்.", "correct": "வாழ்க்கைப் படகு கரை சேரும்.",
             "marked": "வாழ்க்கை படகு", "correction": "வாழ்க்கைப் படகு"},
            {"error": "கண்ணீர் பூக்கள் உதிர்ந்தன.", "correct": "கண்ணீர்ப் பூக்கள் உதிர்ந்தன.",
             "marked": "கண்ணீர் பூக்கள்", "correction": "கண்ணீர்ப் பூக்கள்"},
        ]
    },

    # Rule 87: மெல்ல/உரக்க/நிறம்ப/நிறைய
    {
        "rule_id": "book_087", "book_rule": 87, "book_page": 84,
        "category": "sandhi_doubling", "subcategory": "specific_adverb",
        "rule_name_ta": "மெல்ல/உரக்க/நிறைய பின் ஒற்று மிகுதல்",
        "examples": [
            {"error": "மெல்ல பேசு.", "correct": "மெல்லப் பேசு.",
             "marked": "மெல்ல பேசு", "correction": "மெல்லப் பேசு"},
            {"error": "உரக்க சொல்.", "correct": "உரக்கச் சொல்.",
             "marked": "உரக்க சொல்", "correction": "உரக்கச் சொல்"},
            {"error": "நிறைய கற்றான்.", "correct": "நிறையக் கற்றான்.",
             "marked": "நிறைய கற்றான்", "correction": "நிறையக் கற்றான்"},
        ]
    },

    # Rule 88: எல்லா/அனைத்து
    {
        "rule_id": "book_088", "book_rule": 88, "book_page": 84,
        "category": "sandhi_doubling", "subcategory": "quantifier",
        "rule_name_ta": "எல்லா/அனைத்து பின் ஒற்று மிகுதல்",
        "examples": [
            {"error": "எல்லா குழந்தைகளும் ஒன்றுகூடின.", "correct": "எல்லாக் குழந்தைகளும் ஒன்றுகூடின.",
             "marked": "எல்லா குழந்தைகளும்", "correction": "எல்லாக் குழந்தைகளும்"},
            {"error": "அனைத்து பள்ளிகளுக்கும் நாளை விடுமுறை.", "correct": "அனைத்துப் பள்ளிகளுக்கும் நாளை விடுமுறை.",
             "marked": "அனைத்து பள்ளிகளுக்கும்", "correction": "அனைத்துப் பள்ளிகளுக்கும்"},
        ]
    },

    # Rule 89: ஒற்று இரட்டிக்கும் குற்றியலுகரம்
    {
        "rule_id": "book_089", "book_rule": 89, "book_page": 84,
        "category": "sandhi_doubling", "subcategory": "doubling_ukara",
        "rule_name_ta": "ஒற்று இரட்டிக்கும் குற்றியலுகரம் பின் ஒற்று மிகுதல்",
        "examples": [
            {"error": "நாட்டு பற்று வேண்டும்.", "correct": "நாட்டுப்பற்று வேண்டும்.",
             "marked": "நாட்டு பற்று", "correction": "நாட்டுப்பற்று"},
            {"error": "ஆற்று பெருக்கு வந்தது.", "correct": "ஆற்றுப் பெருக்கு வந்தது.",
             "marked": "ஆற்று பெருக்கு", "correction": "ஆற்றுப் பெருக்கு"},
        ]
    },

    # Rule 90: முற்றியலுகரம்
    {
        "rule_id": "book_090", "book_rule": 90, "book_page": 84,
        "category": "sandhi_doubling", "subcategory": "full_ukara",
        "rule_name_ta": "முற்றியலுகரம் பின் ஒற்று மிகுதல்",
        "examples": [
            {"error": "அறிவு கல்லூரி சிறந்தது.", "correct": "அறிவுக் கல்லூரி சிறந்தது.",
             "marked": "அறிவு கல்லூரி", "correction": "அறிவுக் கல்லூரி"},
            {"error": "பொது பார்வையில் நடந்தான்.", "correct": "பொதுப் பார்வையில் நடந்தான்.",
             "marked": "பொது பார்வையில்", "correction": "பொதுப் பார்வையில்"},
        ]
    },

    # Rule 93: கீழ்/இடை
    {
        "rule_id": "book_093", "book_rule": 93, "book_page": 84,
        "category": "sandhi_doubling", "subcategory": "positional_word",
        "rule_name_ta": "கீழ்/இடை பின் ஒற்று மிகுதல்",
        "examples": [
            {"error": "கீழ் காணும் செய்திகளைப் படியுங்கள்.", "correct": "கீழ்க்காணும் செய்திகளைப் படியுங்கள்.",
             "marked": "கீழ் காணும்", "correction": "கீழ்க்காணும்"},
            {"error": "புலிகளிடை பசு போல.", "correct": "புலிகளிடைப் பசு போல.",
             "marked": "புலிகளிடை பசு", "correction": "புலிகளிடைப் பசு"},
        ]
    },

    # ================================================================
    # GROUP B: SANDHI NO DOUBLING — Rules 94-128
    # ================================================================

    # Rule 94: After demonstrative PRONOUNS — DON'T double
    {
        "rule_id": "book_094", "book_rule": 94, "book_page": 84,
        "category": "sandhi_no_doubling", "subcategory": "demonstrative_pronoun",
        "rule_name_ta": "சுட்டுப்பெயர் பின் ஒற்று மிகாமை",
        "examples": [
            {"error": "அதுக் காண்.", "correct": "அது காண்.",
             "marked": "அதுக் காண்", "correction": "அது காண்"},
            {"error": "இதுச் செய்.", "correct": "இது செய்.",
             "marked": "இதுச் செய்", "correction": "இது செய்"},
            {"error": "அவைக் கடினமானவை.", "correct": "அவை கடினமானவை.",
             "marked": "அவைக் கடினமானவை", "correction": "அவை கடினமானவை"},
        ]
    },

    # Rule 95: After interrogative PRONOUNS — DON'T double
    {
        "rule_id": "book_095", "book_rule": 95, "book_page": 84,
        "category": "sandhi_no_doubling", "subcategory": "interrogative_pronoun",
        "rule_name_ta": "வினாப்பெயர் பின் ஒற்று மிகாமை",
        "examples": [
            {"error": "எதுக் கண்டாய்?", "correct": "எது கண்டாய்?",
             "marked": "எதுக் கண்டாய்", "correction": "எது கண்டாய்"},
            {"error": "யாதுச் செய்தாய்?", "correct": "யாது செய்தாய்?",
             "marked": "யாதுச் செய்தாய்", "correction": "யாது செய்தாய்"},
        ]
    },

    # Rule 96: Nominative case — DON'T double
    {
        "rule_id": "book_096", "book_rule": 96, "book_page": 84,
        "category": "sandhi_no_doubling", "subcategory": "nominative_case",
        "rule_name_ta": "முதல் வேற்றுமை பின் ஒற்று மிகாமை",
        "examples": [
            {"error": "தாமரைப் பூத்தது.", "correct": "தாமரை பூத்தது.",
             "marked": "தாமரைப் பூத்தது", "correction": "தாமரை பூத்தது"},
            {"error": "குதிரைக் கனைத்தது.", "correct": "குதிரை கனைத்தது.",
             "marked": "குதிரைக் கனைத்தது", "correction": "குதிரை கனைத்தது"},
            {"error": "கிளிக் கொஞ்சியது.", "correct": "கிளி கொஞ்சியது.",
             "marked": "கிளிக் கொஞ்சியது", "correction": "கிளி கொஞ்சியது"},
        ]
    },

    # Rule 100: After participial adjectives — DON'T double
    {
        "rule_id": "book_100", "book_rule": 100, "book_page": 85,
        "category": "sandhi_no_doubling", "subcategory": "participial_adjective",
        "rule_name_ta": "பெயரெச்சம் பின் ஒற்று மிகாமை",
        "examples": [
            {"error": "ஓடியக் குதிரை வேகமானது.", "correct": "ஓடிய குதிரை வேகமானது.",
             "marked": "ஓடியக் குதிரை", "correction": "ஓடிய குதிரை"},
            {"error": "படித்தப் பெண் தொழிலில் சிறந்தாள்.", "correct": "படித்த பெண் தொழிலில் சிறந்தாள்.",
             "marked": "படித்தப் பெண்", "correction": "படித்த பெண்"},
            {"error": "சென்றத் தமிழன் வெற்றி பெற்றான்.", "correct": "சென்ற தமிழன் வெற்றி பெற்றான்.",
             "marked": "சென்றத் தமிழன்", "correction": "சென்ற தமிழன்"},
        ]
    },

    # Rule 104: After optative verbs — DON'T double
    {
        "rule_id": "book_104", "book_rule": 104, "book_page": 85,
        "category": "sandhi_no_doubling", "subcategory": "optative_verb",
        "rule_name_ta": "வியங்கோள் வினைமுற்று பின் ஒற்று மிகாமை",
        "examples": [
            {"error": "வாழ்கத் தலைவர்.", "correct": "வாழ்க தலைவர்.",
             "marked": "வாழ்கத் தலைவர்", "correction": "வாழ்க தலைவர்"},
            {"error": "வாழ்கத் தமிழகம்.", "correct": "வாழ்க தமிழகம்.",
             "marked": "வாழ்கத் தமிழகம்", "correction": "வாழ்க தமிழகம்"},
        ]
    },

    # Rule 106: After அத்தனை/இத்தனை/எத்தனை — DON'T double
    {
        "rule_id": "book_106", "book_rule": 106, "book_page": 85,
        "category": "sandhi_no_doubling", "subcategory": "quantity_word",
        "rule_name_ta": "அத்தனை/இத்தனை/எத்தனை பின் ஒற்று மிகாமை",
        "examples": [
            {"error": "அத்தனைப் புத்தகங்களா?", "correct": "அத்தனை புத்தகங்களா?",
             "marked": "அத்தனைப் புத்தகங்களா", "correction": "அத்தனை புத்தகங்களா"},
            {"error": "எத்தனைப் பேர்கள் வந்தார்கள்?", "correct": "எத்தனை பேர்கள் வந்தார்கள்?",
             "marked": "எத்தனைப் பேர்கள்", "correction": "எத்தனை பேர்கள்"},
        ]
    },

    # Rule 107: After அவ்வளவு/இவ்வளவு/எவ்வளவு — DON'T double
    {
        "rule_id": "book_107", "book_rule": 107, "book_page": 85,
        "category": "sandhi_no_doubling", "subcategory": "quantity_word",
        "rule_name_ta": "அவ்வளவு/இவ்வளவு/எவ்வளவு பின் ஒற்று மிகாமை",
        "examples": [
            {"error": "எவ்வளவுக் கொடுத்தாய்?", "correct": "எவ்வளவு கொடுத்தாய்?",
             "marked": "எவ்வளவுக் கொடுத்தாய்", "correction": "எவ்வளவு கொடுத்தாய்"},
            {"error": "இவ்வளவுத் தந்தாள்.", "correct": "இவ்வளவு தந்தாள்.",
             "marked": "இவ்வளவுத் தந்தாள்", "correction": "இவ்வளவு தந்தாள்"},
        ]
    },

    # Rule 109: After numerals other than எட்டு/பத்து — DON'T double
    {
        "rule_id": "book_109", "book_rule": 109, "book_page": 85,
        "category": "sandhi_no_doubling", "subcategory": "numeral",
        "rule_name_ta": "எண்ணுப்பெயர் பின் ஒற்று மிகாமை",
        "examples": [
            {"error": "மூன்றுக் கனி கொண்டு வா.", "correct": "மூன்று கனி கொண்டு வா.",
             "marked": "மூன்றுக் கனி", "correction": "மூன்று கனி"},
            {"error": "ஐந்துப் பழம் வாங்கினேன்.", "correct": "ஐந்து பழம் வாங்கினேன்.",
             "marked": "ஐந்துப் பழம்", "correction": "ஐந்து பழம்"},
            {"error": "ஏழுக் கடல் கடந்தான்.", "correct": "ஏழு கடல் கடந்தான்.",
             "marked": "ஏழுக் கடல்", "correction": "ஏழு கடல்"},
        ]
    },

    # Rule 111: In coordinative compounds — DON'T double
    {
        "rule_id": "book_111", "book_rule": 111, "book_page": 85,
        "category": "sandhi_no_doubling", "subcategory": "coordinative_compound",
        "rule_name_ta": "உம்மைத் தொகை பின் ஒற்று மிகாமை",
        "examples": [
            {"error": "தாய்த் தந்தை வந்தனர்.", "correct": "தாய் தந்தை வந்தனர்.",
             "marked": "தாய்த் தந்தை", "correction": "தாய் தந்தை"},
            {"error": "செடிக் கொடி வளர்ந்தன.", "correct": "செடி கொடி வளர்ந்தன.",
             "marked": "செடிக் கொடி", "correction": "செடி கொடி"},
        ]
    },

    # Rule 112: After அன்று/இன்று/என்று — DON'T double
    {
        "rule_id": "book_112", "book_rule": 112, "book_page": 85,
        "category": "sandhi_no_doubling", "subcategory": "temporal_word",
        "rule_name_ta": "அன்று/இன்று/என்று பின் ஒற்று மிகாமை",
        "examples": [
            {"error": "அன்றுக் கேட்டார்.", "correct": "அன்று கேட்டார்.",
             "marked": "அன்றுக் கேட்டார்", "correction": "அன்று கேட்டார்"},
            {"error": "இன்றுச் சொன்னார்.", "correct": "இன்று சொன்னார்.",
             "marked": "இன்றுச் சொன்னார்", "correction": "இன்று சொன்னார்"},
            {"error": "என்றுத் தருவார்?", "correct": "என்று தருவார்?",
             "marked": "என்றுத் தருவார்", "correction": "என்று தருவார்"},
        ]
    },

    # Rule 113: After அவ்வாறு/இவ்வாறு/எவ்வாறு — DON'T double
    {
        "rule_id": "book_113", "book_rule": 113, "book_page": 85,
        "category": "sandhi_no_doubling", "subcategory": "manner_word",
        "rule_name_ta": "அவ்வாறு/இவ்வாறு/எவ்வாறு பின் ஒற்று மிகாமை",
        "examples": [
            {"error": "அவ்வாறுக் கேட்டார்.", "correct": "அவ்வாறு கேட்டார்.",
             "marked": "அவ்வாறுக் கேட்டார்", "correction": "அவ்வாறு கேட்டார்"},
            {"error": "எவ்வாறுப் பேசினார்?", "correct": "எவ்வாறு பேசினார்?",
             "marked": "எவ்வாறுப் பேசினார்", "correction": "எவ்வாறு பேசினார்"},
        ]
    },

    # Rule 119: After human/rational nouns — DON'T double
    {
        "rule_id": "book_119", "book_rule": 119, "book_page": 86,
        "category": "sandhi_no_doubling", "subcategory": "rational_noun",
        "rule_name_ta": "உயர்திணைப் பெயர் பின் ஒற்று மிகாமை",
        "examples": [
            {"error": "ஆசிரியர்க் கல்வி கற்றார்.", "correct": "ஆசிரியர் கல்வி கற்றார்.",
             "marked": "ஆசிரியர்க் கல்வி", "correction": "ஆசிரியர் கல்வி"},
            {"error": "மாணவர்க் கையேடு.", "correct": "மாணவர் கையேடு.",
             "marked": "மாணவர்க் கையேடு", "correction": "மாணவர் கையேடு"},
        ]
    },

    # Rule 121: After full negative participial — DON'T double
    {
        "rule_id": "book_121", "book_rule": 121, "book_page": 86,
        "category": "sandhi_no_doubling", "subcategory": "negative_participial",
        "rule_name_ta": "எதிர்மறைப் பெயரெச்சம் பின் ஒற்று மிகாமை",
        "examples": [
            {"error": "பார்க்காதப் பயிர் வாடியது.", "correct": "பார்க்காத பயிர் வாடியது.",
             "marked": "பார்க்காதப் பயிர்", "correction": "பார்க்காத பயிர்"},
            {"error": "செல்லாதக் காசு.", "correct": "செல்லாத காசு.",
             "marked": "செல்லாதக் காசு", "correction": "செல்லாத காசு"},
        ]
    },

    # Rule 122: After சிறிய/பெரிய — DON'T double
    {
        "rule_id": "book_122", "book_rule": 122, "book_page": 86,
        "category": "sandhi_no_doubling", "subcategory": "size_adjective",
        "rule_name_ta": "சிறிய/பெரிய பின் ஒற்று மிகாமை",
        "examples": [
            {"error": "சிறியக் கண்ணாடி.", "correct": "சிறிய கண்ணாடி.",
             "marked": "சிறியக் கண்ணாடி", "correction": "சிறிய கண்ணாடி"},
            {"error": "பெரியப் பானை.", "correct": "பெரிய பானை.",
             "marked": "பெரியப் பானை", "correction": "பெரிய பானை"},
        ]
    },

    # Rule 124: Reduplicated words — DON'T double
    {
        "rule_id": "book_124", "book_rule": 124, "book_page": 86,
        "category": "sandhi_no_doubling", "subcategory": "reduplicated_word",
        "rule_name_ta": "அடுக்குத்தொடர் பின் ஒற்று மிகாமை",
        "examples": [
            {"error": "பாம்புப் பாம்பு என்று கத்தினான்.", "correct": "பாம்பு பாம்பு என்று கத்தினான்.",
             "marked": "பாம்புப் பாம்பு", "correction": "பாம்பு பாம்பு"},
            {"error": "பார்ப் பார் என்றான்.", "correct": "பார் பார் என்றான்.",
             "marked": "பார்ப் பார்", "correction": "பார் பார்"},
        ]
    },

    # Rule 126: After loanwords — DON'T double
    {
        "rule_id": "book_126", "book_rule": 126, "book_page": 86,
        "category": "sandhi_no_doubling", "subcategory": "loanword",
        "rule_name_ta": "வடசொல் பின் ஒற்று மிகாமை",
        "examples": [
            {"error": "தேசப் பக்தி மிகவும் முக்கியம்.", "correct": "தேச பக்தி மிகவும் முக்கியம்.",
             "marked": "தேசப் பக்தி", "correction": "தேச பக்தி"},
            {"error": "பந்தப் பாசம் விட்டான்.", "correct": "பந்த பாசம் விட்டான்.",
             "marked": "பந்தப் பாசம்", "correction": "பந்த பாசம்"},
        ]
    },

    # Rule 127: After நல்ல/தீய/அரிய — DON'T double
    {
        "rule_id": "book_127", "book_rule": 127, "book_page": 86,
        "category": "sandhi_no_doubling", "subcategory": "quality_adjective",
        "rule_name_ta": "நல்ல/தீய/அரிய பின் ஒற்று மிகாமை",
        "examples": [
            {"error": "நல்லப் பையன்.", "correct": "நல்ல பையன்.",
             "marked": "நல்லப் பையன்", "correction": "நல்ல பையன்"},
            {"error": "தீயப் பழக்கம்.", "correct": "தீய பழக்கம்.",
             "marked": "தீயப் பழக்கம்", "correction": "தீய பழக்கம்"},
            {"error": "அரியக் காட்சி.", "correct": "அரிய காட்சி.",
             "marked": "அரியக் காட்சி", "correction": "அரிய காட்சி"},
        ]
    },

    # Rule 128: After kinship terms — DON'T double
    {
        "rule_id": "book_128", "book_rule": 128, "book_page": 86,
        "category": "sandhi_no_doubling", "subcategory": "kinship_term",
        "rule_name_ta": "உறவுப்பெயர் பின் ஒற்று மிகாமை",
        "examples": [
            {"error": "தம்பிப் பார்த்தான்.", "correct": "தம்பி பார்த்தான்.",
             "marked": "தம்பிப் பார்த்தான்", "correction": "தம்பி பார்த்தான்"},
            {"error": "தங்கைக் கூப்பிட்டாள்.", "correct": "தங்கை கூப்பிட்டாள்.",
             "marked": "தங்கைக் கூப்பிட்டாள்", "correction": "தங்கை கூப்பிட்டாள்"},
        ]
    },

    # ================================================================
    # GROUP C: NUMBER AGREEMENT — Rules 5-03, 5-04, 5-05
    # ================================================================

    # Rule 5-03: ஒவ்வொரு + singular only
    {
        "rule_id": "book_5_03", "book_rule": 503, "book_page": 0,
        "category": "number_agreement", "subcategory": "ovvoru_singular",
        "rule_name_ta": "ஒவ்வொரு பின் ஒருமை மட்டுமே",
        "examples": [
            {"error": "ஒவ்வொரு வீடுகளிலும் விழா நடந்தது.", "correct": "ஒவ்வொரு வீட்டிலும் விழா நடந்தது.",
             "marked": "ஒவ்வொரு வீடுகளிலும்", "correction": "ஒவ்வொரு வீட்டிலும்"},
            {"error": "ஒவ்வொரு மாணவர்களும் பரிசு பெற்றனர்.", "correct": "ஒவ்வொரு மாணவரும் பரிசு பெற்றார்.",
             "marked": "ஒவ்வொரு மாணவர்களும்", "correction": "ஒவ்வொரு மாணவரும்"},
        ]
    },

    # Rule 5-04: எல்லா + plural only
    {
        "rule_id": "book_5_04", "book_rule": 504, "book_page": 0,
        "category": "number_agreement", "subcategory": "ellaa_plural",
        "rule_name_ta": "எல்லா பின் பன்மை மட்டுமே",
        "examples": [
            {"error": "எல்லா உறுப்பினரும் கூடினர்.", "correct": "எல்லா உறுப்பினர்களும் கூடினர்.",
             "marked": "எல்லா உறுப்பினரும்", "correction": "எல்லா உறுப்பினர்களும்"},
            {"error": "எல்லா ஆசிரியரும் வந்தனர்.", "correct": "எல்லா ஆசிரியர்களும் வந்தனர்.",
             "marked": "எல்லா ஆசிரியரும்", "correction": "எல்லா ஆசிரியர்களும்"},
        ]
    },

    # Rule 5-05: எந்த + singular only
    {
        "rule_id": "book_5_05", "book_rule": 505, "book_page": 0,
        "category": "number_agreement", "subcategory": "entha_singular",
        "rule_name_ta": "எந்த பின் ஒருமை மட்டுமே",
        "examples": [
            {"error": "எந்தப் புத்தகங்களும் எடுக்கலாம்.", "correct": "எந்தப் புத்தகமும் எடுக்கலாம்.",
             "marked": "எந்தப் புத்தகங்களும்", "correction": "எந்தப் புத்தகமும்"},
            {"error": "எந்த நாடுகளுக்கும் செல்லலாம்.", "correct": "எந்த நாட்டுக்கும் செல்லலாம்.",
             "marked": "எந்த நாடுகளுக்கும்", "correction": "எந்த நாட்டுக்கும்"},
        ]
    },

    # ================================================================
    # GROUP D: ARTICLE USAGE — Rule 53, 5-07
    # ================================================================

    # Rule 53: ஒரு vs ஓர்
    {
        "rule_id": "book_053", "book_rule": 53, "book_page": 82,
        "category": "article_usage", "subcategory": "oru_or",
        "rule_name_ta": "ஒரு/ஓர் பயன்பாடு",
        "examples": [
            {"error": "ஒரு ஆடு மேய்ந்தது.", "correct": "ஓர் ஆடு மேய்ந்தது.",
             "marked": "ஒரு ஆடு", "correction": "ஓர் ஆடு"},
            {"error": "ஓர் மரம் நின்றது.", "correct": "ஒரு மரம் நின்றது.",
             "marked": "ஓர் மரம்", "correction": "ஒரு மரம்"},
            {"error": "ஒரு ஊரில் ஒரு ராஜா இருந்தான்.", "correct": "ஓர் ஊரில் ஒரு ராஜா இருந்தான்.",
             "marked": "ஒரு ஊரில்", "correction": "ஓர் ஊரில்"},
        ]
    },

    # Rule 5-07: Don't use ஒரு/ஓர் as article before adj+noun
    {
        "rule_id": "book_5_07", "book_rule": 507, "book_page": 0,
        "category": "article_usage", "subcategory": "unnecessary_article",
        "rule_name_ta": "ஒரு/ஓர் தேவையற்ற இடங்கள்",
        "examples": [
            {"error": "ஓர் அழகான கிளியைக் கண்டேன்.", "correct": "அழகான கிளியைக் கண்டேன்.",
             "marked": "ஓர் அழகான கிளியைக்", "correction": "அழகான கிளியைக்"},
            {"error": "ஒரு நல்ல மனிதனைச் சந்தித்தேன்.", "correct": "நல்ல மனிதனைச் சந்தித்தேன்.",
             "marked": "ஒரு நல்ல மனிதனைச்", "correction": "நல்ல மனிதனைச்"},
        ]
    },

    # ================================================================
    # GROUP E: SPECIFIC WORDS — Chapter 6 (6-19, 6-20)
    # ================================================================

    # Rule 6-19: அல்லது always separate
    {
        "rule_id": "book_6_19", "book_rule": 619, "book_page": 0,
        "category": "word_separation", "subcategory": "conjunction",
        "rule_name_ta": "அல்லது எப்போதும் பிரித்து எழுதுதல்",
        "examples": [
            {"error": "வடையல்லது முறுக்கு வாங்கி வா.", "correct": "வடை அல்லது முறுக்கு வாங்கி வா.",
             "marked": "வடையல்லது", "correction": "வடை அல்லது"},
            {"error": "நீ போகிறாயாவல்லது நான் போகட்டுமா?", "correct": "நீ போகிறாயா அல்லது நான் போகட்டுமா?",
             "marked": "போகிறாயாவல்லது", "correction": "போகிறாயா அல்லது"},
        ]
    },

    # Rule 6-20: ஆனால் — separate as conjunction
    {
        "rule_id": "book_6_20", "book_rule": 620, "book_page": 0,
        "category": "specific_words", "subcategory": "conjunction",
        "rule_name_ta": "ஆனால் இணைப்புச் சொல்லாக பிரித்து எழுதுதல்",
        "examples": [
            {"error": "நேற்று மழை பெய்தது.ஆனால் குளம் நிறையவில்லை.", "correct": "நேற்று மழை பெய்தது. ஆனால் குளம் நிறையவில்லை.",
             "marked": "பெய்தது.ஆனால்", "correction": "பெய்தது. ஆனால்"},
        ]
    },

    # ================================================================
    # GROUP F: TRICKY CONTRASTS (high-value for LLM testing)
    # ================================================================

    # Contrast: சின்ன (doubles) vs சிறிய/பெரிய (don't double)
    {
        "rule_id": "book_contrast_01", "book_rule": 0, "book_page": 0,
        "category": "sandhi_doubling", "subcategory": "contrast_adjective",
        "rule_name_ta": "சின்ன vs சிறிய/பெரிய வேறுபாடு",
        "examples": [
            {"error": "சின்ன குடை.", "correct": "சின்னக்குடை.",
             "marked": "சின்ன குடை", "correction": "சின்னக்குடை"},
        ]
    },

    # Contrast: ஈறுகெட்ட (doubles) vs full negative participial (doesn't)
    {
        "rule_id": "book_contrast_02", "book_rule": 0, "book_page": 0,
        "category": "sandhi_doubling", "subcategory": "contrast_negative",
        "rule_name_ta": "ஈறுகெட்ட எதிர்மறை vs முழு எதிர்மறை வேறுபாடு",
        "examples": [
            {"error": "படா தேனீ.", "correct": "படாத் தேனீ.",
             "marked": "படா தேனீ", "correction": "படாத் தேனீ"},
            {"error": "காணா காட்சி.", "correct": "காணாக் காட்சி.",
             "marked": "காணா காட்சி", "correction": "காணாக் காட்சி"},
        ]
    },

    # Contrast: எட்டு/பத்து (double) vs other numerals (don't)
    {
        "rule_id": "book_contrast_03", "book_rule": 0, "book_page": 0,
        "category": "sandhi_no_doubling", "subcategory": "contrast_numeral",
        "rule_name_ta": "எட்டு/பத்து vs மற்ற எண்கள் வேறுபாடு",
        "examples": [
            {"error": "ஒன்றுக் கூடுவோம்.", "correct": "ஒன்று கூடுவோம்.",
             "marked": "ஒன்றுக் கூடுவோம்", "correction": "ஒன்று கூடுவோம்"},
        ]
    },
]


def build_records(data: list[dict]) -> list[dict]:
    """Convert raw data into JSONL records."""
    records = []
    seq = 0

    for rule_entry in data:
        for i, ex in enumerate(rule_entry["examples"]):
            seq += 1
            record = {
                "id": f"tn_t2_{rule_entry['rule_id']}_{i+1:02d}",
                "source": f"tamilvu_169_p{rule_entry['book_page']}" if rule_entry["book_page"] else "",
                "category": rule_entry["category"],
                "subcategory": rule_entry["subcategory"],
                "rule_id": rule_entry["rule_id"],
                "rule_name": rule_entry["rule_name_ta"],
                "book_page": rule_entry["book_page"],
                "book_rules": [rule_entry["book_rule"]] if rule_entry["book_rule"] else [],
                "error_sentence": ex["error"],
                "correct_sentence": ex["correct"],
                "marked_text": ex["marked"],
                "correction": ex["correction"],
                "error_span": [],
                "message": "",
                "short_description": "",
                "source_url": f"http://www.tamilvu.org/slet/lA100/lA100pd3.jsp?bookid=169&pno={rule_entry['book_page']}" if rule_entry["book_page"] else "",
                "origin": "book_rule",
                "is_error_example": True,
                "uses_postag": False,
                "postags": [],
                "example_type": "error",
                "error_type": _get_error_type(rule_entry["category"]),
                "difficulty": "medium",
                "needs_review": True,
            }
            records.append(record)

    return records


def _get_error_type(category: str) -> str:
    """Map category to error type."""
    return {
        "sandhi_doubling": "missing_vallinam_doubling",
        "sandhi_no_doubling": "unnecessary_vallinam_doubling",
        "word_joining": "incorrect_separation",
        "word_separation": "incorrect_joining",
        "noun_postposition": "noun_postposition_spacing",
        "verb_auxiliary": "verb_auxiliary_separation",
        "number_agreement": "number_agreement_error",
        "article_usage": "article_form_error",
        "case_marker_sandhi": "case_marker_doubling",
        "classical_sandhi": "classical_sandhi_error",
        "specific_words": "specific_word_convention",
    }.get(category, "")


def main():
    project_dir = Path(__file__).resolve().parent.parent
    output_path = project_dir / "dataset" / "tier2_book_rules.jsonl"

    records = build_records(TIER2_DATA)

    with open(output_path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    # Summary
    from collections import Counter
    cats = Counter(r["category"] for r in records)
    rules = set(r["rule_id"] for r in records)

    print(f"Tier 2 generation complete.")
    print(f"Total examples: {len(records)}")
    print(f"Unique rules: {len(rules)}")
    print(f"\nBy category:")
    for cat, count in cats.most_common():
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    main()
