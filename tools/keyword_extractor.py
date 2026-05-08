"""Extract keywords and map them to topic categories."""

import re, string
from collections import Counter
from models.schemas import KeywordResult

STOP_WORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "but",
    "in",
    "on",
    "at",
    "to",
    "for",
    "of",
    "with",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "will",
    "would",
    "could",
    "should",
    "may",
    "might",
    "this",
    "that",
    "these",
    "those",
    "it",
    "its",
    "i",
    "you",
    "he",
    "she",
    "we",
    "they",
    "not",
    "as",
    "from",
    "by",
}

TOPIC_MAP = {
    "finance": {
        "revenue",
        "profit",
        "loss",
        "cost",
        "budget",
        "price",
        "sales",
        "market",
        "stock",
        "investment",
    },
    "technology": {
        "software",
        "hardware",
        "api",
        "data",
        "model",
        "network",
        "cloud",
        "server",
        "code",
        "algorithm",
    },
    "health": {
        "patient",
        "doctor",
        "hospital",
        "disease",
        "treatment",
        "medicine",
        "clinical",
        "health",
        "care",
    },
    "legal": {
        "law",
        "contract",
        "court",
        "judge",
        "legal",
        "rights",
        "regulation",
        "compliance",
        "policy",
    },
    "science": {
        "research",
        "study",
        "experiment",
        "hypothesis",
        "evidence",
        "analysis",
        "result",
        "theory",
    },
}


def extract_keywords(text: str) -> KeywordResult:
    """Identify keywords and topic categories from text."""
    tokens = [w.strip(string.punctuation).lower() for w in text.split()]
    words = [w for w in tokens if w and w not in STOP_WORDS and not w.isdigit()]
    keywords = [w for w, _ in Counter(words).most_common(20)]
    kw_set = set(keywords)
    topics = [topic for topic, vocab in TOPIC_MAP.items() if kw_set & vocab]
    return KeywordResult(keywords=keywords, topics=topics or ["general"])
