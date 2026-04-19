# Exemplos (`examples/`)

## Em poucas palavras

Esta pasta concentra o **contrato do agente em JSON**, o **schema**, a documentação do contrato, o **agente Python gerado** (não editar à mão) e uma **imagem fictícia** de pedido médico para demos e testes.

É o sítio que um recrutador abre para ver **o que o transpilador consome** e **o que sai** em código.

## Comandos

Validar o spec e gerar o agente:

```bash
pip install -r transpiler/requirements.txt
python transpiler/validate_spec.py examples/agent_spec.json
python transpiler/generate_agent.py
python examples/generated_agent.py
```

Testar a CLI com a imagem de exemplo (modo MCP: precisa da stack Docker):

```bash
python run_lab_cli.py examples/sample_prescription.png --dry-run
```

Sem Docker:

```bash
python run_lab_cli.py examples/sample_prescription.png --offline --dry-run
```

**Precisa de serviços a correr?** **Não** para validar o JSON ou gerar código. **Sim** (MCP + API) para a CLI em **modo normal** sem `--offline`. Ver README na **raiz**.

---

## Detalhes técnicos

| Ficheiro | Descrição |
|----------|-----------|
| **`agent_spec.json`** | Spec válida do transpilador |
| **`agent_spec.schema.json`** | JSON Schema (draft-07) |
| **`AGENT_SPEC.md`** | Contrato campo a campo |
| **`generated_agent.py`** | Gerado — usar `transpiler/generate_agent.py` |
| **`sample_prescription.png`** | Imagem fictícia para OCR/demo |
