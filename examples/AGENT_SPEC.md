# Contrato JSON — especificação do agente (transpilador)

Versão do contrato: **`1.0`** (`spec_version`).

Este documento descreve os campos de `agent_spec.json` e o **schema** em `agent_spec.schema.json`. O transpilador deve **validar** o JSON contra o schema e gerar código Python que instancia o agente **exclusivamente** com o Google ADK.

## Alinhamento ao desafio (PDF)

O contrato cobre apenas o que o enunciado exige para o **transpilador** e o **runtime**: identidade do agente (ADK), ligação a **MCP OCR/RAG via SSE**, **API FastAPI** de agendamento, regras de **PII** (antes de LLM e persistência) e modo de saída do **CLI**. O perfil **`lab`** no exemplo corresponde ao caso de uso da clínica laboratorial fictícia; **`generic`** no schema é opcional (kit) e **não** é necessário para cumprir o mínimo do desafio.

## Campos obrigatórios (nível raiz)

| Campo | Tipo | Descrição |
|--------|------|-----------|
| `spec_version` | string | Deve ser `"1.0"` (permite evoluir o contrato em versões futuras). |
| `agent` | object | Nome, `app_name`, modelo, perfil e instrução (ver abaixo). |
| `mcp_servers` | object | `ocr` e `rag`, cada um com `sse_url` (MCP **só SSE**, conforme desafio). |
| `scheduling_api` | object | URL base da FastAPI fictícia e paths de agendamento. |
| `security` | object | Bloco `pii` com flags e regras de mascaramento. |
| `cli` | object | `output_mode` (`human` ou `json`). |

## Campos opcionais (nível raiz)

| Campo | Tipo | Descrição |
|--------|------|-----------|
| `metadata` | object | Título, descrição, tags — **não** afetam o runtime; útil para documentação. |
| `tools` | array | Lista declarativa de tools (`mcp_sse` + `mcp_role`, ou `http_json`) para o transpilador gerar bindings. |

## Objeto `agent`

| Campo | Obrigatório | Descrição |
|--------|-------------|-----------|
| `name` | sim | Nome do agente ADK (ex.: `lab_scheduler`). Alinha com `RuntimeConfig.agent_name`. |
| `app_name` | sim | `app_name` do Runner (ex.: `lab_exam_scheduler_kit`). |
| `model` | sim | Modelo Gemini (ex.: `gemini-2.5-flash`). |
| `profile` | sim | `lab` ou `generic` — mesmo conceito do `AGENT_ACTION`/`get_agent_profile()` no runtime atual. |
| `instruction` | um dos dois | Texto de instrução **inline** (system prompt). |
| `instruction_key` | um dos dois | Chave para resolver o prompt (ex.: `lab_example` → texto em `prompts/laboratory.py` via `prompts/lab_example.py`). **Um** de `instruction` ou `instruction_key` é obrigatório. |

## Objeto `mcp_servers`

| Campo | Descrição |
|--------|-----------|
| `ocr.sse_url` | URL do servidor MCP de OCR (SSE). |
| `ocr.timeout_seconds` | Opcional; timeout em segundos. |
| `rag` | Idem para RAG. |

## Objeto `scheduling_api`

| Campo | Descrição |
|--------|-----------|
| `base_url` | URL base da API (deve bater com o Swagger `/docs`). |
| `create_path` | Path para criar o pedido de agendamento (contrato consumido pelo agente). |
| `health_path` | Opcional; health check. |

## Objeto `security.pii`

| Campo | Descrição |
|--------|-----------|
| `enabled` | Liga/desliga a camada PII. |
| `apply_before_llm` | Obrigatório pelo desafio: mascarar **antes** de enviar ao LLM. |
| `apply_before_persist` | mascarar **antes** de persistir. |
| `note` | Texto livre para implementação (categorias, etc.). |

## Objeto `cli`

| Campo | Descrição |
|--------|-----------|
| `output_mode` | `human` (legível) ou `json` (automação). |

## Itens `tools[]` (opcional)

| Campo | Descrição |
|--------|-----------|
| `id` | Identificador estável no código gerado. |
| `kind` | `mcp_sse` (ligar a `mcp_servers`) ou `http_json` (API HTTP). |
| `mcp_role` | Para `mcp_sse`: `ocr` ou `rag`. |
| `description` | Documentação da ferramenta. |

## Coerência com o runtime atual (`runtime/agent_action/`)

- `agent.profile` ↔ `lab` / `generic` e prompts em `prompt_loader` / `prompts/`.
- `agent.name`, `agent.app_name`, `agent.model` ↔ `RuntimeConfig` + `Agent` em `agent_factory.py`.
- `tools` ↔ lista passada a `get_runtime_config(extra_tools=[...])` (gerada pelo transpilador).
- `mcp_servers` / `scheduling_api` ↔ clientes gerados como tools ADK.
- `security.pii` ↔ camada que substitui/amplia `guardrail_example.py` + módulo em `security/`.

## Validação

```bash
python transpiler/validate_spec.py examples/agent_spec.json
```

Requer o pacote `jsonschema` (ver `transpiler/requirements.txt`).
