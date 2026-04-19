# Segurança (`security/`)

## Em poucas palavras

Esta pasta trata de **dados pessoais fictícios** que possam aparecer no texto (e-mail, telefone, documentos, nome após rótulos como “Paciente:”). A ideia é **mascarar** esse texto **antes** de ir para o modelo de IA ou para registo, alinhado ao desafio (PII).

O fluxo laboratorial continua a ser **demonstração**; não substitui avaliação jurídica em produção.

## Comandos

Testes da camada PII:

```bash
python -m unittest tests.test_pii -v
```

**Precisa de serviços a correr?** **Não** — é uma biblioteca Python importada pelo OCR, CLI e testes. O servidor **MCP OCR** usa esta lógica quando está ligado.

---

## Detalhes técnicos (AI-007)

### Política (resumo)

1. **Quando mascar:** texto livre de OCR (ou similar) antes de LLM, RAG ou persistência. O `mcp_ocr` aplica mascaramento em **`raw_text_preview`**.

2. **Detetado:** e-mail, CNPJ, CPF (antes de heurísticas de telefone), telefone (formatos BR comuns), RG, nome após rótulos (`Paciente:`, `Nome:`, etc.).

3. **Limitações:** sem NER completo; nomes sem rótulo não são mascarados por defeito. `mask_heuristic_names=True` pode dar falsos positivos.

4. **Marcadores:** `[E-MAIL]`, `[TELEFONE]`, `[CPF]`, `[CNPJ]`, `[DOCUMENTO_RG]`, `[NOME]`.

### API

```python
from security import mask_pii

result = mask_pii(texto_ocr)
texto_seguro = result.text
```

Ver `runtime/agent_action/guardrail_example.py` (delega em `mask_pii`). Dados nos testes são fictícios.
