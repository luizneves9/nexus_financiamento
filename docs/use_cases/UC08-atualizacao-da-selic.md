# UC08 - Atualização da Selic

**Status:** Dados no banco; integração por API planejada  
**Ator principal:** Processo de integração ou usuário autorizado  
**Requisitos associados:** RF01, RN02

**Rastreamento detalhado:** [Registro de Status e Pendências](../requirements/status-register.md#uc08---atualização-da-selic)

## Objetivo

Disponibilizar no banco os valores da Selic necessários para os cálculos financeiros.

## Pre-condicoes

1. A fonte oficial ou API está disponível quando a integração for implementada.
2. O processo possui credenciais e permissão de escrita.
3. A tabela `financiamento.selic` está disponível.

## Pos-condicoes

- Os valores recebidos são persistidos por data.
- Contratos e antecipações podem localizar a taxa aplicável.
- As estruturas de projeção podem ser atualizadas conforme o processo definido.

## Fluxo planejado

1. O processo consulta a API oficial.
2. O sistema valida data e valor recebidos.
3. O sistema evita duplicidade ou define a política de atualização da mesma data.
4. O sistema grava os valores em `financiamento.selic`.
5. O sistema atualiza as estruturas de cálculo quando necessário.
6. O processo registra sucesso ou falha operacional.

## Comportamento atual

A aplicação não realiza a importação por API. Ela consulta os dados já armazenados no banco. Triggers localizam a taxa mais recente aplicável ao contrato ou a antecipação.

## Fluxos de exceção

### FE01 - API indisponível

O processo registra a falha e preserva os dados existentes.

### FE02 - Valor inválido

O sistema rejeita registros sem data ou com valor fora do domínio definido.

### FE03 - Taxa ausente para uma data

A projeção deverá seguir a política definida para ausencia de taxa. Essa
política será formalizada durante a implementação da integração.

## Regras de negócio

- A Selic e um insumo do cálculo financeiro.
- A taxa do contrato e preenchida considerando a data BNDES.
- A taxa da antecipação e preenchida considerando a data de tesouraria.
