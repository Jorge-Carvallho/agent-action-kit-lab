# Evidências (`docs/evidence/`)

## Em poucas palavras

Isto é a pasta de **“como provar que funciona”**: comandos para repetir health checks, CLI e exemplos de saída de terminal (**sem dados reais**). O ficheiro **`SAMPLE_OUTPUTS.txt`** mostra o formato típico do que vais ver.

## Comandos

Ver secções abaixo: script `scripts/e2e_demo.sh`, `curl`, CLI, transpilador. Não há um único comando “oficial” — segue o roteiro que preferires.

**Precisa de serviços a correr?** **Sim** para o script que faz `curl` aos três serviços: tens de ter **`docker compose up`** (API + MCPs). Sem Docker, podes ainda correr **`python -m unittest tests.test_e2e_offline_full -v`** no host para um fluxo completo em memória.

---

## Detalhes — roteiro reproduzível

Esta pasta documenta os mesmos passos e obter saídas equivalentes. Não armazenamos credenciais nem dados clínicos reais.

### Pré-requisito

- `docker compose up -d --build` na raiz do repositório (ver `docker/README.md`).

### Script automático

Requer dependências Python do **`requirements.txt`** na raiz (recomenda-se `.venv`; o script usa `.venv/bin/python` automaticamente se existir):

```bash
bash scripts/e2e_demo.sh
```

Executa `curl` nos três `/health` e um `run_lab_cli.py --dry-run` sobre `examples/sample_prescription.png`.

Sem Docker, o mesmo fluxo (OCR + RAG locais + API em memória) está coberto por teste automatizado:

```bash
python -m unittest tests.test_e2e_offline_full -v
```

Com interpretador explícito: `PYTHON=python3 bash scripts/e2e_demo.sh` (após `pip install -r requirements.txt` nesse Python).

### Passos manuais (equivalentes)

#### 1. Estado dos contentores

```bash
docker compose ps
```

#### 2. Health endpoints (JSON)

```bash
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:3100/health
curl -s http://127.0.0.1:3200/health
```

#### 3. Swagger

Abrir no navegador: `http://127.0.0.1:8000/docs`

#### 4. CLI com MCP (sem persistir agendamento)

```bash
python run_lab_cli.py examples/sample_prescription.png --dry-run
```

A saída deve listar **Backend: MCP SSE**, nomes candidatos do OCR, matches RAG e indicar que o agendamento não foi enviado.

#### 5. Transpilador

```bash
python transpiler/validate_spec.py examples/agent_spec.json
python examples/generated_agent.py
```

### Exemplo de formato de saída (ilustrativo)

Forma típica do `GET /health` da API (valores concretos podem variar com versões):

```json
{"status":"ok","service":"lab-scheduling-api"}
```

Para gravar uma cópia local de evidência (opcional):

```bash
curl -s http://127.0.0.1:8000/health > /tmp/evidence-api-health.json
```

Não versionar ficheiros com segredos ou dados reais.

---

## AI-016 — checklist (onde está documentado)

| Item | Onde |
|------|------|
| Visão geral da solução | `docs/01-visao-geral.md` |
| Arquitetura | `docs/02-arquitetura.md` |
| Docker Compose | `docs/03-execucao-docker-compose.md` e `docker/README.md` |
| Transpilador | `docs/04-uso-transpilador.md` e `examples/AGENT_SPEC.md` |
| CLI | `docs/05-uso-cli.md` e `cli/README.md` |
| Testes | `tests/README.md` e `docs/07-revisao-final-e-checklist.md` |
| Uso de IA e referências | `README.md` — «Transparência e uso de IA» |
| Prints / logs exemplo | `docs/evidence/SAMPLE_OUTPUTS.txt`, `docs/evidence/LOGS.md`, `docs/evidence/PRINTS.md` |
| Cards do desafio (AI-001 … AI-016) | `docs/REFERENCIA_CARDS_DESAFIO.md` |

**Parte 1 (fechada):** visão geral, fluxo em texto no README, secção Docker Compose alargada.

**Parte 2 (fechada):** transpilador e CLI detalhados no README; transparência IA reestruturada.

**Parte 3 (fechada):** `SAMPLE_OUTPUTS.txt` actualizado com saídas reproduzíveis (validador, CLI offline dry-run, resumo de testes) e nota sobre `curl` quando a stack não está no ar.
