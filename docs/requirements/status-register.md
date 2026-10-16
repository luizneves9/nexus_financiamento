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
| UC04 | Exclusão física | Implementado | DELETE com confirmação, log e mensagem clara quando há liquidação, antecipação ou quitação. | Avaliar exclusão lógica. |
| UC05 | Bens e veículos | Banco preparado | Tabelas e relacionamentos existem, mas não ha interface nem regras completas. | Implementar telas, validações e regras de chassi/placa. |
| UC06 | Quitação/Antecipação | Implementado (BNDES FINAME SELIC) | Tela única de antecipação e quitação, com cálculo de saldo devedor/Selic pré-confirmação, exclusão de lançamento e recálculo automático do contrato. Não suporta outras modalidades. | Validar cálculo com o financeiro e avaliar suporte a outras modalidades. |
| UC07 | Liquidação de parcelas | Implementado | Tela Liquidação: liquidação manual (ajuste gravado) e estorno, com log; parcela liquidada imutável. | Perfis para liquidar/estornar (BL-005). |
| UC08 | Atualização da Selic | Implementado | Importação sob demanda da série do BNDES (só datas novas), com recálculo e log; tabela recarregada da fonte oficial em 16/10/2026. | Agendar a importação e confirmar acesso do servidor (BL-030). |
| UC09 | Relatório Contas a Pagar | Implementado | Posição na data base (pago × projetado, Selic da data base), antecipações/quitações, filtros e exportação Excel. | Validar com o financeiro. |
| UC10 | Relatório de endividamento | Implementado | Fluxo de caixa na posição da data base, filtros (data base, mês de corte, empresa, banco), meses liquidados destacados e Sub Total. | Exportação e demais modalidades (fora do Nexus). |
| UC11 | Consulta de antecipações | Implementado | Aba Antecipação lista todas as antecipações/quitações com filtros no banco e resumo. | Validar com o financeiro. |
| UC13 | Conciliação com o ERP | Implementado | Importação do CSV do ERP com tabela temporária, prévia por situação, vínculos ERP → Nexus (inclusive grupos com rateio) e liquidação com ajuste. | Antecipações no CSV (BL-028) e tela de vínculos (BL-029). |
| UC14 | Detalhe do contrato e anexos | Implementado | Detalhe em abas (Dados, Contrato, Ficha Financeira, Histórico) com PDFs no banco, visualização na tela, anexar/baixar/excluir e log; anexos também na inclusão do contrato. | Acrescentar novas abas conforme evolução. |
| UC15 | Painel de indicadores | Implementado | Painel > Indicadores com saldo devedor, fluxo de pagamentos, juros, contratado e taxa média comparados ao ano anterior, fluxo mensal e composição por empresa/banco/tipo. | Validar com o financeiro (BL-031). |
| UC12 | Autenticação de usuário | Implementado | Login, primeiro acesso com cadastro de senha (hash scrypt), sessão de 30 min e Sair; eventos registrados no log. Perfis ainda não existem. | Resolver pendências de segurança BL-014 a BL-018. |
| RF03.1 | Filtros de contratos | Parcial | Empresa, banco, contrato e "Somente sem anexos" (padrão `key=`, BL-020 resolvido). | Definir demais filtros (taxa, período, valor, tipo). |
| RF08 | Auditoria | Parcial | Log de auditoria grava todas as escritas e eventos de acesso (RF08.1); não há tela de consulta (RF08.2). | Definir a tela de histórico (BL-021). |
| RF10 | Autenticação e perfis | Parcial | Autenticação implementada (UC12); perfis e permissões por aba/ação não existem. | Definir matriz de perfis e permissões (BL-005). |
| RNF07 | Logs e observabilidade | Parcial | Existem mensagens de erro, mas ha exceções silenciosas e falta padrão de logs. | Definir política de logs e substituir tratamentos silenciosos. |
| RNF11 | Backup e restauração | Planejado | Não ha procedimento operacional aprovado. | Definir RTO, RPO, retenção e teste de restauração. |
| RNF15 | Identidade visual | Implementado | Mesma identidade do Nexus Extrato (DA07): logo, destaque índigo, cabeçalho padrão, menu com ícones e rodapé fixo; testado no Streamlit 1.63.0 local. | Confirmar a versão do Streamlit na imagem `fin-base:1.0` (BL-025). |

## Detalhamento por Use Case

### UC01 - Inclusão de contratos

- **Status:** Parcial.
- **Entregue:** formulario web, validação de campos, validação de valores e
  datas, persistência em `financiamento.contratos` e mensagem de resultado.
  Taxa de juros efetiva com até 6 casas decimais na tela.
- **Pendente:** vínculo de bens e veículos e autenticação; ampliar a precisão
  de `contratos.taxa_juros_efetiva` para 6 casas (`BL-024`).
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
  - Filtros parametrizados: Empresa e Banco por seleção entre os cadastros
    (opção **Todos**; comparação exata pela razão social, mesmo padrão em
    Antecipação, Liquidação, Contas a Pagar e Endividamento) e Contrato
    (busca ILIKE, parcial).
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

### UC06 - Quitação/Antecipação de contrato

- **Status:** Implementado para contratos BNDES FINAME SELIC.
- **Entregue:** botão **Quitação/Antecipação** em Contratos (um contrato
  selecionado); modal único `modal_quitacao_antecipacao.py` para antecipação e
  quitação (`tipo_lancamento`); cálculo do saldo devedor pela parcela mais
  próxima em `projecao_parcelas` e pela Selic da data; validações RN13 e RN14;
  exclusão de lançamento na tela Antecipação (log `ANTECIPACAO_EXCLUIR`); o
  trigger `trg_projecao_antecipacao` recalcula só o contrato (DA08).
- **Pendente:** outras modalidades; validar o cálculo com o financeiro.
- **Evidência:** `src/views/contracts.py`,
  `src/views/components/modal_quitacao_antecipacao.py`,
  `src/services/quitacao_antecipacao.py`, `src/views/include_antecipation.py`,
  `src/views/components/modal_antecipacao_excluir.py`,
  `src/queries/queries_antecipacao.py`, `database/projecao_persistida.sql`.
- **Próxima ação:** avaliar suporte a outras modalidades (BL-013).
- **Critério de conclusão:** cálculo validado pelo financeiro.

### UC07 - Liquidação de parcelas

- **Status:** Implementado.
- **Entregue:** tela **Operacional > Liquidação** (filtros no mês atual,
  prefixo `fl_`); liquidação manual de uma ou mais parcelas abertas (data e
  valor pago, ajuste calculado pelo banco); estorno com motivo; tabela
  `liquidacao` com regras no banco (só estorno; exclusão e TRUNCATE
  bloqueados); log `LIQUIDACAO_INCLUIR` / `LIQUIDACAO_ESTORNAR`.
- **Pendente:** perfis para liquidar/estornar (BL-005).
- **Evidência:** `src/views/liquidacao.py`,
  `src/views/components/modal_liquidacao_manual.py`,
  `src/views/components/modal_liquidacao_estornar.py`,
  `src/services/liquidacao.py`, `src/queries/queries_liquidacao.py`,
  `database/projecao_persistida.sql`.
- **Próxima ação:** validar o uso com o financeiro.
- **Critério de conclusão:** processo mensal de baixa validado.

### UC08 - Atualização da Selic

- **Status:** Implementado (importação sob demanda).
- **Entregue:** tela **Cadastros > Selic** com a lista do que está gravado e o
  botão **Atualizar Selic (BNDES)** (série UM143; só datas posteriores à
  última; um único INSERT; recálculo uma vez por importação; log
  `SELIC_IMPORTAR`). Em 16/10/2026 a tabela foi recarregada da fonte oficial
  (as cargas manuais tinham dia e mês trocados).
- **Pendente:** agendamento automático e confirmação do acesso do servidor de
  produção ao site do BNDES (BL-030).
- **Evidência:** `src/views/selic.py`, `src/services/selic.py`,
  `src/queries/queries_selic.py`, `docs/architecture/integrations.md`.
- **Próxima ação:** testar a importação no servidor de produção.
- **Critério de conclusão:** importação recorrente sem intervenção.

### UC09 - Relatório Contas a Pagar

- **Status:** Implementado.
- **Entregue:** página **Relatórios > Contas a Pagar** (antes "Projeção de
  Pagamentos") com a posição na data base (RN24): liquidado pelo valor pago,
  projetado na Selic da data base, antecipações e quitações até a data base;
  filtros (data base hoje, vencimento no mês atual, empresa, banco, contrato,
  situação; prefixo `fcp_`); resumo por situação; exportação Excel (CSV sem
  `openpyxl`).
- **Pendente:** validação com o financeiro.
- **Evidência:** `src/views/relatorio_contas_a_pagar.py`,
  `src/services/relatorio_contas_a_pagar.py`,
  `src/queries/queries_contas_a_pagar.py` (`CTE_POSICAO_DATA_BASE`).
- **Próxima ação:** validar com o financeiro.
- **Critério de conclusão:** posições conferidas com o controle do financeiro.

### UC10 - Relatório de endividamento

- **Status:** Implementado.
- **Entregue:** fluxo de caixa (ano × mês, milhões) na posição da data base
  (mesma regra do UC09); filtros data base, vencimentos a partir do mês
  (01/01/2026), empresa e banco (prefixo `fe_`); meses com parcelas liquidadas
  na cor do cabeçalho; bloco Sub Total (Financiamentos e Total Geral) com
  total pago e total a pagar; temas automático/claro/escuro.
- **Pendente:** exportação; modalidades fora do Nexus (consórcios,
  tributário, Compra Santo Anjo).
- **Evidência:** `src/views/relatorio_endividamento.py`,
  `src/services/relatorio_endividamento.py`,
  `src/queries/queries_relatorio_endividamento.py`.
- **Próxima ação:** validar com o financeiro.
- **Critério de conclusão:** posição conferida com a planilha do financeiro.

### UC13 - Conciliação com o ERP

- **Status:** Implementado.
- **Entregue:** **Importar ERP** na tela Liquidação: leitura e validação do
  CSV em memória, tabela temporária por operação (DA09), prévia com as
  situações da conciliação (RN22), vínculos permanentes ERP → Nexus montados
  em lista, inclusive grupos com rateio proporcional (RN23), e confirmação
  com a conciliação refeita na mesma transação; log `CONCILIACAO_ERP` por
  lote e `VINCULO_ERP_*` por vínculo.
- **Pendente:** antecipações/quitações vindas no CSV (BL-028); tela de
  cadastro de vínculos (BL-029).
- **Evidência:** `src/views/components/modal_liquidacao_importar.py`,
  `src/services/liquidacao.py`, `src/queries/queries_liquidacao.py`.
- **Próxima ação:** usar no fechamento mensal e coletar ajustes.
- **Critério de conclusão:** conciliação mensal feita sem planilha paralela.

### UC14 - Detalhe do contrato e anexos

- **Status:** Implementado.
- **Entregue:** botão **Detalhes** em Contratos com o modal em abas (Dados,
  Contrato, Ficha Financeira, Histórico); PDFs em `anexo_contrato` e
  `anexo_ficha_financeira` (vários por contrato, até 20 MB, sem repetir o
  mesmo arquivo); visualização na tela (visualizador do navegador montado na
  página principal, pois Chrome/Edge bloqueiam PDF em iframes isolados) e
  "Abrir em nova aba"; anexar, baixar e excluir com log `ANEXO_INCLUIR` /
  `ANEXO_EXCLUIR`; colunas e filtro "Somente sem anexos" na lista.
- **Pendente:** novas abas (ex.: Projeção) conforme evolução; confirmar a
  versão do Streamlit na imagem de produção (BL-025).
- **Evidência:** `src/views/components/modal_contracts_detalhe.py`,
  `src/views/components/visualizador_pdf.py`, `src/services/anexos.py`,
  `src/queries/queries_anexos.py`, `database/contrato_anexos.sql`.
- **Próxima ação:** anexar os documentos dos contratos existentes.
- **Critério de conclusão:** todos os contratos com contrato e ficha
  anexados.

### UC11 - Consulta de antecipações

- **Status:** Implementado.
- **Entregue:**
  - Aba Operacional > **Antecipação** (antes um placeholder "em
    desenvolvimento") lista todas as antecipações e quitações de
    `financiamento.antecipacao`, com empresa e banco (razão social) e número
    do contrato obtidos por join com `contratos`, `empresas` e `bancos`.
  - Colunas: `id`, `nome_empresa`, `banco`, `numero_contrato`,
    `data_pagamento`, `valor_pago`, `tipo_lancamento`.
  - Filtros por Empresa e Banco (seleção entre os cadastros, com **Todos**),
    Contrato (busca parcial) e intervalo de Data de Pagamento (padrão: mês
    atual), aplicados no banco; `session_state` exclusivo (prefixo `fa_`).
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

### UC15 - Painel de indicadores

- **Status:** Implementado.
- **Entregue:** grupo **Painel** no topo do menu com a tela Indicadores;
  filtros data base (hoje), período (início do ano até hoje), empresa e banco
  (prefixo `fi_`); cinco cartões comparados ao mesmo período do ano anterior
  (saldo devedor, fluxo de pagamentos, juros no período, contratado no
  período, taxa média ponderada); gráfico do fluxo de pagamentos por mês
  (ano atual × anterior) e composição do fluxo por empresa, banco ou tipo de
  contrato. Fluxo do período conferido com Contas a Pagar (mesmo valor).
- **Pendente:** validação dos indicadores pelo financeiro; enquanto as
  liquidações de 03/2026 em diante não forem importadas do ERP, o fluxo desses
  meses usa o valor projetado.
- **Evidência:** `src/views/indicadores.py`, `src/services/indicadores.py`,
  `src/queries/queries_indicadores.py`, `src/main.py`.
- **Próxima ação:** validar com o financeiro (BL-031).
- **Critério de conclusão:** indicadores conferidos com os controles do
  financeiro.

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
| BL-004 | Definir e implementar liquidação total/parcial. | Alto | Modelo de dados | Concluído (quitação no UC06; liquidação de parcelas no UC07) |
| BL-005 | Implementar perfis e permissões por aba e ação (autenticação já entregue em UC12). | Alto | Matriz de permissões | Aberto |
| BL-006 | Implementar filtros de contratos e veículos. | Médio | Campos e critérios de busca | Aberto |
| BL-007 | Definir auditoria. | Alto | Eventos obrigatórios | Concluído (RF08.1 — `log_auditoria`) |
| BL-008 | Definir integração da Selic. | Alto | Fonte oficial | Concluído (BNDES UM143, UC08) |
| BL-009 | Criar política de backup e restauração. | Alto | Infraestrutura | Aberto |
| BL-010 | Documentar a view `vw_agrupamento_projecao` no DDL versionado e definir a exportação da tela de Projeção de Pagamentos (filtros já entregues). | Médio | Acesso ao banco para extrair a definição da view | Concluído (view removida; Contas a Pagar com exportação) |
| BL-011 | Adicionar filtros (ano, modalidade) e download/exportação à tela de Relatórios > Endividamento. | Médio | Especificação dos filtros aprovada pelo financeiro | Parcial (filtros entregues; exportação pendente) |
| BL-012 | Sincronizar no DDL versionado a trigger `trg_after_insert_antecipacao` (`AFTER INSERT` em `financiamento.antecipacao`, aciona `refresh_views_contratos()`) e as colunas `tipo_lancamento`/`data_compensacao`. | Médio | Acesso ao banco para extrair a definição da trigger | Concluído |
| BL-013 | Avaliar suporte, em UC06, a contratos de modalidades além de BNDES FINAME SELIC (hoje o cálculo de saldo devedor só atende essa modalidade). | Médio | Definição de regra de cálculo para as demais modalidades | Aberto |
| BL-014 | **Segurança:** remover `.env` do Git (`git rm --cached` + `.gitignore`), criar `.dockerignore` (hoje `.env` e `.git` vão para a imagem), **trocar a senha do banco** (já está no histórico do repositório remoto) e gerar novo `AUTH_SECRET`. Com o `AUTH_SECRET` exposto, é possível fabricar cookie de login de qualquer usuário. | Crítico | Acesso ao banco e ao servidor Git | Aberto |
| BL-015 | **Segurança:** garantir HTTPS no proxy (`rede-proxy`) e incluir `Secure` no cookie de sessão; sem HTTPS, senha e cookie trafegam em texto puro. | Alto | Infraestrutura do proxy | Aberto |
| BL-016 | **Segurança:** limitar tentativas de login (ex.: 5 falhas em 15 min bloqueiam), usando os registros `LOGIN_FALHA` do log. | Alto | — | Aberto |
| BL-017 | **Segurança:** invalidar cookies antigos ao trocar senha, bloquear ou clicar em Sair (versão de sessão no token) e definir tempo máximo absoluto de sessão. | Médio | Coluna nova em `usuarios` | Aberto |
| BL-018 | **Segurança:** avaliar scrypt N=2^15 (135 ms, 32 MiB) com rehash no login; igualar o tempo de resposta do caso "senha não cadastrada"; avaliar bloqueio de senhas óbvias. | Baixo | — | Aberto |
| BL-019 | Sincronizar `database/ddl_financiamento.sql` com as tabelas `usuarios` e `log_auditoria`, a função `log_auditoria_imutavel` e seus triggers (os objetos da projeção persistida estão em `database/projecao_persistida.sql`). | Médio | Extração do DDL do banco | Aberto |
| BL-020 | Corrigir os filtros de `views/contracts.py`: usam `value=st.session_state...`, o que descarta a primeira alteração do usuário (mesmo bug corrigido em Projeção de Pagamentos com `key` própria). | Médio | — | Concluído (UC14) |
| BL-021 | Tela de consulta do histórico de operações (RF08.2) a partir de `log_auditoria`. | Médio | Perfis (acesso restrito) | Aberto |
| BL-022 | Definir retenção do log de auditoria e avaliar usuário de banco da aplicação apenas com INSERT no log (hoje `fin` é dono da tabela e poderia remover o trigger). | Médio | Administração do PostgreSQL | Aberto |
| BL-023 | Exibir mensagem clara ao tentar excluir contrato com antecipação (hoje "Erro ao excluir contrato!"; o motivo só fica no log). | Baixo | — | Concluído (UC04) |
| BL-024 | Ampliar `financiamento.contratos.taxa_juros_efetiva` de `numeric(10, 5)` para 6 casas decimais (script versionado em `database/` + DDL), alinhando a gravação com a tela e a projeção temporária, que já usam 6 casas. Verificar views dependentes antes do `ALTER COLUMN TYPE` (as MVs foram removidas). | Médio | Acesso ao banco de desenvolvimento | Aberto |
| BL-025 | Confirmar que a imagem `fin-base:1.0` tem Streamlit 1.63.0 (o CSS da identidade visual, DA07, depende da estrutura interna dessa versão); se não tiver, atualizar a imagem base ou fixar `streamlit==1.63.0`. | Médio | Acesso ao servidor Docker | Aberto |
| BL-026 | Limpeza final no banco: remover o schema `financiamento_base` (cópias da migração e backup da Selic) e a view sem uso `vw_agrupamento_projecao_parcelas`; avaliar remoção das liquidações de teste estornadas. | Baixo | Aprovação | Aberto |
| BL-027 | Corrigir os bugs herdados das MVs na projeção: TFC ignora antecipação/quitação; SELIC considera uma única antecipação por contrato; parcela do mesmo dia da quitação é cancelada; unificar `projetar_contrato_*` (prévia da inclusão) com `calcular_projecao_contrato`. | Médio | Validação do financeiro | Aberto |
| BL-028 | Tratar antecipações e quitações que venham no CSV do ERP (hoje entram na soma da chave e aparecem como Diferença). | Médio | Regra para identificá-las no relatório | Aberto |
| BL-029 | Tela de cadastro dos vínculos ERP → Nexus (listar, buscar, incluir, remover) fora da importação. | Baixo | — | Aberto |
| BL-031 | Validar com o financeiro os indicadores do Painel (UC15): definição de saldo devedor (só parcelas a vencer), fluxo de pagamentos e comparação com o ano anterior. | Médio | Disponibilidade do financeiro | Aberto |
| BL-030 | Agendar a importação da Selic e confirmar o acesso do servidor de produção a `www.bndes.gov.br`. | Médio | Infraestrutura | Aberto |

## Regra de atualização

Toda nova funcionalidade deve atualizar este documento junto com o requisito,
Use Case, matriz de rastreabilidade, testes e roadmap. Não usar apenas o termo
"parcial" sem registrar o que foi entregue, o que falta e como concluir.
