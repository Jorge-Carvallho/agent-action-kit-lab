"""
Perfil + runtime do agente ADK — domínio **laboratorial** (`lab`) vs **genérico** (`generic`).

Não há fluxo comercial de vendas neste kit; o perfil `lab` está alinhado ao desafio
(OCR → RAG → API fictícia). Ver `prompts/laboratory.py` e `lab_runtime.py`.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Callable

from agent_action.prompt_loader import get_agent_prompt


@dataclass(frozen=True)
class AgentProfile:
    """Contexto de alto nível do agente (sem domínio comercial — kit laboratorial)."""

    action: str
    app_name: str
    display_name: str
    niche: str
    # Alinha a `instruction_key` do transpiler / agent_spec quando aplicável
    instruction_key: str
    domain: str


def get_agent_action() -> str:
    """
    Seletor de contexto (equivalente a AGENT_ACTION=joe|ben no app principal).
    Valores de exemplo neste kit: lab | generic
    """
    raw = (os.getenv("AGENT_ACTION") or "lab").strip().lower()
    if raw in {"lab", "generic"}:
        return raw
    raise ValueError("Invalid AGENT_ACTION. Use 'lab' or 'generic' for this kit.")


def get_agent_profile() -> AgentProfile:
    action = get_agent_action()
    if action == "generic":
        return AgentProfile(
            action="generic",
            app_name="generic_agent_kit",
            display_name="Assistente",
            niche="tarefa genérica",
            instruction_key="generic",
            domain="generic_assistant",
        )
    return AgentProfile(
        action="lab",
        app_name="lab_exam_scheduler_kit",
        display_name="Assistente de agendamento laboratorial",
        niche="exames laboratoriais fictícios — OCR, catálogo e API de pedido",
        instruction_key="lab_example",
        domain="laboratory_scheduling",
    )


@dataclass(frozen=True)
class RuntimeConfig:
    app_name: str
    agent_name: str
    instruction: str
    tools: list[Any]


def get_runtime_config(
    *,
    extra_tools: list[Any] | None = None,
    instruction_factory: Callable[[], str] | None = None,
) -> RuntimeConfig:
    """
    Centraliza nome do agente ADK + instrução + tools (como app/agent_runtime.py).

    extra_tools: injete aqui tools reais (ou deixe [] para smoke test).
    instruction_factory: opcional; default usa prompt_loader.get_agent_prompt().
    """
    profile = get_agent_profile()
    instruction = (
        instruction_factory() if instruction_factory is not None else get_agent_prompt()
    )
    tools = list(extra_tools or [])
    agent_name = "lab_scheduler" if profile.action == "lab" else "generic_assistant"
    return RuntimeConfig(
        app_name=profile.app_name,
        agent_name=agent_name,
        instruction=instruction,
        tools=tools,
    )
