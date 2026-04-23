# File Analysis Agent

### Step 1 – 24.04

---

## 1. System Description & Goal

The File Analysis Agent is a command-line application that lets users ask natural-language questions about the contents of local files. Given a file path and a question, the agent reads and interprets the file, runs the appropriate analysis tools, and returns a structured Markdown report containing a summary, extracted keywords, sentiment classification, and — for tabular data — descriptive statistics.

The goal is to remove the friction of manual file inspection: a data analyst, researcher, or developer can point the agent at any supported file and immediately receive a coherent, machine-generated report without writing a single line of analysis code themselves.

---

## 2. AI & Agent-Based Approach

The system is built around a **ReAct-style tool-use agent** powered by the Google Gemini API (`gemini-1.5-flash`). The agent operates in an iterative loop:

1. Gemini receives the file path and the user's query.
2. It decides which tool to call next (read file, summarise, extract keywords, etc.).
3. The tool is executed locally in Python and its result is fed back to Gemini.
4. The loop repeats until Gemini calls `write_report`, producing the final Markdown output.

Reasoning and tool-selection logic lives entirely inside Gemini — the Python code only handles dispatch and execution. A safety cap of 10 iterations prevents infinite loops, and a fallback path ensures a report is always produced.

---

## 3. Tools Used

**External libraries & APIs**

| Tool                  | Purpose                                                   |
| --------------------- | --------------------------------------------------------- |
| `google-generativeai` | Gemini API SDK — LLM reasoning and tool orchestration     |
| `pydantic` v2         | Typed data models for inter-module communication          |
| `pandas`              | DataFrame operations, CSV parsing, descriptive statistics |
| `pdfplumber`          | Text extraction from PDF files                            |

**Internal Python modules**

| Module                        | Purpose                                                        |
| ----------------------------- | -------------------------------------------------------------- |
| `main.py`                     | CLI entry point — argument parsing, env validation, file check |
| `agent/loop.py`               | Agent loop, tool registry, Gemini conversation management      |
| `models/schemas.py`           | Shared Pydantic return types for all tools                     |
| `tools/file_reader.py`        | Unified reader for `.txt`, `.md`, `.pdf`, `.csv`, `.json`      |
| `tools/text_summariser.py`    | Text cleaning, truncation, re-exports                          |
| `tools/keyword_extractor.py`  | Stop-word filtering, frequency counting, topic categorisation  |
| `tools/sentiment_detector.py` | Lexicon-based sentiment with negation handling                 |
| `tools/csv_analyser.py`       | Descriptive stats and missing-value counts                     |
| `tools/report_writer.py`      | Markdown report assembly and file output                       |

---

## 4. Programming Concepts Required

**Language & runtime**

- Python 3.11+ — type hints, f-strings, `pathlib`, `dataclasses`
- Basic shell/CLI usage — running scripts, setting environment variables

**Core Python**

- Object-oriented design — Pydantic `BaseModel` subclasses as typed data contracts
- Functional patterns — dict dispatch table for tool routing in `agent/loop.py`
- Exception handling — `try/except` around every tool call; errors surfaced as dicts
- File I/O — `pathlib.Path`, `open()`, `write_text()` for reading and writing files
- Standard library — `argparse`, `os`, `json`, `re`, `string`, `collections.Counter`, `datetime`

**API & integration**

- REST / SDK usage — `google-generativeai` Python SDK, chat sessions, multi-turn history
- Tool / function calling — declaring schemas, dispatching calls, feeding results back to the model
- Environment variables — `GEMINI_API_KEY` loaded via `os.environ` at startup
- JSON serialisation — `json.dumps` with `default=str` for non-serialisable types

**Data & text analysis**

- DataFrame operations — `pd.read_csv`, `select_dtypes`, `agg`, `isnull().sum()`
- Text processing — tokenisation, stop-word removal, frequency counting, regex normalisation
- Lexicon-based NLP — keyword-to-topic mapping, negation-aware sentiment scoring

**Software engineering**

- Separation of concerns — tools, agent logic, schemas, and CLI are fully decoupled
- Agent / loop pattern — iterative ReAct loop with a capped iteration safety mechanism
- Typed interfaces — every tool returns a Pydantic model; loop calls `.model_dump()`
- Defensive coding — all three exit paths in `run_agent` produce a valid report

---

## Quick Start

```bash
pip install -r requirements.txt
export GEMINI_API_KEY=your_key_here
python main.py report.pdf "What are the main findings?"
```

Add `--output result.md` to save the report to a file instead of printing to stdout.
