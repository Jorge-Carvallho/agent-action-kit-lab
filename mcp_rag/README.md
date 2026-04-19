# MCP RAG (`mcp_rag/`)

## Em poucas palavras

Este pacote é o **servidor MCP** (com **SSE**) que recebe **nomes de exames** (por exemplo vindos do OCR) e devolve **código**, nome canónico e descrição usando a base mock em **`data/exams_mock.json`**. É o “RAG” do desafio: recuperação simples sobre catálogo fictício.

## Comandos

Na **raiz** do repositório:

```bash
python -m mcp_rag
```

Testes do algoritmo de matching (sem subir o servidor):

```bash
python -m unittest tests.test_mcp_rag_matcher -v
```

**Precisa de serviços a correr?** O ficheiro **`data/exams_mock.json`** tem de existir no clone (vem no repo). Para **chamar** o RAG pela rede, este serviço (ou o contentor Docker) deve estar **ligado** na porta **3200** por omissão. Os testes do matcher **não** precisam do servidor.

---

## Detalhes técnicos

| Variável | Descrição | Omissão |
|----------|-----------|---------|
| `MCP_RAG_HOST` | Bind HTTP | `0.0.0.0` |
| `MCP_RAG_PORT` | Porta HTTP | `3200` |

### Endpoints

| Método | Caminho | Descrição |
|--------|---------|-----------|
| GET | `/` | Descoberta |
| GET | `/sse` | Stream SSE |
| POST | `/messages/` | Mensagens MCP |
| GET | `/health` | Health (`catalog_id`, `record_count`) |

URL típica: `http://localhost:3200/sse`.

### Ferramenta MCP: `lookup_exam_codes`

Entrada: `exam_names` (lista). Saída: `results[]` com `matched`, `code`, `canonical_name`, `confidence`, etc.

**Matching:** `exam_matcher.py` — normalização, igualdade, substrings em sinónimos (≥4 caracteres), tokens.
