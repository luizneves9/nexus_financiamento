# UC07 - Liquidacao de Contrato

**Status:** Planejado para a versao 1.0  
**Ator principal:** Usuario responsavel pelo setor financeiro  
**Requisitos associados:** RF07

## Objetivo

Simular e registrar a liquidacao total ou parcial de um contrato, mantendo os dados financeiros no banco.

## Pre-condicoes

1. O contrato esta cadastrado.
2. A projecao financeira esta disponivel.
3. O usuario informa a data e o valor da liquidacao.
4. A autenticacao e os perfis de acesso estarao disponiveis quando este caso de
	uso for liberado para a versao 1.0.

## Pos-condicoes

- A liquidacao e registrada na estrutura de dados definida para a versao 1.0.
- O saldo e a projecao futura refletem a operacao.
- O sistema apresenta o resultado da operacao ao usuario.

## Fluxo principal

1. O usuario seleciona um contrato.
2. O sistema apresenta o saldo e as parcelas projetadas.
3. O usuario escolhe liquidacao total ou parcial.
4. O usuario informa data, valor e dados de tesouraria.
5. O sistema apresenta a simulacao.
6. O usuario confirma.
7. O banco registra a operacao e recalcula as estruturas dependentes.
8. O sistema informa a liquidacao registrada.

## Fluxos alternativos

### FA01 - Simulacao sem registro

O usuario consulta o valor calculado e cancela antes da confirmacao. Nenhum registro e persistido.

### FA02 - Liquidacao parcial

O sistema registra o valor pago e recalcula o saldo remanescente.

## Fluxos de excecao

### FE01 - Valor invalido

O valor deve ser maior que zero e nao pode exceder o saldo permitido para a modalidade escolhida.

### FE02 - Contrato ja liquidado

O sistema impede nova liquidacao ou direciona o usuario para uma operacao de
ajuste, conforme regra definida para a versao 1.0.

## Regras de negocio

- A liquidacao deve ser registrada, nao apenas simulada.
- A aprovacao por outro usuario nao e obrigatoria no escopo inicial.
- O calculo permanece no PostgreSQL.
