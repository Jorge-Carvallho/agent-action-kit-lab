# -*- coding: utf-8 -*-
# Gerado automaticamente pelo transpilador (AI-005). Não editar à mão — regenerar a partir do JSON.
# spec_version: 1.0

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
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
os.environ.setdefault("AGENT_ACTION", 'lab')

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner

# Valores da especificação (para mensagens de smoke)
_APP_NAME = 'lab_exam_scheduler_kit'
_AGENT_NAME = 'lab_scheduler'

INSTRUCTION = 'Você é o assistente de **agendamento de exames laboratoriais** neste cenário de **demonstração fictícia**.\nO seu papel é operacional: ajudar a identificar exames pedidos, confirmar códigos na base e registar o pedido de agendamento.\n\n**Domínio:** laboratório fictício; todos os dados são de exemplo — nunca trate informação como real ou clínica definitiva.\n\n**Fluxo de trabalho (use as ferramentas nesta ordem quando aplicável):**\n1. **Imagem:** se o utilizador fornecer ou referir o pedido médico como imagem, use a ferramenta de OCR para obter nomes de exames candidatos.\n2. **Resolução de códigos:** com a lista de nomes (ou após o utilizador citar exames), use a ferramenta de RAG para obter **código** (`LAB-F…`), **nome canónico** e descrição curta de cada exame reconhecido.\n3. **Agendamento:** quando tiver uma lista consistente de exames com código e nome canónico, use a ferramenta de agendamento para submeter o pedido à API fictícia e reportar o **ID de confirmação** devolvido.\n\n**Regras obrigatórias:**\n- **Não invente** códigos de exame nem nomes oficiais: use apenas o que as ferramentas devolverem, ou diga claramente que não encontrou correspondência.\n- Se o RAG não encontrar um exame, informe o utilizador e peça reformulação ou confirmação do nome.\n- Respostas **objectivas** e em português; evite jargão de vendas ou marketing.\n- Se faltar imagem ou dados para avançar, peça **um único próximo passo** claro (ex.: enviar imagem em Base64, ou listar nomes dos exames).\n\n'

# --- Tools ligadas ao contrato JSON (spec.tools) ---
# Endpoints MCP e base da API: tools.config (env / defaults alinhados a agent_spec.json).
#   • id='ocr_exams' → ocr_extract_exams
#   • id='rag_exam_codes' → rag_lookup_exam_codes
#   • id='schedule_appointment' → submit_appointment_request
from google.adk.tools.function_tool import FunctionTool
from tools.ocr_tool import ocr_extract_exams
from tools.rag_tool import rag_lookup_exam_codes
from tools.scheduling_tool import submit_appointment_request

def build_agent_and_runner():
    """Instancia Agent + InMemoryRunner (exclusivamente Google ADK)."""
    root_agent = Agent(
        name='lab_scheduler',
        model='gemini-2.5-flash',
        instruction=INSTRUCTION,
        tools=[
            FunctionTool(ocr_extract_exams),  # id='ocr_exams',
            FunctionTool(rag_lookup_exam_codes),  # id='rag_exam_codes',
            FunctionTool(submit_appointment_request),  # id='schedule_appointment'
        ],
    )
    runner = InMemoryRunner(agent=root_agent, app_name='lab_exam_scheduler_kit')
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
        print(f"    app_name={_APP_NAME!r} agent_name={_AGENT_NAME!r}")
        print(f"    GOOGLE_API_KEY definida: {has_key} (use --chat para inferência)")


if __name__ == "__main__":
    main()
