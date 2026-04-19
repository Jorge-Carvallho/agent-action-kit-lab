"""
Espelha o padrão de app/prompt.py: prompt escolhido por AGENT_ACTION no import.

Para testes que trocam AGENT_ACTION, use importlib.reload ou import limpo
(ver tests/test_matrix_example.py).
"""
from __future__ import annotations


def get_agent_prompt() -> str:
    from agent_action.profile_runtime import get_agent_action

    action = get_agent_action()
    if action == "generic":
        from agent_action.prompts import generic as generic_prompt

        return generic_prompt.AGENT_PROMPT
    from agent_action.prompts import laboratory

    return laboratory.AGENT_PROMPT
