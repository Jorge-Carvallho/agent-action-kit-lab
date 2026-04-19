"""Testes da camada PII (dados fictícios)."""
from __future__ import annotations

import unittest

from security.pii import (
    MASK_CNPJ,
    MASK_CPF,
    MASK_EMAIL,
    MASK_NAME,
    MASK_PHONE,
    defensive_filter_exam_candidates,
    mask_pii,
    sanitize_api_text_field,
)


class TestMaskPII(unittest.TestCase):
    def test_email(self) -> None:
        raw = "Contacte ana.silva.ficticia@exemplo-lab.org para resultado."
        r = mask_pii(raw)
        self.assertIn(MASK_EMAIL, r.text)
        self.assertNotIn("ana.silva", r.text)
        kinds = [x["type"] for x in r.replacements if x["type"] == "email"]
        self.assertTrue(kinds)

    def test_cnpj(self) -> None:
        raw = "CNPJ laboratório fictício 12.345.678/0001-90"
        r = mask_pii(raw)
        self.assertIn(MASK_CNPJ, r.text)
        self.assertNotIn("12.345.678", r.text)

    def test_cpf_formatted(self) -> None:
        raw = "CPF do titular (fictício): 123.456.789-09"
        r = mask_pii(raw)
        self.assertIn(MASK_CPF, r.text)
        self.assertNotIn("123.456.789", r.text)

    def test_cpf_digits_only(self) -> None:
        raw = "Documento 52998224725 cadastrado."
        r = mask_pii(raw)
        self.assertIn(MASK_CPF, r.text)
        self.assertNotIn("52998224725", r.text)

    def test_phone_parentheses(self) -> None:
        raw = "Tel (11) 98765-4321 urgência."
        r = mask_pii(raw)
        self.assertIn(MASK_PHONE, r.text)
        self.assertNotIn("98765", r.text)

    def test_labeled_paciente_name(self) -> None:
        raw = "Solicitação\nPaciente: Maria Souza Fictícia\nHemograma"
        r = mask_pii(raw)
        self.assertIn(MASK_NAME, r.text)
        self.assertNotIn("Maria Souza", r.text)

    def test_empty(self) -> None:
        r = mask_pii("")
        self.assertEqual(r.text, "")
        self.assertEqual(r.replacements, [])

    def test_heuristic_names_off_by_default(self) -> None:
        raw = "Exame Hemograma completo"
        r = mask_pii(raw)
        self.assertIn("Hemograma", r.text)


class TestDefensivePII(unittest.TestCase):
    def test_defensive_exam_filter_keeps_valid_names(self) -> None:
        names = ["Hemograma completo", "a", "x@y.com", "123.456.789-00", "Glicemia"]
        out = defensive_filter_exam_candidates(names)
        self.assertIn("Hemograma completo", out)
        self.assertIn("Glicemia", out)
        self.assertNotIn("x@y.com", out)

    def test_sanitize_api_text_truncates(self) -> None:
        long_txt = "n" * 3000
        s = sanitize_api_text_field(long_txt, max_len=100)
        self.assertIsNotNone(s)
        self.assertEqual(len(s), 100)

    def test_sanitize_masks_email_in_free_text(self) -> None:
        raw = "Contacto urgente: paciente.ficticio@lab-exemplo.org antes do exame."
        s = sanitize_api_text_field(raw, max_len=500)
        self.assertIsNotNone(s)
        self.assertIn(MASK_EMAIL, s)
        self.assertNotIn("lab-exemplo.org", s)


if __name__ == "__main__":
    unittest.main()
