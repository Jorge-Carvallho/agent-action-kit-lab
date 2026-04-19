#!/usr/bin/env bash
# Demonstração reproduzível: health checks + CLI em modo --dry-run (MCP SSE).
# Uso: na raiz do repo, com `docker compose up -d` já executado.
#
# Python: usa .venv/bin/python se existir (recomendado após pip install -r requirements.txt);
# senão PYTHON do ambiente ou python3.

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ -x "${ROOT}/.venv/bin/python" ]; then
  PY="${PYTHON:-${ROOT}/.venv/bin/python}"
elif [ -n "${PYTHON:-}" ]; then
  PY="$PYTHON"
else
  PY="python3"
fi

echo "=== Python: $PY ==="

echo "=== Health (localhost) ==="
curl -sf "http://127.0.0.1:8000/health" && echo "" || {
  echo "Erro: API em :8000 indisponível. Suba a stack: docker compose up -d" >&2
  exit 1
}
curl -sf "http://127.0.0.1:3100/health" && echo "" || {
  echo "Aviso: MCP OCR indisponível em :3100" >&2
  exit 1
}
curl -sf "http://127.0.0.1:3200/health" && echo "" || {
  echo "Aviso: MCP RAG indisponível em :3200" >&2
  exit 1
}

echo "=== CLI (MCP SSE, dry-run) ==="
exec "$PY" run_lab_cli.py "${ROOT}/examples/sample_prescription.png" --dry-run
