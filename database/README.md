# Banco de Dados

## Arquivos

| Arquivo | Finalidade |
| --- | --- |
| `ddl_financiamento.sql` | Retrato documental do schema PostgreSQL `financiamento` existente no banco, incluindo tabelas, funções, triggers, views e materialized views. |
| `projection_functions.sql` | Funções parametrizadas para projeção temporária durante a inclusão de contratos. |

## Finalidade

O arquivo `ddl_financiamento.sql` foi gerado a partir do banco existente e é
mantido no projeto para documentar sua estrutura atual. Ele não representa,
neste momento, uma migração ou um instalador completo do banco.

Da mesma forma, `projection_functions.sql` documenta as funções de projeção
criadas para a funcionalidade de inclusão de contratos e deve permanecer
versionado junto ao código.

## Objetos principais

O DDL contém:

- tabelas de empresas, bancos, fornecedores, contratos, bens, veículos,
  feriados, Selic e antecipações;
- funções de dias úteis, Selic, data de referência e atualização das
  projeções;
- triggers de contratos e antecipações, incluindo `trg_after_insert_contratos`
  e `trg_after_insert_antecipacao`, que acionam `refresh_views_contratos()`
  após a inclusão de contrato ou de antecipação/quitação, respectivamente;
- view `vw_controle_contratos`;
- materialized views:
  - `mv_projecao_moeda`: base de cálculo com suporte a antecipações (ANTECIPACAO/QUITACAO), filtragem de quitação via CTE `parcela_quitada`.
  - `mv_projecao_moeda_final`: aplicação de Selic por dia de vencimento e cálculo de parcela H.
  - `mv_projecao_tfc`: cálculo TFC com dias corridos.

## Uso do arquivo

Use o DDL como referência para:

- consultar a estrutura existente;
- entender tabelas e relacionamentos;
- localizar funções, triggers, views e materialized views;
- comparar alterações futuras no banco;
- atualizar a documentação de arquitetura.

Não execute o DDL diretamente em produção. Caso futuramente seja necessário
recriar o banco ou aplicar uma alteração, deverão ser criados scripts de
implantação ou migração próprios, com ordem de dependências, testes, backup e
plano de rollback.

## Fonte de verdade

Alterações no modelo ou nos cálculos devem ser feitas no SQL versionado,
testadas em banco de desenvolvimento e refletidas na documentação de
arquitetura.

## Pendências conhecidas

1. **View `vw_agrupamento_projecao`** — Usada pelas telas:
   - **Relatórios > Projeção de Pagamentos** (`src/queries/queries_projection.py`)
   - **Relatórios > Endividamento** (`src/queries/queries_relatorio_endividamento.py`)
   
   A view ainda não está documentada em `ddl_financiamento.sql`. Assim que a 
   definição da view for extraída do banco, ela deve ser incluída no DDL e no
   [Dicionário de Dados](../docs/architecture/data-dictionary.md). Ver
   [BL-010](../docs/requirements/status-register.md#backlog-rastreável).

