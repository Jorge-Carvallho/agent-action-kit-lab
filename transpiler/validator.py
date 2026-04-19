"""
Validação robusta do input do transpilador (AI-004).

Duas camadas:
  1. JSON Schema (Draft-07) — estrutura e tipos.
  2. Regras semânticas — relações entre campos que o schema não consegue expressar sozinho.

Uso programático:
    from transpiler.validator import validate, ValidationError
    try:
        validate(spec_dict)
    except ValidationError as exc:
        print(exc.user_message())

Uso CLI:
    python transpiler/validate_spec.py examples/agent_spec.json
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
_SCHEMA_PATH = _REPO / "examples" / "agent_spec.schema.json"

_RE_IDENTIFIER = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")
_RE_SSE_PATH = re.compile(r"^https?://")
_SUPPORTED_VERSIONS = {"1.0"}


# ---------------------------------------------------------------------------
# Resultado da validação
# ---------------------------------------------------------------------------

@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def user_message(self) -> str:
        lines: list[str] = []
        if self.errors:
            lines.append(f"{len(self.errors)} erro(s) encontrado(s):")
            for e in self.errors:
                lines.append(f"  ✗ {e}")
        if self.warnings:
            lines.append(f"{len(self.warnings)} aviso(s):")
            for w in self.warnings:
                lines.append(f"  ⚠ {w}")
        if self.ok and not self.warnings:
            lines.append("✓ JSON de especificação válido.")
        return "\n".join(lines)


class ValidationError(Exception):
    def __init__(self, result: ValidationResult) -> None:
        self.result = result
        super().__init__(result.user_message())

    def user_message(self) -> str:
        return self.result.user_message()


# ---------------------------------------------------------------------------
# Camada 1: JSON Schema
# ---------------------------------------------------------------------------

def _schema_errors(instance: dict[str, Any]) -> list[str]:
    try:
        import jsonschema
    except ImportError:
        return ["Dependência 'jsonschema' não instalada. Corre: pip install -r transpiler/requirements.txt"]

    with _SCHEMA_PATH.open(encoding="utf-8") as f:
        schema = json.load(f)

    validator = jsonschema.Draft7Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
    messages: list[str] = []
    for err in errors:
        loc = " > ".join(str(p) for p in err.path) or "raiz"
        messages.append(f"[schema/{loc}] {err.message}")
    return messages


# ---------------------------------------------------------------------------
# Camada 2: Regras semânticas
# ---------------------------------------------------------------------------

def _semantic_errors(spec: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    # --- spec_version --------------------------------------------------
    version = spec.get("spec_version", "")
    if version and version not in _SUPPORTED_VERSIONS:
        errors.append(
            f"spec_version '{version}' não suportada. Versões aceites: {sorted(_SUPPORTED_VERSIONS)}."
        )

    # --- agent ---------------------------------------------------------
    agent = spec.get("agent") or {}

    name: str = agent.get("name", "")
    if name and not _RE_IDENTIFIER.match(name):
        errors.append(
            f"agent.name '{name}' inválido: usa apenas letras, dígitos e '_', e não pode começar com dígito."
        )

    app_name: str = agent.get("app_name", "")
    if app_name and not _RE_IDENTIFIER.match(app_name):
        errors.append(
            f"agent.app_name '{app_name}' inválido: mesmas regras de identificador Python."
        )

    model: str = agent.get("model", "")
    if model and not model.startswith("gemini"):
        warnings.append(
            f"agent.model '{model}' não começa com 'gemini'; o transpilador gera código só para modelos Gemini (Google ADK)."
        )

    instruction: str = agent.get("instruction", "")
    instruction_key: str = agent.get("instruction_key", "")
    if instruction and instruction_key:
        errors.append(
            "agent: define 'instruction' OU 'instruction_key', não ambos em simultâneo."
        )
    if instruction and len(instruction.strip()) < 10:
        warnings.append("agent.instruction muito curta (< 10 chars); poderá não ser útil para o modelo.")

    # --- tools ---------------------------------------------------------
    tools: list[dict] = spec.get("tools") or []
    tool_ids: list[str] = []
    mcp_roles_declared: set[str] = set()
    for i, tool in enumerate(tools):
        tid: str = tool.get("id", "")
        if tid:
            if not _RE_IDENTIFIER.match(tid):
                errors.append(
                    f"tools[{i}].id '{tid}' inválido: deve ser um identificador Python válido."
                )
            if tid in tool_ids:
                errors.append(f"tools[{i}].id '{tid}' duplicado.")
            tool_ids.append(tid)
        kind: str = tool.get("kind", "")
        mcp_role: str = tool.get("mcp_role", "")
        if kind == "mcp_sse":
            if not mcp_role:
                errors.append(
                    f"tools[{i}] (kind=mcp_sse): campo 'mcp_role' é obrigatório ('ocr' ou 'rag')."
                )
            else:
                mcp_roles_declared.add(mcp_role)
        if kind == "http_json" and mcp_role:
            warnings.append(
                f"tools[{i}] (kind=http_json): 'mcp_role' é ignorado; remove-o para clareza."
            )

    # --- mcp_servers ---------------------------------------------------
    mcp_servers: dict = spec.get("mcp_servers") or {}
    for role in ("ocr", "rag"):
        server = mcp_servers.get(role) or {}
        sse_url: str = server.get("sse_url", "")
        if sse_url:
            if not _RE_SSE_PATH.match(sse_url):
                errors.append(
                    f"mcp_servers.{role}.sse_url '{sse_url}' inválida: deve começar com 'http://' ou 'https://'."
                )
            if not sse_url.endswith("/sse"):
                warnings.append(
                    f"mcp_servers.{role}.sse_url não termina em '/sse'; confirma que o servidor MCP segue a convenção SSE."
                )
        timeout = server.get("timeout_seconds")
        if timeout is not None and timeout < 10:
            warnings.append(
                f"mcp_servers.{role}.timeout_seconds={timeout}s parece muito baixo para uma chamada MCP/SSE."
            )

    # --- Cruzamento tools ↔ mcp_servers --------------------------------
    for role in ("ocr", "rag"):
        if role in mcp_roles_declared and role not in mcp_servers:
            errors.append(
                f"tools declara 'mcp_role={role}' mas 'mcp_servers.{role}' está ausente."
            )

    # --- scheduling_api ------------------------------------------------
    api: dict = spec.get("scheduling_api") or {}
    base_url: str = api.get("base_url", "")
    if base_url and not _RE_SSE_PATH.match(base_url):
        errors.append(
            f"scheduling_api.base_url '{base_url}' inválida: deve começar com 'http://' ou 'https://'."
        )
    create_path: str = api.get("create_path", "")
    if create_path and not create_path.startswith("/"):
        errors.append(
            f"scheduling_api.create_path '{create_path}' deve começar com '/'."
        )

    # --- security.pii --------------------------------------------------
    pii: dict = (spec.get("security") or {}).get("pii") or {}
    if pii:
        enabled: bool = pii.get("enabled", True)
        before_llm: bool = pii.get("apply_before_llm", True)
        before_persist: bool = pii.get("apply_before_persist", True)
        if enabled and not (before_llm or before_persist):
            errors.append(
                "security.pii: 'enabled=true' mas ambos 'apply_before_llm' e 'apply_before_persist' são false. "
                "O desafio exige mascaramento antes de LLM e/ou persistência."
            )
        if not enabled:
            warnings.append(
                "security.pii.enabled=false: a camada PII está desativada. "
                "O desafio exige mascaramento antes de LLM e persistência."
            )

    return errors, warnings


# ---------------------------------------------------------------------------
# Ponto de entrada público
# ---------------------------------------------------------------------------

def validate(spec: dict[str, Any], *, raise_on_error: bool = True) -> ValidationResult:
    """
    Valida o dicionário `spec` em duas camadas (schema + semântica).

    Se `raise_on_error=True` (default) levanta ValidationError quando há erros.
    Se False, devolve ValidationResult para o chamador decidir.
    """
    result = ValidationResult()

    schema_errs = _schema_errors(spec)
    result.errors.extend(schema_errs)

    # Regras semânticas só correm se a estrutura de alto nível passou
    if not schema_errs:
        sem_errs, sem_warns = _semantic_errors(spec)
        result.errors.extend(sem_errs)
        result.warnings.extend(sem_warns)

    if raise_on_error and not result.ok:
        raise ValidationError(result)

    return result


def validate_file(
    spec_path: Path | str,
    *,
    raise_on_error: bool = True,
) -> ValidationResult:
    """Lê o ficheiro JSON e valida."""
    path = Path(spec_path)
    if not path.is_file():
        result = ValidationResult(errors=[f"Ficheiro não encontrado: {path}"])
        if raise_on_error:
            raise ValidationError(result)
        return result
    try:
        with path.open(encoding="utf-8") as f:
            spec = json.load(f)
    except json.JSONDecodeError as exc:
        result = ValidationResult(errors=[f"JSON inválido: {exc}"])
        if raise_on_error:
            raise ValidationError(result)
        return result

    if not isinstance(spec, dict):
        result = ValidationResult(errors=["O JSON de especificação deve ser um objecto ({}), não uma lista ou valor simples."])
        if raise_on_error:
            raise ValidationError(result)
        return result

    return validate(spec, raise_on_error=raise_on_error)
