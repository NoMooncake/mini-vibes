# app/cli.py
from __future__ import annotations

import json
from src.analyzer import analyze_checkin
from src.engine import assess_risk


def main() -> None:
    print("mini-vibes CLI")
    emotion = input("emotion (e.g., sad / happy / anxious): ").strip()
    text = input("journal (1-3 sentences): ").strip()

    analysis = analyze_checkin(emotion, text)
    alert = assess_risk(analysis, recent_scores=[])

    print("\n--- result ---")
    print(json.dumps({
        "emotion": analysis.emotion,
        "sentiment_score": analysis.sentiment_score,
        "flags": analysis.flags,
        "features": analysis.features,
        "risk_level": alert.risk_level,
        "engine_flags": [f for f in alert.flags if f not in analysis.flags],
        "explanation": alert.explanation,
        "suggested_action": alert.suggested_action,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
