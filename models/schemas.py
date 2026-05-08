from pydantic import BaseModel
from typing import Any, Optional


class FileReadResult(BaseModel):
    file_type: str
    content: Any  # str for text/json, list[dict] for csv
    row_count: Optional[int] = None
    col_count: Optional[int] = None
    metadata: dict = {}


class SummaryResult(BaseModel):
    cleaned_text: str
    word_count: int


class KeywordResult(BaseModel):
    keywords: list[str]
    topics: list[str]


class SentimentResult(BaseModel):
    sentiment: str  # "positive" | "negative" | "neutral"
    confidence: float
    score: float


class CSVAnalysisResult(BaseModel):
    columns: list[str]
    row_count: int
    col_count: int
    stats: dict[str, dict]  # column → {mean, min, max, std}
    missing: dict[str, int]  # column → null count


class ReportResult(BaseModel):
    report_path: str  # absolute path to written report.md
    markdown: str  # full Markdown content
