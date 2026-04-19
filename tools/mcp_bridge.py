"""Cliente MCP (SSE) mínimo: uma sessão por chamada, resultado JSON-serializável."""
from __future__ import annotations

import json
import logging
from datetime import timedelta
from typing import Any

import mcp.types as mtypes
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

from tools import config

logger = logging.getLogger(__name__)


def _text_from_content_blocks(content: list[mtypes.ContentBlock]) -> str:
    parts: list[str] = []
    for block in content:
        if isinstance(block, mtypes.TextContent):
            parts.append(block.text)
        else:
            parts.append(str(block))
    return "\n".join(parts).strip()


def call_tool_result_to_payload(result: mtypes.CallToolResult) -> dict[str, Any]:
    """Converte ``CallToolResult`` num dicionário estável para o LLM."""
    if result.isError:
        return {
            "error": True,
            "message": _text_from_content_blocks(result.content) or "tool_returned_error",
        }
    if result.structuredContent:
        return dict(result.structuredContent)
    raw = _text_from_content_blocks(result.content)
    if not raw:
        return {"empty": True}
    try:
        parsed: Any = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
        return {"value": parsed}
    except json.JSONDecodeError:
        return {"raw": raw}


async def call_mcp_tool(
    sse_url: str,
    tool_name: str,
    arguments: dict[str, Any] | None,
    *,
    read_timeout_sec: float | None = None,
) -> dict[str, Any]:
    """
    Estabelece sessão MCP via SSE, inicializa e invoca ``tools/call``.

    Erros de rede ou protocolo devolvem ``{"error": ...}`` legível (sem excepção).
    """
    timeout = read_timeout_sec if read_timeout_sec is not None else config.MCP_TOOL_TIMEOUT_SEC
    try:
        async with sse_client(
            sse_url,
            timeout=config.MCP_CONNECT_TIMEOUT_SEC,
            sse_read_timeout=max(timeout, 60.0),
        ) as streams:
            read_stream, write_stream = streams
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                res = await session.call_tool(
                    tool_name,
                    arguments,
                    read_timeout_seconds=timedelta(seconds=timeout),
                )
                return call_tool_result_to_payload(res)
    except TimeoutError as e:
        return {"error": "timeout", "detail": str(e), "tool": tool_name, "sse_url": sse_url}
    except Exception as e:  # noqa: BLE001 — integração: resposta estruturada
        logger.exception("MCP call failed: %s", tool_name)
        return {
            "error": "mcp_call_failed",
            "detail": str(e),
            "tool": tool_name,
            "sse_url": sse_url,
        }
