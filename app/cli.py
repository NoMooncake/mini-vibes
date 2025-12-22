# app/cli.py
from __future__ import annotations

import json
from src.analyzer import analyze_checkin


def main() -> None:
    print("mini-vibes CLI")
    emotion = input("emotion (e.g., sad / happy / anxious): ").strip()
    text = input("journal (1-3 sentences): ").strip()

    result = analyze_checkin(emotion, text)

    print("\n--- result ---")
    print(json.dumps({
        "emotion": result.emotion,
        "sentiment_score": result.sentiment_score,
        "flags": result.flags,
        "features": result.features,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
