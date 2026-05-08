"""Read .txt, .md, .pdf, .csv, or .json and return structured content."""

import json, pathlib
import pandas as pd
from models.schemas import FileReadResult


def read_file(file_path: str) -> FileReadResult:
    p = pathlib.Path(file_path)
    ext = p.suffix.lower()

    if ext in (".txt", ".md"):
        return FileReadResult(file_type=ext[1:], content=p.read_text(errors="replace"))

    if ext == ".pdf":
        import pdfplumber

        with pdfplumber.open(file_path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        return FileReadResult(
            file_type="pdf",
            content=text,
            metadata={"pages": len(pdf.pages) if False else 0},
        )

    if ext == ".csv":
        df = pd.read_csv(file_path)
        return FileReadResult(
            file_type="csv",
            content=df.to_dict(orient="records"),
            row_count=len(df),
            col_count=len(df.columns),
        )

    if ext == ".json":
        data = json.loads(p.read_text())
        return FileReadResult(file_type="json", content=data)

    raise ValueError(f"Unsupported file type: {ext}")
