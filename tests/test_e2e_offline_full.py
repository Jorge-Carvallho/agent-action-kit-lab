"""
E2E do fluxo principal sem Docker nem MCP (AI-015).

Usa a imagem fictícia do repositório, OCR+RAG locais e, no caso completo,
a API FastAPI em memória via ASGITransport (sem portas).
"""
from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from starlette.testclient import TestClient

from api.main import app
from cli.flow import run_pipeline

_REPO = Path(__file__).resolve().parents[1]
_SAMPLE = _REPO / "examples" / "sample_prescription.png"


class TestE2EOfflineFull(unittest.TestCase):
    def test_sample_image_ocr_rag_offline_dry_run(self) -> None:
        self.assertTrue(_SAMPLE.is_file(), f"Falta {_SAMPLE}")
        r = run_pipeline(_SAMPLE, submit_appointment=False, offline=True)
        self.assertEqual(r.flow_backend, "local")
        self.assertTrue(r.skipped_appointment)
        self.assertGreaterEqual(len(r.exam_names), 1)
        self.assertGreaterEqual(len(r.exam_items_for_api), 1)
        self.assertIn("results", r.rag_payload)

    def test_sample_image_offline_through_api_asgi(self) -> None:
        """OCR → RAG locais → POST /api/v1/appointments na app real (TestClient ASGI)."""
        self.assertTrue(_SAMPLE.is_file(), f"Falta {_SAMPLE}")

        class _HttpxShim:
            """Só o que ``_run_pipeline_local`` usa: ``post(url, json=...)``."""

            def __init__(self, tc: TestClient) -> None:
                self._tc = tc

            def post(self, url: str, json: object | None = None):  # noqa: ANN201
                from urllib.parse import urlparse

                parsed = urlparse(url)
                path = parsed.path or "/"
                if parsed.query:
                    path = f"{path}?{parsed.query}"
                return self._tc.post(path, json=json)

        with TestClient(app) as tc:
            shim = _HttpxShim(tc)
            with patch("cli.flow.SCHEDULING_API_BASE", "http://test"):
                with patch("cli.flow.httpx.Client") as mc:
                    cm = MagicMock()
                    cm.__enter__.return_value = shim
                    cm.__exit__.return_value = None
                    mc.return_value = cm
                    r = run_pipeline(
                        _SAMPLE,
                        submit_appointment=True,
                        offline=True,
                    )
        self.assertEqual(r.flow_backend, "local")
        self.assertFalse(r.skipped_appointment)
        self.assertIsNotNone(r.appointment_response)
        body = r.appointment_response or {}
        self.assertEqual(body.get("status"), "confirmed")
        self.assertIn("appointment_id", body)
        self.assertGreaterEqual(int(body.get("exam_count") or 0), 1)


if __name__ == "__main__":
    unittest.main()
