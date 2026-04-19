# Uso da CLI

## Comandos essenciais

Na raiz do repositorio:

```bash
python run_lab_cli.py examples/sample_prescription.png --dry-run
python run_lab_cli.py examples/sample_prescription.png
python run_lab_cli.py examples/sample_prescription.png --offline --dry-run
```

## Quando usar cada modo

- `--dry-run`: roda OCR + RAG e nao envia para API.
- sem `--dry-run`: envia para API de agendamento.
- `--offline`: nao usa MCP SSE; executa motores locais.

## Leitura da saida no terminal

A saida padrao mostra:

- imagem e backend usado
- exames candidatos do OCR
- previa de texto com PII tratada
- resultados do RAG (match/sem match)
- resposta final de agendamento (ou nao envio no dry-run)

## Dependencias de servico

- modo normal: MCP OCR + MCP RAG no ar
- sem `--dry-run`: API tambem no ar
- modo `--offline`: nao depende de MCP
