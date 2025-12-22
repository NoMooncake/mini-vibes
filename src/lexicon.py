# src/lexicon.py
from __future__ import annotations

# 1) Emotion wheel -> base score (tunable)
EMOTION_BASE = {
    "happy": 0.6,
    "excited": 0.7,
    "calm": 0.3,
    "okay": 0.0,
    "tired": -0.2,
    "sad": -0.6,
    "angry": -0.5,
    "anxious": -0.4,
    "stressed": -0.4,
    "numb": -0.3,
}

# 2) Youth-ish negative / positive cue words (very small starter set)
POS_WORDS = {
    "good", "great", "fine", "okay", "ok", "awesome", "better", "happy", "excited", "relieved"
}

NEG_WORDS = {
    "bad", "awful", "sad", "angry", "mad", "upset", "tired", "exhausted", "stressed", "anxious",
    "worried", "scared", "alone", "lonely", "hate", "worthless", "broken"
}

# 3) Intensifiers / diminishers
INTENSIFIERS = {"very", "so", "really", "super", "extremely", "totally"}
DIMINISHERS = {"kinda", "kindof", "sorta", "sortof", "a_bit", "a", "little"}

# 4) Negations
NEGATIONS = {"not", "dont", "don't", "never", "no", "cant", "can't", "wont", "won't"}

# 5) Concerning phrases
# NOTE: This is NOT a diagnosis; it's just a flag for human review.
CONCERNING_PHRASES = {
    # explicit
    "i want to disappear",
    "i don't want to be here",
    "i dont want to be here",
    "hurt myself",
    "hurting myself",

    # implicit / youth-like
    "no one would care",
    "nobody would care",
    "everything feels too heavy",
    "i can't do this anymore",
    "i cant do this anymore",
    "nothing matters anymore",
    "what's the point",
}

