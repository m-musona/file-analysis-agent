"""Perform descriptive statistical analysis on a CSV file."""

import pandas as pd
from models.schemas import CSVAnalysisResult


def analyse_csv(file_path: str) -> CSVAnalysisResult:
    """Read a CSV and return column names, shape, per-column stats, and missing value counts."""
    df = pd.read_csv(file_path)
    numeric = df.select_dtypes(include="number")
    stats = {
        col: {
            k: round(v, 4)
            for k, v in numeric[col].agg(["mean", "min", "max", "std"]).items()
        }
        for col in numeric.columns
    }
    return CSVAnalysisResult(
        columns=df.columns.tolist(),
        row_count=len(df),
        col_count=len(df.columns),
        stats=stats,
        missing=df.isnull().sum().to_dict(),
    )
