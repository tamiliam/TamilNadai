"""
evaluate.py — Step 6: Evaluation script for TamilNadai benchmark.

Scores a model's Tamil grammar correction output against the gold standard.

Metrics:
  Detection:
    - Precision: Of sentences the model flagged as errors, how many truly are?
    - Recall: Of actual error sentences, how many did the model flag?
    - F1: Harmonic mean of precision and recall.

  Correction:
    - Exact match accuracy: Of correctly detected errors, how many corrections
      match the gold standard exactly?

  False positive rate:
    - Of correct sentences (Tier 3), how many did the model incorrectly flag?

Input format (model predictions JSONL):
  {"id": "tn_0001", "model_output": "corrected sentence or empty string"}

  - If model_output == input sentence (or empty): model says "no error"
  - If model_output != input sentence: model says "error, here's the fix"

Usage:
    python Tamil_Nadai/tools/evaluate.py --gold dataset/tamilnadai_v1.jsonl --predictions predictions.jsonl

    Or use as a library:
        from evaluate import evaluate_predictions
"""

import json
import sys
import argparse
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")


def normalize(text: str) -> str:
    """Normalize whitespace for comparison."""
    return " ".join(text.strip().split())


def load_jsonl(path: Path) -> list[dict]:
    """Load a JSONL file."""
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def evaluate_predictions(gold: list[dict], predictions: dict[str, str]) -> dict:
    """
    Evaluate model predictions against gold standard.

    Args:
        gold: List of gold standard records from tamilnadai_v1.jsonl
        predictions: Dict mapping record ID -> model's corrected sentence.
                     Empty string or matching input = model says "no error".

    Returns:
        Dict with detection and correction metrics.
    """
    # Counters
    tp = 0  # True positive: model correctly flags an error
    fp = 0  # False positive: model flags a correct sentence as error
    fn = 0  # False negative: model misses an actual error
    tn = 0  # True negative: model correctly says "no error" on correct sentence

    exact_match = 0  # Correction matches gold exactly
    correction_attempted = 0  # Model flagged AND gold is error

    category_tp = Counter()
    category_fn = Counter()
    category_exact = Counter()

    for record in gold:
        rid = record["id"]
        is_error = record.get("is_error_example", True)
        category = record.get("category", "unknown")

        # Determine the input sentence the model saw
        if is_error:
            input_sentence = record["error_sentence"]
            gold_correction = record["correct_sentence"]
        else:
            input_sentence = record["correct_sentence"]
            gold_correction = ""  # No correction needed

        # Get model prediction
        model_output = predictions.get(rid, "")

        # Determine if model flagged this as an error
        model_says_error = bool(model_output) and normalize(model_output) != normalize(input_sentence)

        if is_error:
            if model_says_error:
                tp += 1
                category_tp[category] += 1
                correction_attempted += 1
                if normalize(model_output) == normalize(gold_correction):
                    exact_match += 1
                    category_exact[category] += 1
            else:
                fn += 1
                category_fn[category] += 1
        else:
            if model_says_error:
                fp += 1
            else:
                tn += 1

    # Calculate metrics
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    correction_accuracy = exact_match / correction_attempted if correction_attempted > 0 else 0.0
    false_positive_rate = fp / (fp + tn) if (fp + tn) > 0 else 0.0

    # Per-category detection recall
    all_cats = set(list(category_tp.keys()) + list(category_fn.keys()))
    per_category = {}
    for cat in sorted(all_cats):
        cat_total = category_tp[cat] + category_fn[cat]
        cat_recall = category_tp[cat] / cat_total if cat_total > 0 else 0.0
        cat_exact = category_exact[cat] / category_tp[cat] if category_tp[cat] > 0 else 0.0
        per_category[cat] = {
            "total": cat_total,
            "detected": category_tp[cat],
            "recall": round(cat_recall, 3),
            "exact_match": category_exact[cat],
            "correction_accuracy": round(cat_exact, 3),
        }

    return {
        "detection": {
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "true_negatives": tn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
        },
        "correction": {
            "attempted": correction_attempted,
            "exact_match": exact_match,
            "accuracy": round(correction_accuracy, 4),
        },
        "false_positive_rate": round(false_positive_rate, 4),
        "total_evaluated": len(gold),
        "total_predictions": len(predictions),
        "per_category": per_category,
    }


def print_results(results: dict):
    """Pretty-print evaluation results."""
    det = results["detection"]
    cor = results["correction"]

    print(f"\n{'='*60}")
    print(f"TAMILNADAI EVALUATION RESULTS")
    print(f"{'='*60}")

    print(f"\nTotal evaluated: {results['total_evaluated']}")
    print(f"Total predictions: {results['total_predictions']}")

    print(f"\n--- Detection ---")
    print(f"  Precision:  {det['precision']:.2%}")
    print(f"  Recall:     {det['recall']:.2%}")
    print(f"  F1:         {det['f1']:.2%}")
    print(f"  TP: {det['true_positives']}  FP: {det['false_positives']}  FN: {det['false_negatives']}  TN: {det['true_negatives']}")

    print(f"\n--- Correction ---")
    print(f"  Exact match: {cor['exact_match']} / {cor['attempted']}")
    print(f"  Accuracy:    {cor['accuracy']:.2%}")

    print(f"\n--- False Positive Rate ---")
    print(f"  FPR: {results['false_positive_rate']:.2%}")

    if results["per_category"]:
        print(f"\n--- Per Category ---")
        print(f"  {'Category':<25} {'Total':>5} {'Det':>4} {'Recall':>7} {'ExMatch':>7} {'CorAcc':>7}")
        print(f"  {'-'*25} {'-'*5} {'-'*4} {'-'*7} {'-'*7} {'-'*7}")
        for cat, stats in sorted(results["per_category"].items()):
            print(f"  {cat:<25} {stats['total']:>5} {stats['detected']:>4} {stats['recall']:>7.1%} {stats['exact_match']:>7} {stats['correction_accuracy']:>7.1%}")


def main():
    parser = argparse.ArgumentParser(description="Evaluate Tamil grammar corrections against TamilNadai benchmark.")
    parser.add_argument("--gold", type=str, required=True, help="Path to gold standard JSONL (tamilnadai_v1.jsonl)")
    parser.add_argument("--predictions", type=str, required=True, help="Path to model predictions JSONL")
    parser.add_argument("--split", type=str, default=None, help="Evaluate only this split (test/validation)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    gold = load_jsonl(Path(args.gold))

    if args.split:
        gold = [r for r in gold if r.get("split") == args.split]
        print(f"Filtering to split={args.split}: {len(gold)} records")

    pred_records = load_jsonl(Path(args.predictions))
    predictions = {r["id"]: r.get("model_output", "") for r in pred_records}

    results = evaluate_predictions(gold, predictions)

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print_results(results)


if __name__ == "__main__":
    main()
