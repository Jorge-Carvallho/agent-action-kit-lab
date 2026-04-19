# Runtime (`runtime/`)

## Em poucas palavras

Esta pasta contém o pacote Python **`agent_action`**: perfis do agente (**laboratório** vs genérico), **prompts**, forma de juntar o **Google ADK** com as **tools** do projeto. É o “cérebro” do agente quando corres `run_adk.py` ou integrações semelhantes.

Não é a API nem os MCP — são **bibliotecas e scripts** de execução do agente.

## Comandos

Na **raiz**, com `PYTHONPATH` a apontar para `runtime`:

```bash
PYTHONPATH=runtime python -m unittest tests.test_matrix_example -v
```

Smoke rápido (na raiz, script já ajusta paths conforme o repo):

```bash
python run_smoke.py
```

**Precisa de serviços a correr?** **Não** para importar o pacote ou smoke mínimo. **Sim** se o agente estiver configurado para chamar **MCP/API** na rede. **`GOOGLE_API_KEY`** só para inferência com o modelo.

---

## Detalhes técnicos

- Para `import agent_action`, o directório **`runtime`** tem de estar no `PYTHONPATH` (o `run_tests.py` na raiz faz isso).
- Conteúdo principal: subpasta **`agent_action/`** — ver `runtime/agent_action/README.md` e `runtime/agent_action/HANDOFF.md`.
