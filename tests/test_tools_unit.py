"""Testes unitários das tools (sem servidores MCP externos)."""
from __future__ import annotations

import unittest
from unittest.mock import patch

import httpx
from google.adk.tools.function_tool import FunctionTool

from api.main import app
from tools.mcp_bridge import call_tool_result_to_payload
from tools.ocr_tool import ocr_extract_exams
from tools.rag_tool import rag_lookup_exam_codes
from tools.scheduling_tool import ExamItemInput, submit_appointment_request


class TestLabToolsRegistry(unittest.TestCase):
    def test_function_tools_from_explicit_imports(self) -> None:
        tools = [
            FunctionTool(ocr_extract_exams),
            FunctionTool(rag_lookup_exam_codes),
            FunctionTool(submit_appointment_request),
        ]
        self.assertEqual(len(tools), 3)
        names = {t.name for t in tools}
        self.assertIn("ocr_extract_exams", names)
        self.assertIn("rag_lookup_exam_codes", names)
        self.assertIn("submit_appointment_request", names)


class TestMcpPayload(unittest.TestCase):
    def test_structured_content(self) -> None:
        import mcp.types as mtypes

        r = mtypes.CallToolResult(
            content=[],
            structuredContent={"ok": True, "exam_names": ["A"]},
            isError=False,
        )
        self.assertEqual(call_tool_result_to_payload(r), {"ok": True, "exam_names": ["A"]})


class TestSubmitToolAsync(unittest.IsolatedAsyncioTestCase):
    async def test_submit_appointment_request_via_asgi(self) -> None:
        real_client = httpx.AsyncClient

        def client_factory(**kwargs: object) -> httpx.AsyncClient:
            kw = dict(kwargs)
            kw["transport"] = httpx.ASGITransport(app=app)
            kw["base_url"] = "http://test"
            return real_client(**kw)

        with patch("tools.scheduling_tool.config.SCHEDULING_API_BASE", "http://test"):
            with patch("tools.scheduling_tool.httpx.AsyncClient", client_factory):
                out = await submit_appointment_request(
                    exam_items=[
                        ExamItemInput(code="LAB-F0001", name="Hemograma completo"),
                    ],
                )
        self.assertNotIn("error", out)
        self.assertEqual(out.get("status"), "confirmed")


if __name__ == "__main__":
    unittest.main()
