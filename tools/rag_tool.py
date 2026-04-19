"""Tool ADK: RAG via MCP SSE (``lookup_exam_codes``)."""
from __future__ import annotations

from typing import Any

from tools import config
from tools.mcp_bridge import call_mcp_tool

MCP_TOOL_NAME = "lookup_exam_codes"


async def rag_lookup_exam_codes(exam_names: list[str]) -> dict[str, Any]:
    """
    Resolve cada nome de exame para código LAB-F*, nome canónico e descrição curta
    na base mock (RAG).

    Utiliza o servidor MCP RAG (SSE). Requer ``MCP_RAG_SSE_URL`` acessível.
    """
    names = [str(x).strip() for x in (exam_names or []) if str(x).strip()]
    return await call_mcp_tool(
        config.MCP_RAG_SSE_URL,
        MCP_TOOL_NAME,
        {"exam_names": names},
        read_timeout_sec=config.MCP_TOOL_TIMEOUT_SEC,
    )
