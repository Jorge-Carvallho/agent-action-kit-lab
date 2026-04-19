"""Tool ADK: agendamento via HTTP (API FastAPI fictícia)."""
from __future__ import annotations

from typing import Any

import httpx
from pydantic import BaseModel, Field

from tools import config


class ExamItemInput(BaseModel):
    """Item de exame para agendamento (eco do contrato ``api/schemas``)."""

    code: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=2, max_length=256)


async def submit_appointment_request(
    exam_items: list[ExamItemInput],
    patient_reference: str | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    """
    Submete pedido de agendamento à API FastAPI fictícia.

    Body alinhado a ``POST /api/v1/appointments`` (ver ``api/schemas``).
    """
    url = f"{config.SCHEDULING_API_BASE}{config.SCHEDULING_APPOINTMENTS_PATH}"
    payload: dict[str, Any] = {
        "exam_items": [e.model_dump() for e in exam_items],
        "patient_reference": patient_reference,
        "notes": notes,
    }
    try:
        async with httpx.AsyncClient(timeout=config.HTTP_TOOL_TIMEOUT_SEC) as client:
            r = await client.post(url, json=payload)
            body: Any
            try:
                body = r.json()
            except Exception:  # noqa: BLE001
                body = {"raw": r.text}
            if r.is_success:
                if isinstance(body, dict):
                    return body
                return {"value": body}
            err: dict[str, Any] = {
                "error": "http_error",
                "status_code": r.status_code,
                "detail": body if isinstance(body, dict) else str(body),
            }
            return err
    except httpx.ConnectError as e:
        return {
            "error": "connection_failed",
            "detail": str(e),
            "url": url,
            "hint": "Confirme que a API está a correr (ex.: python -m api).",
        }
    except httpx.TimeoutException as e:
        return {"error": "timeout", "detail": str(e), "url": url}
