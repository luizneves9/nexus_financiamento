# Registro de Status e Pendências

Este documento e o painel de rastreabilidade operacional do projeto. Ele
responde rápidamente:

- o que já foi implementado;
- o que foi implementado apenas no banco;
- o que está parcial;
- o que falta para concluir cada item;
- onde existe evidência no código ou no banco;
- qual e a próxima ação;
- qual critério permite mudar o status para concluído.

A coluna **Status** do README e dos demais documentos deve ser sempre coerente
com este registro.

## Como consultar

1. Localize o item pelo ID, como `UC03`, `RF07` ou `RNF04`.
2. Leia o motivo do status.
3. Consulte a coluna **Entregue** para saber o que já existe.
4. Consulte **Pendente** para saber o que ainda falta.
5. Abra as evidências indicadas em **Evidência**.
6. Use **Próxima ação** para iniciar o trabalho.
7. Somente altere o status quando o critério de conclusão for aténdido.

## Status padronizados

| Status | Significado | Pode ser considerado entregue? |
| --- | --- | --- |
| Implementado | O fluxo principal existe na aplicação e possui evidência verificável. | Sim, respeitando eventuais limitacoes registradas. |
| Parcial | Parte do fluxo existe, mas uma ou mais etapas do escopo ainda não existem. | Não. |
| Banco preparado | Existem tabelas, funções, triggers ou views, mas falta fluxo completo na aplicação. | Não. |
| Planejado | O comportamento foi definido, mas ainda não existe implementação funcional. | Não. |
| Bloqueado | Existe dependência que impede a conclusão. | Não. |
| A validar | Existe implementação ou decisão, mas falta validação técnica ou do negócio. | Não. |
| Concluído | Implementação, persistência, testes e validação foram aprovados. | Sim. |

## Painel executivo

| ID | Assunto | Status atual | Motivo resumido | Próxima ação |
| --- | --- | --- | --- | --- |
| UC01 | Inclusão de contratos | Parcial | Inclusão e projeção temporária funcionam, mas vínculo de bens/veículos e autenticação ainda faltam. | Implementar vínculo de bens e veículos. |
| UC02 | Consulta de contratos | Implementado | Listagem, filtros por Empresa/Banco/Contrato e validação de vazio implementados. Tratamento de erro e desempenho sob análise. | Validar cenários e otimizar desempenho. |
| UC03 | Visualização de projeção | Parcial | Consulta e cálculos estão corretos; validação específica do impacto de antecipações ainda falta. | Validar antecipações. |
| UC04 | Exclusão física | Implementado | DELETE e confirmação existem, mas dependências e auditoria limitam o fluxo. | Documentar procedimento de dependências e validar comportamento. |
| UC05 | Bens e veículos | Banco preparado | Tabelas e relacionamentos existem, mas não ha interface nem regras completas. | Implementar telas, validações e regras de chassi/placa. |
| UC06 | Antecipação e liquidação antecipada | Implementado (BNDES FINAME SELIC) | Tela única consolida antecipação e quitação (tipo_lancamento), com cálculo de saldo devedor/Selic pré-confirmação e validações. Não suporta outras modalidades de contrato. | Validar cálculo com o financeiro e avaliar suporte a outras modalidades. |
| UC07 | Liquidação | Consolidado em UC06 | Funcionalidade absorvida por UC06 — quitação é um tipo de lançamento no mesmo fluxo de antecipação. | Nenhuma. |
| UC08 | Atualização da Selic | Banco preparado | Tabela e consultas existem, mas não ha importação por API ou job. | Definir fonte e implementar integração idempotente. |
| UC09 | Relatório de projeção de pagamentos | Implementado | Tela consolidada com filtros (Empresa, Banco, Contrato, Data Vcto de/até) no banco e resumo; sem exportação e view não documentada no DDL. | Adicionar exportação e documentar a view no DDL versionado. |
| UC10 | Relatório de endividamento | Implementado | Tela de fluxo de caixa com agrupamento por ano/mês, tema automático e botões de alternância. View ainda não documentada no DDL. | Documentar `vw_agrupamento_projecao` no DDL e adicionar filtros/download. |
| UC11 | Consulta de antecipações | Implementado | Aba Antecipação lista todas as antecipações/quitações com filtros no banco e resumo. | Validar com o financeiro. |
| UC12 | Autenticação de usuário | Implementado | Login, primeiro acesso com cadastro de senha (hash scrypt), sessão de 30 min e Sair; eventos registrados no log. Perfis ainda não existem. | Resolver pendências de segurança BL-014 a BL-018. |
| RF03.1 | Filtros de contratos | Planejado | Tela atual lista registros, mas não possui filtros funcionais. | Definir componentes e testes dos filtros. |
| RF08 | Auditoria | Parcial | Log de auditoria grava todas as escritas e eventos de acesso (RF08.1); não há tela de consulta (RF08.2). | Definir a tela de histórico (BL-021). |
| RF10 | Autenticação e perfis | Parcial | Autenticação implementada (UC12); perfis e permissões por aba/ação não existem. | Definir matriz de perfis e permissões (BL-005). |
| RNF07 | Logs e observabilidade | Parcial | Existem mensagens de erro, mas ha exceções silenciosas e falta padrão de logs. | Definir política de logs e substituir tratamentos silenciosos. |
| RNF11 | Backup e restauração | Planejado | Não ha procedimento operacional aprovado. | Definir RTO, RPO, retenção e teste de restauração. |

## Detalhamento por Use Case

### UC01 - Inclusão de contratos

- **Status:** Parcial.
- **Entregue:** formulario web, validação de campos, validação de valores e
  datas, persistência em `financiamento.contratos` e mensagem de resultado.
- **Pendente:** vínculo de bens e veículos e autenticação.
- **Evidência:** `database/projection_functions.sql`,
  `src/queries/queries_contracts.py`,
  `src/views/components/modal_contracts_incluir.py` e
  `src/services/contracts.py`.
- **Próxima ação:** implementar o vínculo de bens e veículos.
- **Critério de conclusão:** formulário completo, bens vinculados, testes de
  aceite executados e erros tratados.

### UC02 - Consulta de contratos

- **Status:** Implementado.
- **Entregue:** 
  - Listagem da view `financiamento.vw_controle_contratos` com ordenação por Id.
  - Filtros parametrizados por Empresa, Banco e Contrato (busca ILIKE, parcial).
  - Validação de dataframe vazio com aviso ao usuário.
  - Seleção de registro para operações (Projeção, Excluir, Novo).
- **Pendente:** tratamento de erro padronizado em caso de falha de conexão e validação de desempenho com muitos registros.
- **Evidência:** `src/views/contracts.py`, `src/services/contracts.py`, `src/repositories/contract.py` e `src/queries/queries_gerais.py`.
- **Próxima ação:** validar filtros com cenários completos (vazio, um campo, múltiplos campos) e otimizar desempenho se necessário.
- **Critério de conclusão:** filtros funcionais, testes de cenário completos, tratamento de erro consistente e desempenho aceitável.

### UC03 - Visualização de projeção

- **Status:** Parcial.
- **Entregue:** seleção de um contrato, consulta das matérialized views e
  exibição de parcela, vencimento e valor em modal.
- **Pendente:** validação específica do impacto de antecipações.
- **Evidência:** `src/views/contracts.py`,
  `src/services/contracts.py`,
  `src/queries/queries_contracts.py` e
  `src/views/components/modal_contracts_projecao.py`.
- **Próxima ação:** validar o impacto de antecipações.
- **Critério de conclusão:** cenários de antecipação validados e recursos de
  consulta implementados.

### UC04 - Exclusão física de contrato

- **Status:** Implementado com dependência de integridade.
- **Entregue:** seleção única, modal de confirmação e `DELETE` transacional.
- **Pendente:** procedimento para registros dependentes, auditoria e testes
  completos de falha de integridade.
- **Evidência:** `src/views/contracts.py`,
  `src/views/components/modal_contracts_excluir.py`,
  `src/services/contracts.py` e `src/queries/queries_contracts.py`.
- **Próxima ação:** definir o procedimento para contratos com bens ou
  antecipações.
- **Critério de conclusão:** comportamento de sucesso, cancelamento e
  bloqueio por dependências validado pelo negócio.

### UC05 - Cadastro de bens e veículos

- **Status:** Banco preparado.
- **Entregue:** tabelas `bem` e `veiculos`, chaves estrangeiras e sequências.
- **Pendente:** telas, services, queries, regras de placa/chassi, listagem,
  filtros e exclusão.
- **Evidência:** DDL do schema `financiamento` e
  `docs/architecture/database-model.md`.
- **Próxima ação:** definir fluxo de cadastro e regras de unicidade.
- **Critério de conclusão:** cadastro, vínculo, consulta, validações e testes
  disponíveis na aplicação.

### UC06 - Antecipação e liquidação antecipada de contrato

- **Status:** Implementado para contratos BNDES FINAME SELIC.
- **Entregue:**
  - Botão **Liquidar** na tela de Gestão de Contratos, exigindo seleção de
    exatamente um contrato.
  - Modal único (`modal_liquidacao_antecipacao.py`) que consolida
    antecipação parcial e quitação total, diferenciadas pelo campo
    `tipo_lancamento`.
  - Cálculo, sob demanda (botão "Calcular Saldo Devedor"), da parcela mais
    próxima da data de pagamento em `mv_projecao_moeda`, da Selic exata ou
    próxima disponível (com fallback para a mais recente do banco) e do
    saldo devedor em moeda.
  - Validações: campos obrigatórios, quitação única por contrato (RN13),
    ordem das datas de pagamento/tesouraria/compensação (RN14).
  - Persistência em `financiamento.antecipacao`; trigger
    `trg_processar_dados_antecipacao` calcula Selic/valor_moeda; trigger
    `trg_after_insert_antecipacao` aciona `refresh_views_contratos()`.
- **Pendente:** suportar contratos de modalidades além de BNDES FINAME
  SELIC; validar o cálculo do saldo devedor com o financeiro.
- **Evidência:** `src/views/contracts.py`,
  `src/views/components/modal_liquidacao_antecipacao.py`,
  `src/services/liquidacao_antecipacao.py`,
  `src/queries/queries_antecipacao.py`,
  `database/ddl_financiamento.sql` e
  `docs/architecture/financial-calculation.md`.
- **Próxima ação:** avaliar suporte a outras modalidades de contrato.
- **Critério de conclusão:** cálculo validado pelo financeiro para todas as
  modalidades relevantes.

### UC07 - Liquidação de contrato (consolidado em UC06)

- **Status:** Consolidado em UC06.
- **Entregue:** a quitação total de contrato é registrada no mesmo fluxo de
  UC06, com `tipo_lancamento = QUITACAO`, sem modelo de dados ou interface
  próprios.
- **Pendente:** nenhuma pendência própria — acompanhar as pendências de
  UC06.
- **Evidência:** `docs/use_cases/UC07-liquidacao-de-contrato.md` (aponta
  para UC06).
- **Próxima ação:** nenhuma.
- **Critério de conclusão:** já atendido via UC06.

### UC08 - Atualização da Selic

- **Status:** Banco preparado.
- **Entregue:** tabela `selic` e consultas da última taxa aplicável.
- **Pendente:** fonte, cliente API/job, idempotência, retries, logs e refresh.
- **Evidência:** `financiamento.selic`,
  `src/queries/queries_contracts.py` e
  `docs/architecture/integrations.md`.
- **Próxima ação:** escolher fonte oficial e especificar contrato da API.
- **Critério de conclusão:** carga automática repetível, validada, observável
  e refletida nos cálculos.

### UC09 - Relatório de projeção de pagamentos

- **Status:** Implementado.
- **Entregue:**
  - Página "Projeção de Pagamentos" no menu Relatórios, consultando a view
    `financiamento.vw_agrupamento_projecao` em uma tabela somente leitura.
  - Filtros por Empresa (`nome_empresa`), Banco (`banco`), Contrato
    (`numero_contrato`) — busca parcial ILIKE — e intervalo de Data de
    Vencimento (`data_vcto` de/até), aplicados na query (no banco).
  - Filtros guardados em `session_state` exclusivo da página (prefixo `fp_`),
    mantidos ao trocar de aba.
  - Resumo abaixo da tabela: quantidade de empresas, bancos e contratos e
    total das parcelas (`total_parcela`), conforme os filtros aplicados.
- **Pendente:** exportação/download e documentação da view no DDL versionado.
- **Evidência:** `src/views/relatorio_projecao_pagamentos.py`,
  `src/services/relatorio_projecao_pagamentos.py`,
  `src/queries/queries_projection.py` e `src/repositories/funcoes.py`.
- **Próxima ação:** documentar `vw_agrupamento_projecao` em
  `database/ddl_financiamento.sql` e definir a exportação.
- **Critério de conclusão:** view documentada no DDL, exportação
  implementada e conteúdo validado pelo financeiro.

### UC10 - Relatório de endividamento

- **Status:** Implementado.
- **Entregue:** página "Endividamento" no menu Relatórios, consultando query
  que agrupa dados de `vw_agrupamento_projecao` por ano/mês em formato de
  fluxo de caixa. Valores em milhões (3 casas decimais). Tema automático que
  respeita `@media (prefers-color-scheme)` + 3 botões de alternância manual
  (automático, claro, escuro).
- **Pendente:** filtros, exportação/download (previstos no roadmap) e
  documentação da view `vw_agrupamento_projecao` no DDL versionado.
- **Evidência:** `src/views/relatorio_endividamento.py`,
  `src/services/relatorio_endividamento.py` e
  `src/queries/queries_relatorio_endividamento.py`.
- **Próxima ação:** documentar `vw_agrupamento_projecao` em
  `database/ddl_financiamento.sql` e adicionar filtros por ano/modalidade.
- **Critério de conclusão:** view documentada no DDL, filtros e download
  implementados, tema automático/manual validado em diferentes navegadores,
  e conteúdo validado pelo financeiro.

### UC11 - Consulta de antecipações

- **Status:** Implementado.
- **Entregue:**
  - Aba Operacional > **Antecipação** (antes um placeholder "em
    desenvolvimento") lista todas as antecipações e quitações de
    `financiamento.antecipacao`, com empresa e banco (razão social) e número
    do contrato obtidos por join com `contratos`, `empresas` e `bancos`.
  - Colunas: `id`, `nome_empresa`, `banco`, `numero_contrato`,
    `data_pagamento`, `valor_pago`, `tipo_lancamento`.
  - Filtros por Empresa, Banco, Contrato (busca parcial) e intervalo de Data
    de Pagamento, aplicados no banco; `session_state` exclusivo (prefixo `fa_`).
  - Resumo abaixo da tabela: quantidade de empresas, bancos e contratos e
    total pago.
- **Pendente:** validação com o financeiro; exportação (se necessária).
- **Evidência:** `src/views/include_antecipation.py`,
  `src/services/include_antecipation.py` e `src/queries/queries_antecipacao.py`
  (`SELECT_ANTECIPACOES`).
- **Próxima ação:** validar conteúdo e filtros com o financeiro.
- **Critério de conclusão:** tela validada pelo financeiro.

### UC12 - Autenticação de usuário

- **Status:** Implementado (sem perfis).
- **Entregue:**
  - Tela de login (Usuário, Senha, Entrar) antes de qualquer outra tela; sem
    login, nenhuma aba é registrada na navegação.
  - Usuários em `financiamento.usuarios`, criados somente pelo desenvolvedor
    (`database/usuarios.sql`).
  - Primeiro acesso: senha vazia leva ao cadastro de senha (mínimo 8
    caracteres + confirmação); grava só o hash `scrypt` (N=2^14, r=8, p=1,
    salt de 16 bytes).
  - Erros por notificação genérica, sem revelar se o usuário existe.
  - Sessão: cookie `nexus_sessao` assinado (HMAC-SHA256, `AUTH_SECRET`),
    válido por 30 min após o último uso; a restauração confere no banco se o
    usuário continua ativo e com senha; conferência repetida a cada
    renovação (no máximo a cada 5 min).
  - **Sair** registra o logout, apaga o cookie e recarrega a página
    (zerando filtros e estado).
  - Eventos `LOGIN`, `LOGIN_FALHA` (com motivo), `CADASTRO_SENHA`, `LOGOUT`
    e `SESSAO_ENCERRADA` registrados no log de auditoria.
- **Pendente:** perfis e permissões (RF10.4) e pendências de segurança
  BL-014 a BL-018.
- **Evidência:** `src/main.py`, `src/views/login.py`,
  `src/services/login.py`, `src/queries/queries_login.py`,
  `src/repositories/login.py`, `src/config/settings.py` e
  `database/usuarios.sql`.
- **Próxima ação:** BL-014 (remover `.env` do Git e rotacionar segredos).
- **Critério de conclusão:** pendências de segurança resolvidas, perfis
  implementados e acesso validado em produção via HTTPS.

### RF08.1 - Log de auditoria

- **Status:** Implementado.
- **Entregue:**
  - Tabela `financiamento.log_auditoria` (usuário, data/hora, ação,
    entidade, registro, sucesso, detalhes JSON, IP), somente inserção:
    triggers bloqueiam UPDATE, DELETE e TRUNCATE.
  - `services/log.py` com `registrar_log` (na mesma transação da operação)
    e `registrar_log_falha` (transação própria, sem esconder o erro original).
  - Ações registradas: `LOGIN`, `LOGIN_FALHA`, `LOGOUT`, `SESSAO_ENCERRADA`,
    `CADASTRO_SENHA`, `CONTRATO_INCLUIR`, `CONTRATO_EXCLUIR` (com cópia do
    contrato excluído via `DELETE ... RETURNING *`), `ANTECIPACAO_INCLUIR` e
    `QUITACAO_INCLUIR`.
  - Validado em banco de desenvolvimento dentro de transação desfeita
    (sucessos, falhas de integridade e bloqueio de UPDATE/DELETE).
- **Pendente:** tela de consulta (RF08.2/BL-021), política de retenção e
  usuário de banco somente-inserção (BL-022).
- **Evidência:** `src/services/log.py`, `src/queries/queries_log.py`,
  `src/repositories/log.py`, `src/services/contracts.py`,
  `src/services/liquidacao_antecipacao.py`, `src/services/login.py` e
  `database/log_auditoria.sql`.
- **Próxima ação:** definir a tela de histórico.
- **Critério de conclusão:** histórico consultável na interface e política
  de retenção aprovada.

## Backlog rastreável

| ID | Pendência | Impacto | Depende de | Status |
| --- | --- | --- | --- | --- |
| BL-001 | Definir e implementar vínculo de bens e veículos. | Alto | Regras de chassi e placa | Aberto |
| BL-002 | Implementar registro de antecipação na interface. | Alto | Validação financeira | Concluído (UC06) |
| BL-003 | Validar cálculos SELIC e TFC com massa conhecida. | Alto | Dados de teste aprovados | Aberto |
| BL-004 | Definir e implementar liquidação total/parcial. | Alto | Modelo de dados | Concluído (consolidado em UC06 como tipo QUITACAO) |
| BL-005 | Implementar perfis e permissões por aba e ação (autenticação já entregue em UC12). | Alto | Matriz de permissões | Aberto |
| BL-006 | Implementar filtros de contratos e veículos. | Médio | Campos e critérios de busca | Aberto |
| BL-007 | Definir auditoria. | Alto | Eventos obrigatórios | Concluído (RF08.1 — `log_auditoria`) |
| BL-008 | Definir integração da Selic. | Alto | Fonte oficial | Aberto |
| BL-009 | Criar política de backup e restauração. | Alto | Infraestrutura | Aberto |
| BL-010 | Documentar a view `vw_agrupamento_projecao` no DDL versionado e definir a exportação da tela de Projeção de Pagamentos (filtros já entregues). | Médio | Acesso ao banco para extrair a definição da view | Aberto |
| BL-011 | Adicionar filtros (ano, modalidade) e download/exportação à tela de Relatórios > Endividamento. | Médio | Especificação dos filtros aprovada pelo financeiro | Aberto |
| BL-012 | Sincronizar no DDL versionado a trigger `trg_after_insert_antecipacao` (`AFTER INSERT` em `financiamento.antecipacao`, aciona `refresh_views_contratos()`) e as colunas `tipo_lancamento`/`data_compensacao`. | Médio | Acesso ao banco para extrair a definição da trigger | Concluído |
| BL-013 | Avaliar suporte, em UC06, a contratos de modalidades além de BNDES FINAME SELIC (hoje única presente em `mv_projecao_moeda`). | Médio | Definição de regra de cálculo para as demais modalidades | Aberto |
| BL-014 | **Segurança:** remover `.env` do Git (`git rm --cached` + `.gitignore`), criar `.dockerignore` (hoje `.env` e `.git` vão para a imagem), **trocar a senha do banco** (já está no histórico do repositório remoto) e gerar novo `AUTH_SECRET`. Com o `AUTH_SECRET` exposto, é possível fabricar cookie de login de qualquer usuário. | Crítico | Acesso ao banco e ao servidor Git | Aberto |
| BL-015 | **Segurança:** garantir HTTPS no proxy (`rede-proxy`) e incluir `Secure` no cookie de sessão; sem HTTPS, senha e cookie trafegam em texto puro. | Alto | Infraestrutura do proxy | Aberto |
| BL-016 | **Segurança:** limitar tentativas de login (ex.: 5 falhas em 15 min bloqueiam), usando os registros `LOGIN_FALHA` do log. | Alto | — | Aberto |
| BL-017 | **Segurança:** invalidar cookies antigos ao trocar senha, bloquear ou clicar em Sair (versão de sessão no token) e definir tempo máximo absoluto de sessão. | Médio | Coluna nova em `usuarios` | Aberto |
| BL-018 | **Segurança:** avaliar scrypt N=2^15 (135 ms, 32 MiB) com rehash no login; igualar o tempo de resposta do caso "senha não cadastrada"; avaliar bloqueio de senhas óbvias. | Baixo | — | Aberto |
| BL-019 | Sincronizar `database/ddl_financiamento.sql` com as tabelas `usuarios` e `log_auditoria`, a função `log_auditoria_imutavel` e seus triggers. | Médio | Extração do DDL do banco | Aberto |
| BL-020 | Corrigir os filtros de `views/contracts.py`: usam `value=st.session_state...`, o que descarta a primeira alteração do usuário (mesmo bug corrigido em Projeção de Pagamentos com `key` própria). | Médio | — | Aberto |
| BL-021 | Tela de consulta do histórico de operações (RF08.2) a partir de `log_auditoria`. | Médio | Perfis (acesso restrito) | Aberto |
| BL-022 | Definir retenção do log de auditoria e avaliar usuário de banco da aplicação apenas com INSERT no log (hoje `fin` é dono da tabela e poderia remover o trigger). | Médio | Administração do PostgreSQL | Aberto |
| BL-023 | Exibir mensagem clara ao tentar excluir contrato com antecipação (hoje "Erro ao excluir contrato!"; o motivo só fica no log). | Baixo | — | Aberto |

## Regra de atualização

Toda nova funcionalidade deve atualizar este documento junto com o requisito,
Use Case, matriz de rastreabilidade, testes e roadmap. Não usar apenas o termo
"parcial" sem registrar o que foi entregue, o que falta e como concluir.
