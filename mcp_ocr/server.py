#!/usr/bin/env python3
"""
Servidor MCP de OCR com transporte **SSE** (Model Context Protocol).

Expõe a ferramenta `extract_exam_names_from_image` para processar imagens de
pedidos médicos (fictícios) e devolver nomes de exames identificados.

Arranque:
    python -m mcp_ocr.server
    # ou: OCR_PORT=3100 python -m mcp_ocr.server

Por omissão: host 0.0.0.0, porta MCP_OCR_PORT ou 3100.
Endpoints SSE (relativos ao mount): GET /sse , POST /messages/
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Permitir `python mcp_ocr/server.py` a partir da pasta mcp_ocr
_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from mcp.server.fastmcp import FastMCP

from mcp_ocr.ocr_engine import decode_base64_image, ocr_image_bytes
from security.pii import mask_pii

HOST = os.getenv("MCP_OCR_HOST", "0.0.0.0")
PORT = int(os.getenv("MCP_OCR_PORT", "3100"))

mcp = FastMCP(
    "lab-ocr-mcp",
    instructions="Servidor MCP (SSE) de OCR para pedidos médicos fictícios — extrai nomes de exames.",
    host=HOST,
    port=PORT,
    sse_path="/sse",
    message_path="/messages/",
)


@mcp.tool()
def extract_exam_names_from_image(
    image_base64: str,
    mime_type: str = "image/png",
) -> dict:
    """
    Processa uma imagem (pedido médico em Base64) e devolve nomes de exames
    identificados. Dados fictícios para o desafio.

    Entrada:
        image_base64: Imagem codificada em Base64 (pode incluir prefixo data URI).
        mime_type: MIME da imagem (informativo; o motor usa os bytes decodificados).

    Saída (estruturada):
        exam_names: lista de strings
        engine: 'tesseract' | 'demo'
        mime_type: eco do pedido
    """
    try:
        raw = decode_base64_image(image_base64)
    except Exception as exc:  # noqa: BLE001
        return {
            "error": "decode_base64_failed",
            "detail": str(exc),
            "exam_names": [],
        }

    result = ocr_image_bytes(raw)
    raw_text = result.get("raw_text") or ""
    masked = mask_pii(raw_text) if raw_text else None
    out = {
        "exam_names": result.get("exam_names", []),
        "engine": result.get("engine", "unknown"),
        "mime_type": mime_type,
        "pii_masked": bool(masked and masked.replacements),
    }
    if raw_text:
        safe_preview = (masked.text if masked else raw_text)[:2000]
        out["raw_text_preview"] = safe_preview
    if result.get("note"):
        out["note"] = result["note"]
    return out


@mcp.custom_route("/", methods=["GET"])
async def root_info(request):
    """Evita 404 no browser em `/` — o protocolo MCP usa `/sse` e `/messages/`."""
    from starlette.responses import JSONResponse

    _ = request
    return JSONResponse(
        {
            "service": "mcp_ocr",
            "transport": "sse",
            "message": "Servidor MCP (OCR). O cliente liga-se via SSE; esta raiz é só descoberta.",
            "endpoints": {
                "sse": "/sse",
                "messages": "/messages/",
                "health": "/health",
            },
        }
    )


@mcp.custom_route("/favicon.ico", methods=["GET"])
async def no_favicon(request):
    """Silencia 404 do browser quando abre a porta no Chrome, etc."""
    from starlette.responses import Response

    _ = request
    return Response(status_code=204)


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    from starlette.responses import JSONResponse

    _ = request
    return JSONResponse({"status": "ok", "service": "mcp_ocr", "transport": "sse"})


def main() -> None:
    print(f"mcp_ocr SSE em http://{HOST}:{PORT}/sse (POST mensagens: /messages/)", flush=True)
    mcp.run(transport="sse")


if __name__ == "__main__":
    main()
