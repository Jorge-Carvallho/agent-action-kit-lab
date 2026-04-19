# Transpilador (`transpiler/`)

## Em poucas palavras

Aqui está o programa que **lê o JSON** da especificação do agente, **valida** se está correto e **escreve** um ficheiro Python que cria o agente só com **Google ADK**. Resolve o desafio “JSON → código executável”.

O ficheiro gerado fica em **`examples/generated_agent.py`** (por omissão).

## Comandos

Na **raiz** do repositório:

```bash
pip install -r transpiler/requirements.txt
python transpiler/validate_spec.py examples/agent_spec.json
python transpiler/generate_agent.py
python examples/generated_agent.py
```

Chat com o modelo (opcional, precisa de chave Google):

```bash
python examples/generated_agent.py --chat "Olá"
```

**Precisa de serviços a correr?** **Não** para validar ou gerar código, nem para o **smoke** do agente. **Sim** (`GOOGLE_API_KEY`) se usares **`--chat`**. Os MCP e a API só entram quando **corres** o agente gerado num cenário que chama as tools na rede.

---

## Detalhes técnicos

- **Contrato:** `examples/agent_spec.json`, `examples/agent_spec.schema.json`, `examples/AGENT_SPEC.md`.
- **Validação:** `validator.py`, `validate_spec.py`.
- **Geração:** `generator.py`, `generate_agent.py` (opções `-o`, `--no-validate` para debug).

Ver também o README na **raiz** (secção transpilador).
