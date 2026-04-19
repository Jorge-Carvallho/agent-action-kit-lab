# Pacote `agent_action` (`runtime/agent_action/`)

## Em poucas palavras

É o **kit do agente Google ADK** neste repositório: escolhe o **perfil** (laboratório fictício ou genérico), carrega **prompts** e pode registar as **tools** (OCR, RAG, API) quando activadas. O resto do desafio (MCP, API, CLI) vive noutras pastas na raiz; este código **orquestra o ADK** nesse contexto.

Para levar esta pasta a **outro projeto**, ver **`HANDOFF.md`**.

## Comandos

Na **raiz** do repositório:

```bash
python run_tests.py
python run_smoke.py
```

Só testes de perfil/prompt (exige `PYTHONPATH=runtime`):

```bash
PYTHONPATH=runtime python -m unittest tests.test_matrix_example -v
```

**Precisa de serviços a correr?** **Não** para testes/smoke básicos. **Sim** para conversar com MCP/API via tools.

**Chave da API (obrigatória para inferência Gemini / ADK):** copie **`runtime/agent_action/.env.example`** para **`runtime/agent_action/.env`** e defina **`GOOGLE_API_KEY`** com uma chave válida. (Opcionalmente pode repetir a mesma variável num `.env` na raiz do repo; `run_adk.py` / `smoke_adk.py` carregam os dois.)

---

## Detalhes técnicos

| Peça | Função |
|------|--------|
| `profile_runtime.py` | `AGENT_ACTION`, perfil, `instruction_key` |
| `prompt_loader.py`, `prompts/` | Texto do sistema |
| `lab_runtime.py` | Registo das tools ADK do fluxo laboratorial |
| `agent_factory.py` | `Agent` + `InMemoryRunner` |
| `run_adk.py`, `smoke_adk.py` | Execução / smoke |

PII de referência: `security/` na raiz; `guardrail_example.py` ilustra integração.

**Variável:** `AGENT_ACTION` — `lab` (cenário do desafio) ou `generic`.

Inspiração de padrões de um repo maior está documentada nas tabelas históricas do HANDOFF; este kit é **autocontido** para o laboratório fictício.
