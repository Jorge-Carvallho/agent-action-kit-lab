# Execucao do Docker Compose

## Subir servicos

Na raiz do repositorio:

```bash
docker compose up -d --build
```

Servicos esperados:

- API: porta 8000
- MCP OCR: porta 3100
- MCP RAG: porta 3200

## Estado e logs

```bash
docker compose ps
docker compose logs api --tail 80
docker compose logs mcp-ocr --tail 80
docker compose logs mcp-rag --tail 80
```

Acompanhar em tempo real:

```bash
docker compose logs -f api
```

## Health checks

```bash
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:3100/health
curl -s http://127.0.0.1:3200/health
```

## URL util

- Swagger API: `http://127.0.0.1:8000/docs`

## Parar stack

```bash
docker compose down
```

## Observacao de ambiente

As portas 8000, 3100 e 3200 precisam estar livres no host.
