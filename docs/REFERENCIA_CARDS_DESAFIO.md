# Referência — cards do desafio (AI-001 … AI-016)

Este ficheiro reproduz o **backlog** com que a solução foi **planeada e executada**: cada card tem objetivo, escopo, checklist, critérios de pronto, dependências e valor para avaliação. Serve para o **recrutador** alinhar o repositório ao enunciado sem abrir a ferramenta de gestão de tarefas.

**Origem:** export YAML do quadro (`board_id` fictício no script gerador); conteúdo estável para a entrega técnica.

---

## Índice rápido (mapeamento no repo)

| Card | Tema principal | Onde ver no código / docs |
|------|----------------|---------------------------|
| AI-001 | Arquitetura | `README.md` — visão geral, diagrama |
| AI-002 | Estrutura do repo | Pastas `transpiler/`, `runtime/`, `mcp_*`, `api/`, etc. |
| AI-003 | Contrato JSON | `examples/agent_spec.json`, `AGENT_SPEC.md`, schema |
| AI-004 | Validação | `transpiler/validator.py`, `tests/test_validator.py` |
| AI-005 | Geração ADK | `transpiler/generator.py`, `examples/generated_agent.py` |
| AI-006 | MCP OCR | `mcp_ocr/` |
| AI-007 | PII | `security/`, integração no OCR |
| AI-008 | Base mock | `data/exams_mock.json` |
| AI-009 | MCP RAG | `mcp_rag/` |
| AI-010 | API | `api/` |
| AI-011 | Tools | `tools/` |
| AI-012 | Runtime laboratorial | `runtime/agent_action/` |
| AI-013 | CLI | `cli/`, `run_lab_cli.py` |
| AI-014 | Docker | `docker-compose.yml`, `docker/` |
| AI-015 | Testes | `run_tests.py`, `tests/` |
| AI-016 | Documentação / IA | `README.md`, `docs/evidence/` |

---

## AI-001 — Definição da arquitetura final da solução do desafio

**Código:** AI-001  
**Score:** 10

### Objetivo

Definir a arquitetura mínima e oficial da solução para garantir aderência ao desafio, evitar retrabalho e manter o desenvolvimento focado no fluxo principal.

### Escopo técnico

- Definir os componentes obrigatórios da entrega.
- Confirmar que a solução terá: transpilador, agente em Google ADK, OCR via MCP com SSE, RAG via MCP com SSE, API FastAPI, camada de segurança para PII, CLI e Docker Compose.
- Mapear como a base atual do agente será reaproveitada.
- Definir a sequência do fluxo fim a fim: imagem → OCR → mascaramento → RAG → agendamento → saída CLI.

### Checklist sugerida

- [ ] Criar diagrama simples da arquitetura
- [ ] Listar serviços que serão implementados
- [ ] Definir entrada, processamento e saída
- [ ] Validar o escopo mínimo da entrega
- [ ] Registrar decisões iniciais no README

### Critério de pronto

- Arquitetura definida e estável
- Escopo mínimo fechado
- Nenhuma feature extra fora da prioridade principal

### Dependências

- Nenhuma

### Valor para avaliação

Mostra clareza arquitetural, visão de solução e capacidade de priorização.

---

## AI-002 — Estruturação do repositório e organização dos módulos

**Código:** AI-002  
**Score:** 9

### Objetivo

Criar uma estrutura de projeto limpa, legível e coerente com a separação de responsabilidades exigida no desafio.

### Escopo técnico

- Criar os diretórios principais do projeto.
- Separar transpilador, runtime do agente, MCP OCR, MCP RAG, API, segurança, exemplos, testes e documentação.
- Organizar a base para leitura rápida do recrutador e para facilitar evolução.

### Checklist sugerida

- [ ] Criar pasta `transpiler/`
- [ ] Criar pasta `runtime/`
- [ ] Criar pasta `mcp_ocr/`
- [ ] Criar pasta `mcp_rag/`
- [ ] Criar pasta `api/`
- [ ] Criar pasta `security/`
- [ ] Criar pasta `examples/`
- [ ] Criar pasta `tests/`

### Critério de pronto

- Repositório organizado
- Separação de responsabilidades evidente
- Estrutura compreensível sem depender de explicação oral

### Dependências

- AI-001

### Valor para avaliação

Evidencia engenharia de software, organização e cuidado com manutenção.

---

## AI-003 — Modelagem do JSON de especificação do agente

**Código:** AI-003  
**Score:** 10

### Objetivo

Definir o contrato de entrada do transpilador, que será usado para gerar automaticamente o agente em Python com Google ADK.

### Escopo técnico

- Criar o schema do JSON de especificação.
- Modelar campos como nome do agente, instruções, tools, MCP servers, endpoint da API, regras de segurança e modo de saída.
- Garantir que o JSON seja simples de entender e fácil de validar.

### Checklist sugerida

- [ ] Definir campos obrigatórios
- [ ] Definir campos opcionais
- [ ] Criar exemplo válido em `examples/agent_spec.json`
- [ ] Documentar o significado de cada campo
- [ ] Revisar coerência com o runtime do agente

### Critério de pronto

- JSON de exemplo pronto
- Estrutura coerente com o desafio
- Schema documentado e utilizável

### Dependências

- AI-001
- AI-002

### Valor para avaliação

Mostra maturidade na definição do contrato e qualidade do design do transpilador.

---

## AI-004 — Validação robusta do input do transpilador

**Código:** AI-004  
**Score:** 9

### Objetivo

Garantir que o transpilador valide o JSON de entrada de forma robusta, retornando mensagens claras e previsíveis em caso de erro.

### Escopo técnico

- Validar campos obrigatórios.
- Validar estrutura de tools, MCP servers e endpoint da API.
- Retornar erros legíveis para facilitar depuração e demonstrar robustez.
- Cobrir casos inválidos com testes.

### Checklist sugerida

- [ ] Validar ausência de campos obrigatórios
- [ ] Validar nomes inválidos de tools
- [ ] Validar configurações MCP incorretas
- [ ] Validar URL base da API
- [ ] Criar mensagens de erro claras
- [ ] Criar testes de entrada válida e inválida

### Critério de pronto

- Validação funcionando
- Erros legíveis
- Testes cobrindo cenários principais

### Dependências

- AI-003

### Valor para avaliação

Evidencia robustez, confiabilidade e preocupação com qualidade de entrada.

---

## AI-005 — Geração automática do código Python do agente com Google ADK

**Código:** AI-005  
**Score:** 10

### Objetivo

Implementar o núcleo do desafio: transformar o JSON de especificação em um arquivo Python executável que instancie o agente utilizando Google ADK.

### Escopo técnico

- Implementar o gerador de código do transpilador.
- Usar a base arquitetural atual como referência de estrutura.
- Gerar um arquivo como `generated_agent.py`.
- Garantir que o código gerado seja legível, executável e consistente com o schema.

### Checklist sugerida

- [ ] Criar `generator.py`
- [ ] Criar template de geração
- [ ] Gerar `generated_agent.py`
- [ ] Validar imports e estrutura ADK
- [ ] Testar execução do arquivo gerado

### Critério de pronto

- Código gerado automaticamente
- Agente sobe sem ajustes manuais
- Estrutura final legível e correta

### Dependências

- AI-003
- AI-004

### Valor para avaliação

É a peça central do desafio e demonstra capacidade de construir automação real sobre ADK.

---

## AI-006 — Implementação do servidor MCP de OCR com SSE

**Código:** AI-006  
**Score:** 10

### Objetivo

Criar o serviço responsável por receber a imagem do pedido médico e retornar os exames extraídos via MCP com Server-Sent Events.

### Escopo técnico

- Criar um servidor MCP específico para OCR.
- Garantir comunicação via SSE.
- Processar a imagem recebida e retornar os exames identificados.
- Documentar como iniciar o servidor e como o agente se conecta a ele.

### Checklist sugerida

- [ ] Criar estrutura do servidor OCR
- [ ] Expor comunicação via SSE
- [ ] Definir payload de entrada
- [ ] Definir payload de saída
- [ ] Testar extração com imagem de exemplo
- [ ] Documentar inicialização do serviço

### Critério de pronto

- Servidor OCR funcionando
- SSE operacional
- Resposta estruturada pronta para consumo pelo agente

### Dependências

- AI-001
- AI-002

### Valor para avaliação

Atende um dos requisitos técnicos explícitos do desafio.

---

## AI-007 — Camada de segurança para detecção e mascaramento de PII

**Código:** AI-007  
**Score:** 10

### Objetivo

Implementar uma camada de proteção capaz de identificar e mascarar dados sensíveis antes que eles sejam enviados ao modelo ou persistidos.

### Escopo técnico

- Detectar nome, documento, telefone e e-mail no conteúdo extraído.
- Aplicar anonimização ou mascaramento.
- Integrar essa etapa entre OCR e processamento pelo agente.
- Reaproveitar a experiência atual com guardrails, adaptando ao contexto laboratorial.

### Checklist sugerida

- [ ] Definir padrões de PII
- [ ] Implementar mascaramento
- [ ] Posicionar a etapa antes do uso por LLM
- [ ] Testar com exemplos fictícios
- [ ] Documentar a política de segurança adotada

### Critério de pronto

- PII mascarada corretamente
- Fluxo protegido antes da inferência
- Testes básicos aprovados

### Dependências

- AI-006

### Valor para avaliação

Mostra maturidade em segurança, privacidade e engenharia responsável.

---

## AI-008 — Criação da base mock de exames com no mínimo 100 registros

**Código:** AI-008  
**Score:** 8

### Objetivo

Construir a base fictícia que será usada pela etapa de RAG para recuperação de códigos e detalhes dos exames.

### Escopo técnico

- Criar uma base local simples em JSON ou SQLite.
- Inserir pelo menos 100 exames diferentes.
- Associar nome, código e descrição curta.
- Incluir sinônimos quando fizer sentido para melhorar matching.

### Checklist sugerida

- [ ] Definir formato da base
- [ ] Inserir 100+ exames
- [ ] Adicionar códigos consistentes
- [ ] Adicionar descrições curtas
- [ ] Revisar dados para manter tudo fictício

### Critério de pronto

- Base com 100+ registros
- Dados consistentes
- Pronta para consulta pelo serviço de RAG

### Dependências

- AI-001
- AI-002

### Valor para avaliação

Atende diretamente ao requisito da base simulada com volume mínimo.

---

## AI-009 — Implementação do servidor MCP de RAG com SSE

**Código:** AI-009  
**Score:** 10

### Objetivo

Criar o serviço responsável por consultar a base de exames e retornar os códigos corretos, utilizando MCP com SSE.

### Escopo técnico

- Criar o servidor MCP de RAG.
- Receber os nomes dos exames extraídos.
- Buscar correspondência na base mock.
- Retornar nome normalizado, código e detalhes.
- Aplicar busca simples e robusta, sem complexidade excessiva.

### Checklist sugerida

- [ ] Criar servidor RAG
- [ ] Expor comunicação SSE
- [ ] Conectar à base mock
- [ ] Implementar matching por nome/sinônimo
- [ ] Definir resposta estruturada
- [ ] Testar consultas principais

### Critério de pronto

- Servidor RAG funcionando
- Retorno consistente para o agente
- Busca básica confiável

### Dependências

- AI-008

### Valor para avaliação

Mostra capacidade de orquestração e de construir um fluxo de recuperação funcional.

---

## AI-010 — Desenvolvimento da API FastAPI fictícia de agendamento

**Código:** AI-010  
**Score:** 9

### Objetivo

Implementar a API que receberá os exames e devolverá a confirmação de solicitação de agendamento.

### Escopo técnico

- Criar a aplicação FastAPI.
- Definir endpoint principal de agendamento.
- Expor documentação Swagger em `/docs`.
- Garantir que o contrato reflita exatamente o que será consumido pelo agente.

### Checklist sugerida

- [ ] Criar `POST /appointments`
- [ ] Criar `GET /health`
- [ ] Definir schemas Pydantic
- [ ] Validar payload
- [ ] Revisar documentação Swagger
- [ ] Testar resposta de sucesso

### Critério de pronto

- API acessível
- Swagger funcionando
- Contrato claro e compatível com o agente

### Dependências

- AI-001
- AI-002

### Valor para avaliação

Demonstra integração entre agente e serviço externo com contrato claro.

---

## AI-011 — Implementação das tools do agente para OCR, RAG e agendamento

**Código:** AI-011  
**Score:** 10

### Objetivo

Conectar o agente gerado aos serviços do fluxo por meio de tools claras, reutilizáveis e bem organizadas.

### Escopo técnico

- Criar a tool de OCR para consumir o MCP OCR.
- Criar a tool de RAG para consumir o MCP RAG.
- Criar a tool de agendamento para consumir a API FastAPI.
- Tratar erros de integração de forma legível.

### Checklist sugerida

- [ ] Implementar `ocr_extract_exams`
- [ ] Implementar `rag_lookup_exam_codes`
- [ ] Implementar `submit_appointment_request`
- [ ] Padronizar payloads de ida e volta
- [ ] Tratar timeout e erro de conexão
- [ ] Integrar tools ao agente ADK

### Critério de pronto

- Tools conectadas e funcionais
- Chamadas de ponta a ponta funcionando
- Mensagens de erro tratadas

### Dependências

- AI-006
- AI-009
- AI-010

### Valor para avaliação

Mostra integração real do agente com o ecossistema do projeto.

---

## AI-012 — Adaptação do runtime e do contexto do agente para o caso laboratorial

**Código:** AI-012  
**Score:** 9

### Objetivo

Adaptar a base atual do agente para o novo domínio, trocando o contexto comercial por um contexto de agendamento de exames laboratoriais.

### Escopo técnico

- Criar novo profile/contexto do agente.
- Criar novo prompt especializado.
- Definir comportamento esperado no fluxo de exame.
- Reaproveitar a estrutura atual de runtime, mas sem carregar regras do domínio de vendas.

### Checklist sugerida

- [ ] Criar novo profile do agente
- [ ] Criar prompt do domínio laboratorial
- [ ] Registrar tools corretas no runtime
- [ ] Revisar nome, instruções e papel do agente
- [ ] Testar comportamento do agente com contexto novo

### Critério de pronto

- Contexto novo criado com clareza
- Runtime funcionando sem dependência do fluxo antigo
- Agente coerente com o desafio

### Dependências

- AI-005
- AI-011

### Valor para avaliação

Mostra reaproveitamento inteligente de arquitetura com adaptação correta de domínio.

---

## AI-013 — Implementação da interface CLI para execução do fluxo final

**Código:** AI-013  
**Score:** 8

### Objetivo

Disponibilizar uma forma simples de executar o agente pelo terminal, em linha com o caso de uso pedido no desafio.

### Escopo técnico

- Criar um comando de entrada via CLI.
- Receber o caminho da imagem.
- Executar o fluxo completo com o agente gerado.
- Exibir exames encontrados, códigos recuperados e confirmação do agendamento.

### Checklist sugerida

- [ ] Criar script de entrada CLI
- [ ] Receber caminho da imagem por argumento
- [ ] Chamar o agente gerado
- [ ] Exibir saída legível no terminal
- [ ] Testar fluxo completo localmente

### Critério de pronto

- CLI executa o fluxo fim a fim
- Saída terminal clara e objetiva
- Execução simples para demonstração

### Dependências

- AI-005
- AI-011
- AI-012

### Valor para avaliação

Fecha o caso de uso principal solicitado no enunciado.

---

## AI-014 — Dockerização completa e orquestração via docker-compose

**Código:** AI-014  
**Score:** 10

### Objetivo

Conteinerizar toda a solução e permitir que o ambiente seja executado com poucos comandos.

### Escopo técnico

- Criar Dockerfiles para os serviços necessários.
- Criar `docker-compose.yml`.
- Garantir comunicação entre API, MCP OCR, MCP RAG e runtime.
- Facilitar reprodução local pelo avaliador.

### Checklist sugerida

- [ ] Criar Dockerfile da API
- [ ] Criar Dockerfile do MCP OCR
- [ ] Criar Dockerfile do MCP RAG
- [ ] Configurar runtime/transpilador
- [ ] Criar `docker-compose.yml`
- [ ] Testar subida integrada dos serviços

### Critério de pronto

- Ambiente sobe via Docker Compose
- Serviços se enxergam corretamente
- Execução reproduzível e estável

### Dependências

- AI-006
- AI-009
- AI-010
- AI-013

### Valor para avaliação

Atende requisito explícito de infraestrutura e melhora muito a apresentação da entrega.

---

## AI-015 — Testes unitários e teste end-to-end do fluxo completo

**Código:** AI-015  
**Score:** 9

### Objetivo

Garantir confiabilidade mínima da solução e demonstrar disciplina de engenharia de software.

### Escopo técnico

- Testar validação do JSON.
- Testar geração do código do transpilador.
- Testar API FastAPI.
- Testar mascaramento de PII.
- Testar tools principais.
- Criar teste end-to-end cobrindo o fluxo completo.

### Checklist sugerida

- [ ] Testar `validator.py`
- [ ] Testar `generator.py`
- [ ] Testar API de agendamento
- [ ] Testar mascaramento de PII
- [ ] Testar integração OCR/RAG
- [ ] Criar teste E2E do fluxo principal

### Critério de pronto

- Testes principais implementados
- Fluxo crítico coberto
- Erros mais importantes protegidos

### Dependências

- AI-004
- AI-005
- AI-007
- AI-010
- AI-011
- AI-013

### Valor para avaliação

Reforça a imagem de solução séria, confiável e bem construída.

---

## AI-016 — Documentação final, evidências de execução e transparência do uso de IA

**Código:** AI-016  
**Score:** 10

### Objetivo

Produzir a documentação final do projeto com instruções de execução, evidências de funcionamento e uma seção transparente sobre o uso de IA no desenvolvimento.

### Escopo técnico

- Escrever README detalhado.
- Documentar setup, execução, testes e arquitetura.
- Explicar a abordagem de desenvolvimento com apoio de IA.
- Adicionar referências consultadas.
- Registrar prints, logs e evidências de funcionamento.

### Checklist sugerida

- [ ] Escrever visão geral da solução
- [ ] Documentar arquitetura
- [ ] Documentar execução do Docker Compose
- [ ] Documentar uso do transpilador
- [ ] Documentar uso da CLI
- [ ] Adicionar seção sobre uso de IA
- [ ] Incluir prints e logs principais
- [ ] Revisar clareza final da entrega

### Critério de pronto

- README completo
- Evidências organizadas
- Entrega pronta para avaliação técnica e compartilhamento com recrutador

### Dependências

- AI-014
- AI-015

### Valor para avaliação

Fortalece muito a apresentação final, facilita avaliação e demonstra transparência no processo.
