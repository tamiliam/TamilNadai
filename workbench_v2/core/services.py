"""AI sentence generation service using Gemini Flash."""

import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def suggest_sentence(rule, sentence_type: str) -> str | None:
    """Generate ONE short Tamil sentence suggestion for a rule.

    Args:
        rule: Rule instance
        sentence_type: "correct" or "wrong"

    Returns:
        A single sentence string, or None if generation fails.
    """
    try:
        import google.generativeai as genai
    except ImportError:
        logger.error("google-generativeai package not installed")
        return None

    api_key = settings.GEMINI_API_KEY
    if not api_key:
        logger.error("GEMINI_API_KEY not configured")
        return None

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    existing = list(
        rule.sentences.filter(sentence_type=sentence_type)
        .values_list("sentence", flat=True)[:10]
    )

    examples = []
    if rule.example_1:
        examples.append(rule.example_1)
    if rule.example_2:
        examples.append(rule.example_2)

    if sentence_type == "correct":
        instruction = "Generate ONE short Tamil sentence that CORRECTLY follows this rule."
    else:
        instruction = "Generate ONE short Tamil sentence that VIOLATES this rule (shows the common mistake)."

    prompt = f"""You are a Tamil language expert specialising in Tamil writing standards (தமிழ் நடை).

Rule: {rule.title}
{f"Subtitle: {rule.subtitle}" if rule.subtitle else ""}
Description: {rule.description}
Examples from source: {', '.join(examples) if examples else 'None'}
Existing sentences: {json.dumps(existing, ensure_ascii=False) if existing else 'None'}

{instruction}

IMPORTANT:
- Must be a COMPLETE sentence (subject + verb), not a word or phrase
- Keep it SHORT — under 10 words
- Do NOT repeat any existing sentence
- Return ONLY the Tamil sentence, nothing else — no quotes, no explanation
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip().strip('"').strip("'").strip()
        if text:
            return text
        return None
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return None
