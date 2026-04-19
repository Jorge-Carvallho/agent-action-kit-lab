# Tools (`tools/`)

## Em poucas palavras

Aqui estão as **funções que o agente Google ADK chama**: ligar ao **MCP de OCR**, ao **MCP de RAG** e fazer o **POST** na API de agendamento. A CLI e o código gerado pelo transpilador usam os mesmos módulos.

Não é um servidor que “subes” sozinho — é **código de integração** importado por outros pontos do projeto.

## Comandos

Não há comando para “arrancar” esta pasta. Para testar as integrações:

```bash
python -m unittest tests.test_tools_unit -v
```

**Precisa de serviços a correr?** **Só quando** correres o agente ou testes que chamam MCP/API de verdade. O teste unitário acima **moca** a rede onde for preciso.

---

## Detalhes técnicos (AI-011)

Não existe `tools/__init__.py`: **namespace package** (PEP 420). Importas só o que precisas (`tools.ocr_tool`, etc.).

| Módulo | Função |
|--------|--------|
| **`ocr_tool.py`** | `ocr_extract_exams` → MCP `extract_exam_names_from_image` |
| **`rag_tool.py`** | `rag_lookup_exam_codes` → MCP `lookup_exam_codes` |
| **`scheduling_tool.py`** | `submit_appointment_request` + `ExamItemInput` → HTTP |
| **`mcp_bridge.py`** | Sessão MCP SSE por chamada |
| **`config.py`** | URLs e timeouts |

### Padrão ADK

```python
from google.adk.tools.function_tool import FunctionTool
from tools.ocr_tool import ocr_extract_exams
from tools.rag_tool import rag_lookup_exam_codes
from tools.scheduling_tool import submit_appointment_request

tools = [
    FunctionTool(ocr_extract_exams),
    FunctionTool(rag_lookup_exam_codes),
    FunctionTool(submit_appointment_request),
]
```

### Variáveis de ambiente (resumo)

| Variável | Significado | Omissão |
|----------|-------------|---------|
| `MCP_OCR_SSE_URL` | SSE do MCP OCR | `http://localhost:3100/sse` |
| `MCP_RAG_SSE_URL` | SSE do MCP RAG | `http://localhost:3200/sse` |
| `MCP_TOOL_TIMEOUT_SEC` | Timeout MCP | `120` |
| `SCHEDULING_API_BASE` | Base da API | `http://localhost:8000` |
| `LAB_AGENT_TOOLS` | `0` desactiva tools no `run_adk` | `1` |

Alinhar a `examples/agent_spec.json`.
