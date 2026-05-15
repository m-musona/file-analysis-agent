import sys, pathlib, tempfile, os

sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))

import unittest
from tools.csv_analyser import analyse_csv


class TestAnalyseCSV(unittest.TestCase):

    def _csv(self, content):
        f = tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w")
        f.write(content)
        f.close()
        self.addCleanup(os.unlink, f.name)
        return f.name

    def test_returns_csv_analysis_result(self):
        from models.schemas import CSVAnalysisResult

        path = self._csv("a,b\n1,2\n3,4")
        self.assertIsInstance(analyse_csv(path), CSVAnalysisResult)

    def test_column_names(self):
        path = self._csv("name,age,score\nAlice,30,90\nBob,25,85")
        result = analyse_csv(path)
        self.assertEqual(result.columns, ["name", "age", "score"])

    def test_row_and_col_count(self):
        path = self._csv("x,y\n1,2\n3,4\n5,6")
        result = analyse_csv(path)
        self.assertEqual(result.row_count, 3)
        self.assertEqual(result.col_count, 2)

    def test_numeric_stats_present(self):
        path = self._csv("val\n10\n20\n30")
        stats = analyse_csv(path).stats
        self.assertIn("val", stats)
        self.assertIn("mean", stats["val"])
        self.assertIn("min", stats["val"])
        self.assertIn("max", stats["val"])
        self.assertIn("std", stats["val"])

    def test_mean_correct(self):
        path = self._csv("val\n10\n20\n30")
        self.assertEqual(analyse_csv(path).stats["val"]["mean"], 20.0)

    def test_min_max_correct(self):
        path = self._csv("val\n10\n20\n30")
        stats = analyse_csv(path).stats["val"]
        self.assertEqual(stats["min"], 10.0)
        self.assertEqual(stats["max"], 30.0)

    def test_non_numeric_columns_excluded_from_stats(self):
        path = self._csv("name,score\nAlice,90\nBob,80")
        stats = analyse_csv(path).stats
        self.assertNotIn("name", stats)
        self.assertIn("score", stats)

    def test_missing_values_counted(self):
        path = self._csv("a,b\n1,\n3,4")
        result = analyse_csv(path)
        self.assertEqual(result.missing["b"], 1)

    def test_no_missing_values(self):
        path = self._csv("a,b\n1,2\n3,4")
        result = analyse_csv(path)
        self.assertEqual(result.missing["a"], 0)
        self.assertEqual(result.missing["b"], 0)

    def test_stats_rounded_to_four_decimal_places(self):
        path = self._csv("val\n1\n2\n3")
        stats = analyse_csv(path).stats["val"]
        for key in ("mean", "min", "max", "std"):
            self.assertEqual(stats[key], round(stats[key], 4))

    def test_single_row(self):
        path = self._csv("val\n42")
        result = analyse_csv(path)
        self.assertEqual(result.row_count, 1)
        self.assertEqual(result.stats["val"]["mean"], 42.0)


if __name__ == "__main__":
    unittest.main()
