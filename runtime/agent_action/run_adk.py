#!/usr/bin/env python3
"""
Executa o agente ADK com inferência real (Gemini via GOOGLE_API_KEY).

Carrega `.env` na raiz do repositório e depois `agent_action/.env` (mesmo critério do smoke).

Recomendado (na raiz do clone, sem PYTHONPATH):
  python run_adk.py
  python run_adk.py "Em uma frase: qual é o teu papel?"
  python run_adk.py --generic "Olá"

Alternativa:
  PYTHONPATH=runtime python runtime/agent_action/run_adk.py ...
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

_RUNTIME_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(_RUNTIME_ROOT))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

try:
    from dotenv import load_dotenv

    load_dotenv(_REPO_ROOT / ".env")
    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass


def main() -> None:
    parser = argparse.ArgumentParser(description="Executa o agente ADK (modo debug).")
    parser.add_argument(
        "message",
        nargs="?",
        default="Olá. Responde em uma frase: qual é o teu papel neste contexto?",
        help="Mensagem para o agente",
    )
    parser.add_argument(
        "--generic",
        action="store_true",
        help="Força AGENT_ACTION=generic (em vez de lab)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Mostra eventos detalhados (tool calls, etc.)",
    )
    args = parser.parse_args()

    if args.generic:
        os.environ["AGENT_ACTION"] = "generic"
    elif not os.getenv("AGENT_ACTION"):
        os.environ["AGENT_ACTION"] = "lab"

    try:
        import google.adk  # noqa: F401
    except ImportError:
        print(
            "Erro: não existe o módulo 'google' neste Python (falta google-adk).\n"
            f"  Python em uso: {sys.executable}\n"
            "  Instala no mesmo ambiente: pip install -r runtime/agent_action/requirements-kit.txt\n"
            "  Ou corre explicitamente: ./.venv/bin/python runtime/agent_action/run_adk.py",
            file=sys.stderr,
        )
        sys.exit(1)

    if not os.getenv("GOOGLE_API_KEY", "").strip():
        print(
            "Erro: defina GOOGLE_API_KEY no .env da raiz do repo ou em agent_action/.env.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Imports após env e PYTHONPATH
    from agent_action.agent_factory import build_agent_and_runner
    from agent_action.lab_runtime import get_lab_extra_tools
    from agent_action.profile_runtime import get_runtime_config

    def _extra_tools():
        if os.getenv("AGENT_ACTION") != "lab":
            return []
        return get_lab_extra_tools()

    async def _run() -> None:
        runtime = get_runtime_config(extra_tools=_extra_tools())
        _, runner = build_agent_and_runner(runtime)
        await runner.run_debug(args.message, verbose=args.verbose)

    asyncio.run(_run())


if __name__ == "__main__":
    main()
