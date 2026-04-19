# Testes (`tests/`)

## Em poucas palavras

Aqui estão os **testes automatizados**: validam transpilador, API, PII, OCR, RAG, CLI, agente, etc. **Não** “subem” a aplicação sozinhos — alguém corre o comando na máquina (ou CI).

## Precisa de serviços a correr?

**Não** para a suíte normal (`run_tests.py`): os testes usam mocks ou a API em memória onde for preciso. **Docker** só entra se **tu** quiseres validar manualmente a stack em paralelo.

---

## Depois do clone

Na raiz do repositório:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

No Windows: `.\.venv\Scripts\Activate.ps1`

```bash
pip install -U pip
pip install -r requirements.txt
```

Segue com o venv activo e a pasta actual a ser a raiz do clone.

---

## Todos os testes

```bash
python run_tests.py
```

Roda **todos** os testes principais do projecto, um atrás do outro (transpilador, API, PII, OCR, RAG, CLI, fluxo fim-a-fim, etc.).

```bash
make test
```

Roda a **mesma suíte** que o comando acima, usando o Python do `.venv` definido no Makefile.

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Roda **todos** os ficheiros `test_*.py` da pasta `tests/`, descobrindo-os automaticamente.

---

## Um ficheiro de cada vez

Na raiz do clone. Onde aparece `PYTHONPATH=runtime`, é preciso para carregar o código do agente (`agent_action`).

```bash
PYTHONPATH=runtime python -m unittest tests.test_matrix_example -v
```

Roda só os testes do perfil do agente (laboratório vs genérico e prompts).

```bash
python -m unittest tests.test_validator -v
```

Roda só os testes que validam o JSON de especificação do transpilador.

```bash
python -m unittest tests.test_generator -v
```

Roda só os testes que geram o ficheiro Python do agente a partir do JSON.

```bash
python -m unittest tests.test_pii -v
```

Roda só os testes que mascaram dados pessoais (e-mail, telefone, documentos, etc.).

```bash
python -m unittest tests.test_exams_catalog -v
```

Roda só os testes da lista fictícia de exames (quantidade, campos, códigos).

```bash
python -m unittest tests.test_mcp_ocr_engine -v
```

Roda só os testes do OCR (ler imagem / texto e devolver nomes de exames).

```bash
python -m unittest tests.test_mcp_rag_matcher -v
```

Roda só os testes que ligam nomes de exames ao catálogo (RAG).

```bash
python -m unittest tests.test_api_appointments -v
```

Roda só os testes da API de agendamento (inclui health e criar pedido).

```bash
python -m unittest tests.test_tools_unit -v
```

Roda só os testes das ferramentas do agente (OCR, RAG e chamada à API).

```bash
PYTHONPATH=runtime python -m unittest tests.test_lab_runtime -v
```

Roda só os testes do runtime laboratorial no ADK (tools ligadas ou desligadas).

```bash
python -m unittest tests.test_cli_flow -v
```

Roda só os testes da linha de comandos e do pipeline (sem precisar de Docker).

```bash
python -m unittest tests.test_e2e_offline_full -v
```

Roda só o teste que simula o fluxo completo com a imagem de exemplo até ao agendamento.
