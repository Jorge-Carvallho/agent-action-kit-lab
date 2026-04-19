#!/usr/bin/env python3
"""
Smoke test: instancia Agent + InMemoryRunner (ADK) sem chamar o modelo.

Se quiser testar inferência de verdade, defina GOOGLE_API_KEY (ex.: .env na raiz do repo pai).
Recomendado (na raiz do clone, sem PYTHONPATH):
  python run_smoke.py

Alternativa:
  PYTHONPATH=runtime python runtime/agent_action/smoke_adk.py

Para chamar o modelo (Gemini):
  python run_adk.py "a tua mensagem"
"""
from __future__ import annotations

import sys
from pathlib import Path

_RUNTIME_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(_RUNTIME_ROOT))

try:
    from dotenv import load_dotenv

    load_dotenv(_REPO_ROOT / ".env")
    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass

import os

# Este kit só aceita lab|generic; o .env da raiz costuma ter joe|ben.
os.environ["AGENT_ACTION"] = "lab"

from agent_action.agent_factory import build_agent_and_runner
from agent_action.profile_runtime import get_runtime_config


def main() -> None:
    runtime = get_runtime_config(extra_tools=[])
    agent, runner = build_agent_and_runner(runtime)
    has_key = bool(__import__("os").getenv("GOOGLE_API_KEY", "").strip())
    print("OK — ADK: Agent + InMemoryRunner criados.")
    print(f"    app_name={runtime.app_name} agent_name={runtime.agent_name}")
    print(f"    GOOGLE_API_KEY definida: {has_key} (necessária para run_async / chamadas ao modelo)")


if __name__ == "__main__":
    main()
