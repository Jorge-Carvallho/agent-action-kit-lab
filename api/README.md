# API (`api/`)

## Em poucas palavras

Esta pasta é a **API web fictícia de agendamento**: recebe a lista de exames (com código e nome) e devolve uma confirmação com ID. É o “back-end” que o agente e a CLI chamam por HTTP. O contrato está também descrito no **Swagger** (`/docs`).

**Não é o agente de IA** — só guarda o pedido de demonstração; não há base de dados real.

## Comandos

Na **raiz** do repositório, com dependências instaladas:

```bash
pip install -r api/requirements.txt
python -m api
```

Testes só desta API:

```bash
python -m unittest tests.test_api_appointments -v
```

**Precisa de algo a correr antes?** **Não** para arrancar só a API — ela é o serviço. Para o fluxo completo (CLI com MCP), os outros serviços (Docker) são opcionais e tratados à parte.

---

## Detalhes técnicos (AI-010)

Alinhado a `examples/agent_spec.json` (`scheduling_api`).

Variáveis opcionais:

| Variável | Descrição | Omissão |
|----------|-----------|---------|
| `SCHEDULING_API_HOST` | Bind | `0.0.0.0` |
| `SCHEDULING_API_PORT` | Porta | `8000` |

### Contrato (agente)

| Método | Caminho | Descrição |
|--------|---------|-----------|
| **POST** | `/api/v1/appointments` | Submete pedido de agendamento |
| **GET** | `/health` | Estado do serviço |
| **GET** | `/docs` | **Swagger UI** (OpenAPI) |
| **GET** | `/redoc` | ReDoc |

### Corpo JSON (POST)

```json
{
  "exam_items": [
    { "code": "LAB-F0001", "name": "Hemograma completo" }
  ],
  "patient_reference": "opcional, fictício",
  "notes": "opcional"
}
```

- `exam_items`: **obrigatório**, lista **não vazia**; cada item tem `code` e `name` (como devolvido pelo RAG).
- `patient_reference` e `notes`: opcionais.

### Resposta **201 Created**

```json
{
  "appointment_id": "<uuid>",
  "status": "confirmed",
  "message": "...",
  "received_at": "2026-04-18T12:00:00.000000+00:00",
  "exam_count": 1
}
```

Lista vazia de exames → **422** (validação).
