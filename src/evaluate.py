# src/evaluate.py
from __future__ import annotations

import csv
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Tuple

from .analyzer import analyze_checkin
from .engine import assess_risk


ALLOWED = {"safe", "watch", "alert"}


def load_corpus(path: Path) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        required = {"text", "emotion_hint", "risk_label", "reason_tag"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV missing columns: {sorted(missing)}")

        for r in reader:
            rows.append({
                "text": (r.get("text") or "").strip(),
                "emotion_hint": (r.get("emotion_hint") or "").strip(),
                "risk_label": (r.get("risk_label") or "").strip().lower(),
                "reason_tag": (r.get("reason_tag") or "").strip(),
            })
    return rows


def confusion_matrix(labels: List[str], preds: List[str]) -> Dict[Tuple[str, str], int]:
    cm: Dict[Tuple[str, str], int] = {}
    for y, p in zip(labels, preds):
        cm[(y, p)] = cm.get((y, p), 0) + 1
    return cm


def print_cm(cm: Dict[Tuple[str, str], int]) -> None:
    order = ["safe", "watch", "alert"]
    print("\nConfusion matrix (rows=true, cols=pred):")
    header = "true\\pred | " + " | ".join(f"{c:>5}" for c in order)
    print(header)
    print("-" * len(header))
    for r in order:
        row = []
        for c in order:
            row.append(f"{cm.get((r, c), 0):>5}")
        print(f"{r:>8} | " + " | ".join(row))


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    corpus_path = repo_root / "data" / "youth_corpus.csv"

    rows = load_corpus(corpus_path)

    y_true: List[str] = []
    y_pred: List[str] = []
    bad_rows = 0

    # For now: no history; pure single-entry evaluation baseline
    for i, r in enumerate(rows, start=1):
        text = r["text"]
        emo = r["emotion_hint"]
        label = r["risk_label"]

        if not text or label not in ALLOWED:
            bad_rows += 1
            continue

        analysis = analyze_checkin(emo, text)
        alert = assess_risk(analysis, recent_scores=[])

        y_true.append(label)
        y_pred.append(alert.risk_level)

    total = len(y_true)
    correct = sum(1 for a, b in zip(y_true, y_pred) if a == b)
    acc = correct / total if total else 0.0

    print(f"Loaded: {len(rows)} rows | Used: {total} | Skipped: {bad_rows}")
    print(f"Accuracy: {acc:.3f} ({correct}/{total})")

    cm = confusion_matrix(y_true, y_pred)
    print_cm(cm)

    # Show a few mistakes for iteration
    print("\nSample mistakes (up to 10):")
    shown = 0
    for r, yt, yp in zip(rows, y_true, y_pred):
        if yt != yp:
            shown += 1
            print("-" * 60)
            print(f"TRUE={yt}  PRED={yp}  emotion_hint='{r['emotion_hint']}'  tag='{r['reason_tag']}'")
            print(f"text: {r['text']}")
            if shown >= 10:
                break

    if shown == 0:
        print("No mistakes in this run (small dataset / lucky baseline).")


if __name__ == "__main__":
    main()
