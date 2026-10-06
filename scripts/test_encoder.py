"""Keyword encoder: negation, topic word lists, overlapping phrases."""
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
os.environ['NDIM_DATA_DIR'] = tempfile.mkdtemp(prefix='nidm-encoder-')
os.environ['NDIM_SENTIMENT_MODEL'] = '/nonexistent'
from app.encoding import keyword_counts, keyword_lists, KEYWORDS, TOPIC_KEYWORDS


class EncoderTests(unittest.TestCase):
    def test_negated_trust_counts_as_distrust(self):
        for text in ('i do not trust the subsidy', 'nobody trusted the seller', 'we no longer trust them', 'i never believe them'):
            counts = keyword_counts(text)
            self.assertEqual((counts['trust_positive'], counts['trust_negative']), (0, 1), text)
        self.assertEqual(keyword_counts('i trust the nurse')['trust_positive'], 1)

    def test_negation_looks_three_words_back_only(self):
        counts = keyword_counts('it is not that people here in the village trust it')
        self.assertEqual(counts['trust_positive'], 1)

    def test_mixed_stances_are_both_counted(self):
        counts = keyword_counts('i do not trust the vaccine, but i trust the nurse', 'vaccines')
        self.assertEqual((counts['trust_positive'], counts['trust_negative']), (2, 1))

    def test_negated_benefit_counts_as_refusal(self):
        counts = keyword_counts('it did not save money')
        self.assertEqual((counts['positive_stance'], counts['negative_stance']), (0, 1))

    def test_topic_lists_add_to_the_cooking_lists(self):
        self.assertEqual(keyword_counts('they say it causes infertility')['misinformation'], 0)
        self.assertEqual(keyword_counts('they say it causes infertility', 'vaccines')['misinformation'], 1)
        for topic, extra in TOPIC_KEYWORDS.items():
            merged = keyword_lists(topic)
            for name, words in KEYWORDS.items():
                self.assertEqual(merged[name][:len(words)], words, (topic, name))  # cooking lists unchanged, first

    def test_a_phrase_inside_a_longer_match_counts_once(self):
        self.assertEqual(keyword_counts('the community health worker came', 'vaccines')['trust_positive'], 1)
        self.assertEqual(keyword_counts('the health worker came')['trust_positive'], 1)


if __name__ == '__main__':
    unittest.main()
