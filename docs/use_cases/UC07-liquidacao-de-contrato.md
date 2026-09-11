# UC07 - Liquidação de Contrato

**Status:** Planejado para a versão 1.0  
**Ator principal:** Usuario responsável pelo setor financeiro  
**Requisitos associados:** RF07

**Rastreamento detalhado:** [Registro de Status e Pendências](../requirements/status-register.md#uc07---liquidação-de-contrato)

## Objetivo

Simular e registrar a liquidação total ou parcial de um contrato, mantendo os dados financeiros no banco.

## Pre-condicoes

1. O contrato está cadastrado.
2. A projeção financeira está disponível.
3. O usuário informa a data e o valor da liquidação.
4. A autenticação e os perfis de acesso estarão disponíveis quando este caso de
	uso for liberado para a versão 1.0.

## Pos-condicoes

- A liquidação e registrada na estrutura de dados definida para a versão 1.0.
- O saldo e a projeção futura refletem a operação.
- O sistema apresenta o resultado da operação ao usuário.

## Fluxo principal

1. O usuário seleciona um contrato.
2. O sistema apresenta o saldo e as parcelas projetadas.
3. O usuário escolhe liquidação total ou parcial.
4. O usuário informa data, valor e dados de tesouraria.
5. O sistema apresenta a simulação.
6. O usuário confirma.
7. O banco registra a operação e recalcula as estruturas dependentes.
8. O sistema informa a liquidação registrada.

## Fluxos alternativos

### FA01 - Simulação sem registro

O usuário consulta o valor calculado e cancela antes da confirmação. Nenhum registro e persistido.

### FA02 - Liquidação parcial

O sistema registra o valor pago e recalcula o saldo remanescente.

## Fluxos de exceção

### FE01 - Valor inválido

O valor deve ser maior que zero e não pode exceder o saldo permitido para a modalidade escolhida.

### FE02 - Contrato já liquidado

O sistema impede nova liquidação ou direciona o usuário para uma operação de
ajuste, conforme regra definida para a versão 1.0.

## Regras de negócio

- A liquidação deve ser registrada, não apenas simulada.
- A aprovação por outro usuário não e obrigatoria no escopo inicial.
- O cálculo permanece no PostgreSQL.
