#!/usr/bin/env python3
"""
CLI do fluxo laboratorial fictício: imagem → OCR (MCP SSE) → PII → RAG (MCP SSE) → API.

Uso (na raiz do repositório):
  python run_lab_cli.py /caminho/para/pedido.png
  python run_lab_cli.py imagem.png --dry-run
  python run_lab_cli.py imagem.png --offline --dry-run   # motores locais, sem MCP
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from cli.flow import LabFlowResult, run_pipeline


def format_report(r: LabFlowResult) -> str:
    lines: list[str] = []
    lines.append("")
    lines.append("=== Fluxo laboratorial (demonstração fictícia) ===")
    lines.append(f"Imagem: {r.image_path}")
    backend = "MCP SSE (OCR + RAG)" if r.flow_backend == "mcp_sse" else "local (sem servidores MCP)"
    lines.append(f"Backend: {backend}")
    lines.append(f"Motor OCR: {r.ocr_engine}")
    if r.ocr_note:
        lines.append(f"Nota OCR: {r.ocr_note}")
    lines.append("")
    lines.append("— Exames (candidatos do OCR) —")
    if r.exam_names:
        for i, name in enumerate(r.exam_names, 1):
            lines.append(f"  {i}. {name}")
    else:
        lines.append("  (nenhuma linha candidata)")
    lines.append("")
    if r.raw_text_preview_masked:
        lines.append("— Prévia do texto OCR (PII mascarada) —")
        short = r.raw_text_preview_masked.replace("\n", " ")
        if len(short) > 300:
            short = short[:297] + "..."
        lines.append(f"  {short}")
        lines.append("")
    lines.append("— RAG (códigos na base mock) —")
    for row in r.rag_payload.get("results", []):
        q = row.get("query", "")
        if row.get("matched"):
            lines.append(
                f"  • {q!r} → {row.get('code')} | {row.get('canonical_name')} "
                f"({row.get('confidence', '?')})"
            )
        else:
            lines.append(f"  • {q!r} → sem match")
    lines.append("")
    lines.append("— Agendamento (API FastAPI fictícia) —")
    if r.skipped_appointment and r.appointment_response is None and not r.appointment_error:
        lines.append("  (pedido não enviado)")
    if r.appointment_error:
        lines.append(f"  Erro: {r.appointment_error}")
    if r.appointment_response:
        ar = r.appointment_response
        lines.append(f"  Estado: {ar.get('status', '—')}")
        lines.append(f"  ID: {ar.get('appointment_id', '—')}")
        lines.append(f"  Mensagem: {ar.get('message', '—')}")
        lines.append(f"  Exames no pedido: {ar.get('exam_count', '—')}")
    for e in r.errors:
        lines.append(f"  Aviso: {e}")
    lines.append("")
    lines.append("=== Fim ===")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Executa o fluxo imagem → OCR → PII → RAG → agendamento (dados fictícios).",
    )
    parser.add_argument(
        "image",
        type=Path,
        help="Caminho para ficheiro de imagem (pedido médico fictício).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Não chama a API de agendamento (só OCR + RAG).",
    )
    parser.add_argument(
        "--patient-ref",
        default=os.getenv("CLI_PATIENT_REF"),
        help="Referência fictícia do utente (opcional; ou env CLI_PATIENT_REF).",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Usa OCR+RAG em processo (sem MCP SSE). Predefinição é MCP real (URLs em tools.config / env).",
    )
    args = parser.parse_args(argv)

    offline = args.offline or os.getenv("LAB_CLI_OFFLINE", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )

    if not args.image.is_file():
        print(f"Erro: ficheiro não encontrado: {args.image}", file=sys.stderr)
        return 2

    r = run_pipeline(
        args.image,
        submit_appointment=not args.dry_run,
        patient_reference=args.patient_ref,
        offline=offline,
    )
    sys.stdout.write(format_report(r))
    if r.errors:
        return 1
    if args.dry_run:
        return 0
    if r.appointment_response is not None:
        return 0
    if r.appointment_error and "Nenhum exame com match" in r.appointment_error:
        return 0
    if r.appointment_error:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
