"""Testes do motor OCR (sem subir o servidor SSE)."""
from __future__ import annotations

import base64
import unittest

from mcp_ocr.ocr_engine import decode_base64_image, ocr_image_bytes


class TestDecodeBase64(unittest.TestCase):
    def test_plain_roundtrip(self) -> None:
        raw = b"hello"
        b64 = base64.b64encode(raw).decode("ascii")
        self.assertEqual(decode_base64_image(b64), raw)

    def test_data_uri(self) -> None:
        raw = b"\x89PNG"
        b64 = base64.b64encode(raw).decode("ascii")
        self.assertEqual(decode_base64_image(f"data:image/png;base64,{b64}"), raw)


class TestOcrDemo(unittest.TestCase):
    def test_ocr_returns_exam_names(self) -> None:
        r = ocr_image_bytes(b"not-a-valid-image")
        self.assertIn("exam_names", r)
        self.assertIsInstance(r["exam_names"], list)
        self.assertGreaterEqual(len(r["exam_names"]), 1)
        self.assertEqual(r.get("engine"), "demo")
