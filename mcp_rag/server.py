#!/usr/bin/env python3
"""
Servidor MCP de RAG com transporte **SSE** — consulta a base mock de exames (AI-009).

Arranque:
    python -m mcp_rag.server
    # ou: MCP_RAG_PORT=3200 python -m mcp_rag.server

Por omissão: host 0.0.0.0, porta MCP_RAG_PORT ou 3200 (alinhado a examples/agent_spec.json).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from mcp.server.fastmcp import FastMCP

from mcp_rag.exam_matcher import catalog_stats, resolve_exam_names

HOST = os.getenv("MCP_RAG_HOST", "0.0.0.0")
PORT = int(os.getenv("MCP_RAG_PORT", "3200"))

mcp = FastMCP(
    "lab-rag-mcp",
    instructions="Servidor MCP (SSE) de RAG fictício — resolve nomes de exames para códigos e detalhes na base mock.",
    host=HOST,
    port=PORT,
    sse_path="/sse",
    message_path="/messages/",
)


@mcp.tool()
def lookup_exam_codes(exam_names: list[str]) -> dict:
    """
    Recebe nomes de exames (ex.: extraídos do OCR) e devolve, para cada um,
    o melhor match na base mock: código canónico, nome normalizado e descrição curta.

    Entrada:
        exam_names: Lista de strings (uma por linha ou exame candidato).

    Saída:
        catalog_id, record_count, results: lista de objetos com matched, code,
        canonical_name, short_description, confidence, match_reason, query.
    """
    return resolve_exam_names(list(exam_names or []))


@mcp.custom_route("/", methods=["GET"])
async def root_info(request):
    from starlette.responses import JSONResponse

    _ = request
    return JSONResponse(
        {
            "service": "mcp_rag",
            "transport": "sse",
            "message": "Servidor MCP (RAG). O cliente liga-se via SSE; esta raiz é só descoberta.",
            "endpoints": {
                "sse": "/sse",
                "messages": "/messages/",
                "health": "/health",
            },
        }
    )


@mcp.custom_route("/favicon.ico", methods=["GET"])
async def no_favicon(request):
    from starlette.responses import Response

    _ = request
    return Response(status_code=204)


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    from starlette.responses import JSONResponse

    _ = request
    cid, nrec = catalog_stats()
    return JSONResponse(
        {
            "status": "ok",
            "service": "mcp_rag",
            "transport": "sse",
            "catalog_id": cid,
            "record_count": nrec,
        }
    )


def main() -> None:
    print(f"mcp_rag SSE em http://{HOST}:{PORT}/sse (POST mensagens: /messages/)", flush=True)
    mcp.run(transport="sse")


if __name__ == "__main__":
    main()
