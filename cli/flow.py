"""
Pipeline determinístico: imagem → OCR → PII (prévia) → RAG → API de agendamento.

Por defeito usa **MCP SSE** (mesmas tools que o agente ADK). Com ``offline=True``,
usa motores em processo (OCR + matcher) sem servidores MCP — apenas para desenvolvimento.
"""
from __future__ import annotations

import asyncio
import base64
import mimetypes
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx

from mcp_ocr.ocr_engine import ocr_image_bytes
from mcp_rag.exam_matcher import resolve_exam_names
from security.pii import (
    defensive_filter_exam_candidates,
    mask_pii,
    sanitize_api_text_field,
)
from tools.config import (
    HTTP_TOOL_TIMEOUT_SEC,
    SCHEDULING_APPOINTMENTS_PATH,
    SCHEDULING_API_BASE,
)


def _exam_items_from_rag(rag: dict[str, Any]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for row in rag.get("results", []):
        if not row.get("matched"):
            continue
        code = row.get("code")
        name = row.get("canonical_name")
        if code and name:
            items.append({"code": str(code), "name": str(name)})
    return items


@dataclass
class LabFlowResult:
    image_path: str
    ocr_engine: str
    exam_names: list[str]
    raw_text_preview_masked: str | None
    ocr_note: str | None
    rag_payload: dict[str, Any]
    exam_items_for_api: list[dict[str, str]]
    appointment_response: dict[str, Any] | None = None
    appointment_error: str | None = None
    skipped_appointment: bool = False
    errors: list[str] = field(default_factory=list)
    flow_backend: str = "mcp_sse"  # mcp_sse | local


def _run_pipeline_local(
    image_path: Path,
    *,
    submit_appointment: bool = True,
    patient_reference: str | None = None,
    notes: str | None = None,
) -> LabFlowResult:
    """OCR + RAG em processo (sem MCP SSE)."""
    errs: list[str] = []
    path_str = str(image_path.resolve())
    try:
        raw = image_path.read_bytes()
    except OSError as e:
        return LabFlowResult(
            image_path=path_str,
            ocr_engine="error",
            exam_names=[],
            raw_text_preview_masked=None,
            ocr_note=None,
            rag_payload={},
            exam_items_for_api=[],
            errors=[f"Falha ao ler a imagem: {e}"],
            flow_backend="local",
        )

    ocr = ocr_image_bytes(raw)
    engine = str(ocr.get("engine", "unknown"))
    exam_names = defensive_filter_exam_candidates(list(ocr.get("exam_names") or []))
    raw_text = ocr.get("raw_text") or ""
    note = ocr.get("note")
    preview_masked: str | None = None
    if raw_text:
        preview_masked = mask_pii(raw_text).text[:2000]

    rag = resolve_exam_names(exam_names)
    items = _exam_items_from_rag(rag)

    result = LabFlowResult(
        image_path=path_str,
        ocr_engine=engine,
        exam_names=exam_names,
        raw_text_preview_masked=preview_masked,
        ocr_note=note,
        rag_payload=rag,
        exam_items_for_api=items,
        flow_backend="local",
    )

    if not submit_appointment:
        result.skipped_appointment = True
        return result

    if not items:
        result.skipped_appointment = True
        result.appointment_error = (
            "Nenhum exame com match no catálogo RAG — pedido de agendamento não enviado."
        )
        return result

    url = f"{SCHEDULING_API_BASE}{SCHEDULING_APPOINTMENTS_PATH}"
    safe_ref = sanitize_api_text_field(patient_reference, max_len=128)
    safe_notes = sanitize_api_text_field(
        notes,
        max_len=2000,
        default="Pedido gerado pela CLI de demonstração (fictício).",
    ) or "Pedido gerado pela CLI de demonstração (fictício)."
    payload = {
        "exam_items": items,
        "patient_reference": safe_ref,
        "notes": safe_notes,
    }
    try:
        with httpx.Client(timeout=HTTP_TOOL_TIMEOUT_SEC) as client:
            r = client.post(url, json=payload)
            try:
                body: Any = r.json()
            except Exception:  # noqa: BLE001
                body = {"raw": r.text}
            if r.is_success and isinstance(body, dict):
                result.appointment_response = body
            else:
                result.appointment_error = (
                    f"HTTP {r.status_code}: {body if isinstance(body, dict) else body}"
                )
    except httpx.HTTPError as e:
        result.appointment_error = f"Erro de rede/API: {e}"
        errs.append(str(e))

    result.errors.extend(errs)
    return result


async def _run_pipeline_mcp(
    image_path: Path,
    *,
    submit_appointment: bool = True,
    patient_reference: str | None = None,
    notes: str | None = None,
) -> LabFlowResult:
    """OCR MCP SSE → prévia já mascarada no servidor → RAG MCP SSE → API (tool HTTP)."""
    from tools.ocr_tool import ocr_extract_exams
    from tools.rag_tool import rag_lookup_exam_codes
    from tools.scheduling_tool import ExamItemInput, submit_appointment_request

    errs: list[str] = []
    path_str = str(image_path.resolve())
    try:
        raw = image_path.read_bytes()
    except OSError as e:
        return LabFlowResult(
            image_path=path_str,
            ocr_engine="error",
            exam_names=[],
            raw_text_preview_masked=None,
            ocr_note=None,
            rag_payload={},
            exam_items_for_api=[],
            errors=[f"Falha ao ler a imagem: {e}"],
            flow_backend="mcp_sse",
        )

    mime = mimetypes.guess_type(str(image_path))[0] or "image/png"
    b64 = base64.standard_b64encode(raw).decode("ascii")

    ocr = await ocr_extract_exams(b64, mime_type=mime)
    if ocr.get("error") or ocr.get("empty"):
        detail = ocr.get("detail") or ocr.get("message") or ocr
        return LabFlowResult(
            image_path=path_str,
            ocr_engine="error",
            exam_names=[],
            raw_text_preview_masked=None,
            ocr_note=None,
            rag_payload={},
            exam_items_for_api=[],
            errors=[f"OCR MCP: {detail}"],
            flow_backend="mcp_sse",
        )

    engine = str(ocr.get("engine", "unknown"))
    exam_names = defensive_filter_exam_candidates(list(ocr.get("exam_names") or []))
    note = ocr.get("note")
    # Servidor MCP já aplica ``mask_pii`` em ``raw_text_preview`` antes de devolver.
    preview_masked: str | None = None
    if ocr.get("raw_text_preview"):
        preview_masked = str(ocr["raw_text_preview"])[:2000]

    rag = await rag_lookup_exam_codes(exam_names)
    if rag.get("error"):
        return LabFlowResult(
            image_path=path_str,
            ocr_engine=engine,
            exam_names=exam_names,
            raw_text_preview_masked=preview_masked,
            ocr_note=note,
            rag_payload=rag,
            exam_items_for_api=[],
            errors=[f"RAG MCP: {rag}"],
            flow_backend="mcp_sse",
        )

    items = _exam_items_from_rag(rag)
    result = LabFlowResult(
        image_path=path_str,
        ocr_engine=engine,
        exam_names=exam_names,
        raw_text_preview_masked=preview_masked,
        ocr_note=note,
        rag_payload=rag,
        exam_items_for_api=items,
        flow_backend="mcp_sse",
    )

    if not submit_appointment:
        result.skipped_appointment = True
        return result

    if not items:
        result.skipped_appointment = True
        result.appointment_error = (
            "Nenhum exame com match no catálogo RAG — pedido de agendamento não enviado."
        )
        return result

    exam_models = [ExamItemInput(code=x["code"], name=x["name"]) for x in items]
    safe_ref = sanitize_api_text_field(patient_reference, max_len=128)
    safe_notes = sanitize_api_text_field(
        notes,
        max_len=2000,
        default="Pedido gerado pela CLI de demonstração (fictício).",
    ) or "Pedido gerado pela CLI de demonstração (fictício)."
    resp = await submit_appointment_request(
        exam_models,
        patient_reference=safe_ref,
        notes=safe_notes,
    )
    if resp.get("error"):
        result.appointment_error = str(resp.get("detail", resp))
    else:
        result.appointment_response = resp

    result.errors.extend(errs)
    return result


def run_pipeline(
    image_path: Path,
    *,
    submit_appointment: bool = True,
    patient_reference: str | None = None,
    notes: str | None = None,
    offline: bool = False,
) -> LabFlowResult:
    """
    Executa o fluxo completo até à API (se ``submit_appointment`` e houver matches).

    * ``offline=False`` (predefinição): MCP SSE real (OCR + RAG) e tool HTTP da API.
    * ``offline=True``: motores locais, útil sem Docker/red MCP.
    """
    if offline:
        return _run_pipeline_local(
            image_path,
            submit_appointment=submit_appointment,
            patient_reference=patient_reference,
            notes=notes,
        )
    return asyncio.run(
        _run_pipeline_mcp(
            image_path,
            submit_appointment=submit_appointment,
            patient_reference=patient_reference,
            notes=notes,
        )
    )
