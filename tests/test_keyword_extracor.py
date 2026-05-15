import sys, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))

import unittest
from tools.keyword_extractor import extract_keywords


class TestExtractKeywords(unittest.TestCase):

    def test_returns_keyword_result_type(self):
        from models.schemas import KeywordResult

        self.assertIsInstance(extract_keywords("data software cloud"), KeywordResult)

    def test_stop_words_excluded(self):
        result = extract_keywords("the and or but is are was")
        self.assertEqual(
            result.keywords, [], "All stop words — keywords should be empty"
        )

    def test_keywords_are_lowercased(self):
        result = extract_keywords("Revenue PROFIT Loss")
        self.assertTrue(all(k == k.lower() for k in result.keywords))

    def test_punctuation_stripped(self):
        result = extract_keywords("revenue, profit! loss.")
        self.assertIn("revenue", result.keywords)
        self.assertIn("profit", result.keywords)
        self.assertIn("loss", result.keywords)

    def test_digits_excluded(self):
        result = extract_keywords("123 456 revenue")
        self.assertNotIn("123", result.keywords)
        self.assertNotIn("456", result.keywords)

    def test_topic_finance_detected(self):
        result = extract_keywords("revenue profit budget sales market investment")
        self.assertIn("finance", result.topics)

    def test_topic_technology_detected(self):
        result = extract_keywords("software api cloud server network algorithm")
        self.assertIn("technology", result.topics)

    def test_topic_health_detected(self):
        result = extract_keywords("patient doctor hospital treatment medicine")
        self.assertIn("health", result.topics)

    def test_topic_defaults_to_general(self):
        result = extract_keywords("random words without domain vocabulary")
        self.assertIn("general", result.topics)

    def test_max_twenty_keywords(self):
        text = " ".join(f"word{i}" for i in range(50))
        result = extract_keywords(text)
        self.assertLessEqual(len(result.keywords), 20)

    def test_empty_string(self):
        result = extract_keywords("")
        self.assertEqual(result.keywords, [])
        self.assertEqual(result.topics, ["general"])

    def test_frequency_ordering(self):
        result = extract_keywords("revenue revenue revenue profit profit loss")
        self.assertEqual(result.keywords[0], "revenue")
        self.assertEqual(result.keywords[1], "profit")

    def test_multiple_topics_detected(self):
        result = extract_keywords("revenue profit software api patient doctor")
        self.assertIn("finance", result.topics)
        self.assertIn("technology", result.topics)
        self.assertIn("health", result.topics)


if __name__ == "__main__":
    unittest.main()
