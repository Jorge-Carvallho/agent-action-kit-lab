#!/usr/bin/env python3
"""Agente ADK (inferência) — corre na raiz do clone, sem PYTHONPATH.

Exemplos:
  python run_adk.py
  python run_adk.py "Qual é o teu papel?"
  python run_adk.py --generic "Olá"
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_RUNTIME = _ROOT / "runtime"
if str(_RUNTIME) not in sys.path:
    sys.path.insert(0, str(_RUNTIME))

from agent_action.run_adk import main

if __name__ == "__main__":
    main()
