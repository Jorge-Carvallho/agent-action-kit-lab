# Visao geral da solucao

## Objetivo

Demonstrar um fluxo completo de laboratorio ficticio:
imagem de pedido medico -> OCR -> tratamento de PII -> RAG para codigos -> envio para API de agendamento.

## Entrada e saida

- Entrada principal: `examples/sample_prescription.png`
- Saida principal para o usuario: relatorio no terminal via `run_lab_cli.py`
- Saida de API: confirmacao com `appointment_id`, `status` e `exam_count`

## Fluxo resumido

1. OCR extrai candidatos de exames da imagem.
2. Camada de seguranca mascara dados sensiveis (PII).
3. RAG consulta catalogo mock e retorna codigos canonicos.
4. API FastAPI recebe os exames validados e confirma pedido.
5. CLI mostra o resumo fim a fim no console.

## Onde estao os blocos principais

- OCR: `mcp_ocr/`
- PII: `security/`
- RAG: `mcp_rag/` + `data/exams_mock.json`
- API: `api/`
- CLI: `cli/` + `run_lab_cli.py`
- Runtime ADK: `runtime/agent_action/`
- Integracoes (tools): `tools/`

## O que o avaliador consegue validar rapidamente

- Stack em pe com Docker Compose
- Health endpoints respondendo
- CLI rodando pipeline completo
- Testes automatizados passando
