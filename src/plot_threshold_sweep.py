# src/plot_threshold_sweep.py
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict

import matplotlib.pyplot as plt


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    in_path = repo_root / "results" / "threshold_sweep.json"
    out_dir = repo_root / "results"
    out_dir.mkdir(parents=True, exist_ok=True)

    data: List[Dict] = json.loads(in_path.read_text(encoding="utf-8"))

    # Sort by threshold (ascending)
    data.sort(key=lambda d: d["watch_threshold"])

    thresholds = [d["watch_threshold"] for d in data]
    total_cost = [d["total_cost"] for d in data]
    avg_cost = [d["avg_cost"] for d in data]
    watch_recall = [d["watch_recall"] for d in data]
    alert_recall = [d["alert_recall"] for d in data]

    # -----------------------------
    # Plot 1: Total cost vs threshold
    # -----------------------------
    fig1, ax1 = plt.subplots()
    ax1.plot(thresholds, total_cost, marker="o", label="total_cost")
    ax1.plot(thresholds, avg_cost, marker="o", label="avg_cost")

    ax1.set_title("Cost vs Watch Threshold (Hybrid C)")
    ax1.set_xlabel("watch_threshold")
    ax1.set_ylabel("cost")
    ax1.legend()
    fig1.tight_layout()

    out1 = out_dir / "threshold_cost_curve.png"
    fig1.savefig(out1, dpi=200)
    plt.close(fig1)

    # -----------------------------
    # Plot 2: Recall vs threshold
    # -----------------------------
    fig2, ax2 = plt.subplots()
    ax2.plot(thresholds, watch_recall, marker="o", label="watch_recall")
    ax2.plot(thresholds, alert_recall, marker="o", label="alert_recall")

    ax2.set_title("Recall vs Watch Threshold (Hybrid C)")
    ax2.set_xlabel("watch_threshold")
    ax2.set_ylabel("recall")
    ax2.set_ylim(0, 1.0)
    ax2.legend()
    fig2.tight_layout()

    out2 = out_dir / "threshold_recall_curve.png"
    fig2.savefig(out2, dpi=200)
    plt.close(fig2)

    print(f"Saved: {out1}")
    print(f"Saved: {out2}")


if __name__ == "__main__":
    main()
