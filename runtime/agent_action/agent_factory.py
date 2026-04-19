"""
Espelha a criação de Agent + InMemoryRunner (app/agent.py e webhook_server.py).

Uso típico:
    runtime = get_runtime_config(extra_tools=[...])
    root_agent, runner = build_agent_and_runner(runtime)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from google.adk.agents import Agent
    from google.adk.runners import InMemoryRunner

    from agent_action.profile_runtime import RuntimeConfig


def build_agent_and_runner(runtime: RuntimeConfig) -> tuple[Agent, InMemoryRunner]:
    from google.adk.agents import Agent
    from google.adk.runners import InMemoryRunner

    root_agent = Agent(
        name=runtime.agent_name,
        model="gemini-2.5-flash",
        instruction=runtime.instruction,
        tools=runtime.tools,
    )
    runner = InMemoryRunner(agent=root_agent, app_name=runtime.app_name)
    return root_agent, runner
