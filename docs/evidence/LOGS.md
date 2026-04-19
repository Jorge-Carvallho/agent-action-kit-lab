# Logs principais

Este arquivo resume os logs/saidas mais importantes para avaliacao rapida.

## 1) Estado da stack

```bash
docker compose ps
```

Esperado: `api`, `mcp-ocr`, `mcp-rag` ativos.

## 2) Health dos servicos

```bash
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:3100/health
curl -s http://127.0.0.1:3200/health
```

## 3) CLI (dry-run)

```bash
python run_lab_cli.py examples/sample_prescription.png --dry-run
```

## 4) Testes

```bash
python run_tests.py
```

## 5) Referencia de saidas

Para trechos de saida prontos e formato esperado, ver:

- `docs/evidence/SAMPLE_OUTPUTS.txt`
