# Banco de Dados

> **Não existe banco de testes.** Os scripts são executados direto na
> produção: faça backup antes e escreva testes de escrita como blocos que se
> desfazem sozinhos (ex.: `DO $$ ... RAISE EXCEPTION 'TESTE DESFEITO' $$`).

## Arquivos

| Arquivo | Finalidade |
| --- | --- |
| `ddl_financiamento.sql` | Retrato documental do schema PostgreSQL `financiamento` (tabelas, funções, triggers e views originais). Não inclui os objetos da projeção persistida. |
| `projecao_persistida.sql` | **Estado final** da projeção persistida, liquidação e vínculo ERP (DA08, DA09): tabelas `projecao_controle`, `projecao_parcelas`, `liquidacao` e `contrato_erp_vinculo`, funções de cálculo/recálculo, triggers e carga inicial. **Já aplicado na produção** em 15-16/10/2026; serve de documentação e para montar um banco novo. Não executar de novo na produção. |
| `contrato_anexos.sql` | Tabelas `anexo_contrato` e `anexo_ficha_financeira` (PDFs dos contratos, DA12). Já executado em 16/10/2026. |
| `consorcio_outros_pagamentos.sql` | Tabelas `consorcio_pago`, `consorcio_a_pagar`, `consorcio_credito` e `outros_pagamentos` (modalidades do Endividamento fora da projeção, DA14; UC16 e UC17). Já executado (a coluna `consorcio_a_pagar.nome_consorciado` foi incluída depois, em 06/11/2026). |
| `data_contabilizacao.sql` | Coluna `contratos.data_contabilizacao` (preenchida com a emissão, `NOT NULL`, ≥ emissão) e trigger `trg_projecao_contratos` restrito às colunas do cálculo (DA13). Já executado em 09/11/2026, inclusive a etapa 2 (`NOT NULL`). |
| `projection_functions.sql` | Funções parametrizadas para projeção temporária durante a inclusão de contratos (DA05). |
| `usuarios.sql` | Script de criação da tabela `usuarios` (autenticação, UC12). Já executado. **Substituída** pelo cadastro único `nexus.usuarios` (ver `usuarios_nexus.sql`); mantida para consulta do log antigo e volta atrás. |
| `usuarios_nexus.sql` | Troca do login para o cadastro único do portal (`nexus.usuarios` + `nexus.usuario_modulos`, `nexus_portal/database/01_nexus.sql`): copia a senha de quem ainda não tinha no `nexus` e troca a FK de `log_auditoria.id_usuario` para `nexus.usuarios(id)` com `NOT VALID` (logs anteriores guardam o id de `financiamento.usuarios`). Executar uma única vez com o container parado, junto com o código novo do login. |
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
- anexos: `anexo_contrato` e `anexo_ficha_financeira` (`contrato_anexos.sql`);
- consórcio e outros pagamentos: `consorcio_pago`, `consorcio_a_pagar`,
  `consorcio_credito` e `outros_pagamentos` (`consorcio_outros_pagamentos.sql`);
- `contratos.data_contabilizacao` e o trigger `trg_projecao_contratos`
  restrito (`data_contabilizacao.sql`; o estado final do trigger também está em
  `projecao_persistida.sql`);
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

1. **Tabelas `usuarios`, `log_auditoria`, de consórcio e outros pagamentos e
   a coluna `contratos.data_contabilizacao`** — criadas por `usuarios.sql`,
   `log_auditoria.sql`, `consorcio_outros_pagamentos.sql` e
   `data_contabilizacao.sql`, ainda não refletidas em `ddl_financiamento.sql`. Ver
   [BL-019](../docs/requirements/status-register.md#backlog-rastreável).
2. **Limpeza final** — schema `financiamento_base` (cópias da migração e
   backup da Selic) e a view sem uso `vw_agrupamento_projecao_parcelas`. Ver
   [BL-026](../docs/requirements/status-register.md#backlog-rastreável).
