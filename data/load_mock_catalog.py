"""Carrega a base fictícia `exams_mock.json` para o futuro serviço RAG MCP."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent


def catalog_path() -> Path:
    return _ROOT / "exams_mock.json"


def load_mock_catalog() -> dict[str, Any]:
    """Devolve o documento JSON completo (metadados + lista `exams`)."""
    p = catalog_path()
    with p.open(encoding="utf-8") as f:
        return json.load(f)


def load_mock_exams() -> list[dict[str, Any]]:
    """Lista de exames: cada item tem ``code``, ``name``, ``short_description``, ``synonyms``."""
    data = load_mock_catalog()
    exams = data.get("exams")
    if not isinstance(exams, list):
        return []
    return exams
