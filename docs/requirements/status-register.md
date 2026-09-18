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
| UC02 | Consulta de contratos | Implementado | Listagem pela view existe. Filtros e tratamento de erro completo ainda faltam. | Validar filtros e tratamento de erros. |
| UC03 | Visualização de projeção | Parcial | Consulta e cálculos estão corretos; validação específica do impacto de antecipações ainda falta. | Validar antecipações. |
| UC04 | Exclusão física | Implementado | DELETE e confirmação existem, mas dependências e auditoria limitam o fluxo. | Documentar procedimento de dependências e validar comportamento. |
| UC05 | Bens e veículos | Banco preparado | Tabelas e relacionamentos existem, mas não ha interface nem regras completas. | Implementar telas, validações e regras de chassi/placa. |
| UC06 | Antecipação | Parcialmente implementado | Banco completo com tipo_lancamento (ANTECIPACAO/QUITACAO) e projeção atualizada para truncar em quitação. Falta tela de registro. | Implementar fluxo UI de antecipação. |
| UC07 | Liquidação | Planejado | Não existe fluxo de interface nem modelo funcional fechado para liquidação. | Definir modelo e implementar registro total/parcial. |
| UC08 | Atualização da Selic | Banco preparado | Tabela e consultas existem, mas não ha importação por API ou job. | Definir fonte e implementar integração idempotente. |
| UC09 | Relatório de projeção de pagamentos | Implementado | Tela consolidada com a view `vw_agrupamento_projecao` existe, mas sem filtros, exportação nem a view documentada no DDL. | Adicionar filtros/exportação e documentar a view no DDL versionado. |
| UC10 | Relatório de endividamento | Implementado | Tela de fluxo de caixa com agrupamento por ano/mês, tema automático e botões de alternância. View ainda não documentada no DDL. | Documentar `vw_agrupamento_projecao` no DDL e adicionar filtros/download. |
| RF03.1 | Filtros de contratos | Planejado | Tela atual lista registros, mas não possui filtros funcionais. | Definir componentes e testes dos filtros. |
| RF08 | Auditoria | Planejado | Não existe histórico de alterações ou operações. | Definir modelo de auditoria e eventos obrigatórios. |
| RF10 | Autenticação e perfis | Planejado | Aplicação ainda não controla identidade ou permissões. | Definir perfis e implementar autenticação. |
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
- **Entregue:** listagem da view `financiamento.vw_controle_contratos` e
  seleção de registro.
- **Pendente:** filtros de negócio, tratamento de erro padronizado e validação
  de desempenho.
- **Evidência:** `src/views/contracts.py`, `src/services/contracts.py` e
  `src/queries/queries_gerais.py`.
- **Próxima ação:** implementar filtros e registrar cenários de consulta.
- **Critério de conclusão:** filtros aprovados, testes executados e falhas
  apresentadas sem ocultação.

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

### UC06 - Registro de antecipação

- **Status:** Banco preparado.
- **Entregue:** tabela `antecipacao` e trigger
  `processar_dados_antecipacao`.
- **Pendente:** tela, service, repository, query, confirmação e atualização
  verificável da projeção.
- **Evidência:** DDL, `src/views/include_antecipation.py` e
  `docs/architecture/financial-calculation.md`.
- **Próxima ação:** substituir o placeholder da tela e testar o trigger.
- **Critério de conclusão:** registro completo pela interface, resultado
  financeiro validado e fluxo de erro coberto.

### UC07 - Liquidação de contrato

- **Status:** Planejado.
- **Entregue:** conceito funcional documentado.
- **Pendente:** modelo de dados, regras de liquidação, interface, persistência,
  recálculo, testes e permissão.
- **Evidência:** `docs/use_cases/UC07-liquidacao-de-contrato.md`.
- **Próxima ação:** definir se liquidação usará `antecipacao` ou estrutura
  própria e aprovar as regras com o financeiro.
- **Critério de conclusão:** liquidação total e parcial registradas, saldo
  recalculado e testes aprovados.

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
- **Entregue:** página "Projeção de Pagamentos" no menu Relatórios,
  consultando a view `financiamento.vw_agrupamento_projecao` em uma tabela
  somente leitura, sem botões.
- **Pendente:** filtros, exportação/download (previstos no roadmap para a
  tela consolidada de projeções) e documentação da view no DDL versionado.
- **Evidência:** `src/views/relatorio_projecao_pagamentos.py`,
  `src/services/relatorio_projecao_pagamentos.py` e
  `src/queries/queries_projection.py`.
- **Próxima ação:** documentar `vw_agrupamento_projecao` em
  `database/ddl_financiamento.sql` e definir os filtros da tela consolidada.
- **Critério de conclusão:** view documentada no DDL, filtros e exportação
  implementados, e conteúdo validado pelo financeiro.

### UC06 - Registro de antecipação

- **Status:** Parcialmente implementado (banco 100%, interface 0%).
- **Entregue:** 
  - Tabela `financiamento.antecipacao` com colunas: `tipo_lancamento` (ANTECIPACAO/QUITACAO), `data_pagamento`, `selic`, `valor_pago`, `valor_moeda`.
  - View `mv_projecao_moeda` detecta e filtra quitações: CTE `parcela_quitada` trunca projeção na parcela de quitação.
  - Query `SELECT_PROJECAO` (UC03) traz antecipações em bloco separado com tipo e valor.
  - Suporte completo a múltiplas antecipações parciais e uma quitação final.
- **Pendente:** Tela de registro de antecipação na aplicação; interface de listagem e edição de antecipações.
- **Evidência:** 
  - Banco: `financiamento.antecipacao`, triggers, `mv_projecao_moeda`, `mv_projecao_moeda_final`.
  - Código: `src/queries/queries_contracts.py` (CTE `valores_antecipacao`).
  - Documentação: `docs/architecture/financial-calculation.md` (seção Antecipação e Tratamento de Quitação).
- **Próxima ação:** Implementar tela em `src/views/` para registro/listagem de antecipações com seleção de tipo (ANTECIPACAO/QUITACAO).
- **Critério de conclusão:** Tela funcional, registro em banco confirmado, projeção recalculada corretamente após registro, testes de quitação executados.

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

## Backlog rastreável

| ID | Pendência | Impacto | Depende de | Status |
| --- | --- | --- | --- | --- |
| BL-001 | Definir e implementar vínculo de bens e veículos. | Alto | Regras de chassi e placa | Aberto |
| BL-002 | Implementar registro de antecipação na interface. | Alto | Validação financeira | Aberto |
| BL-003 | Validar cálculos SELIC e TFC com massa conhecida. | Alto | Dados de teste aprovados | Aberto |
| BL-004 | Definir e implementar liquidação total/parcial. | Alto | Modelo de dados | Aberto |
| BL-005 | Implementar autenticação e perfis. | Alto | Matriz de permissões | Aberto |
| BL-006 | Implementar filtros de contratos e veículos. | Médio | Campos e critérios de busca | Aberto |
| BL-007 | Definir auditoria. | Alto | Eventos obrigatórios | Aberto |
| BL-008 | Definir integração da Selic. | Alto | Fonte oficial | Aberto |
| BL-009 | Criar política de backup e restauração. | Alto | Infraestrutura | Aberto |
| BL-010 | Documentar a view `vw_agrupamento_projecao` no DDL versionado e definir filtros/exportação da tela de Projeção de Pagamentos. | Médio | Acesso ao banco para extrair a definição da view | Aberto |
| BL-011 | Adicionar filtros (ano, modalidade) e download/exportação à tela de Relatórios > Endividamento. | Médio | Especificação dos filtros aprovada pelo financeiro | Aberto |

## Regra de atualização

Toda nova funcionalidade deve atualizar este documento junto com o requisito,
Use Case, matriz de rastreabilidade, testes e roadmap. Não usar apenas o termo
"parcial" sem registrar o que foi entregue, o que falta e como concluir.
