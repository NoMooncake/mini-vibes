# src/cost_sensitive_eval.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

from .run_experiments import (
    load_corpus,
    predict_emotion_only,
    predict_text_lexicon_only,
    predict_hybrid,
    LABELS,
)

# ------------------------------------------------------------
# Cost matrix (example)
# Tune these to reflect your risk preference.
#
# Interpretation:
# - Missing an alert entirely (alert -> safe) is most costly.
# - Downgrading alert to watch still costly.
# - False alerts cost more than false watch.
# ------------------------------------------------------------
COSTS: Dict[Tuple[str, str], float] = {
    # False negatives (missed detections)
    ("alert", "safe"): 10.0,
    ("alert", "watch"): 6.0,
    ("watch", "safe"): 3.0,

    # False positives (over-flagging)
    ("safe", "watch"): 1.0,
    ("safe", "alert"): 5.0,
    ("watch", "alert"): 2.0,
}


def cost_of(y_true: str, y_pred: str) -> float:
    """0 if correct; otherwise look up cost; default 0 if unspecified."""
    if y_true == y_pred:
        return 0.0
    return COSTS.get((y_true, y_pred), 0.0)


def predict(exp_name: str, text: str, emotion_hint: str) -> str:
    if exp_name == "A_emotion_only":
        return predict_emotion_only(emotion_hint)
    if exp_name == "B_text_only":
        return predict_text_lexicon_only(text, emotion_hint)
    if exp_name == "C_hybrid":
        return predict_hybrid(text, emotion_hint)
    raise ValueError(f"Unknown experiment: {exp_name}")


def evaluate_cost(exp_name: str, rows: List[Dict[str, str]]) -> Dict:
    total_cost = 0.0
    used = 0

    # Optional breakdowns
    by_true: Dict[str, float] = {c: 0.0 for c in LABELS}
    by_pair: Dict[str, float] = {}  # e.g., "alert->safe": 20.0

    for r in rows:
        text = r["text"]
        emo = r["emotion_hint"]
        y_true = r["risk_label"]

        if y_true not in LABELS or not text:
            continue

        y_pred = predict(exp_name, text, emo)
        c = cost_of(y_true, y_pred)

        total_cost += c
        used += 1

        by_true[y_true] += c
        if y_true != y_pred:
            key = f"{y_true}->{y_pred}"
            by_pair[key] = by_pair.get(key, 0.0) + c

    avg_cost = total_cost / used if used else 0.0

    return {
        "name": exp_name,
        "n": used,
        "total_cost": total_cost,
        "avg_cost_per_entry": avg_cost,
        "by_true_label_cost": by_true,
        "by_error_pair_cost": dict(sorted(by_pair.items(), key=lambda kv: -kv[1])),
        "cost_matrix": {f"{k[0]}->{k[1]}": v for k, v in COSTS.items()},
    }


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    corpus_path = repo_root / "data" / "youth_corpus.csv"
    out_dir = repo_root / "results"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = load_corpus(corpus_path)

    experiments = ["A_emotion_only", "B_text_only", "C_hybrid"]
    results = [evaluate_cost(name, rows) for name in experiments]

    out_path = out_dir / "cost_metrics.json"
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Cost-sensitive summary:")
    for r in results:
        print(
            f"- {r['name']}: n={r['n']}  total_cost={r['total_cost']:.1f}  "
            f"avg_cost={r['avg_cost_per_entry']:.2f}"
        )

    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
