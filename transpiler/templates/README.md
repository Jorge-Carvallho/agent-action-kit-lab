# Templates (`transpiler/templates/`)

## Em poucas palavras

Esta pasta serve de **referência**: o código que gera o ficheiro `generated_agent.py` está **dentro** de `transpiler/generator.py` (função `generate_source`), não em ficheiros `.tpl` separados. Aqui só se explica isso para quem procura um “template” no disco.

## Comandos

Não há comandos próprios desta pasta. Para gerar o agente:

```bash
python transpiler/generate_agent.py
```

**Precisa de serviços a correr?** **Não.**

---

## Detalhes técnicos

No futuro o texto de geração pode extrair-se para ficheiros `.tpl` **sem mudar** o contrato JSON (`examples/agent_spec.json`).
