# Youth Language Corpus – Annotation Guidelines

This corpus simulates short journal-style expressions from middle school students
(grades 6–8) for the purpose of prototyping sentiment and risk detection systems.

This dataset is **synthetic** and **non-diagnostic**. It is intended only for
research and system design practice.

---

## Fields

Each entry contains the following fields:

- `text`  
  A short journal-style sentence (1–2 sentences max).

- `emotion_hint`  
  Optional emotion label suggested by the writer (e.g., sad, angry, okay).
  This may be empty to simulate missing or unclear emotion selection.

- `risk_label`  
  One of:
  - `safe`   – normal emotional expression, no concern
  - `watch`  – negative or concerning tone that may require monitoring
  - `alert`  – language that should be reviewed by a human counselor

- `reason_tag`  
  Primary reason for the assigned risk label (one main tag).

---

## Risk Label Definitions

### SAFE
- Mild emotions (positive or neutral)
- Temporary stress without hopelessness
- No self-blame or withdrawal language

Examples:
- "I was tired today but it got better later."
- "School was boring but fine."

---

### WATCH
- Repeated negativity or emotional exhaustion
- Withdrawal, loneliness, or helplessness language
- No explicit self-harm intent

Examples:
- "I feel tired all the time and don’t really want to talk to anyone."
- "Nothing really makes me happy lately."

---

### ALERT
- Explicit or implicit signals of self-harm or desire to disappear
- Statements implying hopelessness combined with distress
- Language that should trigger **human review**, not automated decisions

Examples:
- "I don’t want to be here anymore."
- "Sometimes I think it would be easier if I just disappeared."

---

## Reason Tags (non-exhaustive)

- `stress_school`
- `withdrawal`
- `loneliness`
- `self_blame`
- `hopelessness`
- `bullying`
- `anger_outburst`
- `numbness`
- `self_harm_hint`

Each entry should have **one primary reason tag**.
