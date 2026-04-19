"""
Motor de OCR (fictício / desafio): extrai nomes de exames a partir de bytes de imagem.

- Se ``Pillow`` + ``pytesseract`` + binário Tesseract estiverem disponíveis, tenta OCR real.
- Caso contrário (ou texto vazio), modo **demo** determinístico via ``OCR_DEMO_EXAMS_JSON``.
"""
from __future__ import annotations

import base64
import io
import json
import os
import re
from typing import Any

_NOISE = re.compile(r"^\s*(pedido|solicitação|exame|dr|dra|paciente|data|crm)\b", re.I)


def _lines_to_exam_candidates(lines: list[str]) -> list[str]:
    out: list[str] = []
    for raw in lines:
        line = raw.strip()
        if len(line) < 3:
            continue
        if _NOISE.match(line):
            continue
        if len(line) < 4 and not re.search(r"[A-Za-zÀ-ÿ]{4,}", line):
            continue
        if line not in out:
            out.append(line)
    return out[:20]


def _demo_payload(raw_text: str | None) -> dict[str, Any]:
    demo = os.getenv(
        "OCR_DEMO_EXAMS_JSON",
        '["Hemograma completo", "Glicemia em jejum", "Perfil lipídico"]',
    )
    try:
        names = json.loads(demo)
        if not isinstance(names, list):
            names = ["Hemograma completo", "Glicemia em jejum"]
        else:
            names = [str(x) for x in names]
    except json.JSONDecodeError:
        names = ["Hemograma completo", "Glicemia em jejum"]

    return {
        "exam_names": names,
        "engine": "demo",
        "raw_text": raw_text,
        "note": "Tesseract/Pillow indisponível, OCR vazio ou sem linhas úteis — lista fictícia (OCR_DEMO_EXAMS_JSON).",
    }


def ocr_image_bytes(image_bytes: bytes) -> dict[str, Any]:
    raw_text: str | None = None

    try:
        from PIL import Image  # noqa: PLC0415
        import pytesseract  # noqa: PLC0415
    except ImportError:
        return _demo_payload(None)

    try:
        img = Image.open(io.BytesIO(image_bytes))
    except Exception:  # noqa: BLE001
        return _demo_payload(None)

    try:
        try:
            raw_text = pytesseract.image_to_string(img, lang="por+eng")
        except Exception:  # noqa: BLE001
            raw_text = pytesseract.image_to_string(img, lang="eng")
    except Exception:  # noqa: BLE001 — Tesseract não instalado no sistema
        return _demo_payload(None)

    lines = [ln for ln in (raw_text or "").splitlines()]
    names = _lines_to_exam_candidates(lines)
    if names:
        return {"exam_names": names, "engine": "tesseract", "raw_text": raw_text}

    return _demo_payload(raw_text)


def decode_base64_image(data: str) -> bytes:
    """Decodifica base64 (com ou sem prefixo data:image/...;base64,)."""
    s = data.strip()
    if "base64," in s:
        s = s.split("base64,", 1)[1]
    s = re.sub(r"\s+", "", s)
    return base64.b64decode(s, validate=True)
