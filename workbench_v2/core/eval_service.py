"""LLM evaluation service — send Tamil sentences to models, score responses."""

import json
import logging
import urllib.request
import urllib.error

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

EVAL_PROMPT = (
    "You are a Tamil language expert. The following Tamil sentence may contain "
    "a writing convention error (such as incorrect word joining, missing sandhi "
    "doubling, or wrong usage). If there is an error, return ONLY the corrected "
    "sentence. If the sentence is already correct, return it unchanged. "
    "Return ONLY the Tamil sentence — no explanation, no quotes, no other text.\n\n"
    "Sentence: {sentence}"
)


def _call_gemini(sentence: str) -> str | None:
    """Call Gemini 2.0 Flash via the google-generativeai SDK."""
    try:
        import google.generativeai as genai
    except ImportError:
        logger.error("google-generativeai not installed")
        return None

    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return None

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = EVAL_PROMPT.format(sentence=sentence)

    try:
        response = model.generate_content(prompt)
        return response.text.strip().strip('"').strip("'").strip()
    except Exception as e:
        logger.error(f"Gemini eval error: {e}")
        return None


def _call_claude(sentence: str) -> str | None:
    """Call Claude via the Anthropic Messages API (HTTP, no SDK)."""
    api_key = settings.ANTHROPIC_API_KEY
    if not api_key:
        return None

    prompt = EVAL_PROMPT.format(sentence=sentence)
    payload = json.dumps({
        "model": "claude-sonnet-4-5-20250929",
        "max_tokens": 256,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            text = data.get("content", [{}])[0].get("text", "")
            return text.strip().strip('"').strip("'").strip()
    except Exception as e:
        logger.error(f"Claude eval error: {e}")
        return None


def _call_openai(sentence: str) -> str | None:
    """Call GPT-4o via the OpenAI Chat Completions API (HTTP, no SDK)."""
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        return None

    prompt = EVAL_PROMPT.format(sentence=sentence)
    payload = json.dumps({
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 256,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            text = data["choices"][0]["message"]["content"]
            return text.strip().strip('"').strip("'").strip()
    except Exception as e:
        logger.error(f"OpenAI eval error: {e}")
        return None


MODEL_CALLERS = {
    "gemini-2.0-flash": _call_gemini,
    "claude-sonnet-4-5": _call_claude,
    "gpt-4o": _call_openai,
}


def get_available_models() -> list[dict]:
    """Return list of models with availability status."""
    return [
        {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash", "available": bool(settings.GEMINI_API_KEY)},
        {"id": "claude-sonnet-4-5", "name": "Claude Sonnet 4.5", "available": bool(settings.ANTHROPIC_API_KEY)},
        {"id": "gpt-4o", "name": "GPT-4o", "available": bool(settings.OPENAI_API_KEY)},
    ]


def _normalize(text: str) -> str:
    """Normalize Tamil text for comparison — strip whitespace and punctuation."""
    import unicodedata
    text = unicodedata.normalize("NFC", text.strip())
    # Remove trailing punctuation (period, question mark, etc.)
    text = text.rstrip(".")
    return text


def score_result(sentence_obj, model_response: str) -> str:
    """Score a single model response against the gold standard.

    Args:
        sentence_obj: Sentence instance (has .sentence, .sentence_type, .rule)
        model_response: The LLM's returned text

    Returns:
        One of: true_positive, partial, false_negative, true_negative, false_positive, error
    """
    if not model_response:
        return "error"

    original = _normalize(sentence_obj.sentence)
    response = _normalize(model_response)

    if sentence_obj.sentence_type == "wrong":
        # For wrong sentences, check if the model corrected it
        if response == original:
            # Model returned it unchanged — missed the error
            return "false_negative"

        # Model made a change — check if it matches any correct sentence for this rule
        correct_sentences = list(
            sentence_obj.rule.sentences
            .filter(sentence_type="correct")
            .values_list("sentence", flat=True)
        )
        for correct in correct_sentences:
            if _normalize(correct) == response:
                return "true_positive"

        # Model changed it but not to the expected correction
        return "partial"

    else:
        # For correct sentences, check if model left it unchanged
        if response == original:
            return "true_negative"
        else:
            return "false_positive"


def run_evaluation(eval_run, sentences):
    """Execute an evaluation run against a list of sentences.

    Designed to run in a background thread. Updates eval_run.status
    to 'running', 'completed', or 'failed' as it progresses.

    Args:
        eval_run: EvalRun instance (already saved with model_name etc.)
        sentences: QuerySet of Sentence objects to test
    """
    from .models import EvalResult

    caller = MODEL_CALLERS.get(eval_run.model_name)
    if not caller:
        logger.error(f"No caller for model: {eval_run.model_name}")
        eval_run.status = "failed"
        eval_run.save()
        return

    try:
        eval_run.status = "running"
        eval_run.started_at = timezone.now()
        eval_run.total_sentences = len(sentences)
        eval_run.save()

        results = []
        for sentence_obj in sentences:
            response = caller(sentence_obj.sentence)
            outcome = score_result(sentence_obj, response)
            results.append(EvalResult(
                eval_run=eval_run,
                sentence=sentence_obj,
                model_response=response or "",
                outcome=outcome,
            ))

        EvalResult.objects.bulk_create(results)

        # Calculate aggregate metrics
        total = len(results)
        if total == 0:
            eval_run.status = "completed"
            eval_run.completed_at = timezone.now()
            eval_run.save()
            return

        wrong_results = [r for r in results if r.sentence.sentence_type == "wrong"]
        correct_results = [r for r in results if r.sentence.sentence_type == "correct"]

        # Detection rate: % of wrong sentences where model made any change
        if wrong_results:
            detected = sum(1 for r in wrong_results if r.outcome != "false_negative")
            eval_run.detection_rate = round(detected / len(wrong_results) * 100, 1)
        else:
            eval_run.detection_rate = 0

        # Correction accuracy: % of wrong sentences fixed to exact correct form
        if wrong_results:
            correct_fixes = sum(1 for r in wrong_results if r.outcome == "true_positive")
            eval_run.correction_accuracy = round(correct_fixes / len(wrong_results) * 100, 1)
        else:
            eval_run.correction_accuracy = 0

        # False positive rate: % of correct sentences wrongly changed
        if correct_results:
            false_pos = sum(1 for r in correct_results if r.outcome == "false_positive")
            eval_run.false_positive_rate = round(false_pos / len(correct_results) * 100, 1)
        else:
            eval_run.false_positive_rate = 0

        eval_run.status = "completed"
        eval_run.completed_at = timezone.now()
        eval_run.save()

    except Exception as e:
        logger.error(f"Evaluation run {eval_run.id} failed: {e}")
        eval_run.status = "failed"
        eval_run.completed_at = timezone.now()
        eval_run.save()
