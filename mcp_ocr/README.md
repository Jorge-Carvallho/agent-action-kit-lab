# MCP OCR (`mcp_ocr/`)

## Em poucas palavras

Este pacote é o **servidor MCP** (com **SSE**) que recebe uma **imagem** em Base64 e devolve **nomes de exames** extraídos. É uma peça do desafio: o agente e a CLI falam com ele pela rede, em vez de fazer OCR “embutido” só no notebook.

Dados sempre tratados como **fictícios**.

## Comandos

Na **raiz** do repositório:

```bash
pip install -r mcp_ocr/requirements.txt
python -m mcp_ocr
```

Testes do motor (sem subir o servidor SSE):

```bash
python -m unittest tests.test_mcp_ocr_engine -v
```

**Precisa de serviços a correr?** Para **usar** o OCR na pipeline completa, este processo (ou o contentor Docker equivalente) tem de estar **ligado** na porta configurada (**3100** por omissão). Os testes unitários do motor **não** precisam do servidor.

---

## Detalhes técnicos

| Variável | Descrição | Omissão |
|----------|-----------|---------|
| `MCP_OCR_HOST` | Bind | `0.0.0.0` |
| `MCP_OCR_PORT` | Porta HTTP | `3100` |
| `OCR_DEMO_EXAMS_JSON` | Lista JSON quando não há OCR real | lista demo pré-definida |

### Endpoints

| Método | Caminho | Descrição |
|--------|---------|-----------|
| GET | `/` | JSON de descoberta |
| GET | `/sse` | Stream SSE (MCP) |
| POST | `/messages/` | Mensagens MCP |
| GET | `/health` | Health check |

URL típica: `http://localhost:3100/sse` (como em `agent_spec.json`).

### Ferramenta MCP: `extract_exam_names_from_image`

Entrada: `image_base64`, `mime_type` opcional. Saída: `exam_names`, `engine` (`tesseract` ou `demo`), `raw_text_preview` já passado por **`security.mask_pii`**.

**OCR real vs demo:** com Pillow + pytesseract + Tesseract no sistema, tenta ler a imagem; senão, modo **demo** (lista configurável).
