import os, json
import google.generativeai as genai
from tools.file_reader import read_file
from tools.text_summariser import summarise
from tools.keyword_extractor import extract_keywords
from tools.sentiment_detector import detect_sentiment
from tools.csv_analyser import analyse_csv
from tools.report_writer import write_report

TOOLS = {
    "read_file": (read_file, {"file_path": {"type": "string"}}),
    "summarise": (summarise, {"text": {"type": "string"}}),
    "extract_keywords": (extract_keywords, {"text": {"type": "string"}}),
    "detect_sentiment": (detect_sentiment, {"text": {"type": "string"}}),
    "analyse_csv": (analyse_csv, {"file_path": {"type": "string"}}),
    "write_report": (
        write_report,
        {
            "file_path": {"type": "string"},
            "query": {"type": "string"},
            "summary": {"type": "string"},
            "keywords": {"type": "string"},
            "sentiment": {"type": "string"},
            "analysis": {"type": "string"},
        },
    ),
}

TOOL_DECLARATIONS = [
    genai.protos.Tool(
        function_declarations=[
            genai.protos.FunctionDeclaration(
                name=name,
                description=fn.__doc__ or name,
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        k: genai.protos.Schema(type=genai.protos.Type.STRING)
                        for k in params
                    },
                    required=list(params),
                ),
            )
            for name, (fn, params) in TOOLS.items()
        ]
    )
]

SYSTEM_PROMPT = (
    "You are a file analysis agent. Use the available tools to read, analyse, and summarise the file. "
    "Always finish by calling write_report with all findings compiled — "
    "its markdown field is the final answer returned to the user."
)


def _dispatch(call) -> dict:
    fn, _ = TOOLS.get(call.name, (None, None))
    if fn is None:
        return {"error": f"Unknown tool: {call.name}"}
    try:
        result = fn(**{k: v for k, v in call.args.items()})
        return result.model_dump() if hasattr(result, "model_dump") else result
    except Exception as e:
        return {"error": str(e)}


def run_agent(file_path: str, query: str, max_iterations: int = 10) -> str:
    """Run the agent loop; always returns a structured Markdown report string."""
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel(
        "gemini-1.5-flash", tools=TOOL_DECLARATIONS, system_instruction=SYSTEM_PROMPT
    )
    chat = model.start_chat()
    response = chat.send_message(f"File: {file_path}\nQuery: {query}")

    for _ in range(max_iterations):
        calls = [p.function_call for p in response.parts if p.function_call.name]
        if not calls:
            # Gemini gave a text reply with no tool call — wrap it as a minimal report
            text = "".join(p.text for p in response.parts if p.text)
            result = write_report(file_path, query, text, "", "", "")
            return result.markdown

        tool_results, last_report = [], None
        for call in calls:
            result = _dispatch(call)
            # Capture report markdown if write_report was called
            if call.name == "write_report" and "markdown" in result:
                last_report = result["markdown"]
            tool_results.append(
                genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=call.name,
                        response={"result": json.dumps(result, default=str)},
                    )
                )
            )

        if last_report:
            return last_report  # report generated — return immediately

        response = chat.send_message(tool_results)

    # Safety fallback: generate a minimal report with whatever the last response text was
    fallback_text = "Agent reached maximum iterations."
    result = write_report(file_path, query, fallback_text, "", "", "")
    return result.markdown
