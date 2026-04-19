"""Camada de segurança: deteção e mascaramento de PII antes de LLM/persistência."""

from security.pii import PIIMaskResult, mask_pii

__all__ = ["PIIMaskResult", "mask_pii"]
