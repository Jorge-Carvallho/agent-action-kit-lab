# Validação em clone limpo

Roteiro **copiar/colar** para quem acabou de clonar o repositório. Cada passo indica **o que rodar** e **o que esperar**.

**Pré-requisitos:** Git, Python 3.12+, Docker 24+, Docker Compose v2.

---

## 1) Clonar e entrar na pasta

```bash
git clone <URL_DO_REPO> agent-action-kit-lab
cd agent-action-kit-lab
```

Troque `<URL_DO_REPO>` pelo SSH ou HTTPS do seu fork/repositório. Se a branch principal for outra (ex.: `developer`), faça `git checkout <branch>`.

**Esperado:** pasta do projeto com `README.md`, `docker-compose.yml`, `run_lab_cli.py`, etc.

---

## 2) Ambiente Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Esperado:** instalação termina com `Successfully installed ...` sem erro.

---

## 3) (Opcional) Chave Gemini / ADK

Só necessário para **inferência real** com o modelo (`--chat`, etc.). O fluxo **CLI + Docker + testes** funciona sem isso na maior parte dos cenários.

```bash
cp runtime/agent_action/.env.example runtime/agent_action/.env
```

Edite `runtime/agent_action/.env` e defina `GOOGLE_API_KEY` com uma chave válida.

---

## 4) Subir a stack Docker

Na raiz do clone:

```bash
docker compose up -d --build
docker compose ps
```

**Esperado:** serviços `api`, `mcp-ocr`, `mcp-rag` em execução; após o healthcheck, estado **healthy** (pode levar alguns segundos).

---

## 5) Health HTTP

```bash
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:3100/health
curl -s http://127.0.0.1:3200/health
```

**Esperado:** três respostas JSON com `"status":"ok"` (e campos como `service`, `transport` nos MCPs).

> Dica: rode um `curl` por linha se preferir ver cada JSON separado.

---

## 6) Testes automatizados

```bash
python run_tests.py
```

**Esperado:** linha final `Ran N tests in ...` e **`OK`** (sem falhas). O número `N` pode crescer com o tempo; o importante é zero erros.

---

## 7) CLI — sem enviar agendamento

```bash
python run_lab_cli.py examples/sample_prescription.png --dry-run
```

**Esperado:** relatório no terminal com:

- **Backend:** MCP SSE (OCR + RAG) (com stack no ar)
- secção **Exames (candidatos do OCR)**
- secção **RAG** com matches (ex.: códigos `LAB-F...`) ou `sem match` para ruído
- **Agendamento:** indicação de que o pedido **não foi enviado**

---

## 8) CLI — fluxo completo (com API)

```bash
python run_lab_cli.py examples/sample_prescription.png
```

**Esperado:** mesmo relatório até o RAG; em **Agendamento**, algo como `Estado: confirmed`, um `ID` (UUID) e contagem de exames (ex.: 3).

---

## 9) (Opcional) Smoke ADK + transpilador

```bash
python run_smoke.py
python transpiler/validate_spec.py examples/agent_spec.json
python transpiler/generate_agent.py
python examples/generated_agent.py
```

**Esperado:** mensagens `OK` / smoke do agente; validação do JSON com sucesso; geração de `examples/generated_agent.py`. Sem `GOOGLE_API_KEY`, o smoke pode mostrar que a chave não está definida — normal para validação sem inferência.

---

## 10) (Opcional) Script E2E rápido

```bash
bash scripts/e2e_demo.sh
```

**Esperado:** health nos três serviços e execução da CLI em `--dry-run` (requer stack Docker no ar e dependências do passo 2).

---

## 11) Parar Docker

```bash
docker compose down
```

---

## Problemas comuns

| Sintoma | O que verificar |
|--------|------------------|
| `Connection refused` nos `curl` | Stack não está no ar ou portas 8000/3100/3200 ocupadas |
| CLI não fala com MCP | `docker compose ps` e logs: `docker compose logs mcp-ocr --tail 80` |
| Testes falham | venv ativo, `pip install -r requirements.txt` na raiz do clone |

Mais detalhes: `README.md` (raiz), `docs/evidence/README.md`, `docs/evidence/SAMPLE_OUTPUTS.txt`.
