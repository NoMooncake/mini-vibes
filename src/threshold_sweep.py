# src/threshold_sweep.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

from .run_experiments import load_corpus, LABELS
from .analyzer import analyze_checkin
from .engine import assess_risk

COSTS: Dict[Tuple[str, str], float] = {
    ("alert", "safe"): 10.0,
    ("alert", "watch"): 6.0,
    ("watch", "safe"): 3.0,
    ("safe", "watch"): 1.0,
    ("safe", "alert"): 5.0,
    ("watch", "alert"): 2.0,
}

def cost_of(y_true: str, y_pred: str) -> float:
    if y_true == y_pred:
        return 0.0
    return COSTS.get((y_true, y_pred), 0.0)

def safe_div(a: float, b: float) -> float:
    return a / b if b else 0.0

def confusion_counts(y_true: List[str], y_pred: List[str]) -> Dict[Tuple[str, str], int]:
    cm: Dict[Tuple[str, str], int] = {}
    for t, p in zip(y_true, y_pred):
        cm[(t, p)] = cm.get((t, p), 0) + 1
    return cm

def recall_for(label: str, cm: Dict[Tuple[str, str], int]) -> float:
    # recall = TP / (TP + FN)
    tp = cm.get((label, label), 0)
    fn = sum(cm.get((label, p), 0) for p in LABELS if p != label)
    return safe_div(tp, tp + fn)

def sweep(rows: List[Dict[str, str]], thresholds: List[float], alert_threshold: float = -0.75) -> List[Dict]:
    out: List[Dict] = []
    for thr in thresholds:
        y_true: List[str] = []
        y_pred: List[str] = []
        costs: List[float] = []

        for r in rows:
            text = r["text"]
            emo = r["emotion_hint"]
            yt = r["risk_label"]

            if yt not in LABELS or not text:
                continue

            analysis = analyze_checkin(emo, text)
            alert = assess_risk(
                analysis,
                recent_scores=[],
                watch_threshold=thr,
                alert_threshold=alert_threshold,
            )
            yp = alert.risk_level

            y_true.append(yt)
            y_pred.append(yp)
            costs.append(cost_of(yt, yp))

        cm = confusion_counts(y_true, y_pred)
        total_cost = sum(costs)
        avg_cost = safe_div(total_cost, len(costs))

        out.append({
            "watch_threshold": thr,
            "n": len(y_true),
            "watch_recall": recall_for("watch", cm),
            "alert_recall": recall_for("alert", cm),
            "total_cost": total_cost,
            "avg_cost": avg_cost,
            "confusion_matrix": {f"{a}->{b}": cm.get((a, b), 0) for a in LABELS for b in LABELS},
        })
    return out

def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    corpus_path = repo_root / "data" / "youth_corpus.csv"
    out_dir = repo_root / "results"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = load_corpus(corpus_path)

    # Sweep from more aggressive (higher threshold) to more conservative (lower threshold)
    thresholds = [-0.20, -0.30, -0.35, -0.40, -0.45, -0.50, -0.55, -0.60]

    results = sweep(rows, thresholds, alert_threshold=-0.75)

    # Save for plotting / reporting
    out_path = out_dir / "threshold_sweep.json"
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Threshold sweep summary (Hybrid C; varying watch_threshold):")
    for r in results:
        print(
            f"- thr={r['watch_threshold']:.2f} | "
            f"watch_recall={r['watch_recall']:.3f} | alert_recall={r['alert_recall']:.3f} | "
            f"total_cost={r['total_cost']:.1f} | avg_cost={r['avg_cost']:.2f}"
        )

    print(f"\nSaved: {out_path}")

if __name__ == "__main__":
    main()
