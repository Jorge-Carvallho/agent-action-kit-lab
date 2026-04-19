"""Testes do motor de matching RAG (sem subir servidor HTTP)."""
from __future__ import annotations

import unittest

from mcp_rag.exam_matcher import match_single_exam, resolve_exam_names


class TestExamMatcher(unittest.TestCase):
    def test_synonym_hmg(self) -> None:
        r = match_single_exam("HMG")
        self.assertTrue(r["matched"])
        self.assertEqual(r.get("code"), "LAB-F0001")
        self.assertIn("Hemograma", r.get("canonical_name", ""))
        self.assertEqual(r.get("confidence"), "high")

    def test_substring_glicemia(self) -> None:
        r = match_single_exam("glicemia em jejum")
        self.assertTrue(r["matched"])
        self.assertEqual(r.get("code"), "LAB-F0003")

    def test_unmatched(self) -> None:
        r = match_single_exam("xyz_nao_existe_no_catalogo_qwerty")
        self.assertFalse(r["matched"])
        self.assertIsNone(r.get("code"))

    def test_resolve_multiple(self) -> None:
        out = resolve_exam_names(["HbA1c", "creatinina", ""])
        self.assertIn("catalog_id", out)
        self.assertEqual(len(out["results"]), 3)
        self.assertTrue(out["results"][0]["matched"])
        self.assertTrue(out["results"][1]["matched"])
        self.assertFalse(out["results"][2]["matched"])

    def test_accent_insensitive(self) -> None:
        r = match_single_exam("glicose jejum")
        self.assertTrue(r["matched"])


if __name__ == "__main__":
    unittest.main()
