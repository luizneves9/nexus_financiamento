# UC06 - Registro de Antecipação

**Status:** Planejado para a versão 1.0; estrutura de banco disponível  
**Ator principal:** Usuario responsável pelo setor financeiro  
**Requisitos associados:** RF07, RN02

**Rastreamento detalhado:** [Registro de Status e Pendências](../requirements/status-register.md#uc06---registro-de-antecipação)

## Objetivo

Registrar um pagamento antecipado associado a um contrato e refletir o valor na projeção financeira.

## Pre-condicoes

1. O contrato está cadastrado.
2. O usuário possui os dados de pagamento e tesouraria.
3. A Selic correspondente está disponível no banco ou pode ser localizada pela
	regra de busca definida no trigger.

## Pos-condicoes

- O registro é persistido em `financiamento.antecipacao`.
- O trigger calcula a Selic e o `valor_moeda` quando aplicável.
- A projeção considera o valor antecipado quando as estruturas de cálculo estão
	atualizadas.

## Fluxo principal

1. O usuário seleciona o contrato.
2. O usuário informa data de pagamento, data de tesouraria e valor pago.
3. O sistema valida os campos obrigatórios.
4. O sistema grava a antecipação.
5. O trigger `processar_dados_antecipacao` preenche a Selic e calcula o valor em moeda.
6. O sistema informa o registro da antecipação.

## Fluxos de exceção

### FE01 - Contrato inexistente

A chave estrangeira impede o registro.

### FE02 - Selic indisponível

Quando não existe taxa aplicável, o banco pode manter a Selic e o valor em
moeda nulos. O tratamento funcional dessa situação será definido na versão
1.0.

### FE03 - Falha de persistência

O sistema informa o erro e não confirma o registro.

## Regras de negócio

- A antecipação pertence a um contrato.
- A Selic e procurada até a data de tesouraria.
- O valor em moeda e calculado pela divisão do valor pago pela Selic.
- O registro da antecipação deve ser efetivo, e não apenas uma simulação.
