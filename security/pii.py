"""
Deteção e mascaramento de PII em texto extraído por OCR (ou outras fontes).

Abordagem: padrões (regex) e rótulos comuns em contexto laboratorial (PT-BR).
Não substitui classificação por ML/NLP para todos os nomes livres; extensível.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

# Placeholders estáveis para auditoria e testes
MASK_EMAIL = "[E-MAIL]"
MASK_PHONE = "[TELEFONE]"
MASK_CPF = "[CPF]"
MASK_CNPJ = "[CNPJ]"
MASK_RG = "[DOCUMENTO_RG]"
MASK_NAME = "[NOME]"


@dataclass
class PIIMaskResult:
    """Texto sanitizado e registro das substituições (tipos fictícios para checklist)."""

    text: str
    replacements: list[dict[str, str]] = field(default_factory=list)


def _append_rep(out: list[dict[str, str]], kind: str, placeholder: str, snippet: str) -> None:
    """Regista substituição sem guardar o valor completo em logs longos (truncar)."""
    preview = (snippet or "").strip()
    if len(preview) > 40:
        preview = preview[:37] + "..."
    out.append({"type": kind, "placeholder": placeholder, "length_chars": str(len(snippet or ""))})


# E-mail (RFC simplificado, cobre casos típicos em OCR)
_RE_EMAIL = re.compile(
    r"\b[A-Za-z0-9][A-Za-z0-9._%+-]{0,63}@[A-Za-z0-9][A-Za-z0-9.-]{0,251}[A-Za-z0-9]\.[A-Za-z]{2,63}\b",
    re.IGNORECASE,
)

# Telefone BR: celular/fixo com DDI opcional
_RE_PHONE = re.compile(
    r"(?:\+55\s*)?"
    r"(?:\(\s*\d{2}\s*\)|\b\d{2})\s*"
    r"(?:9\s*)?\d{4}\s*[-.]?\s*\d{4}\b"
    r"|\+55\s*\d{10,11}\b"
    r"|\b\d{2}\s9\d{8}\b",
    re.VERBOSE,
)

# CPF 000.000.000-00 ou só dígitos 11
_RE_CPF = re.compile(
    r"\b(?:\d{3}[.\s]\d{3}[.\s]\d{3}[-\s]\d{2}|\d{11})\b",
)

# CNPJ
_RE_CNPJ = re.compile(
    r"\b\d{2}[.\s]?\d{3}[.\s]?\d{3}[/\s]?\d{4}[-\s]?\d{2}\b",
)

# RG comum BR (varia por estado; padrão flexível)
_RE_RG = re.compile(
    r"\b(?:RG|Rg|r\.g\.?)\s*[:]?\s*([0-9A-Za-z.\-]{4,20})\b"
    r"|\b\d{1,2}[.\s]?\d{3}[.\s]?\d{3}[-\s]?[0-9Xx]\b",
    re.IGNORECASE,
)

# Nome após rótulos típicos (receita / cadastro laboratorial)
_RE_LABELED_NAME = re.compile(
    r"(?im)^\s*(?:"
    r"paciente|nome\s*(?:completo)?|nome\s+do\s+paciente|beneficiário|titular"
    r")\s*[:]\s*(.+?)(?=\s*$|\n)",
)

# Sequência de 2+ tokens com iniciais maiúsculas (heurística fraca; opcional)
_RE_PROPER_SEQUENCE = re.compile(
    r"\b(?:[A-ZÀ-Ý][a-zà-ÿ]+(?:\s+[A-ZÀ-Ý][a-zà-ÿ]+){1,4})\b",
)


def _mask_cpf(text: str, reps: list[dict[str, str]]) -> str:
    def sub(m: re.Match[str]) -> str:
        _append_rep(reps, "cpf", MASK_CPF, m.group(0))
        return MASK_CPF

    return _RE_CPF.sub(sub, text)


def _mask_cnpj(text: str, reps: list[dict[str, str]]) -> str:
    def sub(m: re.Match[str]) -> str:
        _append_rep(reps, "cnpj", MASK_CNPJ, m.group(0))
        return MASK_CNPJ

    return _RE_CNPJ.sub(sub, text)


def _mask_email(text: str, reps: list[dict[str, str]]) -> str:
    def sub(m: re.Match[str]) -> str:
        _append_rep(reps, "email", MASK_EMAIL, m.group(0))
        return MASK_EMAIL

    return _RE_EMAIL.sub(sub, text)


def _mask_phone(text: str, reps: list[dict[str, str]]) -> str:
    def sub(m: re.Match[str]) -> str:
        _append_rep(reps, "phone", MASK_PHONE, m.group(0))
        return MASK_PHONE

    return _RE_PHONE.sub(sub, text)


def _mask_rg(text: str, reps: list[dict[str, str]]) -> str:
    def sub(m: re.Match[str]) -> str:
        _append_rep(reps, "rg", MASK_RG, m.group(0))
        return MASK_RG

    return _RE_RG.sub(sub, text)


def _mask_labeled_names(text: str, reps: list[dict[str, str]]) -> str:
    """Substitui conteúdo após rótulos Paciente:, Nome:, etc."""

    def sub(m: re.Match[str]) -> str:
        label = m.group(0).split(":", 1)[0]
        value = m.group(1).strip()
        if len(value) < 3:
            return m.group(0)
        _append_rep(reps, "name_labeled", MASK_NAME, value)
        return f"{label.strip()}: {MASK_NAME}"

    return _RE_LABELED_NAME.sub(sub, text)


def _mask_proper_names_aggressive(text: str, reps: list[dict[str, str]], enabled: bool) -> str:
    """
    Heurística opcional: sequências tipo Nome Sobrenome.
    Desligada por defeito para evitar mascarar nomes de exames ou laboratório.
    """
    if not enabled:
        return text

    seen: set[str] = set()

    def sub(m: re.Match[str]) -> str:
        g = m.group(0)
        if g in seen:
            return g
        seen.add(g)
        _append_rep(reps, "name_heuristic", MASK_NAME, g)
        return MASK_NAME

    return _RE_PROPER_SEQUENCE.sub(sub, text)


_RE_DIGITS_HEAVY = re.compile(r"^[\d\s.\-/()]+$")


def defensive_filter_exam_candidates(
    names: list[str],
    *,
    max_len: int = 160,
) -> list[str]:
    """
    Remove da lista de candidatos a exame itens que frequentemente são PII
    ou ruído (CPF, e-mail, linhas só com dígitos, texto curto demais sem letras).

    Não substitui o RAG; reduz vazamento de dados para o MCP RAG e para logs.
    """
    out: list[str] = []
    for raw in names or []:
        s = (raw or "").strip()
        if len(s) < 2:
            continue
        if len(s) > max_len:
            s = s[:max_len].rstrip()
        if _RE_EMAIL.search(s) or "@" in s:
            continue
        if _RE_DIGITS_HEAVY.match(s) and len(s) < 48:
            continue
        letters = sum(1 for c in s if c.isalpha())
        if letters < 3:
            continue
        # Linha com muitos dígitos e poucas letras = provável documento
        digits = sum(1 for c in s if c.isdigit())
        if digits >= 8 and digits > letters * 2:
            continue
        if s not in out:
            out.append(s)
    return out


def mask_pii(
    text: str,
    *,
    mask_heuristic_names: bool = False,
) -> PIIMaskResult:
    """
    Aplica mascaramento de PII ao texto.

    Ordem: e-mail e telefone (podem colidir com dígitos), depois CNPJ/CPF, RG,
    nomes por rótulo, e por fim heurística de nomes próprios se solicitada.

    Args:
        text: conteúdo bruto (ex.: saída de OCR).
        mask_heuristic_names: se True, tenta mascarar sequências Nome Sobrenome
            (pode gerar falsos positivos em títulos ou nomes de exames).
    """
    if not text:
        return PIIMaskResult(text=text or "")

    reps: list[dict[str, str]] = []
    out = text

    out = _mask_email(out, reps)
    # CPF/CNPJ antes de telefone: sequências de 11 dígitos não viram DDD+9 dígitos por engano
    out = _mask_cnpj(out, reps)
    out = _mask_cpf(out, reps)
    out = _mask_phone(out, reps)
    out = _mask_rg(out, reps)
    out = _mask_labeled_names(out, reps)
    out = _mask_proper_names_aggressive(out, reps, mask_heuristic_names)

    return PIIMaskResult(text=out, replacements=reps)


def sanitize_api_text_field(
    value: str | None,
    *,
    max_len: int = 512,
    default: str | None = None,
    apply_pii_mask: bool = True,
) -> str | None:
    """
    Normaliza campos livres antes de HTTP (patient_reference, notes):
    caracteres imprimíveis, mascaramento PII (predefinição), truncagem.
    """
    if value is None:
        return default
    t = "".join(c for c in value if c.isprintable())
    t = " ".join(t.split())
    if not t:
        return default
    if apply_pii_mask:
        t = mask_pii(t).text
    if len(t) > max_len:
        t = t[:max_len].rstrip()
    return t if t else default
