# File Analysis Agent

### Step 1 – 24.04 | Step 2 – 08.05

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

---

---

# Step 2 – 08.05

---

## 5. Updated System Description

The File Analysis Agent has been fully implemented as a modular, nine-module Python package. The system takes a file path and a natural-language query from the command line, then drives a Gemini-powered agent loop that selects and calls local analysis tools iteratively until it has enough information to compile a final Markdown report.

Since Step 1, the following has been built and integrated:

- **`tools/report_writer.py`** was added as the mandatory final step in every agent run. Gemini is instructed via a system prompt to always conclude by calling `write_report`, ensuring the return value of `run_agent` is always a structured Markdown document rather than a raw text string.
- **Three guaranteed exit paths** exist in `agent/loop.py`: normal tool-call completion (Gemini calls `write_report`), text-only fallback (Gemini responds with prose and no tool calls), and max-iteration fallback — all three route through `write_report` so a `report.md` file is always written to disk.
- **`models/schemas.py`** was extended with `ReportResult` to give the report writer a typed return like every other tool.
- The tool registry in `loop.py` is a plain dict — adding a new tool requires one line there and nowhere else.

---

## 6. Programming Concepts Actually Used

The following concepts from the Step 1 preliminary list were confirmed in implementation, with removals and additions noted.

**Confirmed and used**

| Concept                         | Where                                                              |
| ------------------------------- | ------------------------------------------------------------------ |
| Type hints throughout           | Every function signature and Pydantic model field                  |
| Pydantic `BaseModel` subclasses | `models/schemas.py` — six typed result models                      |
| Dict dispatch table             | `TOOLS` dict in `agent/loop.py`                                    |
| `try/except` per tool call      | `_dispatch()` in `agent/loop.py`                                   |
| `pathlib.Path` file I/O         | `file_reader.py`, `report_writer.py`                               |
| `argparse` CLI                  | `main.py`                                                          |
| `os.environ` for API key        | `main.py` and `loop.py`                                            |
| `json.dumps(default=str)`       | Tool result serialisation in `loop.py`                             |
| `re` regex                      | Text normalisation in `text_summariser.py`                         |
| `collections.Counter`           | Frequency ranking in `keyword_extractor.py`                        |
| `string.punctuation`            | Token stripping in `keyword_extractor.py`, `sentiment_detector.py` |
| `datetime.now()`                | Report timestamp in `report_writer.py`                             |
| `pandas` DataFrame ops          | `csv_analyser.py` — `read_csv`, `select_dtypes`, `agg`, `isnull`   |
| `pdfplumber`                    | PDF text extraction in `file_reader.py`                            |
| Gemini multi-turn chat          | `chat = model.start_chat()` + iterative `chat.send_message()`      |
| Gemini function declarations    | `TOOL_DECLARATIONS` built from `TOOLS` dict in `loop.py`           |
| `.model_dump()` serialisation   | Called on every Pydantic result before JSON encoding               |

**Removed from preliminary list** (not needed in practice)

- `dataclasses` — superseded entirely by Pydantic models
- `WidthType`, `HeadingLevel` and other docx concepts — report output is plain Markdown, not Word

**Added during implementation** (not anticipated in Step 1)

- `genai.protos.FunctionDeclaration` / `FunctionResponse` — low-level Gemini protobuf types needed for tool schema declaration and result injection
- `system_instruction` parameter on `GenerativeModel` — used to instruct Gemini to always end with `write_report`
- `hasattr(result, "model_dump")` guard — defensive check before serialising tool results, since the dict-dispatch table also handles error dicts

---

## 7. How Concepts Are Applied in the Project

**Pydantic models as data contracts**
Every tool function has a typed return: `read_file` returns `FileReadResult`, `analyse_csv` returns `CSVAnalysisResult`, and so on. This means `loop.py` never inspects tool output structure directly — it calls `.model_dump()` and serialises to JSON. If a tool's output changes shape, the schema in `models/schemas.py` is the single source of truth and type errors are caught at the Pydantic layer, not at runtime inside the agent loop.

**Dict dispatch instead of if/elif chains**

```python
TOOLS = {
    "read_file":    (read_file,    {"file_path": ...}),
    "analyse_csv":  (analyse_csv,  {"file_path": ...}),
    ...
}
```

`_dispatch()` looks up `call.name` in this dict and calls the function. Adding a new tool is one line. The same dict drives `TOOL_DECLARATIONS` — the Gemini schema is generated by iterating `TOOLS`, so tool registration and schema declaration are never out of sync.

**Iterative agent loop with safety cap**
`run_agent` sends the user query to Gemini, collects any `function_call` parts from the response, dispatches them, and feeds `FunctionResponse` parts back in the next message. This repeats up to `max_iterations=10`. The loop exits as soon as `write_report` is called, or falls back to a minimal report if Gemini stops calling tools or the cap is hit — guaranteeing the caller always receives a Markdown string.

**Negation-aware sentiment without an NLP library**
`sentiment_detector.py` tracks a `negate` flag: when a token matches the `NEGATORS` set, the next sentiment word's polarity is flipped. This implements basic negation handling (`"not good"` → negative) with nothing beyond the standard library. Score and confidence are normalised to `[-1, 1]` and `[0, 1]` respectively.

**Stop-word filtering and topic mapping**
`keyword_extractor.py` strips punctuation, lowercases, filters against a hardcoded `STOP_WORDS` set, and ranks by `Counter.most_common(20)`. The top keywords are then matched against a `TOPIC_MAP` dict that associates domain vocabulary (e.g. `"revenue"`, `"profit"` → `"finance"`) to infer document topics without any trained model.

---

## 8. Tool Integration

Tools are integrated at three levels: **declaration**, **dispatch**, and **result injection**.

### Declaration

At module load time, `loop.py` iterates the `TOOLS` dict and builds a `genai.protos.Tool` object containing a `FunctionDeclaration` for each entry. Each declaration includes the tool name (used by Gemini to request a call), its docstring as the description, and a flat string-property schema for its parameters. Gemini uses these declarations to decide which tool to invoke and what arguments to pass.

```
TOOLS dict  →  TOOL_DECLARATIONS  →  GenerativeModel(tools=TOOL_DECLARATIONS)
```

### Dispatch

When Gemini responds with one or more `function_call` parts, `_dispatch()` is called for each:

```
response.parts  →  [function_call, ...]  →  _dispatch(call)
                                              ├─ TOOLS[call.name] → fn
                                              ├─ fn(**call.args)
                                              └─ result.model_dump() or {"error": ...}
```

All tool calls in a single Gemini turn are dispatched and collected before any result is sent back, matching the Gemini multi-tool-call contract.

### Result injection

Each dispatched result is wrapped in a `genai.protos.FunctionResponse` and sent back to the chat session as the next user message. Gemini sees the structured JSON result and uses it to decide the next tool call or to compose the final report.

```
tool result (dict)  →  FunctionResponse(name, result)  →  chat.send_message([...responses])
```

### Special handling for `write_report`

`write_report` is the only tool whose result triggers immediate loop exit. When `_dispatch` returns a result that contains a `"markdown"` key, `run_agent` captures it and returns without sending any further messages to Gemini. This ensures the structured Markdown from `report_writer.py` — not a Gemini-generated prose summary — is always the final output.

---

## Quick Start

```bash
pip install -r requirements.txt
export GEMINI_API_KEY=your_key_here
python main.py report.pdf "What are the main findings?"
```

Add `--output result.md` to save the report to a file instead of printing to stdout.

---

---

# Step 3 – 15.05

---

## 9. Testing Process

Testing uses Python's built-in `unittest` framework across 7 test files and 83 tests. The suite runs entirely without a live `GEMINI_API_KEY` — the agent loop tests mock both `genai.configure` and `genai.GenerativeModel` so no network calls are made.

**Run the suite:**

```bash
python -m pytest tests/ -v
```

**Test files and coverage:**

| File                               | Module under test             | Tests  |
| ---------------------------------- | ----------------------------- | ------ |
| `tests/test_keyword_extractor.py`  | `tools/keyword_extractor.py`  | 13     |
| `tests/test_sentiment_detector.py` | `tools/sentiment_detector.py` | 13     |
| `tests/test_text_summariser.py`    | `tools/text_summariser.py`    | 10     |
| `tests/test_file_reader.py`        | `tools/file_reader.py`        | 15     |
| `tests/test_csv_analyser.py`       | `tools/csv_analyser.py`       | 11     |
| `tests/test_report_writer.py`      | `tools/report_writer.py`      | 13     |
| `tests/test_agent_loop.py`         | `agent/loop.py`               | 9      |
| **Total**                          |                               | **83** |

**Approach by layer:**

- **Unit tests (tools)** — each tool is called directly with controlled inputs. Temporary files are written via `tempfile.mkdtemp()` and cleaned up with `addCleanup(os.unlink, ...)` so no artefacts persist on disk.
- **Schema tests** — every tool test asserts the return value is an instance of its declared Pydantic model, catching contract breakage at the boundary.
- **Edge-case tests** — each tool has at least one empty-input test, one malformed-input test, and boundary tests (e.g. exactly 4 000 words, single-row CSVs, all-stop-word strings).
- **Agent loop tests** — `genai.GenerativeModel` is replaced with a `MagicMock` whose `send_message.side_effect` returns pre-built response objects. `genai.configure` is also patched to a no-op and `GEMINI_API_KEY` is injected via `patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"})`, so the full suite runs without the `.env` file.

---

## 10. Test Scenarios

| #   | Scenario                                                 | Test file                    | Key assertion                                  |
| --- | -------------------------------------------------------- | ---------------------------- | ---------------------------------------------- |
| 1   | Stop words produce empty keyword list                    | `test_keyword_extractor.py`  | `keywords == []`                               |
| 2   | Keywords lowercased and punctuation stripped             | `test_keyword_extractor.py`  | `"revenue" in keywords`                        |
| 3   | Digits excluded from keywords                            | `test_keyword_extractor.py`  | `"123" not in keywords`                        |
| 4   | Finance topic detected from vocabulary                   | `test_keyword_extractor.py`  | `"finance" in topics`                          |
| 5   | Technology / health topics detected                      | `test_keyword_extractor.py`  | `"technology" in topics`                       |
| 6   | Defaults to `"general"` when no topic matches            | `test_keyword_extractor.py`  | `topics == ["general"]`                        |
| 7   | Multiple topics detected simultaneously                  | `test_keyword_extractor.py`  | `len(topics) == 3`                             |
| 8   | Max 20 keywords returned                                 | `test_keyword_extractor.py`  | `len(keywords) <= 20`                          |
| 9   | Frequency ordering respected                             | `test_keyword_extractor.py`  | `keywords[0] == "revenue"`                     |
| 10  | Empty string returns empty keywords                      | `test_keyword_extractor.py`  | `keywords == []`                               |
| 11  | Positive text classified correctly                       | `test_sentiment_detector.py` | `sentiment == "positive"`                      |
| 12  | Negative text classified correctly                       | `test_sentiment_detector.py` | `sentiment == "negative"`                      |
| 13  | Neutral text classified correctly                        | `test_sentiment_detector.py` | `sentiment == "neutral"`                       |
| 14  | `"not good"` → negative (negation flips positive)        | `test_sentiment_detector.py` | `sentiment == "negative"`                      |
| 15  | `"not terrible"` → positive (negation flips negative)    | `test_sentiment_detector.py` | `sentiment == "positive"`                      |
| 16  | `"not good not bad"` → neutral (two negations cancel)    | `test_sentiment_detector.py` | `sentiment == "neutral"`                       |
| 17  | Empty string → neutral, confidence 0.0                   | `test_sentiment_detector.py` | `confidence == 0.0`                            |
| 18  | Confidence always in `[0.0, 1.0]`                        | `test_sentiment_detector.py` | `0.0 <= confidence <= 1.0`                     |
| 19  | Score and confidence rounded to 2 decimal places         | `test_sentiment_detector.py` | `score == round(score, 2)`                     |
| 20  | Punctuation does not break scoring                       | `test_sentiment_detector.py` | `sentiment == "positive"`                      |
| 21  | Text truncated at 4 000 words                            | `test_text_summariser.py`    | `word_count <= 4000`, ends `[truncated]`       |
| 22  | Text under limit not truncated                           | `test_text_summariser.py`    | `"[truncated]" not in cleaned_text`            |
| 23  | Triple blank lines collapsed to double                   | `test_text_summariser.py`    | `"" not in cleaned_text`                       |
| 24  | Double blank lines preserved                             | `test_text_summariser.py`    | `"" in cleaned_text`                           |
| 25  | Leading/trailing whitespace stripped                     | `test_text_summariser.py`    | `cleaned_text == "hello world"`                |
| 26  | Word count correct                                       | `test_text_summariser.py`    | `word_count == 5`                              |
| 27  | `extract_keywords`and`detect_sentiment`re-exported       | `test_text_summariser.py`    | `callable(extract_keywords)`                   |
| 28  | `.txt`file read as string                                | `test_file_reader.py`        | `isinstance(content, str)`                     |
| 29  | `.md`file read as string, content preserved              | `test_file_reader.py`        | `"# Title" in content`                         |
| 30  | `.json`file parsed to dict                               | `test_file_reader.py`        | `isinstance(content, dict)`                    |
| 31  | `.json`list parsed correctly                             | `test_file_reader.py`        | `content == [1, 2, 3]`                         |
| 32  | `.csv`content is list of dicts                           | `test_file_reader.py`        | `isinstance(content[0], dict)`                 |
| 33  | `.csv`row and column counts correct                      | `test_file_reader.py`        | `row_count == 2`, `col_count == 3`             |
| 34  | Empty`.txt`file returns empty string                     | `test_file_reader.py`        | `content == ""`                                |
| 35  | Unsupported extension raises`ValueError`                 | `test_file_reader.py`        | `assertRaises(ValueError)`                     |
| 36  | Returns`FileReadResult`Pydantic model                    | `test_file_reader.py`        | `isinstance(result, FileReadResult)`           |
| 37  | Column names extracted correctly                         | `test_csv_analyser.py`       | `columns == ["name", "age", "score"]`          |
| 38  | Row and column counts correct                            | `test_csv_analyser.py`       | `row_count == 3`, `col_count == 2`             |
| 39  | Mean / min / max / std present per numeric column        | `test_csv_analyser.py`       | `"mean" in stats["val"]`                       |
| 40  | Mean value correct                                       | `test_csv_analyser.py`       | `stats["val"]["mean"] == 20.0`                 |
| 41  | Min and max correct                                      | `test_csv_analyser.py`       | `min == 10.0`, `max == 30.0`                   |
| 42  | Non-numeric columns excluded from stats                  | `test_csv_analyser.py`       | `"name" not in stats`                          |
| 43  | Missing values counted per column                        | `test_csv_analyser.py`       | `missing["b"] == 1`                            |
| 44  | Zero missing values reported correctly                   | `test_csv_analyser.py`       | `missing["a"] == 0`                            |
| 45  | Stats rounded to 4 decimal places                        | `test_csv_analyser.py`       | `val == round(val, 4)`                         |
| 46  | Single-row CSV handled without error                     | `test_csv_analyser.py`       | `row_count == 1`                               |
| 47  | `report.md`written to disk                               | `test_report_writer.py`      | `Path("report.md").exists()`                   |
| 48  | Disk content matches`markdown`field                      | `test_report_writer.py`      | `disk == result.markdown`                      |
| 49  | `report_path`is absolute                                 | `test_report_writer.py`      | `Path(report_path).is_absolute()`              |
| 50  | File path appears in Markdown output                     | `test_report_writer.py`      | `"myfile.csv" in markdown`                     |
| 51  | Query appears in Markdown output                         | `test_report_writer.py`      | `"What are the totals?" in markdown`           |
| 52  | Summary appears in Markdown output                       | `test_report_writer.py`      | `"Revenue grew by 10%." in markdown`           |
| 53  | Keywords appear in Markdown output                       | `test_report_writer.py`      | `"revenue, profit" in markdown`                |
| 54  | Sentiment appears in Markdown output                     | `test_report_writer.py`      | `"positive (0.85)" in markdown`                |
| 55  | Analysis appears in Markdown output                      | `test_report_writer.py`      | `"Mean value is 42." in markdown`              |
| 56  | Report contains`# File Analysis Report`header            | `test_report_writer.py`      | `assertIn("# File Analysis Report", markdown)` |
| 57  | Empty fields still produce valid report                  | `test_report_writer.py`      | `"# File Analysis Report" in markdown`         |
| 58  | Returns`ReportResult`Pydantic model                      | `test_report_writer.py`      | `isinstance(result, ReportResult)`             |
| 59  | Text-only Gemini response → report produced              | `test_agent_loop.py`         | `"# File Analysis Report" in result`           |
| 60  | Text-only response content included in report            | `test_agent_loop.py`         | `"Direct answer here." in result`              |
| 61  | `write_report`tool call exits loop and returns Markdown  | `test_agent_loop.py`         | `"# File Analysis Report" in result`           |
| 62  | `write_report`call count — send_message called once only | `test_agent_loop.py`         | `send_message.call_count == 1`                 |
| 63  | Max-iteration fallback produces report                   | `test_agent_loop.py`         | `Path("report.md").exists()`                   |
| 64  | Unknown tool name →`{"error": ...}`dict                  | `test_agent_loop.py`         | `"error" in result`                            |
| 65  | Tool exception →`{"error": ...}`dict                     | `test_agent_loop.py`         | `"error" in result`                            |
| 66  | `\_dispatch`returns dict for Pydantic result             | `test_agent_loop.py`         | `isinstance(result, dict)`                     |
| 67  | `run_agent`always returns a string                       | `test_agent_loop.py`         | `isinstance(result, str)`                      |

---

## 11. Deployment Preparation

The system is a self-contained Python package with no server, database, or build step required. Running it involves three steps:

**1. Install dependencies**

```bash
pip install -r requirements.txt
```

This installs `google-generativeai`, `pydantic`, `pandas`, and `pdfplumber`. Python 3.11 or later is required.

**2. Set the API key**

```bash
export GEMINI_API_KEY=your_key_here   # Linux / macOS
set GEMINI_API_KEY=your_key_here      # Windows CMD
$env:GEMINI_API_KEY="your_key_here"   # Windows PowerShell
```

The key is read at startup by `main.py` via `os.environ`; the application exits immediately with a clear message if it is absent.

**3. Run**

```bash
python main.py <file_path> "<query>"
python main.py <file_path> "<query>" --output result.md
```

No containerisation or deployment pipeline is needed for the current scope. If the project were to be packaged for wider distribution the natural next steps would be:

- Add a `pyproject.toml` and expose a `file-agent` console script entry point so users can run `file-agent report.pdf "..."` after `pip install`.
- Add a `Dockerfile` with `COPY . .` + `RUN pip install -r requirements.txt` for reproducible environments.
- Store the API key in a `.env` file and load it with `python-dotenv` so it persists across shell sessions without manual exporting.

---

## 12. Data Conversion & Porting

The agent handles five distinct input formats and applies a format-specific conversion at the `file_reader.py` boundary so that all downstream tools operate on uniform Python types.

### Input → internal representation

| Format         | Conversion                                                  | Internal type |
| -------------- | ----------------------------------------------------------- | ------------- |
| `.txt` / `.md` | `pathlib.Path.read_text()`                                  | `str`         |
| `.pdf`         | `pdfplumber` page-by-page text extraction, joined with `\n` | `str`         |
| `.csv`         | `pandas.read_csv()` → `DataFrame.to_dict(orient="records")` | `list[dict]`  |
| `.json`        | `json.loads(Path.read_text())`                              | `dict`        |

All formats return a `FileReadResult` Pydantic model. The `content` field is typed as `Any` to accommodate both `str` and structured types; downstream tools receive only what they need (text tools get the string, `csv_analyser` re-reads the file path directly with `pd.read_csv`).

### Text normalisation pipeline

Before any text-based tool runs, `text_summariser.summarise()` applies a lightweight normalisation pass:

1. `re.sub(r"\n{3,}", "\n\n", text)` — collapses runs of three or more blank lines to a single blank line, removing PDF extraction artefacts and inconsistent line spacing.
2. `.strip()` — removes leading/trailing whitespace.
3. Word-count truncation to 4 000 words — prevents oversized payloads from being sent to Gemini and keeps tool result JSON within the API's context limits.

### Serialisation for Gemini

Tool results (Pydantic models) cannot be sent directly over the Gemini API. The conversion chain is:

```
Pydantic model  →  .model_dump()  →  dict  →  json.dumps(default=str)  →  JSON string
```

`default=str` handles any non-serialisable values (e.g. `numpy.float64` from pandas, `pathlib.Path` objects) by converting them to their string representation, ensuring the agent loop never raises a serialisation error regardless of what a tool returns.

---

---

# Step 3 – 15.05 (updated)

---

## 9. Testing Process

Testing uses Python's built-in `unittest` framework with five test files covering every module that contains logic. The agent loop tests use `unittest.mock` to patch the Gemini API, so the full suite runs without a live `GEMINI_API_KEY`.

**Run all tests:**

```bash
pip install pytest        # one-time
pytest tests/ -v
```

**Test files:**

| File                               | Module under test             | Tests  |
| ---------------------------------- | ----------------------------- | ------ |
| `tests/test_keyword_extractor.py`  | `tools/keyword_extractor.py`  | 13     |
| `tests/test_sentiment_detector.py` | `tools/sentiment_detector.py` | 13     |
| `tests/test_text_summariser.py`    | `tools/text_summariser.py`    | 10     |
| `tests/test_file_reader.py`        | `tools/file_reader.py`        | 15     |
| `tests/test_csv_analyser.py`       | `tools/csv_analyser.py`       | 11     |
| `tests/test_report_writer.py`      | `tools/report_writer.py`      | 13     |
| `tests/test_agent_loop.py`         | `agent/loop.py`               | 9      |
| **Total**                          |                               | **74** |

**Approach by layer:**

- **Unit tests (tools)** — each tool function is called directly with controlled inputs. Temporary files are written to `tempfile.mkdtemp()` directories and cleaned up via `addCleanup(os.unlink, ...)` so no test artefacts persist on disk.
- **Schema tests** — every tool test asserts the return value is an instance of its declared Pydantic model, catching any `model_dump` contract breakage early.
- **Edge-case tests** — each tool has at least one empty-input test, one malformed-input test, and boundary tests (e.g. exactly 4 000 words, single-row CSVs, all-stop-word strings).
- **Integration tests (agent loop)** — `unittest.mock.patch` replaces `genai.GenerativeModel` with a `MagicMock` whose `chat.send_message.side_effect` returns pre-built response objects. This lets the three exit paths (text-only fallback, `write_report` call, max-iteration fallback) and `_dispatch` error handling all be tested without touching the network.

---

## 10. Test Scenarios

| #   | Scenario                                              | File                         | Key assertion                                 |
| --- | ----------------------------------------------------- | ---------------------------- | --------------------------------------------- |
| 1   | Stop words produce empty keyword list                 | `test_keyword_extractor.py`  | `keywords == []`                              |
| 2   | Keywords lowercased and punctuation stripped          | `test_keyword_extractor.py`  | `"revenue" in keywords`                       |
| 3   | Finance topic detected from vocabulary                | `test_keyword_extractor.py`  | `"finance" in topics`                         |
| 4   | Defaults to `"general"` topic                         | `test_keyword_extractor.py`  | `topics == ["general"]`                       |
| 5   | Max 20 keywords returned                              | `test_keyword_extractor.py`  | `len(keywords) <= 20`                         |
| 6   | Frequency ordering respected                          | `test_keyword_extractor.py`  | `keywords[0] == "revenue"`                    |
| 7   | Positive text classified correctly                    | `test_sentiment_detector.py` | `sentiment == "positive"`                     |
| 8   | Negative text classified correctly                    | `test_sentiment_detector.py` | `sentiment == "negative"`                     |
| 9   | `"not good"` → negative (negation)                    | `test_sentiment_detector.py` | `sentiment == "negative"`                     |
| 10  | `"not terrible"` → positive (negation)                | `test_sentiment_detector.py` | `sentiment == "positive"`                     |
| 11  | `"not good not bad"` → neutral (two negations cancel) | `test_sentiment_detector.py` | `sentiment == "neutral"`                      |
| 12  | Empty string → neutral, confidence 0.0                | `test_sentiment_detector.py` | `confidence == 0.0`                           |
| 13  | Confidence always in [0, 1]                           | `test_sentiment_detector.py` | `0.0 <= confidence <= 1.0`                    |
| 14  | Text truncated at 4 000 words                         | `test_text_summariser.py`    | `word_count <= 4000`, ends with `[truncated]` |
| 15  | Text under limit not truncated                        | `test_text_summariser.py`    | `"[truncated]" not in cleaned_text`           |
| 16  | Triple blank lines collapsed                          | `test_text_summariser.py`    | `"\n\n\n" not in cleaned_text`                |
| 17  | `extract_keywords` and `detect_sentiment` re-exported | `test_text_summariser.py`    | `callable(extract_keywords)`                  |
| 18  | `.txt` file content read as string                    | `test_file_reader.py`        | `isinstance(content, str)`                    |
| 19  | `.json` file parsed to dict                           | `test_file_reader.py`        | `isinstance(content, dict)`                   |
| 20  | `.csv` file returns list of dicts + row/col counts    | `test_file_reader.py`        | `row_count == 2`, `col_count == 3`            |
| 21  | Unsupported extension raises `ValueError`             | `test_file_reader.py`        | `assertRaises(ValueError)`                    |
| 22  | CSV mean/min/max/std correct                          | `test_csv_analyser.py`       | `stats["val"]["mean"] == 20.0`                |
| 23  | Non-numeric columns excluded from stats               | `test_csv_analyser.py`       | `"name" not in stats`                         |
| 24  | Missing values counted per column                     | `test_csv_analyser.py`       | `missing["b"] == 1`                           |
| 25  | Stats rounded to 4 decimal places                     | `test_csv_analyser.py`       | `val == round(val, 4)`                        |
| 26  | `report.md` written to disk                           | `test_report_writer.py`      | `Path("report.md").exists()`                  |
| 27  | Disk content matches `markdown` field                 | `test_report_writer.py`      | `disk == result.markdown`                     |
| 28  | `report_path` is absolute                             | `test_report_writer.py`      | `Path(report_path).is_absolute()`             |
| 29  | All input fields appear in Markdown output            | `test_report_writer.py`      | `assertIn` for each field                     |
| 30  | Empty fields still produce valid report               | `test_report_writer.py`      | `"# File Analysis Report" in markdown`        |
| 31  | Text-only Gemini response → report produced           | `test_agent_loop.py`         | `"# File Analysis Report" in result`          |
| 32  | `write_report` tool call exits loop immediately       | `test_agent_loop.py`         | `send_message.call_count == 2`                |
| 33  | Max-iteration fallback → report produced              | `test_agent_loop.py`         | `Path("report.md").exists()`                  |
| 34  | Unknown tool name → `{"error": ...}` dict             | `test_agent_loop.py`         | `"error" in result`                           |
| 35  | Tool exception → `{"error": ...}` dict                | `test_agent_loop.py`         | `"error" in result`                           |
| 36  | `_dispatch` returns dict for Pydantic result          | `test_agent_loop.py`         | `isinstance(result, dict)`                    |
| 37  | `run_agent` always returns a string                   | `test_agent_loop.py`         | `isinstance(result, str)`                     |

---

## 11. Deployment Preparation

The system is a self-contained Python package with no server, database, or build step required. Running it involves three steps:

**1. Install dependencies**

```bash
pip install -r requirements.txt
```

This installs `google-generativeai`, `pydantic`, `pandas`, and `pdfplumber`. Python 3.11 or later is required.

**2. Set the API key**

```bash
export GEMINI_API_KEY=your_key_here   # Linux / macOS
set GEMINI_API_KEY=your_key_here      # Windows CMD
$env:GEMINI_API_KEY="your_key_here"   # Windows PowerShell
```

**3. Run**

```bash
python main.py <file_path> "<query>"
python main.py <file_path> "<query>" --output result.md
```

For wider distribution, natural next steps would be adding a `pyproject.toml` console script entry point, a `Dockerfile`, and `python-dotenv` for persistent key management.

---

## 12. Data Conversion & Porting

### Input → internal representation

| Format         | Conversion                                                  | Internal type |
| -------------- | ----------------------------------------------------------- | ------------- |
| `.txt` / `.md` | `pathlib.Path.read_text()`                                  | `str`         |
| `.pdf`         | `pdfplumber` page-by-page extraction joined with `\n`       | `str`         |
| `.csv`         | `pandas.read_csv()` → `DataFrame.to_dict(orient="records")` | `list[dict]`  |
| `.json`        | `json.loads(Path.read_text())`                              | `dict`        |

### Text normalisation pipeline

`text_summariser.summarise()` applies three steps before any tool receives text:

1. `re.sub(r"\n{3,}", "\n\n", text)` — collapses excessive blank lines
2. `.strip()` — removes leading/trailing whitespace
3. Truncation to 4 000 words — keeps Gemini payloads within context limits

### Serialisation for Gemini

```
Pydantic model  →  .model_dump()  →  dict  →  json.dumps(default=str)  →  JSON string
```

`default=str` handles non-serialisable values (`numpy.float64`, `pathlib.Path`) without raising.
