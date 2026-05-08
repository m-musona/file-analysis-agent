"""Classify text sentiment as positive, negative, or neutral with a confidence score."""

import string
from models.schemas import SentimentResult

POS = {
    "good",
    "great",
    "excellent",
    "outstanding",
    "positive",
    "success",
    "best",
    "love",
    "wonderful",
    "fantastic",
    "well",
    "improve",
}
NEG = {
    "bad",
    "poor",
    "terrible",
    "negative",
    "fail",
    "worst",
    "hate",
    "awful",
    "disappointing",
    "loss",
    "error",
    "problem",
    "issue",
}
NEGATORS = {
    "not",
    "no",
    "never",
    "neither",
    "nor",
    "hardly",
    "barely",
    "scarcely",
    "dont",
    "doesnt",
    "didnt",
    "wont",
    "wouldnt",
}


def detect_sentiment(text: str) -> SentimentResult:
    """Tokenize text, handle negation, classify sentiment, return score and confidence."""
    tokens = [w.strip(string.punctuation).lower() for w in text.split()]
    score, negate = 0, False
    for word in tokens:
        if word in NEGATORS:
            negate = True
            continue
        if word in POS:
            score += -1 if negate else 1
        elif word in NEG:
            score += 1 if negate else -1
        negate = False

    total = len([w for w in tokens if w in POS | NEG]) or 1
    confidence = round(min(abs(score) / total, 1.0), 2)
    sentiment = "positive" if score > 0 else "negative" if score < 0 else "neutral"
    return SentimentResult(
        sentiment=sentiment, confidence=confidence, score=round(score / total, 2)
    )
