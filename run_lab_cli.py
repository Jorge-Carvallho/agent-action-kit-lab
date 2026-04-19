#!/usr/bin/env python3
"""
CLI do fluxo laboratorial — corre na raiz do clone, sem PYTHONPATH manual.

  python run_lab_cli.py /caminho/imagem.png
  python run_lab_cli.py --dry-run examples/algo.png
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_RUNTIME = _ROOT / "runtime"
if str(_RUNTIME) not in sys.path:
    sys.path.insert(0, str(_RUNTIME))
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from cli.main import main

if __name__ == "__main__":
    raise SystemExit(main())
