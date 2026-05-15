import sys, pathlib, json, tempfile, os

sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))

import unittest
from tools.file_reader import read_file


class TestReadFile(unittest.TestCase):

    def _tmp(self, suffix, content, mode="w"):
        f = tempfile.NamedTemporaryFile(suffix=suffix, delete=False, mode=mode)
        f.write(content)
        f.close()
        self.addCleanup(os.unlink, f.name)
        return f.name

    # ── .txt ────────────────────────────────────────────────────────────────
    def test_txt_file_type(self):
        path = self._tmp(".txt", "hello world")
        self.assertEqual(read_file(path).file_type, "txt")

    def test_txt_content_string(self):
        path = self._tmp(".txt", "hello world")
        self.assertEqual(read_file(path).content, "hello world")

    def test_txt_empty_file(self):
        path = self._tmp(".txt", "")
        self.assertEqual(read_file(path).content, "")

    # ── .md ─────────────────────────────────────────────────────────────────
    def test_md_file_type(self):
        path = self._tmp(".md", "# Title\ncontent")
        self.assertEqual(read_file(path).file_type, "md")

    def test_md_content_preserved(self):
        path = self._tmp(".md", "# Title\ncontent")
        self.assertIn("# Title", read_file(path).content)

    # ── .json ────────────────────────────────────────────────────────────────
    def test_json_file_type(self):
        path = self._tmp(".json", json.dumps({"key": "value"}))
        self.assertEqual(read_file(path).file_type, "json")

    def test_json_content_is_dict(self):
        path = self._tmp(".json", json.dumps({"key": "value"}))
        self.assertIsInstance(read_file(path).content, dict)

    def test_json_content_values(self):
        path = self._tmp(".json", json.dumps({"name": "agent", "version": 2}))
        content = read_file(path).content
        self.assertEqual(content["name"], "agent")
        self.assertEqual(content["version"], 2)

    def test_json_list_content(self):
        path = self._tmp(".json", json.dumps([1, 2, 3]))
        self.assertEqual(read_file(path).content, [1, 2, 3])

    # ── .csv ─────────────────────────────────────────────────────────────────
    def test_csv_file_type(self):
        path = self._tmp(".csv", "a,b\n1,2\n3,4")
        self.assertEqual(read_file(path).file_type, "csv")

    def test_csv_content_is_list_of_dicts(self):
        path = self._tmp(".csv", "a,b\n1,2\n3,4")
        content = read_file(path).content
        self.assertIsInstance(content, list)
        self.assertIsInstance(content[0], dict)

    def test_csv_row_and_col_counts(self):
        path = self._tmp(".csv", "x,y,z\n1,2,3\n4,5,6")
        result = read_file(path)
        self.assertEqual(result.row_count, 2)
        self.assertEqual(result.col_count, 3)

    # ── unsupported type ─────────────────────────────────────────────────────
    def test_unsupported_extension_raises(self):
        path = self._tmp(".xyz", "data")
        with self.assertRaises(ValueError):
            read_file(path)

    # ── FileReadResult schema ────────────────────────────────────────────────
    def test_returns_file_read_result(self):
        from models.schemas import FileReadResult

        path = self._tmp(".txt", "test")
        self.assertIsInstance(read_file(path), FileReadResult)


if __name__ == "__main__":
    unittest.main()
