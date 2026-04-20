# Demo reproduzível (GitHub Actions)

Este documento é um **guia curto** para quem vai **avaliar a entrega no GitHub**, sem precisar rodar nada localmente.

## Antes de começar (30 segundos de leitura)

Quando você “rodar” aqui, o GitHub vai executar um **pipeline** (CI) em uma máquina temporária. Você vai ver, principalmente:

- uma lista de passos (**steps**) com ✅ ou ❌
- **logs** com o que aconteceu (testes, Docker subindo, saída da CLI)
- opcionalmente **Artifacts** (arquivos ZIP) com um “pacote” do resultado

O projeto demonstra um fluxo **OCR → RAG → API**. Em termos práticos:

- **`--dry-run`**: roda o fluxo e mostra o resultado, **sem enviar** o agendamento (POST) na API.
- **Sem `--dry-run`**: roda o fluxo e **envia** o agendamento para a API (dentro do ambiente do CI).

## Como saber em qual branch rodou (e por que às vezes não aparece “escolher branch”)

Existem dois jeitos comuns de executar um workflow no GitHub:

- **Automático por `push`**: quando alguém faz commit/push na `main`, o GitHub já sabe a branch. Por isso você vê **`Triggered via push`** e aparece um badge **`main`** ao lado do commit — **não tem** o menu “Use workflow from”.
- **Manual (`Run workflow`)**: aí sim aparece o seletor de branch, porque você está escolhendo explicitamente de onde rodar.

Se você clicar em **Re-run jobs** / **Re-run all jobs** (ou **Executar novamente todos os trabalhos**), o GitHub **repete o mesmo run** (na mesma branch/commit). Por isso também **não aparece** seletor: não é um disparo novo “do zero”.

Dica: no **Job Summary** (aba **Summary**), normalmente aparece `Ref: refs/heads/main` — isso confirma a branch.

## Vamos executar — Passo 1 (apertar e ver rodando)

Objetivo: você mesmo dispara a execução e acompanha o resultado no GitHub.

Workflow: **`Demo full (tests + docker + POST)`**

- O jeito mais comum de “ver de novo” é **reexecutar um run que já existe** (não precisa escolher branch).
- Também pode ser disparado manualmente via **Run workflow** (isso **só** aparece quando o workflow ainda não tem histórico / quando você está na tela correta de disparo manual).
- Executa a CLI **sem `--dry-run`** (faz o **POST** na API do ambiente do runner).

### Passo a passo (cliques)

1. Aba **Actions**
2. No menu esquerdo, clique em **`Demo full (tests + docker + POST)`**
3. Abra o **run mais recente** (o da lista)
4. No canto superior direito, clique em **Re-run all jobs**  
   - Se o GitHub estiver em português: **Executar novamente todos os trabalhos**
5. Aguarde terminar e volte para a mesma página do run
6. Clique no job **`demo-full`**
7. Expanda o step **`Run CLI demo (POST real)`** (é onde aparece o “resultado” do fluxo)

#### Se não existir nenhum run ainda (primeira vez)

1. Ainda em **`Demo full (tests + docker + POST)`**, use **Run workflow**
2. Em **Use workflow from**, selecione **`main`**
3. Clique em **Run workflow**

### O que olhar sem baixar nada

- Na página do run (aba **Summary**), procure o **Job Summary** gerado automaticamente.

### Artefato (opcional)

- Artifact **`demo-full-report`** (ZIP).

## Passo 2 (opcional): evidência automática na `main` (sem POST)

Workflow: **`Demo (tests + docker + cli)`**

- Dispara em **push na branch `main`** e também pode ser executado manualmente via **Run workflow**.
- Executa a CLI com **`--dry-run`** (não envia POST na API).

### Passo a passo (cliques)

1. Aba **Actions**
2. No menu esquerdo, clique em **`Demo (tests + docker + cli)`**
3. Abra o run com **✅ Success**
4. (Opcional) Se quiser repetir a evidência: **Re-run all jobs** / **Executar novamente todos os trabalhos**
5. Clique no job **`demo`**
6. Expanda o step **`Run CLI demo (dry-run)`**

### O que olhar sem baixar nada

- Na página do run (aba **Summary**), procure o **Job Summary** gerado automaticamente.

### Artefato (opcional)

- Artifact **`demo-report`** (ZIP) com saída da CLI + JSONs de `/health` + `docker compose ps`.

## Detalhes adicionais (opcional)

Para uma versão mais detalhada do passo a passo (com mais contexto e checklist), veja:

- [`docs/DEMO_GITHUB_ACTIONS.md`](docs/DEMO_GITHUB_ACTIONS.md)
