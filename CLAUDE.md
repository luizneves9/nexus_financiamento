# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Sobre o projeto

Nexus é uma aplicação Streamlit interna para o Grupo GBS que centraliza a
gestão de contratos de financiamento (dados financeiros, empresas, bancos,
fornecedores e bens vinculados). O ciclo cobre inclusão, consulta, projeção de
parcelas, antecipações e liquidação de contratos. A documentação funcional
completa vive em `docs/` — comece por [docs/README.md](docs/README.md), que
indexa requisitos, regras de negócio, arquitetura, casos de uso, operação,
segurança e testes, e por
[docs/requirements/status-register.md](docs/requirements/status-register.md),
que é a fonte de consulta rápida sobre o que está implementado, parcial,
"banco preparado" ou planejado.

Autenticação (login, primeiro acesso, sessão de 30 min) e log de auditoria já
estão implementados; **perfis/permissões ainda não** (ver
`docs/architecture/decisions.md`, DA04 e DA06). Não trate o estado atual como
pronto para produção sem resolver as pendências de segurança do backlog
(`BL-014` a `BL-018` em `docs/requirements/status-register.md`).

## Comandos

Não há `requirements.txt`/`pyproject.toml` no repositório: as dependências
Python (streamlit, pandas, sqlalchemy, psycopg2, python-dotenv) vêm
pré-instaladas na imagem base `fin-base:1.0` usada pelo `Dockerfile`. Não há
suíte de testes automatizados neste repositório no momento.

Rodar a aplicação localmente (requer Python com as dependências acima
instaladas e um `.env` com `DB_USER`, `DB_PASS`, `DB_HOST`, `DB_PORT`,
`DB_NAME` e `AUTH_SECRET` — chave que assina o cookie de login; sem ela o
login funciona, mas não persiste ao fechar o navegador):

```bash
streamlit run src/main.py --client.toolbarMode=viewer
```

Rodar sempre a partir da **raiz** do repositório: é de lá que o Streamlit lê
`.streamlit/config.toml` (cor de destaque índigo da identidade visual), igual
ao Docker (`WORKDIR /app`). O `config.toml` só é lido na inicialização.

Rodar via Docker (como em produção, porta 8502):

```bash
docker compose up --build
```

O `Dockerfile` assume a existência local da imagem `fin-base:1.0`.

## Arquitetura

Camadas estritas, com o PostgreSQL (schema `financiamento`) concentrando a
lógica financeira — ver `docs/architecture/system-overview.md` e
`docs/architecture/decisions.md` (DA01: PostgreSQL é o motor financeiro;
funções, triggers, views e materialized views são a fonte de verdade dos
cálculos):

```
views (Streamlit) → services → repositories/queries → PostgreSQL (schema financiamento)
```

- `src/main.py` — entrypoint Streamlit. Sem usuário logado, registra só a
  página de login (`st.navigation(..., position='hidden')`); logado, renova a
  sessão, mostra usuário/**Sair** na sidebar e define a navegação em três
  grupos: *Operacional* (Contratos, Antecipação), *Cadastros* (Empresas,
  Bancos, Fornecedor) e *Relatórios* (Projeção de Pagamentos, Endividamento).
- Autenticação — `views/login.py` + `services/login.py`: usuários em
  `financiamento.usuarios` (criados só pelo desenvolvedor, ver
  `database/usuarios.sql`); primeiro acesso com senha vazia leva ao cadastro
  de senha; senha guardada só como hash `scrypt`; cookie `nexus_sessao`
  assinado com HMAC (`AUTH_SECRET`), 30 min deslizantes.
- Log de auditoria — `services/log.py` (`registrar_log`,
  `registrar_log_falha` e o catálogo de ações) grava em
  `financiamento.log_auditoria` (somente inserção, ver
  `database/log_auditoria.sql`).
- `src/views/` — telas e componentes de interface (`views/components/` tem os
  modais, ex. inclusão/exclusão/projeção de contrato). Views chamam services;
  não devem conter SQL. Telas de relatório somente leitura (sem botões/ações)
  seguem o padrão mais simples de `views/bancos.py`
  (`st.data_editor` com coluna `sel`, sem linha de botões), não o de
  `views/contracts.py`.
- `src/services/` — orquestração e regras de negócio: validação de campos
  (via `session_state`), regras de datas/valores, tratamento de
  `IntegrityError`/`OperationalError` do SQLAlchemy, mensagens de
  sucesso/erro em `session_state['mensagem_sucesso']` /
  `session_state['mensagem_erro']`.
- `src/repositories/` — funções finas de execução (`conn.execute`,
  `pd.read_sql`) que recebem query e parâmetros já prontos dos services.
- `src/queries/` — strings SQL nomeadas em maiúsculas, uma por domínio
  (`queries_contracts.py`, `queries_bancos.py`, `queries_empresas.py`,
  `queries_fornecedores.py`, `queries_gerais.py`). Todo SQL da aplicação deve
  ficar aqui, não espalhado pelas views/services.
- `src/database/connection.py` — `ConexaoBancoSQL` cria a engine SQLAlchemy
  (`postgresql://...`) sob demanda a partir de `ImportacaoENV`.
- `src/config/settings.py` — `ImportacaoENV` lê `.env` via `python-dotenv`
  (`DB_USER`, `DB_PASS`, `DB_HOST`, `DB_PORT`, `DB_NAME`).
- `src/tools/` — utilitários (ex. formatação de valores para exibição).

Padrão observado: cada módulo de `services/` instancia sua própria
`ConexaoBancoSQL()`/`engine` no nível do módulo (não há engine
compartilhada/injetada). Escritas usam `with engine.begin() as conn:` para
transação; leituras simples às vezes usam `engine` diretamente.

### Formatação de data e valor em dataframes (padrão de views/contracts.py)

Toda tela que exibe datas ou valores monetários em `st.dataframe`/
`st.data_editor` segue o mesmo padrão de `src/views/contracts.py`:

- **Datas:** não transformar a coluna em string; manter o tipo nativo e
  formatar via `column_config`, ex.
  `st.column_config.DateColumn(format='DD/MM/YYYY')`, chaveado pelo nome
  real da coluna retornada pela query.
- **Valores monetários:** aplicar `df[coluna] = df[coluna].map(transformar_float_em_str)`
  (formato brasileiro, milhar com ponto e decimal com vírgula) **antes** de
  inserir a coluna `sel`. Importar a função de `tools.funcoes` (versão
  canônica) em vez de duplicá-la localmente — `views/contracts.py` tem uma
  cópia local da mesma função por legado; não repita esse padrão em telas
  novas.
- Os nomes de coluna não são inventados: a query em geral retorna exatamente
  o que a view do PostgreSQL expõe (sem alias em Python). Quando a view não
  estiver documentada em `database/ddl_financiamento.sql` (caso de
  `vw_agrupamento_projecao`, ver `database/README.md`), **peça ao usuário os
  nomes reais das colunas de data/valor** antes de escrever a formatação —
  não adivinhe.

### Identidade visual (mesma do Nexus Extrato, CSS feito para o Streamlit 1.63.0)

- Cor de destaque em `.streamlit/config.toml` (índigo `#6366F1`); CSS geral,
  logo (`src/assets/`) e rodapé do menu (`sb_rodape`) em `src/main.py`.
- Toda tela começa com `cabecalho('Título', 'Subtítulo.', 'icone')`
  (`views/components/cabecalho.py`), com o ícone Material do grupo no menu
  (`request_quote` Operacional, `folder_open` Cadastros, `bar_chart`
  Relatórios) — não usar `<h2>` em HTML nem `st.title`.
- A ação principal de cada tela/modal usa `type='primary'`
  (`views/components/botao_principal.py`); não estilizar botão por botão.
  Filtrar e a linha de ações das telas (ex. Novo/Projeção/Liquidar/Excluir
  em Contratos) ficam como botões normais; o destaque fica no Confirmar dos
  modais e no Entrar/Cadastrar senha do login.
- Consultas que podem demorar em `with st.spinner('Consultando ...'):`.

### Filtros de tela (padrão de views/relatorio_projecao_pagamentos.py)

- `st.form` com os campos em `st.container(horizontal=True, vertical_alignment='bottom')`
  e botão **Filtrar**; filtragem sempre no banco (query com
  `(:param IS NULL OR coluna ILIKE :param)` e intervalos de data `de/até`).
- `session_state` exclusivo da página com prefixo próprio (`fp_` Projeção,
  `fa_` Antecipação, `fc_` Contratos) guardando o filtro aplicado.
- Cada widget usa `key='<prefixo>_<campo>_input'` inicializada a partir do
  filtro salvo — **nunca** `value=st.session_state...`: um `value` que muda
  recria o widget e descarta o que o usuário digitou (bug corrigido na
  Projeção; `views/contracts.py` ainda tem o padrão antigo, ver `BL-020`).
- Resumo abaixo da tabela: uma única `st.caption` com os itens separados por
  `&nbsp;&nbsp;|&nbsp;&nbsp;`, calculado no service **antes** da formatação
  dos valores.

### Banco de dados

- `database/ddl_financiamento.sql` é um retrato documental do schema
  `financiamento` (tabelas de empresas, bancos, fornecedores, contratos,
  bens, veículos, feriados, Selic, antecipações; funções de dias úteis/Selic/
  projeção; triggers; a view `vw_controle_contratos`; e as materialized views
  `mv_projecao_moeda`, `mv_projecao_moeda_final`, `mv_projecao_tfc`). **Não é
  um instalador/migração** — não execute em produção.
- `database/usuarios.sql` e `database/log_auditoria.sql` são scripts de
  criação (já executados em desenvolvimento) das tabelas de autenticação e
  auditoria; ainda não refletidos no `ddl_financiamento.sql` (`BL-019`).
- `database/projection_functions.sql` documenta as funções PostgreSQL de
  projeção temporária usadas na inclusão de contratos (DA05: a projeção roda
  via função no banco, sem persistir o contrato, para evitar efeitos
  colaterais de insert+rollback).
- Fonte de verdade para alterações de modelo/cálculo: o SQL versionado em
  `database/`, testado em banco de desenvolvimento e refletido na
  documentação de arquitetura — não altere o comportamento apenas no Python.

## Convenções (docs/operations/development-guide.md)

- Preservar as camadas existentes (views → services → repositories/queries)
  ao criar funcionalidades; não colocar SQL fora de `src/queries/`.
- Usar transações (`engine.begin()`) para operações de escrita.
- Não ocultar exceções de banco sem registrar ou apresentar contexto ao
  usuário (ver o padrão de `mensagem_erro`/`mensagem_sucesso` em
  `src/services/contracts.py`).
- Ao mudar um fluxo funcional, atualizar também o Use Case correspondente em
  `docs/use_cases/`, os requisitos/regras de negócio relevantes e a
  [Matriz de Rastreabilidade](docs/requirements/traceability-matrix.md).
- Uma funcionalidade com tabela/trigger já existente no banco não deve ser
  considerada entregue só por isso — distinguir "banco preparado" de
  "implementado" (ver status em `docs/requirements/status-register.md`).
- **Avaliar log de auditoria em toda funcionalidade nova** (ver seção
  "Log de auditoria" abaixo).

## Log de auditoria

Ao finalizar qualquer funcionalidade nova, **avalie se ela precisa gravar
log** em `financiamento.log_auditoria` e informe o usuário da decisão (com o
motivo) antes de considerar a entrega concluída.

- **Precisa de log:** toda operação que grava/altera/exclui dados (inclusão,
  exclusão, antecipação, cadastro de senha...), eventos de acesso (login,
  falha, logout, sessão encerrada) e, quando existirem, negativas de
  permissão. Consultas e relatórios somente leitura **não** são registrados
  (decisão atual, para não gerar volume sem valor).
- **Como registrar:**
  - Escrita: chamar `registrar_log(ACAO, entidade, id_registro, detalhes=..., conn=conn)`
    **dentro do mesmo `with engine.begin() as conn:`** da operação — se o log
    falhar, a operação é desfeita. Use `RETURNING id` (inclusão) ou
    `RETURNING *` (exclusão, para guardar a cópia do registro) na query.
  - Falha da operação: `registrar_log_falha(ACAO, erro, entidade, ...)` nos
    `except` (transação própria; não esconde a mensagem original).
  - Ação nova: criar a constante no catálogo de `services/log.py` e
    documentá-la no comentário da coluna `acao` em
    `database/log_auditoria.sql` e na lista de ações de
    `docs/architecture/decisions.md` (DA06).
- **Nunca** gravar senha, hash, token/cookie ou segredos em `detalhes`.
- O log é somente inserção (trigger bloqueia UPDATE/DELETE/TRUNCATE): para
  testar escritas no banco de desenvolvimento sem deixar registros, rode o
  teste dentro de uma transação desfeita no final (savepoints + rollback).

## Fluxo de trabalho para novas funcionalidades

Processo padrão (validado na sessão que criou o relatório de Projeção de
Pagamentos — UC09/RF07.3):

1. **Levantar contexto antes de codificar:** ler o Use Case/RF/RN citados
   pelo usuário e o arquivo de domínio mais próximo já existente
   (view/service/repository/query) para replicar o padrão exato, em vez de
   inventar um novo.
2. **Perguntar antes de decidir** quando houver mais de uma leitura razoável
   (nome/local de arquivo, componente de UI, reuso vs. novo arquivo) — usar
   perguntas objetivas com opção recomendada, não assumir silenciosamente.
3. **Implementar seguindo a camada 1:1 já usada no projeto:** view e service
   com o mesmo nome de arquivo (ex. `views/x.py` ↔ `services/x.py`), query
   dedicada em `src/queries/`, reaproveitando `repositories/funcoes.py`
   quando a operação for uma leitura simples.
4. **Avaliar o log de auditoria** da funcionalidade (seção "Log de
   auditoria") e implementá-lo quando necessário.
5. **Testar a funcionalidade** no Streamlit antes de documentar (não presumir que
   compilação Python = funcionamento correto):
   - Para consultas ao banco: validar que os dados chegam; se a view/tabela não estiver documentada no DDL (ex. `vw_agrupamento_projecao`), registrar em `database/README.md` após confirmar que funciona.
   - Para telas: navegar até o caminho novo e validar visualmente.
   - Só após teste bem-sucedido e aprovação do usuário, prosseguir para documentação.
6. **Atualizar a documentação**, nesta ordem (apenas após teste aprovado), só criando o que for
   realmente novo:
   - **RF** em `docs/requirements/functional-requirements.md` — criar um
     novo ID (ou subitem, ex. `RF07.3` de `RF07`) só se o comportamento não
     estiver coberto por um RF existente.
   - **RN** em `docs/requirements/business-rules.md` — só criar uma regra
     nova se a funcionalidade introduzir uma política de domínio nova.
     Uma tela que apenas expõe/agrupa um cálculo já existente (ex. reaproveita
     a mesma view/função de projeção) deve referenciar as RNs já existentes
     (ex. RN02 - cálculo no banco, RN03 - dias úteis) em vez de duplicá-las.
   - **Use Case** novo ou atualizado em `docs/use_cases/` (próximo `UCxx`
     sequencial), seguindo a estrutura de UC02/UC03.
   - [Matriz de Rastreabilidade](docs/requirements/traceability-matrix.md) —
     linha com RF, RNs, UC, status e pendência principal.
   - [Registro de Status e Pendências](docs/requirements/status-register.md)
     — linha no painel executivo, seção de detalhamento do UC, e item no
     backlog rastreável (`BL-XXX`) se houver pendência a acompanhar.
   - Tabela "Status dos Use Cases" em `docs/README.md`.
   - `docs/roadmap.md`, se a entrega tocar um item do roadmap.
   - Se a query referenciar um objeto do banco (view/função/tabela) que não
     está em `database/ddl_financiamento.sql`, **não presumir sua estrutura**
     — registrar a pendência em `database/README.md` e no backlog do
     status-register para documentação futura do DDL.
