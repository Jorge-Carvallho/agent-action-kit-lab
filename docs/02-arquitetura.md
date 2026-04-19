# Arquitetura

## Componentes

- `transpiler/`: valida `agent_spec.json` e gera codigo ADK
- `runtime/agent_action/`: runtime do agente (perfil, prompts, tools)
- `mcp_ocr/`: servidor MCP SSE para extracao de texto de imagem
- `mcp_rag/`: servidor MCP SSE para resolucao de codigos de exame
- `api/`: FastAPI de agendamento ficticio
- `cli/`: orquestracao do fluxo no terminal
- `security/`: regras de tratamento de PII
- `tools/`: ponte entre agente/CLI e servicos MCP/API

## Integracoes

- CLI -> MCP OCR (`/sse`) para extrair exames
- CLI -> MCP RAG (`/sse`) para mapear codigos
- CLI -> API (`/api/v1/appointments`) para confirmar pedido
- Runtime ADK -> `tools/*` para usar o mesmo caminho de integracao

## Contratos e configuracao

- Contrato JSON do agente: `examples/agent_spec.json`
- Schema: `examples/agent_spec.schema.json`
- Documentacao do contrato: `examples/AGENT_SPEC.md`
- URLs default de integracao: `tools/config.py`

## Seguranca e dados

- Dados do dominio sao ficticios.
- PII e tratada antes de persistencia ou continuidade do fluxo.
- Catalogo de exames e mock: `data/exams_mock.json`.

## Rastreabilidade com cards

Mapeamento completo AI-001 ... AI-016 em `docs/REFERENCIA_CARDS_DESAFIO.md`.
