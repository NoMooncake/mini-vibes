from src.analyzer import analyze_checkin

def test_analyze_returns_score_in_range():
    r = analyze_checkin("sad", "I feel really tired and alone.")
    assert -1.0 <= r.sentiment_score <= 1.0

def test_concerning_phrase_flag():
    r = analyze_checkin("okay", "Sometimes I can't do this anymore.")
    assert "concerning_language" in r.flags
