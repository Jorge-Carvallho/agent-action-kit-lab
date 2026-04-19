#!/usr/bin/env python3
"""
CLI de validação do JSON de especificação do transpilador (AI-004).

Usa duas camadas: JSON Schema (estrutura/tipos) + regras semânticas.

Uso (na raiz do clone):
  pip install -r transpiler/requirements.txt
  python transpiler/validate_spec.py                        # valida o exemplo
  python transpiler/validate_spec.py examples/agent_spec.json
  python transpiler/validate_spec.py meu_agente.json --warn
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Valida agent_spec.json (schema + semântica).",
    )
    parser.add_argument(
        "spec_file",
        type=Path,
        nargs="?",
        default=_REPO / "examples" / "agent_spec.json",
        help="Caminho para o JSON (default: examples/agent_spec.json)",
    )
    parser.add_argument(
        "--warn",
        action="store_true",
        help="Termina com código 1 se houver avisos (além de erros)",
    )
    args = parser.parse_args()

    sys.path.insert(0, str(_REPO))
    from transpiler.validator import validate_file  # noqa: PLC0415

    try:
        result = validate_file(args.spec_file, raise_on_error=False)
    except Exception as exc:  # noqa: BLE001
        print(f"Erro inesperado: {exc}", file=sys.stderr)
        return 2

    print(result.user_message(), file=sys.stderr if not result.ok else sys.stdout)

    if not result.ok:
        return 1
    if args.warn and result.warnings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
