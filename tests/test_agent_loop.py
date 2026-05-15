import sys, pathlib, tempfile, os

sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))

import unittest
from unittest.mock import patch, MagicMock

ENV = {"GEMINI_API_KEY": "test-key"}


def _make_text_response(text):
    """Gemini response that contains only a text part (no tool calls)."""
    part = MagicMock()
    part.function_call.name = ""
    part.text = text
    response = MagicMock()
    response.parts = [part]
    return response


def _make_tool_call_response(tool_name, args: dict):
    """Gemini response that requests a single tool call."""
    fc = MagicMock()
    fc.name = tool_name
    fc.args = args
    part = MagicMock()
    part.function_call = fc
    part.function_call.name = tool_name
    response = MagicMock()
    response.parts = [part]
    return response


class TestAgentLoop(unittest.TestCase):

    def setUp(self):
        self._orig_dir = os.getcwd()
        self._tmp_dir = tempfile.mkdtemp()
        os.chdir(self._tmp_dir)
        pathlib.Path("sample.txt").write_text("hello world")

    def tearDown(self):
        os.chdir(self._orig_dir)

    def _patch_gemini(self, side_effects):
        """Patch GenerativeModel so chat.send_message returns side_effects in order."""
        mock_chat = MagicMock()
        mock_chat.send_message.side_effect = side_effects
        mock_model = MagicMock()
        mock_model.start_chat.return_value = mock_chat
        return patch("agent.loop.genai.GenerativeModel", return_value=mock_model)

    # ── text-only fallback ────────────────────────────────────────────────────
    def test_text_only_response_produces_report(self):
        responses = [_make_text_response("Gemini answered directly.")]
        with patch.dict("os.environ", ENV), patch(
            "agent.loop.genai.configure"
        ), self._patch_gemini(responses):
            from agent import loop as L

            result = L.run_agent("sample.txt", "What is this?")
        self.assertIn("# File Analysis Report", result)
        self.assertTrue(pathlib.Path("report.md").exists())

    def test_text_only_response_includes_gemini_text(self):
        responses = [_make_text_response("Direct answer here.")]
        with patch.dict("os.environ", ENV), patch(
            "agent.loop.genai.configure"
        ), self._patch_gemini(responses):
            from agent import loop as L

            result = L.run_agent("sample.txt", "q?")
        self.assertIn("Direct answer here.", result)

    # ── write_report tool call ────────────────────────────────────────────────
    def test_write_report_tool_call_exits_loop(self):
        wr_args = dict(
            file_path="sample.txt",
            query="q?",
            summary="s",
            keywords="k",
            sentiment="pos",
            analysis="a",
        )
        responses = [_make_tool_call_response("write_report", wr_args)]
        with patch.dict("os.environ", ENV), patch(
            "agent.loop.genai.configure"
        ), self._patch_gemini(responses):
            from agent import loop as L

            result = L.run_agent("sample.txt", "q?")
        self.assertIn("# File Analysis Report", result)

    def test_write_report_tool_call_stops_further_api_calls(self):
        wr_args = dict(
            file_path="sample.txt",
            query="q?",
            summary="s",
            keywords="k",
            sentiment="pos",
            analysis="a",
        )
        mock_chat = MagicMock()
        mock_chat.send_message.side_effect = [
            _make_tool_call_response("write_report", wr_args)
        ]
        mock_model = MagicMock()
        mock_model.start_chat.return_value = mock_chat
        with patch.dict("os.environ", ENV), patch("agent.loop.genai.configure"), patch(
            "agent.loop.genai.GenerativeModel", return_value=mock_model
        ):
            from agent import loop as L

            L.run_agent("sample.txt", "q?")
        # write_report triggers immediate return — tool result is never sent back,
        # so send_message is called exactly once (the initial query only)
        self.assertEqual(mock_chat.send_message.call_count, 1)

    # ── max-iteration fallback ────────────────────────────────────────────────
    def test_max_iteration_fallback_produces_report(self):
        read_args = {"file_path": "sample.txt"}
        responses = [_make_tool_call_response("read_file", read_args)] * 15
        with patch.dict("os.environ", ENV), patch(
            "agent.loop.genai.configure"
        ), self._patch_gemini(responses):
            from agent import loop as L

            result = L.run_agent("sample.txt", "q?", max_iterations=3)
        self.assertIn("# File Analysis Report", result)
        self.assertTrue(pathlib.Path("report.md").exists())

    # ── _dispatch error handling ──────────────────────────────────────────────
    def test_dispatch_unknown_tool_returns_error_dict(self):
        with patch.dict("os.environ", ENV), patch("agent.loop.genai.configure"):
            from agent.loop import _dispatch
        call = MagicMock()
        call.name = "nonexistent_tool"
        call.args = {}
        result = _dispatch(call)
        self.assertIn("error", result)

    def test_dispatch_tool_exception_returns_error_dict(self):
        with patch.dict("os.environ", ENV), patch("agent.loop.genai.configure"):
            from agent.loop import _dispatch
        call = MagicMock()
        call.name = "read_file"
        call.args = {"file_path": "/nonexistent/path/file.txt"}
        result = _dispatch(call)
        self.assertIn("error", result)

    def test_dispatch_returns_model_dump_for_pydantic_result(self):
        with patch.dict("os.environ", ENV), patch("agent.loop.genai.configure"):
            from agent.loop import _dispatch
        call = MagicMock()
        call.name = "detect_sentiment"
        call.args = {"text": "great excellent"}
        result = _dispatch(call)
        self.assertIsInstance(result, dict)
        self.assertIn("sentiment", result)

    # ── return type ───────────────────────────────────────────────────────────
    def test_run_agent_always_returns_string(self):
        responses = [_make_text_response("ok")]
        with patch.dict("os.environ", ENV), patch(
            "agent.loop.genai.configure"
        ), self._patch_gemini(responses):
            from agent import loop as L

            result = L.run_agent("sample.txt", "q?")
        self.assertIsInstance(result, str)


if __name__ == "__main__":
    unittest.main()
