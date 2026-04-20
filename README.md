
---

# Agent Action Kit — entrega técnica (laboratório fictício)

Projeto do desafio **Sênior de Inteligência Artificial**.

Este repositório demonstra um fluxo completo de automação com agentes de IA, onde uma imagem de pedido médico é processada ponta a ponta (OCR → normalização → RAG → API) até gerar um agendamento estruturado.

Na prática, o fluxo:

* lê uma **imagem de pedido médico**,
* extrai os **nomes dos exames**,
* resolve os **códigos corretos** em um catálogo fictício,
* e envia um **pedido de agendamento** para uma API.

> **Importante:** todos os dados, imagens e exemplos usados aqui são **100% fictícios**.

## Base do desafio (cards)

Para quem avalia a entrega: o planeamento e o mapeamento **card a card** (**AI-001** … **AI-016**) estão em **[`docs/REFERENCIA_CARDS_DESAFIO.md`](docs/REFERENCIA_CARDS_DESAFIO.md)** (índice no início do ficheiro).

## Documentação complementar

* [`DEMO.md`](DEMO.md) — **demo reproduzível no GitHub Actions** (passo a passo curto para avaliação)
* [`docs/README.md`](docs/README.md) — índice da documentação por tópicos (arquitetura, Docker, transpilador, CLI, IA e revisão final)
* [`docs/VALIDACAO_CLONE.md`](docs/VALIDACAO_CLONE.md) — validação em clone limpo (comando a comando)
* `examples/AGENT_SPEC.md`
* `runtime/agent_action/README.md`
* `runtime/agent_action/HANDOFF.md`
* `docs/evidence/README.md`
* [`docs/REFERENCIA_CARDS_DESAFIO.md`](docs/REFERENCIA_CARDS_DESAFIO.md) — cards **AI-001** … **AI-016** (ver também secção **Base do desafio** no topo deste README)

---

## O que este projeto faz

A **entrada principal** é um **arquivo de imagem** (foto ou digitalização), por exemplo em **PNG** ou **JPEG**: não é texto copiável, mas sim uma imagem contendo texto que precisa ser interpretado via OCR.

Neste repositório há um exemplo pronto (dados fictícios):

```text
examples/sample_prescription.png
```

Pode abrir esse arquivo no visualizador de imagens do seu sistema para ver como é um pedido de exames em formato de imagem.

**Termos rápidos usados no fluxo:**

* **OCR** (*optical character recognition*): reconhecimento de texto **a partir da imagem** (converter pixels em caracteres).
* **PII** (*personally identifiable information*): dados que identificam ou podem identificar uma pessoa (nome, documento, etc.); aqui são **mascarados ou tratados** antes de seguir para IA ou armazenamento.
* **RAG** (*retrieval-augmented generation*): em vez de “adivinhar” códigos só com o modelo, o sistema **consulta uma base/catálogo** (aqui mock) para recuperar o que bate com o texto extraído.

A partir da imagem, o sistema executa este fluxo:

1. faz **OCR** para identificar os exames na imagem,
2. trata **PII / dados sensíveis** antes de IA ou persistência,
3. consulta um serviço de **RAG** para encontrar os nomes e códigos oficiais no catálogo,
4. envia o pedido para a **API de agendamento**,
5. mostra o resultado no terminal ou no agente ADK.

## Diferenciais da solução

* Transpilador que converte JSON em agentes usando Google ADK.
* Integração com serviços via MCP (SSE).
* Tratamento de PII antes de IA ou persistência.
* Arquitetura desacoplada (OCR, RAG e API independentes).
* Execução completa via CLI ou agente.

---

## Como rodar

Cada pasta do projeto tem um `README.md` próprio com mais detalhes.
Este README principal mostra apenas o necessário para subir e testar sem dúvidas.

## Execução rápida para avaliação

Se você quer validar o projeto em menos de 1 minuto:

## TL;DR (execução rápida)

```bash
docker compose up -d --build
python run_tests.py
python run_lab_cli.py examples/sample_prescription.png --dry-run
```

Se esses comandos rodarem sem erro, o projeto está funcional e o fluxo OCR → RAG → API estará validado.

Roteiro **passo a passo** (clone limpo, com o que esperar em cada comando): [`docs/VALIDACAO_CLONE.md`](docs/VALIDACAO_CLONE.md).

### Requisitos

Você precisa ter instalado:

* **Python 3.12+**
* **Docker 24+**
* **Docker Compose v2**

---

## Passo 1 — preparar o ambiente Python

Na raiz do projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Linux / macOS
# .venv\Scripts\activate           # Windows

python -m pip install --upgrade pip   # opcional: atualiza só o pip *dentro* deste venv
pip install -r requirements.txt
```

A linha `python -m pip install --upgrade pip` é **opcional**: serve para atualizar o programa `pip` dentro do ambiente virtual (é o mesmo que `pip install -U pip`: a flag `-U` significa `--upgrade`). Se preferir, **pode apagar essa linha** e rodar só `pip install -r requirements.txt`; na maior parte dos casos funciona do mesmo jeito.

## Configuração opcional (Google ADK)

Para executar o agente com inferência real via Gemini, defina uma `GOOGLE_API_KEY` válida:

```bash
cp runtime/agent_action/.env.example runtime/agent_action/.env
```

Depois, edite `runtime/agent_action/.env` e substitua `cole_sua_chave_aqui` pela sua chave.

Se não configurar a chave, o restante do fluxo (CLI, OCR, RAG, API e testes) continua funcionando normalmente.

---

## Passo 2 — subir os serviços

Na raiz do projeto:

```bash
docker compose up -d --build
```

Isso sobe os serviços principais:

* **API** na porta `8000`
* **MCP OCR** na porta `3100`
* **MCP RAG** na porta `3200`

### Depois do `up`

`docker compose up -d --build` arranca a stack e **volta ao prompt**; não abre browser. Para ver o arranque no primeiro plano (logs misturados): `docker compose up --build` **sem** `-d` — **Ctrl+C** para; depois `docker compose down` se quiser remover os contentores.

**Estado**

```bash
docker compose ps
```

Esperado: `api`, `mcp-ocr`, `mcp-rag` em execução; após o healthcheck, estado de saúde **healthy**.

**Logs (um comando por serviço)**

```bash
docker compose logs api --tail 60
docker compose logs mcp-ocr --tail 60
docker compose logs mcp-rag --tail 60
```

Acompanhamento contínuo de um serviço: `docker compose logs -f api` (sair: **Ctrl+C**).

**URLs no host** (o que pode abrir no navegador ou testar com `curl`)

| Serviço | URL |
|--------|-----|
| API | http://127.0.0.1:8000/health · http://127.0.0.1:8000/docs |
| MCP OCR | http://127.0.0.1:3100/health |
| MCP RAG | http://127.0.0.1:3200/health |

```bash
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:3100/health
curl -s http://127.0.0.1:3200/health
```

**Fluxo completo no terminal** (na raiz, venv ativo, stack no ar)

```bash
python run_lab_cli.py examples/sample_prescription.png --dry-run
```

Relatório OCR → RAG no stdout; sem `--dry-run`, também envia para a API.

**Parar**

```bash
docker compose down
```

### Portas no host

Para subir esta stack, as portas **8000** (API), **3100** (MCP OCR) e **3200** (MCP RAG) precisam estar **livres** no seu PC. Se outra aplicação ou container já estiver a usar alguma delas, pare esse serviço ou ajuste o mapeamento no `docker-compose.yml` / variáveis de ambiente do projeto.

### OCR “demo” vs Tesseract real

A **imagem Docker do MCP OCR** já instala **Tesseract** (`docker/Dockerfile.mcp-ocr`). Se você testar OCR **no host** sem Docker (ou com `--offline`) e aparecer aviso de Tesseract/Pillow indisponível, o motor cai no modo **demo determinístico** — útil para testes, mas não é OCR real. Para OCR real no host, instale Tesseract (e dependências) no sistema ou use sempre o serviço no container.

---

## Passo 3 — validar rapidamente

Depois de subir os containers, estes são os 3 comandos principais para avaliação rápida:

```bash
python run_tests.py
python run_lab_cli.py examples/sample_prescription.png --dry-run
python run_lab_cli.py examples/sample_prescription.png
```

### O que cada um faz

* `python run_tests.py`
  executa a suíte principal de testes.

* `python run_lab_cli.py examples/sample_prescription.png --dry-run`
  roda o fluxo completo **sem enviar para a API**.

* `python run_lab_cli.py examples/sample_prescription.png`
  roda o fluxo completo **com envio para a API**.

### Saída esperada

A CLI deve mostrar:

* exames extraídos pelo OCR;
* códigos resolvidos pelo RAG;
* (opcional) resposta da API de agendamento.

Exemplos completos estão em:

```text
docs/evidence/SAMPLE_OUTPUTS.txt
```

---

## Estrutura principal do projeto

### `transpiler/`

Valida o arquivo `agent_spec.json` e gera o agente em Python usando **Google ADK**.

### `mcp_ocr/`

Serviço MCP via SSE responsável por ler a imagem e extrair os nomes de exames.

### `mcp_rag/`

Serviço MCP via SSE responsável por converter nomes extraídos em códigos oficiais do catálogo fictício.

### `api/`

API FastAPI que recebe o pedido de agendamento.

### `cli/` + `run_lab_cli.py`

Fluxo ponta a ponta no terminal.

### `security/`

Regras de tratamento de dados sensíveis / PII.

### `examples/`

Arquivos de exemplo, incluindo:

* `agent_spec.json`
* `generated_agent.py`
* `sample_prescription.png`

### `docs/evidence/`

Evidências, roteiro alternativo e saídas de exemplo.

---

## Fluxo resumido

```text
Imagem -> OCR -> tratamento de PII -> RAG -> API de agendamento -> saída no terminal
```

---

## Modo principal de uso

O modo padrão usa:

* **MCP OCR**
* **MCP RAG**
* **API FastAPI**

Ou seja, para o fluxo completo, o esperado é ter os containers rodando via Docker Compose.

Exemplo:

```bash
python run_lab_cli.py examples/sample_prescription.png --dry-run
```

---

## Modo offline

Também existe um modo offline, sem depender dos servidores MCP.

Exemplo:

```bash
python run_lab_cli.py examples/sample_prescription.png --offline --dry-run
```

Nesse modo:

* OCR e RAG rodam no mesmo processo,
* a API só é chamada se você **não** usar `--dry-run`.

---

## Onde olhar evidências

Se quiser um roteiro alternativo de validação ou exemplos prontos de saída:

```text
docs/evidence/
```

Arquivos úteis:

* `docs/evidence/README.md`
* `docs/evidence/SAMPLE_OUTPUTS.txt`

---

## Problemas comuns

### 1. `ModuleNotFoundError`

Normalmente significa que o ambiente virtual não foi ativado ou que faltou executar:

```bash
pip install -r requirements.txt
```

### 2. A CLI não consegue falar com OCR ou RAG

Verifique se o Docker Compose está no ar:

```bash
docker compose ps
```

### 3. Erro ao chamar a API

Verifique se a API está respondendo:

```bash
curl -s http://127.0.0.1:8000/health
```

### 4. Nenhum exame encontrado no RAG

Pode acontecer se os nomes extraídos pelo OCR não baterem com o catálogo mock.
Nesse caso, o fluxo pode terminar sem POST na API, o que é um comportamento esperado.

---

# Detalhes técnicos

Esta seção fica por último de propósito, para não atrapalhar a leitura inicial.

## Componentes da solução

* **Transpilador**: valida `agent_spec.json` e gera `examples/generated_agent.py`
* **Google ADK**: runtime do agente
* **MCP (SSE)**: integração com OCR e RAG
* **FastAPI**: API de agendamento
* **PII**: tratamento de dados sensíveis antes de IA ou persistência
* **CLI**: execução ponta a ponta
* **Docker Compose**: sobe API + MCPs

---

## Portas padrão

* **8000** → API
* **3100** → MCP OCR
* **3200** → MCP RAG

---

## Transpilador

Contrato e exemplo:

* `examples/AGENT_SPEC.md`
* `examples/agent_spec.json`

Validar o spec:

```bash
python transpiler/validate_spec.py examples/agent_spec.json
```

Gerar o agente:

```bash
python transpiler/generate_agent.py
```

Saída padrão:

```bash
examples/generated_agent.py
```

> Esse arquivo deve ser regenerado a partir do JSON e não editado manualmente.

---

## Testes

Executar suíte principal:

```bash
python run_tests.py
```

Ou:

```bash
make test
```

Executar descoberta completa:

```bash
python -m unittest discover -s tests -p 'test*.py' -v
```

Executar apenas o E2E offline:

```bash
python -m unittest tests.test_e2e_offline_full -v
```

---

## Variáveis importantes

Valores padrão usados no fluxo:

* `MCP_OCR_SSE_URL=http://localhost:3100/sse`
* `MCP_RAG_SSE_URL=http://localhost:3200/sse`
* `SCHEDULING_API_BASE=http://localhost:8000`
* `SCHEDULING_APPOINTMENTS_PATH=/api/v1/appointments`

---

## Transparência sobre uso de IA

A IA foi usada como apoio para:

* rascunhos iniciais,
* desenvolvimento,
* refatoração,
* padronização,
* apoio em documentação.

As decisões de arquitetura, revisão, validação final e critérios da entrega permaneceram sob controle humano.

Todo o conteúdo clínico e laboratorial usado aqui é **fictício**.

---

