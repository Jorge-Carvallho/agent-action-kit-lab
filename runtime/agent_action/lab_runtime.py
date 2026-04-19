"""
Registo das tools ADK do domínio laboratorial (OCR MCP, RAG MCP, API de agendamento).

Mantém o `run_adk.py` simples e concentra a lógica de activação aqui.
"""
from __future__ import annotations

import os
from typing import Any


def lab_adk_tools_enabled() -> bool:
    v = os.getenv("LAB_AGENT_TOOLS", "1").strip().lower()
    return v not in ("0", "false", "no")


def get_lab_extra_tools() -> list[Any]:
    """
    Lista de ``FunctionTool`` para o perfil `lab`, ou lista vazia se desactivado.

    Requer a raiz do repositório no ``sys.path`` (o ``run_adk.py`` já faz isso).
    """
    if not lab_adk_tools_enabled():
        return []
    from google.adk.tools.function_tool import FunctionTool

    from tools.ocr_tool import ocr_extract_exams
    from tools.rag_tool import rag_lookup_exam_codes
    from tools.scheduling_tool import submit_appointment_request

    return [
        FunctionTool(ocr_extract_exams),
        FunctionTool(rag_lookup_exam_codes),
        FunctionTool(submit_appointment_request),
    ]
