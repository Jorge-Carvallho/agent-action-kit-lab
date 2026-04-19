"""
Compatibilidade com ``instruction_key: "lab_example"`` (transpiler / agent_spec).

O conteúdo canónico do prompt laboratorial está em ``laboratory.py``.
"""

from agent_action.prompts.laboratory import AGENT_PROMPT

__all__ = ["AGENT_PROMPT"]
