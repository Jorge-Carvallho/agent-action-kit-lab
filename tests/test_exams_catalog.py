"""Validação da base mock de exames (AI-008)."""
from __future__ import annotations

import unittest

from data.load_mock_catalog import load_mock_catalog, load_mock_exams


class TestExamsCatalog(unittest.TestCase):
    def test_at_least_100_records(self) -> None:
        exams = load_mock_exams()
        self.assertGreaterEqual(len(exams), 100)

    def test_schema_and_unique_codes(self) -> None:
        raw = load_mock_catalog()
        self.assertEqual(raw.get("schema_version"), 1)
        self.assertIn("exams", raw)
        codes = [e["code"] for e in raw["exams"]]
        self.assertEqual(len(codes), len(set(codes)), "códigos duplicados")

    def test_each_record_fields(self) -> None:
        for ex in load_mock_exams():
            self.assertIn("code", ex)
            self.assertIn("name", ex)
            self.assertIn("short_description", ex)
            self.assertIn("synonyms", ex)
            self.assertIsInstance(ex["synonyms"], list)
            self.assertTrue(str(ex["code"]).strip())
            self.assertTrue(str(ex["name"]).strip())


if __name__ == "__main__":
    unittest.main()
