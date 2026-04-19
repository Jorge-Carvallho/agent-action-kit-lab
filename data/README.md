# Dados (`data/`)

## Em poucas palavras

Aqui fica a **lista fictícia de exames laboratoriais** em JSON (mais de cem entradas, com código, nome, descrição curta e sinónimos). O serviço **RAG** usa este ficheiro para transformar nomes vindos do OCR em **códigos** oficiais do catálogo mock.

**Não são dados reais de pacientes** — só cenário de desafio.

## Comandos

Regenerar o JSON a partir do script (se alterares a lista no código):

```bash
python data/build_exams_mock.py
```

Testes do catálogo:

```bash
python -m unittest tests.test_exams_catalog -v
```

**Precisa de serviços a correr?** **Não** para editar o ficheiro ou correr o script. O **MCP RAG** lê este JSON quando **esse** serviço está ligado.

---

## Detalhes técnicos (AI-008)

- **`exams_mock.json`** — catálogo; códigos tipo `LAB-F0001`, …
- **`build_exams_mock.py`** — gera/atualiza o JSON.
- **`load_mock_catalog.py`** — `load_mock_catalog()` / `load_mock_exams()` para o código Python carregar sem duplicar caminhos.

Consumo: **`mcp_rag`** (tool `lookup_exam_codes`) — ver `mcp_rag/README.md`.
