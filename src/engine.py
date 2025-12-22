# src/engine.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Optional

from .analyzer import AnalysisResult


@dataclass
class AlertResult:
    risk_level: str               # "safe" | "watch" | "alert"
    flags: List[str]              # merged flags (from analyzer + engine rules)
    explanation: List[str]        # human-readable reasons
    suggested_action: str         # non-diagnostic next step


def assess_risk(
    current: AnalysisResult,
    recent_scores: Optional[List[float]] = None,
    recent_flags: Optional[List[List[str]]] = None,
) -> AlertResult:
    """
    Explainable rule-based engine.

    Inputs:
      - current: analysis of current check-in
      - recent_scores: previous sentiment scores (most recent last), optional
      - recent_flags: previous flags list per entry, optional

    Output:
      - risk_level + explanation + suggested_action
    """
    recent_scores = recent_scores or []
    recent_flags = recent_flags or []

    explanation: List[str] = []
    engine_flags: List[str] = []

    score = current.sentiment_score

    # Rule A: concerning language => alert (human review)
    if "concerning_language" in current.flags:
        engine_flags.append("needs_human_review")
        explanation.append("Journal contains concerning phrases that warrant human review.")

    # Rule B: very low score
    if score <= -0.75:
        engine_flags.append("very_negative_entry")
        explanation.append("Current check-in is strongly negative (low sentiment score).")

    # Rule C: strong negative signal from analyzer
    if "strong_negative_signal" in current.flags:
        engine_flags.append("negative_cues_cluster")
        explanation.append("Multiple negative cues detected in the journal text.")

    # Rule D: persistence over recent history (e.g., 3+ negatives in last 5)
    window = recent_scores[-4:] + [score]  # include current; up to 5 entries
    neg_count = sum(1 for s in window if s < -0.25)
    if len(window) >= 5 and neg_count >= 3:
        engine_flags.append("persistent_negative_pattern")
        explanation.append("Negative mood appears repeatedly across recent check-ins.")

    # Rule E: moderate negative score => watch
    if -0.55 <= score <= -0.30:
        engine_flags.append("moderate_negative_entry")
        explanation.append("Overall sentiment indicates moderate and persistent negativity.")

    # Determine risk level (simple priority)
    if "needs_human_review" in engine_flags:
        risk = "alert"
    elif (
        score <= -0.75
        or "persistent_negative_pattern" in engine_flags
        or "moderate_negative_entry" in engine_flags
    ):
        risk = "watch"
    else:
        risk = "safe"

    # Suggested action (non-diagnostic)
    if risk == "alert":
        action = "Recommend a timely counselor check-in and human review of the entry."
    elif risk == "watch":
        action = "Recommend monitoring and a supportive check-in if patterns continue."
    else:
        action = "No action needed; continue regular check-ins."

    merged_flags = sorted(set(current.flags + engine_flags))

    # If nothing triggered, still provide a minimal explanation
    if not explanation:
        explanation.append("No concerning patterns detected in this check-in.")

    return AlertResult(
        risk_level=risk,
        flags=merged_flags,
        explanation=explanation,
        suggested_action=action,
    )
