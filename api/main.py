"""
API FastAPI fictícia de agendamento laboratorial.

Contrato alinhado a ``examples/agent_spec.json`` → ``scheduling_api``:
  POST {base_url}/api/v1/appointments
  GET  {base_url}/health

Documentação interactiva: GET /docs , GET /redoc
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.responses import Response

from api.schemas import AppointmentCreate, AppointmentCreated

API_TITLE = "Agendamento laboratorial (API fictícia)"
API_VERSION = "1.0.0"

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=(
        "Recebe listas de exames (código + nome) e devolve confirmação de pedido de agendamento. "
        "Dados de demonstração — sem persistência real nem dados sensíveis."
    ),
    openapi_tags=[
        {"name": "appointments", "description": "Criação de pedidos de agendamento."},
        {"name": "health", "description": "Estado do serviço."},
    ],
)


@app.get("/", tags=["health"], summary="Descoberta")
async def root() -> dict:
    """Evita 404 ao abrir a raiz no browser; o contrato do agente usa `/api/v1/appointments` e `/health`."""
    return {
        "service": "lab-scheduling-api",
        "docs": "/docs",
        "health": "/health",
        "create_appointment": "/api/v1/appointments",
    }


@app.get("/health", tags=["health"], summary="Health check")
async def health() -> dict:
    return {"status": "ok", "service": "lab-scheduling-api"}


@app.post(
    "/api/v1/appointments",
    response_model=AppointmentCreated,
    status_code=201,
    tags=["appointments"],
    summary="Submeter pedido de agendamento",
    response_description="Pedido registado com identificador fictício.",
)
async def create_appointment(payload: AppointmentCreate) -> AppointmentCreated:
    """
    Regista um pedido de agendamento com os exames indicados.

    O agente deve enviar, para cada exame, o **código** e o **nome** devolvidos
    pelo serviço RAG após o pipeline OCR → PII → RAG.
    """
    now = datetime.now(timezone.utc)
    appointment_id = str(uuid.uuid4())
    n = len(payload.exam_items)
    return AppointmentCreated(
        appointment_id=appointment_id,
        status="confirmed",
        message=(
            f"Pedido fictício registado com sucesso ({n} exame"
            f"{'s' if n != 1 else ''}). Utilize o ID para acompanhamento de demonstração."
        ),
        received_at=now,
        exam_count=n,
    )


# Silencia pedido de favicon do browser (Swagger UI não precisa de ícone no tab mock)
@app.get("/favicon.ico", include_in_schema=False)
async def favicon() -> Response:
    return Response(status_code=204)


def _port() -> int:
    return int(os.getenv("SCHEDULING_API_PORT", "8000"))


def main() -> None:
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=os.getenv("SCHEDULING_API_HOST", "0.0.0.0"),
        port=_port(),
        reload=False,
    )


if __name__ == "__main__":
    main()
