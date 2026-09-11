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
| `antecipacao` | Pagamentos antecipados | Referencia contrato |

## Views e cálculos

- `vw_controle_contratos`: resumo usado na listagem.
- `mv_projecao_moeda`: projeção para contratos BNDES FINAME SELIC.
- `mv_projecao_moeda_final`: valores de pagamento considerando Selic por data.
- `mv_projecao_tfc`: projeção para contratos BNDES FINAME TFC.

## Funções e triggers

- `próximo_dia_util`: avanca fins de semana e feriados.
- `dias_úteis_entre`: calcula dias úteis entre datas.
- `preencher_selic_contrato`: preenche Selic do contrato até a data BNDES.
- `set_data_referencia_contrato`: calcula a data de referencia.
- `processar_dados_antecipacao`: preenche Selic e valor em moeda.
- `refresh_views_contratos`: atualiza matérialized views apos inclusão de contrato.

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
Alterações no banco devem ser refletidas neste documento e, quando aplicável,
na matriz de rastreabilidade.
