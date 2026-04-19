# Docker (`docker/` + `docker-compose.yml`)

## Em poucas palavras

Esta pasta guarda os **Dockerfiles** e um único **`docker/requirements.txt`** com as dependências pip partilhadas pelas três imagens de serviço (API + MCP OCR + MCP RAG). O **`docker-compose.yml`** está na **raiz**. O compose sobe a **API** e os dois **MCP**. É a forma mais simples para **reproduzir o ambiente** sem instalar tudo à mão.

## Comandos

Na **raiz** do repositório:

```bash
docker compose up -d --build
docker compose ps
docker compose down
```

Validar o JSON do agente dentro de um contentor (opcional):

```bash
docker compose --profile tools run --rm validate-spec
```

**Precisa de algo a correr antes?** **Só o Docker** instalado na máquina. Este compose **é** o que “põe a aplicação a correr” (API + MCPs). A CLI e os testes no **host** são um passo à parte (Python + venv).

---

## Detalhes técnicos (AI-014)

- **Dependências das imagens:** `docker/requirements.txt` — **não** é o mesmo que `requirements.txt` da raiz (esse cobre desenvolvimento, testes e ADK no host). As três imagens instalam a mesma lista (mais simples de manter; imagens um pouco maiores).
- Docker Engine **24+** e Compose **v2** (`docker compose`).
- Portas no host (como em `examples/agent_spec.json`): **8000** API, **3100** MCP OCR, **3200** MCP RAG.
- **Portas:** no host, por omissão **8000**, **3100** e **3200** têm de estar livres (ou altere o compose / env conforme o seu ambiente).
- Imagens com utilizador não-root e **HEALTHCHECK** nos serviços HTTP.

Ver estado:

```bash
docker compose ps
docker inspect --format='{{.State.Health.Status}}' lab-api
```

### Rede interna (contentores a falar entre si)

| Variável | Valor interno |
|----------|----------------|
| `MCP_OCR_SSE_URL` | `http://mcp-ocr:3100/sse` |
| `MCP_RAG_SSE_URL` | `http://mcp-rag:3200/sse` |
| `SCHEDULING_API_BASE` | `http://api:8000` |

No **teu PC** (CLI, browser), usa `http://localhost:PORT` (predefinição em `tools/config.py`). A tabela acima só interessa se adicionares **outro contentor** na mesma rede `lab` e precisares de URLs internas.

### Notas de produção (futuro)

- Fixar digests `FROM python@sha256:...` em CI.
- Scan de imagem (Trivy) e `read_only: true` + `tmpfs` para `/tmp` quando fizer sentido.
