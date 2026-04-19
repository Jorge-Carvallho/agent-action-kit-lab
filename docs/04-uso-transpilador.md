# Uso do transpilador

## Objetivo

Transformar a especificacao JSON do agente em codigo Python executavel com Google ADK.

## Comandos principais

Na raiz do repositorio:

```bash
python transpiler/validate_spec.py examples/agent_spec.json
python transpiler/generate_agent.py
python examples/generated_agent.py
```

## Resultado esperado

- Validacao retorna sucesso para um spec conforme schema.
- Geracao cria/atualiza `examples/generated_agent.py`.
- Execucao sem `--chat` faz smoke do agente.

## Chat com modelo (opcional)

Requer `GOOGLE_API_KEY` valida:

```bash
python examples/generated_agent.py --chat "Ola"
```

## Arquivos-chave

- `examples/agent_spec.json`
- `examples/agent_spec.schema.json`
- `examples/AGENT_SPEC.md`
- `transpiler/validator.py`
- `transpiler/generator.py`
