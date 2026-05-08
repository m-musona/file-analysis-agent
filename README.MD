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
