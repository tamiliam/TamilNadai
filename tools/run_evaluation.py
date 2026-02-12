"""
run_evaluation.py — End-to-end LLM evaluation runner for TamilNadai benchmark.

Feeds Tamil sentences to an LLM, collects its grammar corrections, and scores
the results using evaluate.py.

Supported models:
  - OpenAI: gpt-4o, gpt-4o-mini
  - Anthropic: claude-sonnet-4-5-20250929, claude-haiku-4-5-20251001
  - Google: gemini-2.0-flash (via google-genai)

Usage:
    python tools/run_evaluation.py --model gpt-4o-mini --split test
    python tools/run_evaluation.py --model claude-sonnet-4-5-20250929 --split test
    python tools/run_evaluation.py --model gemini-2.0-flash --split test

Output:
    - predictions saved to results/{model}_{timestamp}.jsonl
    - scorecard printed to stdout and saved to results/{model}_{timestamp}_score.json
"""

import json
import sys
import os
import time
import argparse
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = PROJECT_DIR / "dataset" / "tamilnadai_v1.jsonl"
RESULTS_DIR = PROJECT_DIR / "results"

# Import the evaluation function
sys.path.insert(0, str(PROJECT_DIR / "tools"))
from evaluate import evaluate_predictions, print_results


# --- System prompt for all models ---
SYSTEM_PROMPT = """You are a Tamil grammar expert specializing in word joining and separation rules
(சொற்களை எழுதும் முறை) as defined by the Tamil Virtual University style guide.

Your task: Given a Tamil sentence, check if there is a grammar error related to:
- Word joining vs separation (சேர்த்து / பிரித்து எழுதல்)
- Sandhi rules (சந்தி — consonant doubling when words join)
- Suffix attachment (விகுதி இணைப்பு)

Rules:
- If the sentence has a grammar error in word joining/separation, return ONLY the corrected sentence.
- If the sentence is grammatically correct, return ONLY the original sentence unchanged.
- Return nothing else — no explanation, no metadata, just the sentence."""

USER_PROMPT_TEMPLATE = """Check this Tamil sentence for word joining/separation errors and return the corrected version (or the original if correct):

{sentence}"""


def load_dataset(split: str | None = None) -> list[dict]:
    """Load the gold standard dataset."""
    records = []
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            if split and rec.get("split") != split:
                continue
            records.append(rec)
    return records


def get_input_sentence(record: dict) -> str:
    """Get the sentence to feed to the model."""
    if record.get("is_error_example", True):
        return record["error_sentence"]
    else:
        return record["correct_sentence"]


# --- Provider implementations ---

def query_openai(sentence: str, model: str, api_key: str) -> str:
    """Query OpenAI API."""
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(sentence=sentence)},
        ],
        temperature=0.0,
        max_tokens=500,
    )
    return response.choices[0].message.content.strip()


def query_anthropic(sentence: str, model: str, api_key: str) -> str:
    """Query Anthropic API."""
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(sentence=sentence)},
        ],
        temperature=0.0,
    )
    return response.content[0].text.strip()


def query_google(sentence: str, model: str, api_key: str) -> str:
    """Query Google Generative AI API."""
    from google import genai
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=f"{SYSTEM_PROMPT}\n\n{USER_PROMPT_TEMPLATE.format(sentence=sentence)}",
    )
    return response.text.strip()


# --- Model routing ---

MODEL_PROVIDERS = {
    "gpt-4o": ("openai", "OPENAI_API_KEY"),
    "gpt-4o-mini": ("openai", "OPENAI_API_KEY"),
    "claude-sonnet-4-5-20250929": ("anthropic", "ANTHROPIC_API_KEY"),
    "claude-haiku-4-5-20251001": ("anthropic", "ANTHROPIC_API_KEY"),
    "gemini-2.0-flash": ("google", "GOOGLE_API_KEY"),
    "gemini-2.0-flash-lite": ("google", "GOOGLE_API_KEY"),
}

QUERY_FUNCTIONS = {
    "openai": query_openai,
    "anthropic": query_anthropic,
    "google": query_google,
}


def run_evaluation(
    model: str,
    split: str | None = None,
    api_key: str | None = None,
    limit: int | None = None,
    delay: float = 0.5,
) -> tuple[dict, Path]:
    """Run end-to-end evaluation.

    Args:
        model: Model identifier (e.g. "gpt-4o-mini").
        split: Dataset split to evaluate ("test", "validation", or None for all).
        api_key: API key. Falls back to env variable.
        limit: Max number of examples to evaluate (for testing).
        delay: Seconds between API calls (rate limiting).

    Returns:
        Tuple of (results dict, predictions file path).
    """
    # Resolve provider and API key
    if model not in MODEL_PROVIDERS:
        raise ValueError(
            f"Unknown model: {model}. "
            f"Supported: {', '.join(MODEL_PROVIDERS.keys())}"
        )

    provider, env_key = MODEL_PROVIDERS[model]
    if not api_key:
        api_key = os.environ.get(env_key, "")
    if not api_key:
        # Try .env file
        env_path = PROJECT_DIR / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith(f"{env_key}="):
                    api_key = line.split("=", 1)[1].strip().strip('"')
                    break
    if not api_key:
        raise ValueError(f"No API key found. Set {env_key} env variable or pass --api-key.")

    query_fn = QUERY_FUNCTIONS[provider]

    # Load dataset
    gold = load_dataset(split)
    if limit:
        gold = gold[:limit]

    print(f"Model: {model} ({provider})")
    print(f"Split: {split or 'all'}")
    print(f"Examples: {len(gold)}")
    print()

    # Prepare output
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_short = model.replace("/", "-").replace(".", "-")
    pred_path = RESULTS_DIR / f"{model_short}_{timestamp}.jsonl"
    score_path = RESULTS_DIR / f"{model_short}_{timestamp}_score.json"

    # Run queries
    predictions = {}
    errors = 0
    start_time = time.time()

    with open(pred_path, "w", encoding="utf-8") as f:
        for i, record in enumerate(gold):
            rid = record["id"]
            sentence = get_input_sentence(record)

            try:
                output = query_fn(sentence, model, api_key)
                predictions[rid] = output
                f.write(json.dumps({"id": rid, "model_output": output}, ensure_ascii=False) + "\n")
                f.flush()

                # Progress
                if (i + 1) % 10 == 0:
                    elapsed = time.time() - start_time
                    rate = (i + 1) / elapsed
                    eta = (len(gold) - i - 1) / rate if rate > 0 else 0
                    print(f"  [{i+1}/{len(gold)}] {rate:.1f} examples/sec, ETA: {eta:.0f}s")

            except Exception as e:
                print(f"  ERROR on {rid}: {e}")
                predictions[rid] = ""
                errors += 1

            if delay > 0 and i < len(gold) - 1:
                time.sleep(delay)

    elapsed = time.time() - start_time
    print(f"\nDone in {elapsed:.1f}s ({errors} errors)")
    print(f"Predictions saved to: {pred_path}")

    # Evaluate
    results = evaluate_predictions(gold, predictions)
    results["metadata"] = {
        "model": model,
        "provider": provider,
        "split": split or "all",
        "total_examples": len(gold),
        "errors": errors,
        "elapsed_seconds": round(elapsed, 1),
        "timestamp": timestamp,
    }

    # Save scorecard
    with open(score_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Scorecard saved to: {score_path}")

    # Print results
    print_results(results)

    return results, pred_path


def main():
    parser = argparse.ArgumentParser(
        description="Run LLM evaluation against TamilNadai benchmark."
    )
    parser.add_argument(
        "--model", type=str, required=True,
        help=f"Model to evaluate. Options: {', '.join(MODEL_PROVIDERS.keys())}",
    )
    parser.add_argument(
        "--split", type=str, default="test",
        help="Dataset split to evaluate (test/validation/all). Default: test",
    )
    parser.add_argument(
        "--api-key", type=str, default=None,
        help="API key (falls back to env variable).",
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Max number of examples (for testing).",
    )
    parser.add_argument(
        "--delay", type=float, default=0.5,
        help="Seconds between API calls. Default: 0.5",
    )
    args = parser.parse_args()

    split = None if args.split == "all" else args.split

    run_evaluation(
        model=args.model,
        split=split,
        api_key=args.api_key,
        limit=args.limit,
        delay=args.delay,
    )


if __name__ == "__main__":
    main()
