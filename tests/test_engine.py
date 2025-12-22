from src.analyzer import analyze_checkin
from src.engine import assess_risk

def test_alert_when_concerning_language():
    a = analyze_checkin("okay", "Sometimes I can't do this anymore.")
    r = assess_risk(a)
    assert r.risk_level == "alert"

def test_watch_when_persistent_negative():
    # simulate history: 4 recent, current makes 5
    recent = [-0.4, -0.3, 0.1, -0.5]  # 3 negative in last 4 already
    a = analyze_checkin("sad", "I feel tired and alone.")
    r = assess_risk(a, recent_scores=recent)
    assert r.risk_level in ("watch", "alert")
