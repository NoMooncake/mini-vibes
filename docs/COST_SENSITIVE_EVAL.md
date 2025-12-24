# Cost-Sensitive Evaluation

This document provides a detailed explanation of the **cost-sensitive evaluation framework**
used in the Mini-Vibes project.

In youth mental-health and school counseling contexts, different prediction errors carry
**unequal real-world consequences**. As a result, optimizing for raw accuracy alone can
produce systems that appear strong numerically while failing in practice.

This note formalizes that intuition and explains how cost-sensitive evaluation complements
standard classification metrics.

---

## 1. Motivation

Traditional metrics such as accuracy implicitly assume that all errors are equally costly.
This assumption is inappropriate in safety-critical domains.

Examples:

- Missing an **alert** case (false negative) may delay critical human intervention.
- Over-flagging a **watch** case may create minor inefficiencies.
- Excessive false alerts can overwhelm counselors and erode trust.

Cost-sensitive evaluation makes these trade-offs explicit.

---

## 2. Cost Matrix Design

We define a cost matrix that assigns higher penalties to more harmful errors.

### Example Cost Matrix

| True \ Pred | safe | watch | alert |
|-------------|------|-------|-------|
| safe  | 0 | 1 | 5 |
| watch | 3 | 0 | 2 |
| alert | 10 | 6 | 0 |

Interpretation:

- `alert → safe` is the most costly error.
- `alert → watch` remains severe but less extreme.
- Over-flagging safe entries incurs smaller penalties.

These values are **configurable** and encode institutional risk preferences.

---

## 3. Evaluation Method

For each prediction:

- Cost = 0 if the prediction is correct.
- Otherwise, cost is determined by the cost matrix.

We report two summary statistics:

- **Total Cost**: cumulative risk cost across the dataset.
- **Average Cost per Entry**: normalized risk exposure.

Lower values indicate safer overall system behavior.

---

## 4. Application to Baseline Experiments

This framework is applied to three baseline systems:

- **A — Emotion-only**
- **B — Text-only**
- **C — Hybrid (emotion + text + explainable rules)**

While accuracy-based evaluation shows modest differences, cost-sensitive analysis reveals
qualitative behavioral distinctions:

- Emotion-only systems incur high cost due to missed alerts.
- Text-only systems reduce alert misses but fail to capture moderate risk.
- Hybrid systems shift errors toward lower-cost categories.

---

## 5. Key Insight

> In safety-critical domains, the optimal system is not the one that makes the fewest
> mistakes, but the one that makes the *least harmful* mistakes.

Cost-sensitive evaluation aligns model assessment with real-world consequences rather than
pure classification performance.

---

## 6. Limitations

- Cost values are subjective and context-dependent.
- Small synthetic datasets limit statistical generalization.
- Longitudinal context is not modeled.

Despite these limitations, cost-sensitive analysis provides a more realistic evaluation
lens for youth risk-flagging systems.

---

## 7. Conclusion

This document motivates and explains the use of cost-sensitive evaluation in Mini-Vibes.
By explicitly modeling error severity, it supports more responsible and interpretable
system design decisions.
