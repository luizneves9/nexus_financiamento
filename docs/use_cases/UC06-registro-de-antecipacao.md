# UC06 - Registro de Antecipacao

**Status:** Planejado para a versao 1.0; estrutura de banco disponivel  
**Ator principal:** Usuario responsavel pelo setor financeiro  
**Requisitos associados:** RF07, RN02

## Objetivo

Registrar um pagamento antecipado associado a um contrato e refletir o valor na projecao financeira.

## Pre-condicoes

1. O contrato esta cadastrado.
2. O usuario possui os dados de pagamento e tesouraria.
3. A Selic correspondente esta disponivel no banco ou pode ser localizada pela
	regra de busca definida no trigger.

## Pos-condicoes

- O registro e persistido em `financiamento.antecipacao`.
- O trigger calcula a Selic e o `valor_moeda` quando aplicavel.
- A projecao considera o valor antecipado quando as estruturas de calculo estao
	atualizadas.

## Fluxo principal

1. O usuario seleciona o contrato.
2. O usuario informa data de pagamento, data de tesouraria e valor pago.
3. O sistema valida os campos obrigatorios.
4. O sistema grava a antecipacao.
5. O trigger `processar_dados_antecipacao` preenche a Selic e calcula o valor em moeda.
6. O sistema informa o registro da antecipacao.

## Fluxos de excecao

### FE01 - Contrato inexistente

A chave estrangeira impede o registro.

### FE02 - Selic indisponivel

Quando nao existe taxa aplicavel, o banco pode manter a Selic e o valor em
moeda nulos. O tratamento funcional dessa situacao sera definido na versao
1.0.

### FE03 - Falha de persistencia

O sistema informa o erro e nao confirma o registro.

## Regras de negocio

- A antecipacao pertence a um contrato.
- A Selic e procurada ate a data de tesouraria.
- O valor em moeda e calculado pela divisao do valor pago pela Selic.
- O registro da antecipacao deve ser efetivo, e nao apenas uma simulacao.
