# CLI (`cli/`)

## Em poucas palavras

Aqui está o código da **linha de comandos** do desafio: lê uma **imagem** de pedido médico (fictícia), passa por OCR e RAG e, se quiseres, **envia o agendamento** para a API. O comando que corres na raiz é `run_lab_cli.py` (não `cli/` isolado).

Serve para **demonstrar o fluxo** sem abrir o IDE.

## Comandos

Sempre na **raiz** do repositório, com `pip install -r requirements.txt` feito:

```bash
# Exemplo com imagem versionada; sem gravar agendamento
python run_lab_cli.py examples/sample_prescription.png --dry-run

# Até à API (precisa da API acessível)
python run_lab_cli.py examples/sample_prescription.png
```

Sem Docker / sem MCP — motores locais:

```bash
python run_lab_cli.py examples/sample_prescription.png --offline --dry-run
```

Testes do fluxo CLI:

```bash
python -m unittest tests.test_cli_flow -v
```

**Precisa de serviços a correr?**

- **Modo normal (predefinição):** **Sim** — MCP OCR (SSE), MCP RAG (SSE) e, para agendar, a **API** (ex.: `docker compose up` na raiz).
- **Com `--dry-run`:** não chama a API; mesmo assim, em modo normal precisas dos **dois MCP** no ar.
- **Com `--offline`:** **Não** precisas dos MCP; a API só é necessária se **não** usares `--dry-run`.

---

## Detalhes técnicos

Fluxo predefinido: **OCR (MCP)** → prévia com PII → **RAG (MCP)** → **POST** na FastAPI (`tools/config.py` — URLs por omissão `localhost:3100`, `3200`, `8000`).

| Argumento | Efeito |
|-----------|--------|
| `--dry-run` | Não chama `POST` de agendamento; executa OCR + RAG. |
| `--offline` | Não usa MCP SSE; motores locais. |
| `--patient-ref` | Referência fictícia (ou env `CLI_PATIENT_REF`). |

Env: `LAB_CLI_OFFLINE=1` equivale a `--offline`. Ver também o README na **raiz** do projeto (secção CLI).
