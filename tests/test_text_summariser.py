import sys, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))

import unittest
from tools.text_summariser import summarise


class TestSummarise(unittest.TestCase):

    def test_returns_summary_result_type(self):
        from models.schemas import SummaryResult

        self.assertIsInstance(summarise("hello world"), SummaryResult)

    def test_word_count_correct(self):
        result = summarise("one two three four five")
        self.assertEqual(result.word_count, 5)

    def test_strips_leading_trailing_whitespace(self):
        result = summarise("   hello world   ")
        self.assertEqual(result.cleaned_text, "hello world")

    def test_collapses_excessive_blank_lines(self):
        result = summarise("line one\n\n\n\nline two")
        self.assertNotIn("\n\n\n", result.cleaned_text)

    def test_two_blank_lines_preserved(self):
        result = summarise("line one\n\nline two")
        self.assertIn("\n\n", result.cleaned_text)

    def test_truncation_at_4000_words(self):
        long_text = " ".join(["word"] * 5000)
        result = summarise(long_text)
        self.assertLessEqual(result.word_count, 4000)
        self.assertTrue(result.cleaned_text.endswith("[truncated]"))

    def test_no_truncation_under_limit(self):
        text = " ".join(["word"] * 100)
        result = summarise(text)
        self.assertEqual(result.word_count, 100)
        self.assertNotIn("[truncated]", result.cleaned_text)

    def test_empty_string(self):
        result = summarise("")
        self.assertEqual(result.word_count, 0)
        self.assertEqual(result.cleaned_text, "")

    def test_reexports_extract_keywords(self):
        from tools.text_summariser import extract_keywords

        self.assertTrue(callable(extract_keywords))

    def test_reexports_detect_sentiment(self):
        from tools.text_summariser import detect_sentiment

        self.assertTrue(callable(detect_sentiment))


if __name__ == "__main__":
    unittest.main()
