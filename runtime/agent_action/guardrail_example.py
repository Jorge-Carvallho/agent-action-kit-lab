"""
Padrão inspirado em app/enterprise/guardrail.py: decisão antes do LLM.

Substitua ou estenda para PII (desafio): mascarar CPF, nomes, telefones, etc.
antes de persistir ou enviar ao modelo.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

# security/ na raiz do repositório
_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from security.pii import mask_pii


@dataclass
class GuardrailResult:
    allowed: bool
    reason: str = ""
    user_message: str = ""


# Exemplo mínimo: bloqueio de padrões de injeção (mesma ideia do guardrail principal)
_INJECTION_RE = re.compile(
    r"\b(ignore|disregard)\b.*\b(instructions|system)\b",
    re.IGNORECASE | re.UNICODE,
)


def validate_user_input(user_msg: str) -> GuardrailResult:
    t = (user_msg or "").strip()
    if not t:
        return GuardrailResult(allowed=True, user_message=t)
    if _INJECTION_RE.search(t):
        return GuardrailResult(
            allowed=False,
            reason="prompt_injection_detected",
            user_message="Não posso seguir esse tipo de instrução. Como posso ajudar no agendamento?",
        )
    return GuardrailResult(allowed=True, user_message=t)


def mask_cpf_like(text: str) -> str:
    """Delega para ``security.mask_pii`` (CPF, e-mail, telefone, RG, nomes por rótulo)."""
    return mask_pii(text).text
