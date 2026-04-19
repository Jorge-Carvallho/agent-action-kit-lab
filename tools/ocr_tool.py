"""Tool ADK: OCR via MCP SSE (``extract_exam_names_from_image``)."""
from __future__ import annotations

from typing import Any

from tools import config
from tools.mcp_bridge import call_mcp_tool

MCP_TOOL_NAME = "extract_exam_names_from_image"


async def ocr_extract_exams(image_base64: str, mime_type: str = "image/png") -> dict[str, Any]:
    """
    Extrai nomes de exames a partir da imagem do pedido médico (Base64).

    Utiliza o servidor MCP OCR (SSE). Requer ``MCP_OCR_SSE_URL`` acessível.
    """
    return await call_mcp_tool(
        config.MCP_OCR_SSE_URL,
        MCP_TOOL_NAME,
        {"image_base64": image_base64, "mime_type": mime_type},
        read_timeout_sec=config.MCP_TOOL_TIMEOUT_SEC,
    )
