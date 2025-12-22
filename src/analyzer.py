# src/analyzer.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Tuple
import re

from .lexicon import (
    EMOTION_BASE,
    POS_WORDS,
    NEG_WORDS,
    INTENSIFIERS,
    NEGATIONS,
    CONCERNING_PHRASES,
)

_WORD_RE = re.compile(r"[a-zA-Z']+")


@dataclass
class AnalysisResult:
    emotion: str
    sentiment_score: float   # -1.0 ~ 1.0
    flags: List[str]
    features: Dict[str, int]


def _clamp(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def _tokenize(text: str) -> List[str]:
    return [m.group(0).lower() for m in _WORD_RE.finditer(text)]


def analyze_checkin(emotion: str, text: str) -> AnalysisResult:
    """
    Lightweight, explainable scoring:
    - base score from emotion wheel
    - word cues +/- adjustments
    - intensifier + negation handling (simple heuristic)
    - concerning phrase flags
    """
    emo = (emotion or "").strip().lower()
    base = EMOTION_BASE.get(emo, 0.0)

    tokens = _tokenize(text or "")
    flags: List[str] = []
    features = {
        "pos_hits": 0,
        "neg_hits": 0,
        "intensifier_hits": 0,
        "negation_hits": 0,
        "concerning_phrase_hits": 0,
    }

    # Phrase flags (cheap but useful)
    lowered = (text or "").strip().lower()
    for phrase in CONCERNING_PHRASES:
        if phrase in lowered:
            features["concerning_phrase_hits"] += 1
            flags.append("concerning_language")

    score = base

    # Simple cue scoring with local context
    for i, w in enumerate(tokens):
        prev = tokens[i - 1] if i - 1 >= 0 else ""
        prev2 = tokens[i - 2] if i - 2 >= 0 else ""

        is_negated = prev in NEGATIONS or prev2 in NEGATIONS
        if prev in INTENSIFIERS:
            features["intensifier_hits"] += 1
            boost = 1.5
        else:
            boost = 1.0

        if prev in NEGATIONS or prev2 in NEGATIONS:
            features["negation_hits"] += 1

        if w in POS_WORDS:
            features["pos_hits"] += 1
            delta = 0.12 * boost
            score += (-delta if is_negated else delta)

        if w in NEG_WORDS:
            features["neg_hits"] += 1
            delta = 0.14 * boost
            score += (delta if is_negated else -delta)

    # Mild penalty if emotion itself is unknown but text is very negative
    if emo not in EMOTION_BASE and features["neg_hits"] >= 3:
        flags.append("unknown_emotion_with_negative_text")

    # Flag persistent negativity in single entry (very rough heuristic)
    if score < -0.6 and features["neg_hits"] >= 2:
        flags.append("strong_negative_signal")

    return AnalysisResult(
        emotion=emo if emo else "unknown",
        sentiment_score=_clamp(score),
        flags=sorted(set(flags)),
        features=features,
    )
