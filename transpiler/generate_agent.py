#!/usr/bin/env python3
"""
CLI: gera `generated_agent.py` a partir do JSON de especificação (AI-005).

Uso (na raiz do clone):
  python transpiler/generate_agent.py
  python transpiler/generate_agent.py examples/agent_spec.json -o examples/generated_agent.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera código Python do agente ADK a partir do JSON.")
    parser.add_argument(
        "spec",
        type=Path,
        nargs="?",
        default=_REPO / "examples" / "agent_spec.json",
        help="Caminho para agent_spec.json",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=_REPO / "examples" / "generated_agent.py",
        help="Ficheiro Python de saída (default: examples/generated_agent.py)",
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Não validar o JSON (apenas para debugging)",
    )
    args = parser.parse_args()

    sys.path.insert(0, str(_REPO))
    from transpiler.generator import write_generated_agent  # noqa: PLC0415

    out = write_generated_agent(
        args.spec,
        args.output,
        validate_first=not args.no_validate,
    )
    print(f"OK — gerado: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
