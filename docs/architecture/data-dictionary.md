# Dicionario de Dados

Este documento resume os campos principais do schema `financiamento`. O DDL
continua sendo a fonte normativa para tipos, nulidade, indices e restricoes.

## Contratos

| Campo | Significado |
| --- | --- |
| `id` | Identificador do contrato. |
| `id_empresa` | Empresa relacionada. |
| `id_banco` | Banco relacionado. |
| `número_contrato` | Numero informado no contrato. |
| `data_emissão` | Data de emissão. |
| `data_bndes` | Data usada para localizar Selic. |
| `selic` | Taxa preenchida pelo trigger quando nula. |
| `tipo_contrato` | Tipo de cálculo, como SELIC ou TFC. |
| `valor_financiado` | Valor principal financiado. |
| `pos_fixado` | Indicador/modalidade pos-fixada. |
| `taxa_juros_efetiva` | Taxa efetiva usada na projeção. |
| `prazo_total` | Prazo total informado. |
| `prazo_carencia` | Prazo de carência. |
| `prazo_final` | Prazo de amortização final. |
| `data_referencia` | Data calculada pelo trigger. |
| `carencia_pagamento` | Quantidade de pagamentos durante carência. |
| `registro_cobrança` | Regra de registro da cobrança. |

## Antecipação

| Campo | Significado |
| --- | --- |
| `id_contrato` | Contrato da antecipação. |
| `data_pagamento` | Data do pagamento. |
| `data_tesouraria` | Data usada para localizar Selic. |
| `selic` | Taxa aplicada a antecipação. |
| `valor_pago` | Valor financeiro pago. |
| `valor_moeda` | Valor calculado pela taxa aplicável. |

## Bem e veiculo

`bem` armazena fornecedor, contrato, descricao, marca, modelo, anos, placa,
chassi e valor de venda. `veiculos` associa um bem de chassi e um bem de
carroceria.

## Tabelas auxiliares

- `selic`: data e valor da taxa.
- `feriados`: data e descricao do feriado.
- `empresas`, `bancos` e `fornecedor`: CNPJ e razao social.

## Convenções

Campos financeiros utilizam tipos numericos do PostgreSQL. Datas são
armazenadas como `daté`. Regras de nulidade e unicidade devem ser consultadas
no DDL vigente antes de qualquer integração.
