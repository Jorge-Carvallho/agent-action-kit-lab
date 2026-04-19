# Handoff — pasta `agent_action` para outro projeto

## O que já funciona (ADK)

- O kit instancia **`google.adk.agents.Agent`** + **`InMemoryRunner`** com `gemini-2.5-flash`, igual ao padrão do repo pai (`app/agent.py`).
- **Instanciar** o agente não exige rede; **gerar texto** exige credencial Google (veja abaixo).
- Valide rápido na raiz deste repo (com **venv** que tenha `google-adk` instalado): `python run_smoke.py` (força `AGENT_ACTION=lab`; carrega `.env` da raiz se existir).

## Padrões reutilizados

| Ideia | Onde está no kit |
|-------|------------------|
| `AGENT_ACTION` + perfil + runtime | `profile_runtime.py` |
| Prompt laboratorial | `prompts/laboratory.py` (e `lab_example.py` como alias `instruction_key`) |
| Tools `lab` no ADK | `lab_runtime.py` |
| Prompt por ação | `prompt_loader.py`, `prompts/` |
| Fábrica Agent + Runner | `agent_factory.py` |
| Guardrail / stub PII | `guardrail_example.py` |
| Testes de matriz de contexto | `tests/test_matrix_example.py` (na raiz do repo) |

## Chave API (teste) — não está no Git

- **Não** há chave real nesta pasta (por segurança).
- Coloque **`GOOGLE_API_KEY`** no `.env` da **raiz** do clone (não commite).

Variáveis mínimas para Gemini API direta:

```bash
GOOGLE_API_KEY=sua_chave_aqui
GOOGLE_GENAI_USE_VERTEXAI=False
```

## Relação com o resto do kit (raiz do repositório)

O desafio laboratorial fictício está fechado no repo: **CLI** (`run_lab_cli.py`), **Docker Compose** (API + MCP OCR + MCP RAG), **transpilador** com `instruction` / `instruction_key` (ex.: `lab_example` → `prompts/laboratory.py`), e **testes** (`run_tests.py`, incluindo E2E offline). Ver **`README.md`** na raiz e **`docs/evidence/README.md`**.

## Como copiar esta pasta para outro projeto

1. Copie a pasta inteira `runtime/agent_action/` (ou o pacote `agent_action` para a estrutura do projeto novo).
2. Instale deps: `pip install google-adk` (alinhar versão; ver `requirements-kit.txt`).
3. `PYTHONPATH` deve incluir o diretório **pai** do pacote `agent_action` (neste repo: **`runtime`**) ou instale como pacote.
4. Crie `.env` com `GOOGLE_API_KEY` (ver `.env.example` na raiz, se existir).
5. Rode testes: `python run_tests.py` (a partir da raiz do clone).

## Independência

Este kit **não importa** aplicações externas de CRM ou vendas; o perfil laboratorial é autocontido em `runtime/agent_action/`.
