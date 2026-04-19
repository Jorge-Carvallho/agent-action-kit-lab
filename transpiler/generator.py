"""
Geração de código Python a partir do JSON de especificação (AI-005).

O ficheiro gerado instancia exclusivamente `google.adk.agents.Agent` e
`google.adk.runners.InMemoryRunner`, alinhado ao padrão de `agent_factory.py`.

Uso:
    from transpiler.generator import generate_source, write_generated_agent
    write_generated_agent(Path("examples/agent_spec.json"), Path("examples/generated_agent.py"))
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]


def _binding_for_tool_entry(t: dict[str, Any]) -> tuple[str, str, str]:
    """
    Mapeia uma entrada de ``spec.tools`` para (módulo Python, símbolo, id no JSON).

    Usado apenas após ``validate()``; entradas inválidas levantam ``ValueError`` claro.
    """
    tid = str(t.get("id", "?"))
    kind = t.get("kind")
    if kind == "mcp_sse":
        role = t.get("mcp_role")
        if role == "ocr":
            return ("tools.ocr_tool", "ocr_extract_exams", tid)
        if role == "rag":
            return ("tools.rag_tool", "rag_lookup_exam_codes", tid)
        raise ValueError(
            f"spec.tools[{tid!r}]: kind=mcp_sse requer mcp_role 'ocr' ou 'rag'."
        )
    if kind == "http_json":
        return ("tools.scheduling_tool", "submit_appointment_request", tid)
    raise ValueError(f"spec.tools[{tid!r}]: kind desconhecido {kind!r}.")


def _build_tools_codegen(spec: dict[str, Any]) -> tuple[str, str]:
    """
    Devolve (bloco de imports + comentários, expressão Python para o argumento ``tools=``).

    Se ``spec.tools`` vazio/ausente, ``tools=[]``.
    """
    entries = spec.get("tools") or []
    if not entries:
        return ("", "[]")

    lines_comment = [
        "# --- Tools ligadas ao contrato JSON (spec.tools) ---",
        "# Endpoints MCP e base da API: tools.config (env / defaults alinhados a agent_spec.json).",
    ]
    ordered: list[tuple[str, str, str]] = []
    for t in entries:
        ordered.append(_binding_for_tool_entry(t))

    for _mod, sym, tid in ordered:
        lines_comment.append(f"#   • id={tid!r} → {sym}")

    seen: set[tuple[str, str]] = set()
    import_lines: list[str] = []
    for mod, sym, _ in ordered:
        key = (mod, sym)
        if key in seen:
            continue
        seen.add(key)
        import_lines.append(f"from {mod} import {sym}")

    ft_lines = [f"            FunctionTool({sym}),  # id={tid!r}" for mod, sym, tid in ordered]
    tools_list = "[\n" + ",\n".join(ft_lines) + "\n        ]"

    body = "\n".join(
        [
            "\n".join(lines_comment),
            "from google.adk.tools.function_tool import FunctionTool",
            "\n".join(import_lines),
            "",
        ]
    )
    return body, tools_list


def _parents_index_to_repo_root(output_path: Path, repo: Path) -> int:
    """Índice `n` tal que `Path(__file__).resolve().parents[n]` é a raiz do repositório."""
    out = output_path.resolve()
    repo = repo.resolve()
    rel_parent = out.relative_to(repo).parent
    return len(rel_parent.parts)


def _resolve_instruction(spec: dict[str, Any], repo: Path) -> str:
    """Resolve instrução inline ou via instruction_key (módulos em prompts/)."""
    agent = spec["agent"]
    if agent.get("instruction"):
        return str(agent["instruction"])
    key = (agent.get("instruction_key") or "").strip()
    if not key:
        raise ValueError("agent: falta 'instruction' ou 'instruction_key'.")

    runtime = repo / "runtime"
    if str(runtime) not in sys.path:
        sys.path.insert(0, str(runtime))

    if key == "lab_example":
        from agent_action.prompts.lab_example import AGENT_PROMPT

        return AGENT_PROMPT
    if key == "generic":
        from agent_action.prompts.generic import AGENT_PROMPT

        return AGENT_PROMPT

    raise ValueError(
        f"instruction_key desconhecida: {key!r}. "
        "Suportadas neste gerador: 'lab_example', 'generic' (ou use 'instruction' inline)."
    )


def generate_source(
    spec: dict[str, Any],
    *,
    repo_root: Path | None = None,
    output_path: Path | None = None,
) -> str:
    """
    Devolve o código-fonte Python completo.
    `spec` deve já ter passado `validate()`.
    """
    repo = repo_root or _REPO
    out = output_path or (repo / "examples" / "generated_agent.py")
    parent_idx = _parents_index_to_repo_root(out, repo)

    agent = spec["agent"]
    name = agent["name"]
    app_name = agent["app_name"]
    model = agent["model"]
    profile = agent["profile"]
    instruction = _resolve_instruction(spec, repo)

    instruction_literal = repr(instruction)

    tools_import_block, tools_expr = _build_tools_codegen(spec)

    return f'''# -*- coding: utf-8 -*-
# Gerado automaticamente pelo transpilador (AI-005). Não editar à mão — regenerar a partir do JSON.
# spec_version: {spec.get("spec_version", "?")}

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[{parent_idx}]
_RUNTIME = _REPO_ROOT / "runtime"
if str(_RUNTIME) not in sys.path:
    sys.path.insert(0, str(_RUNTIME))

# Raiz do repositório (pacote `tools/` no topo) — necessário para imports das FunctionTools geradas.
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(_REPO_ROOT / ".env")
    load_dotenv(_RUNTIME / "agent_action" / ".env")
except ImportError:
    pass

# Perfil alinhado à especificação (útil se forem importados módulos do kit).
os.environ.setdefault("AGENT_ACTION", {profile!r})

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner

# Valores da especificação (para mensagens de smoke)
_APP_NAME = {app_name!r}
_AGENT_NAME = {name!r}

INSTRUCTION = {instruction_literal}

{tools_import_block}
def build_agent_and_runner():
    """Instancia Agent + InMemoryRunner (exclusivamente Google ADK)."""
    root_agent = Agent(
        name={name!r},
        model={model!r},
        instruction=INSTRUCTION,
        tools={tools_expr},
    )
    runner = InMemoryRunner(agent=root_agent, app_name={app_name!r})
    return root_agent, runner


def main() -> None:
    parser = argparse.ArgumentParser(description="Agente gerado pelo transpilador (Google ADK).")
    parser.add_argument(
        "--chat",
        action="store_true",
        help="Chama o modelo (requer GOOGLE_API_KEY). Sem isto, apenas smoke (instancia sem rede).",
    )
    parser.add_argument(
        "message",
        nargs="?",
        default="Olá. Responde em uma frase qual é o teu papel.",
        help="Mensagem para --chat",
    )
    args = parser.parse_args()

    if args.chat:
        if not os.getenv("GOOGLE_API_KEY", "").strip():
            print("Erro: define GOOGLE_API_KEY no .env da raiz do repositório.", file=sys.stderr)
            sys.exit(1)
        _, runner = build_agent_and_runner()

        async def _run():
            await runner.run_debug(args.message, verbose=False)

        asyncio.run(_run())
    else:
        _, runner = build_agent_and_runner()
        has_key = bool(os.getenv("GOOGLE_API_KEY", "").strip())
        print("OK — ADK: Agent + InMemoryRunner criados (smoke).")
        print(f"    app_name={{_APP_NAME!r}} agent_name={{_AGENT_NAME!r}}")
        print(f"    GOOGLE_API_KEY definida: {{has_key}} (use --chat para inferência)")


if __name__ == "__main__":
    main()
'''


def write_generated_agent(
    spec_path: Path | str,
    output_path: Path | str,
    *,
    repo_root: Path | None = None,
    validate_first: bool = True,
) -> Path:
    """
    Lê o JSON, valida (opcional), gera e escreve o ficheiro Python.
    """
    repo = repo_root or _REPO
    spec_path = Path(spec_path)
    output_path = Path(output_path)

    with spec_path.open(encoding="utf-8") as f:
        spec = json.load(f)

    if validate_first:
        sys.path.insert(0, str(repo))
        from transpiler.validator import validate  # noqa: PLC0415

        validate(spec, raise_on_error=True)

    source = generate_source(spec, repo_root=repo, output_path=output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(source, encoding="utf-8")
    return output_path.resolve()
