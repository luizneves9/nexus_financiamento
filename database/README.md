# Banco de Dados

> **Não existe banco de testes.** Os scripts são executados direto na
> produção: faça backup antes e escreva testes de escrita como blocos que se
> desfazem sozinhos (ex.: `DO $$ ... RAISE EXCEPTION 'TESTE DESFEITO' $$`).

## Arquivos

| Arquivo | Finalidade |
| --- | --- |
| `ddl_financiamento.sql` | Retrato documental do schema PostgreSQL `financiamento` (tabelas, funções, triggers e views originais). Não inclui os objetos da projeção persistida. |
| `projecao_persistida.sql` | **Estado final** da projeção persistida, liquidação e vínculo ERP (DA08, DA09): tabelas `projecao_controle`, `projecao_parcelas`, `liquidacao` e `contrato_erp_vinculo`, funções de cálculo/recálculo, triggers e carga inicial. **Já aplicado na produção** em 15-16/10/2026; serve de documentação e para montar um banco novo. Não executar de novo na produção. |
| `projection_functions.sql` | Funções parametrizadas para projeção temporária durante a inclusão de contratos (DA05). |
| `usuarios.sql` | Script de criação da tabela `usuarios` (autenticação, UC12) e comandos do desenvolvedor: criar usuário, resetar senha, bloquear e conferir. Já executado. |
| `log_auditoria.sql` | Script de criação da tabela `log_auditoria`, índices, função `log_auditoria_imutavel` e triggers que bloqueiam UPDATE/DELETE/TRUNCATE (DA06), mais consultas úteis de auditoria. Executar depois de `usuarios.sql`. Já executado. |

## Finalidade

`ddl_financiamento.sql` foi gerado a partir do banco e documenta a estrutura
original. Em 16/10/2026 foram retirados dele os objetos excluídos do banco
(materialized views `mv_projecao_moeda`, `mv_projecao_moeda_final`,
`mv_projecao_tfc`, a função `refresh_views_contratos()` e os triggers
`trg_after_insert_contratos` / `trg_after_insert_antecipacao`). Os objetos
novos estão em `projecao_persistida.sql`.

`projection_functions.sql` documenta as funções de projeção da inclusão de
contratos. Unificá-las com `calcular_projecao_contrato` está no backlog
(BL-027).

## Objetos principais

- tabelas de empresas, bancos, fornecedores, contratos, bens, veículos,
  feriados, Selic e antecipações (`ddl_financiamento.sql`);
- projeção persistida: `projecao_controle`, `projecao_parcelas`,
  `calcular_projecao_contrato(id, data_base opcional)`,
  `recalcular_projecao_contrato`, `recalcular_projecao_selic`,
  `atualizar_controle_contrato` e os triggers `trg_projecao_contratos`,
  `trg_projecao_antecipacao` e `trg_projecao_selic_*`;
- liquidação: `liquidacao` e os triggers `trg_liquidacao_*` (só inclusão e
  estorno);
- vínculo ERP: `contrato_erp_vinculo`;
- views: `vw_controle_contratos` (lista de contratos).

## Uso dos arquivos

Use o DDL e o `projecao_persistida.sql` como referência para consultar a
estrutura, entender relacionamentos, localizar funções e triggers e comparar
alterações futuras. Alterações novas devem ganhar um script próprio, com
backup, testes que se desfazem sozinhos e plano de volta, e depois ser
incorporadas ao arquivo de estado final correspondente.

## Fonte de verdade

Alterações no modelo ou nos cálculos devem ser feitas no SQL versionado,
aplicadas com cuidado (não há banco de testes) e refletidas na documentação de
arquitetura.

## Pendências conhecidas

1. **Tabelas `usuarios` e `log_auditoria`** — criadas por `usuarios.sql` e
   `log_auditoria.sql`, ainda não refletidas em `ddl_financiamento.sql`. Ver
   [BL-019](../docs/requirements/status-register.md#backlog-rastreável).
2. **Limpeza final** — schema `financiamento_base` (cópias da migração e
   backup da Selic) e a view sem uso `vw_agrupamento_projecao_parcelas`. Ver
   [BL-026](../docs/requirements/status-register.md#backlog-rastreável).
