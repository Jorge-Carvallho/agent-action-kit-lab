"""Esquemas Pydantic do contrato de agendamento (dados fictícios)."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ExamItem(BaseModel):
    """Um exame a agendar (tipicamente após resolução pelo RAG)."""

    code: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="Código do exame na base mock (ex.: LAB-F0001).",
        examples=["LAB-F0001"],
    )
    name: str = Field(
        ...,
        min_length=2,
        max_length=256,
        description="Nome canónico do exame.",
        examples=["Hemograma completo"],
    )


class AppointmentCreate(BaseModel):
    """Pedido de agendamento submetido pelo agente."""

    exam_items: list[ExamItem] = Field(
        ...,
        min_length=1,
        description="Lista de exames a agendar (não vazia).",
    )
    patient_reference: str | None = Field(
        None,
        max_length=128,
        description="Referência fictícia do utente (opcional; pode ser mascarada pelo pipeline PII).",
    )
    notes: str | None = Field(
        None,
        max_length=2000,
        description="Notas livres para o laboratório (opcional).",
    )


class AppointmentCreated(BaseModel):
    """Confirmação devolvida pelo laboratório fictício."""

    appointment_id: str = Field(..., description="Identificador único do pedido de agendamento.")
    status: Literal["confirmed"] = Field(
        ...,
        description="Estado do pedido (fictício: sempre confirmado como recebido).",
    )
    message: str = Field(..., description="Mensagem legível para o utilizador.")
    received_at: datetime = Field(..., description="Instante de receção ISO 8601.")
    exam_count: int = Field(..., ge=1, description="Número de exames incluídos.")
