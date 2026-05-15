import sys, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))

import unittest
from tools.sentiment_detector import detect_sentiment


class TestDetectSentiment(unittest.TestCase):

    def test_returns_sentiment_result_type(self):
        from models.schemas import SentimentResult

        self.assertIsInstance(detect_sentiment("good"), SentimentResult)

    def test_positive_text(self):
        result = detect_sentiment("great excellent wonderful fantastic")
        self.assertEqual(result.sentiment, "positive")

    def test_negative_text(self):
        result = detect_sentiment("terrible awful bad worst hate")
        self.assertEqual(result.sentiment, "negative")

    def test_neutral_text(self):
        result = detect_sentiment("the cat sat on the mat")
        self.assertEqual(result.sentiment, "neutral")

    def test_negation_flips_positive(self):
        result = detect_sentiment("not good")
        self.assertEqual(result.sentiment, "negative")

    def test_negation_flips_negative(self):
        result = detect_sentiment("not terrible")
        self.assertEqual(result.sentiment, "positive")

    def test_confidence_between_zero_and_one(self):
        for text in ["great", "bad", "not good", "the cat sat"]:
            result = detect_sentiment(text)
            self.assertGreaterEqual(result.confidence, 0.0)
            self.assertLessEqual(result.confidence, 1.0)

    def test_score_normalised(self):
        result = detect_sentiment("good bad")  # score = 0
        self.assertEqual(result.score, 0.0)

    def test_empty_string_is_neutral(self):
        result = detect_sentiment("")
        self.assertEqual(result.sentiment, "neutral")
        self.assertEqual(result.confidence, 0.0)

    def test_punctuation_does_not_break_scoring(self):
        result = detect_sentiment("great! excellent. wonderful,")
        self.assertEqual(result.sentiment, "positive")

    def test_mixed_case_handled(self):
        result = detect_sentiment("GREAT excellent BAD")
        # 2 pos, 1 neg → positive
        self.assertEqual(result.sentiment, "positive")

    def test_multiple_negators_independent(self):
        # "not good not bad" — each negator flips only the next word
        result = detect_sentiment("not good not bad")
        self.assertEqual(result.sentiment, "neutral")  # -1 + 1 = 0

    def test_score_rounds_to_two_decimal_places(self):
        result = detect_sentiment("good bad good")
        self.assertEqual(result.score, round(result.score, 2))
        self.assertEqual(result.confidence, round(result.confidence, 2))


if __name__ == "__main__":
    unittest.main()
