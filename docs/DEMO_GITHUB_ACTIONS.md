# Demo no GitHub Actions (passo a passo para avaliação)

Guia curto (raiz do repositório): [`DEMO.md`](../DEMO.md)

Este repositório tem **duas demos** no GitHub Actions, com objetivos diferentes:

- **Demo “completa” (com POST na API)**: roda **somente quando alguém clica** em **Run workflow** (não dispara sozinha em push).
- **Demo “segura” (sem agendar)**: roda automaticamente em **push na branch `main`** (e também pode ser disparada manualmente via **Run workflow**, se você quiser repetir a evidência).

> Observação: workflows novos costumam aparecer na UI do GitHub depois que o arquivo existe na branch default (`main`). Por isso o workflow “POST real” fica em `demo-full.yml` na `main`, mesmo que você desenvolva em outra branch.

---

## 1) O que você vai ver como “prova”

Em qualquer execução bem-sucedida, a evidência fica em 3 lugares (do mais simples ao mais “anexável”):

1. **Status verde** no run (prova objetiva de que passou).
2. **Logs do job** (detalhe técnico completo).
3. **Artifacts** (arquivos para baixar e anexar em relatório/e-mail).

Além disso, estes workflows também escrevem um **Job Summary** (relatório em Markdown na página do run), para quem não quiser baixar ZIP.

O **Job Summary** aparece no topo da página do run (aba **Summary**), e costuma incluir:

- metadados do run (workflow, `run_id`, commit, ref)
- JSON dos `/health` (API + MCP OCR + MCP RAG)
- um trecho inicial da saída da CLI (para leitura rápida)

### `push` vs `Run workflow` vs `Re-run`

- **`push`**: o GitHub mostra **“Triggered via push”** e um badge da branch (ex.: **`main`**). Não aparece seletor “Use workflow from”, porque a branch já está definida pelo commit.
- **`Run workflow`**: aparece o seletor de branch, porque o disparo é manual.
- **`Re-run`**: repete o mesmo contexto (branch/commit) do run anterior — por isso também **não** mostra seletor.

---

## 2) Demo completa (com POST) — `Demo full (tests + docker + POST)`

### O que ela faz

É igual à demo segura, mas a CLI roda **sem `--dry-run`**, ou seja:

- tenta executar o fluxo até o **POST** na API de agendamento do ambiente do runner.

### Onde clicar no GitHub (manual)

1. Abra o repositório no GitHub
2. Vá em **Actions**
3. No menu esquerdo, clique em **`Demo full (tests + docker + POST)`**
4. Clique em **Run workflow** (canto superior direito)
5. Em **Use workflow from**, escolha a branch (normalmente **`main`**)
6. Clique no botão verde **Run workflow**
7. Abra o run que aparecer e entre no job **`demo-full`**
8. Expanda o step **`Run CLI demo (POST real)`**

### Artifact (opcional)

Na página **Summary** do run:

- Baixe **`demo-full-report`**
- Dentro, procure:
  - `demo-full-output.txt` (saída completa da CLI, incluindo agendamento quando aplicável)
  - `health-*.json` e `docker-compose.ps.txt` (mesma ideia da demo segura)

---

## 3) Demo segura (sem agendar) — `Demo (tests + docker + cli)`

### O que ela faz

Roda, na ordem:

1. Instala dependências Python (`requirements.txt`)
2. Executa testes (`python run_tests.py`)
3. Sobe a stack com Docker Compose (`api`, `mcp-ocr`, `mcp-rag`)
4. Espera os `/health` ficarem disponíveis
5. Executa a CLI em **`--dry-run`** (não envia agendamento)
6. Publica artifact `demo-report` (pasta com evidências)
7. Encerra a stack (`docker compose down`)

### Onde clicar no GitHub

1. Abra o repositório no GitHub
2. Vá em **Actions**
3. No menu esquerdo, clique em **`Demo (tests + docker + cli)`**
4. Clique na execução mais recente com **✅ Success**
5. Clique no job **`demo`**
6. Expanda o step **`Run CLI demo (dry-run)`** para ver a saída completa

### Artifact (opcional)

Na página **Summary** do run:

- Baixe **`demo-report`** (ZIP)
- Dentro, procure:
  - `demo-output.txt` (saída completa da CLI)
  - `health-api.json`, `health-mcp-ocr.json`, `health-mcp-rag.json` (respostas dos `/health`)
  - `docker-compose.ps.txt` (estado/containers após o `up`)
