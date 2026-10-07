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
| `taxa_juros_efetiva` | Taxa efetiva usada na projeção, em % (`numeric(10, 5)`; a tela aceita 6 casas decimais, ver `BL-024`). |
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
| `data_pagamento` | Data do pagamento antecipado. |
| `data_tesouraria` | Data usada para localizar Selic. |
| `selic` | Taxa Selic aplicada a antecipação. |
| `valor_pago` | Valor financeiro pago. |
| `valor_moeda` | Valor calculado pela taxa Selic aplicável. |
| `tipo_lancamento` | Classificação do lançamento: 'ANTECIPACAO' (pagamento parcial) ou 'QUITACAO' (liquidação total do contrato). |

## Usuários

| Campo | Significado |
| --- | --- |
| `id` | Identificador do usuário. |
| `usuario` | Login (único), criado pelo desenvolvedor. |
| `senha_hash` | Hash `scrypt$n$r$p$salt$hash` da senha; `NULL` até o primeiro acesso (ou após reset). |
| `ativo` | `false` bloqueia login e derruba sessões abertas. |
| `criado_em` | Data/hora de criação do usuário. |
| `senha_definida_em` | Data/hora do cadastro da senha. |

## Log de auditoria

| Campo | Significado |
| --- | --- |
| `id` | Sequencial do registro (bigint). |
| `data_hora` | Data/hora da ação, com fuso horário. |
| `id_usuario` | Usuário autenticado; `NULL` em falha de login de usuário inexistente. |
| `usuario` | Nome do usuário no momento da ação (ou o nome digitado na falha de login). |
| `acao` | Ação do catálogo (DA06), ex.: `LOGIN`, `CONTRATO_EXCLUIR`. |
| `entidade` | Tabela afetada (`contratos`, `antecipacao`, `usuarios`). |
| `id_registro` | Id do registro afetado, sem chave estrangeira (o registro pode ter sido excluído). |
| `sucesso` | `false` quando a operação falhou. |
| `detalhes` | JSON com os dados da ação (cópia do contrato excluído, valores, motivo da falha). Nunca contém senha, hash ou token. |
| `ip` | IP de origem identificado pelo Streamlit (atrás de proxy pode ser o IP do proxy). |

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
