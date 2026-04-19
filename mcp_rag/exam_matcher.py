"""
Correspondência simples entre nomes vindos do OCR e a base mock de exames.

Estratégia: normalização (minúsculas, sem acentos), igualdade/substrings em nome
e sinónimos, mais sobreposição de tokens relevantes — sem dependências pesadas.
"""
from __future__ import annotations

import re
import unicodedata
from functools import lru_cache
from typing import Any

# Carregamento preguiçoso do catálogo
_catalog_cache: list[dict[str, Any]] | None = None


def _load_exams() -> list[dict[str, Any]]:
    global _catalog_cache
    if _catalog_cache is None:
        from data.load_mock_catalog import load_mock_exams

        _catalog_cache = load_mock_exams()
    return _catalog_cache


def reload_catalog_for_tests() -> None:
    """Limpa cache (apenas testes)."""
    global _catalog_cache
    _catalog_cache = None


def normalize_text(s: str) -> str:
    s = (s or "").strip().lower()
    if not s:
        return ""
    decomposed = unicodedata.normalize("NFD", s)
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn")


def _tokens(norm: str) -> set[str]:
    parts = re.split(r"[^\w]+", norm, flags=re.UNICODE)
    return {p for p in parts if len(p) >= 3}


def _score_query_against_exam(q: str, exam: dict[str, Any]) -> tuple[int, str]:
    """
    Devolve (pontuação, motivo). Pontuação 0 = sem correspondência utilizável.
    """
    nq = normalize_text(q)
    if not nq:
        return (0, "empty_query")

    name = exam.get("name") or ""
    nn = normalize_text(name)
    if not nn:
        return (0, "none")

    if nq == nn:
        return (1000, "exact_name")
    if nq in nn:
        return (920, "query_in_canonical")
    if nn in nq:
        return (900, "canonical_in_query")

    for syn in exam.get("synonyms") or []:
        ns = normalize_text(str(syn))
        if not ns:
            continue
        if nq == ns:
            return (960, "synonym_exact")
        # Sinónimos muito curtos ("Ca", "Na") não usam substring (evita acertos em "catalogo", etc.)
        if len(ns) >= 4 and (nq in ns or ns in nq):
            return (880, "synonym_substring")

    qt, nt = _tokens(nq), _tokens(nn)
    inter = qt & nt
    if inter:
        # Uma palavra curta demais é fraca; exige token mais longo ou vários tokens
        long_hits = sum(1 for t in inter if len(t) >= 5)
        score = 320 + 55 * len(inter) + 30 * long_hits
        if len(inter) == 1:
            only = next(iter(inter))
            if len(only) < 5 and long_hits == 0:
                score = min(score, 200)
        return (score, "token_overlap")

    return (0, "none")


_MIN_SCORE = 350


def match_single_exam(query: str) -> dict[str, Any]:
    """
    Encontra o melhor exame para uma string de consulta.

    Devolve dicionário com chaves: matched, code, canonical_name, short_description,
    confidence, match_reason, query.
    """
    q = (query or "").strip()
    base: dict[str, Any] = {
        "query": q,
        "matched": False,
        "code": None,
        "canonical_name": None,
        "short_description": None,
        "confidence": "none",
        "match_reason": "none",
    }

    if not normalize_text(q):
        base["match_reason"] = "empty_query"
        return base

    exams = _load_exams()
    best: tuple[int, str, dict[str, Any]] | None = None
    for exam in exams:
        score, reason = _score_query_against_exam(q, exam)
        if score < _MIN_SCORE:
            continue
        if best is None or score > best[0] or (
            score == best[0] and (exam.get("code") or "") < (best[2].get("code") or "")
        ):
            best = (score, reason, exam)

    if best is None:
        return base

    score, reason, exam = best
    base.update(
        {
            "matched": True,
            "code": exam.get("code"),
            "canonical_name": exam.get("name"),
            "short_description": exam.get("short_description"),
            "match_reason": reason,
        }
    )
    if score >= 900:
        base["confidence"] = "high"
    elif score >= 700:
        base["confidence"] = "medium"
    else:
        base["confidence"] = "low"

    return base


def resolve_exam_names(exam_names: list[str]) -> dict[str, Any]:
    """
    Resolve uma lista de nomes (ex.: saída do OCR) contra o catálogo.

    Devolve ``catalog_id``, ``record_count`` e ``results`` (lista alinhada à entrada).
    """
    from data.load_mock_catalog import load_mock_catalog

    meta = load_mock_catalog()
    results = [match_single_exam(x) for x in (exam_names or [])]
    return {
        "catalog_id": meta.get("catalog_id", "unknown"),
        "record_count": meta.get("record_count", len(_load_exams())),
        "results": results,
    }


@lru_cache(maxsize=1)
def catalog_stats() -> tuple[str, int]:
    from data.load_mock_catalog import load_mock_catalog

    m = load_mock_catalog()
    return (str(m.get("catalog_id", "")), int(m.get("record_count", 0)))
