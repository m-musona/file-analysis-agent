import sys, pathlib, tempfile, os

sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))

import unittest
from tools.report_writer import write_report


class TestWriteReport(unittest.TestCase):

    def setUp(self):
        # Run each test in a temp directory so report.md doesn't pollute the project root
        self._orig_dir = os.getcwd()
        self._tmp_dir = tempfile.mkdtemp()
        os.chdir(self._tmp_dir)

    def tearDown(self):
        os.chdir(self._orig_dir)

    def _call(self, **kwargs):
        defaults = dict(
            file_path="sample.txt",
            query="What is this?",
            summary="A summary.",
            keywords="word1, word2",
            sentiment="positive",
            analysis="Some analysis.",
        )
        defaults.update(kwargs)
        return write_report(**defaults)

    def test_returns_report_result(self):
        from models.schemas import ReportResult

        self.assertIsInstance(self._call(), ReportResult)

    def test_report_md_written_to_disk(self):
        self._call()
        self.assertTrue(pathlib.Path("report.md").exists())

    def test_markdown_field_not_empty(self):
        result = self._call()
        self.assertTrue(len(result.markdown) > 0)

    def test_report_path_is_absolute(self):
        result = self._call()
        self.assertTrue(pathlib.Path(result.report_path).is_absolute())

    def test_file_path_in_markdown(self):
        result = self._call(file_path="data/myfile.csv")
        self.assertIn("myfile.csv", result.markdown)

    def test_query_in_markdown(self):
        result = self._call(query="What are the totals?")
        self.assertIn("What are the totals?", result.markdown)

    def test_summary_in_markdown(self):
        result = self._call(summary="Revenue grew by 10%.")
        self.assertIn("Revenue grew by 10%.", result.markdown)

    def test_keywords_in_markdown(self):
        result = self._call(keywords="revenue, profit, growth")
        self.assertIn("revenue, profit, growth", result.markdown)

    def test_sentiment_in_markdown(self):
        result = self._call(sentiment="positive (0.85)")
        self.assertIn("positive (0.85)", result.markdown)

    def test_analysis_in_markdown(self):
        result = self._call(analysis="Mean value is 42.")
        self.assertIn("Mean value is 42.", result.markdown)

    def test_markdown_contains_generated_header(self):
        result = self._call()
        self.assertIn("# File Analysis Report", result.markdown)

    def test_disk_content_matches_markdown_field(self):
        result = self._call()
        disk_content = pathlib.Path("report.md").read_text()
        self.assertEqual(disk_content, result.markdown)

    def test_empty_fields_produce_valid_report(self):
        result = write_report("f.txt", "q?", "", "", "", "")
        self.assertIn("# File Analysis Report", result.markdown)
        self.assertTrue(pathlib.Path("report.md").exists())


if __name__ == "__main__":
    unittest.main()
