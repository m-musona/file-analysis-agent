"""Clean and prepare text for summarization; re-export keyword and sentiment helpers."""

import re
from models.schemas import SummaryResult
from tools.keyword_extractor import extract_keywords  # re-exported
from tools.sentiment_detector import detect_sentiment  # re-exported

MAX_WORDS = 4000


def summarise(text: str) -> SummaryResult:
    """Clean input text and return it with its word count for downstream summarization."""
    text = re.sub(r"\n{3,}", "\n\n", text).strip()  # collapse blank lines
    words = text.split()
    if len(words) > MAX_WORDS:
        text = " ".join(words[:MAX_WORDS]) + " [truncated]"
        words = words[:MAX_WORDS]
    return SummaryResult(cleaned_text=text, word_count=len(words))


__all__ = ["summarise", "extract_keywords", "detect_sentiment"]
