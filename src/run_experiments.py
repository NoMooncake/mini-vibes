# src/run_experiments.py
from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt

from .analyzer import analyze_checkin
from .engine import assess_risk


LABELS = ["safe", "watch", "alert"]
ALLOWED = set(LABELS)


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


def cm_counts(y_true: List[str], y_pred: List[str]) -> Dict[Tuple[str, str], int]:
    cm: Dict[Tuple[str, str], int] = {}
    for t, p in zip(y_true, y_pred):
        cm[(t, p)] = cm.get((t, p), 0) + 1
    return cm


def cm_matrix(cm: Dict[Tuple[str, str], int]) -> List[List[int]]:
    return [[cm.get((r, c), 0) for c in LABELS] for r in LABELS]


def safe_div(a: float, b: float) -> float:
    return a / b if b != 0 else 0.0


def prf_from_cm(mat: List[List[int]]) -> Dict[str, Dict[str, float]]:
    # mat rows=true, cols=pred
    out: Dict[str, Dict[str, float]] = {}
    for i, cls in enumerate(LABELS):
        tp = mat[i][i]
        fp = sum(mat[r][i] for r in range(len(LABELS)) if r != i)
        fn = sum(mat[i][c] for c in range(len(LABELS)) if c != i)
        precision = safe_div(tp, tp + fp)
        recall = safe_div(tp, tp + fn)
        f1 = safe_div(2 * precision * recall, precision + recall) if (precision + recall) else 0.0
        out[cls] = {"precision": precision, "recall": recall, "f1": f1}
    return out


def macro_f1(prf: Dict[str, Dict[str, float]]) -> float:
    return sum(prf[c]["f1"] for c in LABELS) / len(LABELS)


def accuracy(y_true: List[str], y_pred: List[str]) -> float:
    correct = sum(1 for a, b in zip(y_true, y_pred) if a == b)
    return safe_div(correct, len(y_true))


# -------------------------
# Experiment baselines
# -------------------------

def predict_emotion_only(emotion_hint: str) -> str:
    """
    Baseline A: use only emotion selection (no text).
    Very conservative mapping (tuneable).
    """
    e = (emotion_hint or "").strip().lower()
    if e in {"sad", "angry", "anxious", "stressed", "numb"}:
        return "watch"
    if e in {"tired"}:
        return "safe"
    return "safe"


def predict_text_lexicon_only(text: str, emotion_hint: str) -> str:
    """
    Baseline B: ignore selected emotion, analyze text only.
    We feed empty emotion into analyzer to reduce dependence on emotion base.
    """
    a = analyze_checkin("", text)
    r = assess_risk(a, recent_scores=[])
    return r.risk_level


def predict_hybrid(text: str, emotion_hint: str) -> str:
    """
    Baseline C: emotion + text + explainable rules (your main system).
    """
    a = analyze_checkin(emotion_hint, text)
    r = assess_risk(a, recent_scores=[])
    return r.risk_level


def run_experiment(name: str, rows: List[Dict[str, str]]) -> Dict:
    y_true: List[str] = []
    y_pred: List[str] = []
    used_rows: List[Dict[str, str]] = []

    for r in rows:
        text = r["text"]
        emo = r["emotion_hint"]
        label = r["risk_label"]

        if not text or label not in ALLOWED:
            continue

        if name == "A_emotion_only":
            pred = predict_emotion_only(emo)
        elif name == "B_text_only":
            pred = predict_text_lexicon_only(text, emo)
        elif name == "C_hybrid":
            pred = predict_hybrid(text, emo)
        else:
            raise ValueError(f"Unknown experiment: {name}")

        y_true.append(label)
        y_pred.append(pred)
        used_rows.append(r)

    cm = cm_counts(y_true, y_pred)
    mat = cm_matrix(cm)
    prf = prf_from_cm(mat)

    return {
        "name": name,
        "n": len(y_true),
        "accuracy": accuracy(y_true, y_pred),
        "macro_f1": macro_f1(prf),
        "per_class": prf,
        "confusion_matrix": {
            "labels": LABELS,
            "matrix": mat,
        },
    }


# -------------------------
# Plotting (Hybrid only, for now)
# -------------------------

def plot_confusion_matrix(mat: List[List[int]], out_path: Path, title: str) -> None:
    fig, ax = plt.subplots()
    im = ax.imshow(mat)
    ax.set_xticks(range(len(LABELS)))
    ax.set_yticks(range(len(LABELS)))
    ax.set_xticklabels(LABELS)
    ax.set_yticklabels(LABELS)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title(title)

    # Annotate counts
    for i in range(len(LABELS)):
        for j in range(len(LABELS)):
            ax.text(j, i, str(mat[i][j]), ha="center", va="center")

    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def plot_prf(per_class: Dict[str, Dict[str, float]], out_path: Path, title: str) -> None:
    classes = LABELS
    metrics = ["precision", "recall", "f1"]

    # Prepare grouped bars: 3 metrics per class
    x = list(range(len(classes)))
    width = 0.25

    fig, ax = plt.subplots()
    for k, m in enumerate(metrics):
        vals = [per_class[c][m] for c in classes]
        ax.bar([i + (k - 1) * width for i in x], vals, width, label=m)

    ax.set_xticks(x)
    ax.set_xticklabels(classes)
    ax.set_ylim(0, 1.0)
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    corpus_path = repo_root / "data" / "youth_corpus.csv"
    out_dir = repo_root / "results"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = load_corpus(corpus_path)

    experiments = ["A_emotion_only", "B_text_only", "C_hybrid"]
    results = [run_experiment(name, rows) for name in experiments]

    # Save metrics.json
    metrics_path = out_dir / "metrics.json"
    with metrics_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # Print summary (compact, GitHub-friendly)
    print("Experiment summary:")
    for r in results:
        print(
            f"- {r['name']}: n={r['n']}  acc={r['accuracy']:.3f}  macro_f1={r['macro_f1']:.3f}  "
            f"alert_recall={r['per_class']['alert']['recall']:.3f}  watch_recall={r['per_class']['watch']['recall']:.3f}"
        )

    # Plots for Hybrid (C)
    hybrid = next(rr for rr in results if rr["name"] == "C_hybrid")
    mat = hybrid["confusion_matrix"]["matrix"]
    plot_confusion_matrix(mat, out_dir / "confusion_matrix_C.png", "Confusion Matrix (C: Hybrid)")
    plot_prf(hybrid["per_class"], out_dir / "prf_C.png", "Per-class Precision/Recall/F1 (C: Hybrid)")

    print(f"\nSaved: {metrics_path}")
    print(f"Saved: {out_dir / 'confusion_matrix_C.png'}")
    print(f"Saved: {out_dir / 'prf_C.png'}")


if __name__ == "__main__":
    main()
