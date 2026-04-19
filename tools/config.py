"""URLs e timeouts alinhados a ``examples/agent_spec.json`` (sobrescrevíveis por env)."""
from __future__ import annotations

import os

# MCP SSE (OCR / RAG)
MCP_OCR_SSE_URL = os.getenv("MCP_OCR_SSE_URL", "http://localhost:3100/sse")
MCP_RAG_SSE_URL = os.getenv("MCP_RAG_SSE_URL", "http://localhost:3200/sse")
MCP_TOOL_TIMEOUT_SEC = float(os.getenv("MCP_TOOL_TIMEOUT_SEC", "120"))
MCP_CONNECT_TIMEOUT_SEC = float(os.getenv("MCP_CONNECT_TIMEOUT_SEC", "30"))

# API de agendamento
SCHEDULING_API_BASE = os.getenv("SCHEDULING_API_BASE", "http://localhost:8000").rstrip("/")
SCHEDULING_APPOINTMENTS_PATH = os.getenv(
    "SCHEDULING_APPOINTMENTS_PATH",
    "/api/v1/appointments",
)
HTTP_TOOL_TIMEOUT_SEC = float(os.getenv("HTTP_TOOL_TIMEOUT_SEC", "60"))
