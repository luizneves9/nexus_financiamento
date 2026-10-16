# Modelo de Dados PostgreSQL

## Schema

O banco utiliza o schema `financiamento`, autorizado para o usuário de banco
configurado no ambiente.

## Entidades

| Tabela | Responsabilidade | Relacionamentos principais |
| --- | --- | --- |
| `empresas` | Empresas contratantes | Referenciada por `contratos` |
| `bancos` | Instituicoes financeiras | Referenciada por `contratos` |
| `fornecedor` | Fornecedores de bens | Referenciada por `bem` |
| `contratos` | Dados do financiamento | Referencia empresa e banco |
| `bem` | Dados de bens, chassi e carroceria | Referencia fornecedor e contrato |
| `veiculos` | Associação entre bens | Referencia dois registros de `bem` |
| `selic` | Historico de Selic | Consultada por contratos e antecipações |
| `feriados` | Calendario de dias não úteis | Consultada pelos cálculos |
| `antecipacao` | Pagamentos antecipados e quitações | Referencia contrato |
| `projecao_controle` | Controle da projeção por contrato (status, motivo e data do último cálculo, contagens) | Referencia contrato (CASCADE) |
| `projecao_parcelas` | Parcelas projetadas por contrato (moeda e R$), situação ABERTA / LIQUIDADA / CANCELADA_QUITACAO | Referencia contrato (CASCADE); chave única (contrato, parcela) |
| `liquidacao` | Baixa das parcelas (valor projetado, pago e ajuste; origem manual ou ERP; estorno) | Referencia parcela e contrato (RESTRICT); só inclusão e estorno |
| `contrato_erp_vinculo` | De-para código do ERP → contrato(s) do Nexus | Referencia contrato (CASCADE); chave única (código, contrato) |
| `usuarios` | Usuários do sistema (login, hash da senha, ativo) | Referenciada por `log_auditoria` |
| `log_auditoria` | Log de auditoria das interações (somente inserção) | Referencia `usuarios`; `entidade`/`id_registro` apontam para o registro afetado sem chave estrangeira |

## Views e cálculos

- `vw_controle_contratos`: resumo usado na listagem.
- As materialized views `mv_projecao_moeda`, `mv_projecao_moeda_final` e
  `mv_projecao_tfc` e a view `vw_agrupamento_projecao` foram removidas em
  16/10/2026 (DA08); a projeção está em `projecao_parcelas`.
- Os relatórios usam a consulta `CTE_POSICAO_DATA_BASE` (aplicação), que monta
  a posição numa data base (DA10).

## Funções e triggers

- `próximo_dia_util`: avanca fins de semana e feriados.
- `dias_úteis_entre`: calcula dias úteis entre datas.
- `preencher_selic_contrato`: preenche Selic do contrato até a data BNDES.
- `set_data_referencia_contrato`: calcula a data de referencia.
- `processar_dados_antecipacao`: preenche Selic e valor em moeda.
- `calcular_projecao_contrato(id, data_base opcional)`: calcula a projeção de
  um contrato (sem gravar).
- `recalcular_projecao_contrato(id, motivo)`: grava a projeção de um contrato
  (preserva parcelas liquidadas) e atualiza o controle.
- `recalcular_projecao_selic(data)`: recalcula os contratos afetados por nova
  Selic.
- `atualizar_controle_contrato(id)`: contagens e status (ATIVO / QUITADO /
  ENCERRADO).
- Triggers `trg_projecao_contratos`, `trg_projecao_antecipacao` e
  `trg_projecao_selic_*` (recálculo automático) e `trg_liquidacao_*` (regras da
  liquidação). Definições em `database/projecao_persistida.sql`.
- `log_auditoria_imutavel`: usada pelos triggers `trg_log_auditoria_imutavel`
  (UPDATE/DELETE) e `trg_log_auditoria_sem_truncate` (TRUNCATE) para manter o
  log somente inserção.

## Integridade atual

- CNPJ e unico em empresas, bancos e fornecedores.
- O número do contrato possui unicidade conforme a restrição atual do DDL.
- Chaves estrangeiras conectam contratos, empresas, bancos, bens,
  fornecedores, veículos e antecipações.
- Não existem ainda restricoes documentadas de unicidade para placa ou chassi.

## Fonte de referência

O DDL versionado em [database/ddl_financiamento.sql](../../database/ddl_financiamento.sql)
é a fonte técnica do schema `financiamento`. As funções de projeção temporária
estão em [database/projection_functions.sql](../../database/projection_functions.sql).
As tabelas de autenticação e auditoria estão em
[database/usuarios.sql](../../database/usuarios.sql) e
[database/log_auditoria.sql](../../database/log_auditoria.sql) (ainda não
sincronizadas no DDL — BL-019).
Alterações no banco devem ser refletidas neste documento e, quando aplicável,
na matriz de rastreabilidade.
