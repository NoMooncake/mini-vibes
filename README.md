# Mini-Vibes (Local Research Prototype)

A local, reproducible research prototype that explores **explainable risk flagging**
for middle-school student check-ins.

Students select an emotion and write a short journal entry.
The system produces:
- a lightweight sentiment score
- an explainable **risk level** (`safe` / `watch` / `alert`)
- human-readable reasons for each flag (non-diagnostic)

**Important**
This project uses **synthetic data only** and is **not a medical or clinical tool**.
It is intended for research, experimentation, and system design exploration.

---

## Overview

This repository studies a **rule-based, explainable baseline** for detecting
potential emotional risk in short youth journal entries.

Rather than maximizing raw accuracy, the system prioritizes:
- interpretability
- conservative flagging
- class-aware evaluation (especially for rare but critical cases)

The goal is to demonstrate how different signal sources contribute to risk detection
and why **accuracy alone is insufficient** in safety-critical domains.

---

## Inputs and Outputs

### Inputs
- `emotion_hint`
  A self-reported emotion selected from an emotion wheel (may be missing).
- `text`
  A short journal-style entry (1–2 sentences).

### Outputs
- `sentiment_score` in range `[-1.0, 1.0]`
- `risk_level`: `safe`, `watch`, or `alert`
- `flags`: triggered signals from analyzer and rule engine
- `explanation`: human-readable reasons
- `suggested_action`: non-diagnostic next step

Example CLI output:

```json
{
  "emotion": "sad",
  "sentiment_score": -0.68,
  "risk_level": "watch",
  "flags": ["negative_cues_cluster"],
  "explanation": [
    "Multiple negative cues detected in the journal text."
  ],
  "suggested_action": "Recommend monitoring and a supportive check-in if patterns continue."
}
```

---

## Reproducibility (Local)

### Environment setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run interactive CLI
```bash
python -m app.cli
```

### Run experiments (A / B / C baselines)
```bash
python -m src.run_experiments
```

### Run tests
```bash
pytest -q
```

All results are generated **locally** with no cloud dependencies.

---

## Dataset

- Synthetic corpus: `data/youth_corpus.csv`
- Annotation guidelines: `data/README.md`

### Risk labels
- **safe**: Normal emotional expression, no concern.
- **watch**: Negative or concerning tone that may require monitoring.
- **alert**: Language that should trigger **human review**, not automated decisions.

---

## Experiments

Three baselines are evaluated on the same corpus:

- **A — Emotion-only**: Uses only the selected emotion (no text).
- **B — Text-only**: Uses lexicon-based sentiment and rules from text alone.
- **C — Hybrid**: Combines emotion + text + explainable rule engine.

---

## Results Summary (n = 15)

| Experiment | Accuracy | Macro-F1 | Watch Recall | Alert Recall |
|----------|----------|----------|--------------|--------------|
| A Emotion-only | 0.667 | 0.509 | 1.000 | 0.000 |
| B Text-only | 0.533 | 0.482 | 0.000 | 0.750 |
| C Hybrid | 0.533 | 0.547 | 0.167 | 0.750 |

### Why accuracy is misleading here

The emotion-only baseline achieves higher accuracy, yet **fails to detect any
`alert` cases**.
This demonstrates why **macro-averaged metrics and per-class recall** are essential
when evaluating risk-flagging systems.

---

## Hybrid Model Visualizations

### Confusion Matrix
![Confusion Matrix (Hybrid)](results/confusion_matrix_C.png)

### Per-class Precision / Recall / F1
![PRF (Hybrid)](results/prf_C.png)

Full experiment outputs are stored in:
```
results/metrics.json
```

---

## Ethics and Limitations

- This system performs **risk flagging**, not diagnosis.
- All outputs are intended for **human interpretation and review**.
- Data is synthetic and does not represent real individuals.
- Youth language includes sarcasm, slang, and context dependence that remain challenging
  for rule-based systems.

---

## Project Structure

```
mini-vibes/
  app/                # CLI interface
  src/                # analyzer, engine, experiments
  data/               # synthetic corpus and annotation guide
  results/            # metrics and plots
  tests/              # unit tests
```

---

## License

This project is provided for educational and research purposes only.
