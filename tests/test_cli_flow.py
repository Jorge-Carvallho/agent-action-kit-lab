"""Testes do CLI laboratorial (`cli/flow`, `cli/main`)."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from cli.flow import LabFlowResult, run_pipeline
from cli.main import format_report


class TestFormatReport(unittest.TestCase):
    def test_contains_sections(self) -> None:
        r = LabFlowResult(
            image_path="/tmp/x.png",
            ocr_engine="demo",
            exam_names=["Hemograma completo"],
            raw_text_preview_masked=None,
            ocr_note=None,
            rag_payload={"results": []},
            exam_items_for_api=[],
            appointment_response={"status": "confirmed", "appointment_id": "id-1", "message": "ok", "exam_count": 1},
        )
        text = format_report(r)
        self.assertIn("Fluxo laboratorial", text)
        self.assertIn("Hemograma", text)
        self.assertIn("id-1", text)


class TestRunPipelineDry(unittest.TestCase):
    def test_dry_run_no_http_offline(self) -> None:
        """Modo local/offline: OCR in-process, sem MCP."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(_minimal_png_bytes())
            path = Path(tmp.name)
        try:
            with patch("cli.flow.ocr_image_bytes") as ocr_m:
                ocr_m.return_value = {
                    "exam_names": ["Hemograma completo"],
                    "engine": "test",
                    "raw_text": "Pedido fictício. Paciente: Teste Silva",
                }
                r = run_pipeline(path, submit_appointment=False, offline=True)
            self.assertEqual(r.flow_backend, "local")
            self.assertTrue(r.skipped_appointment)
            self.assertIsNone(r.appointment_response)
            self.assertGreaterEqual(len(r.exam_items_for_api), 1)
        finally:
            path.unlink(missing_ok=True)


class TestRunPipelineMcpMocked(unittest.TestCase):
    def test_mcp_path_with_async_mocks(self) -> None:
        """Fluxo predefinido (MCP SSE): tools async mockadas, sem rede."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(_minimal_png_bytes())
            path = Path(tmp.name)
        try:

            async def fake_ocr(*_a, **_k):
                return {
                    "exam_names": ["Hemograma completo"],
                    "engine": "pytest",
                    "raw_text_preview": "[NOME] Hemograma fictício.",
                }

            async def fake_rag(names: list[str]):
                from mcp_rag.exam_matcher import resolve_exam_names

                return resolve_exam_names(list(names or []))

            async def fake_submit(exams, **_k):
                return {
                    "status": "confirmed",
                    "appointment_id": "e2e-mock",
                    "message": "ok",
                    "exam_count": len(exams),
                }

            with (
                patch("tools.ocr_tool.ocr_extract_exams", AsyncMock(side_effect=fake_ocr)),
                patch("tools.rag_tool.rag_lookup_exam_codes", AsyncMock(side_effect=fake_rag)),
                patch(
                    "tools.scheduling_tool.submit_appointment_request",
                    AsyncMock(side_effect=fake_submit),
                ),
            ):
                r = run_pipeline(path, submit_appointment=True, offline=False)
            self.assertEqual(r.flow_backend, "mcp_sse")
            self.assertIsNotNone(r.appointment_response)
            self.assertEqual(r.appointment_response.get("appointment_id"), "e2e-mock")
        finally:
            path.unlink(missing_ok=True)


def _minimal_png_bytes() -> bytes:
    """PNG 1x1 mínimo válido (sem Pillow)."""
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT"
        b"\x08\xd7c\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xdc\xccY\xe7\x00\x00\x00"
        b"\x00IEND\xaeB`\x82"
    )


if __name__ == "__main__":
    unittest.main()
