# UC03 - Visualizacao de Projecao Financeira

**Status:** Parcialmente implementado  
**Ator principal:** Usuario responsavel pelo setor financeiro  
**Requisitos associados:** RF07, RN02

## Objetivo

Permitir a consulta das parcelas projetadas de um contrato.

## Pre-condicoes

1. O contrato esta cadastrado.
2. O contrato esta selecionado na tela de contratos.
3. As estruturas de calculo do banco estao disponiveis.

## Pos-condicoes

O usuario visualiza parcela, data de vencimento e valor calculado para o contrato selecionado.

## Fluxo principal

1. O usuario acessa a pagina de contratos.
2. O usuario seleciona exatamente um contrato.
3. O usuario aciona **Projecao**.
4. A aplicacao consulta as materialized views de projecao.
5. O sistema apresenta os valores em uma janela de dialogo.

## Fluxos alternativos

### FA01 - Contrato TFC

A consulta utiliza a materialized view correspondente ao tipo de contrato. A
consulta atual combina os resultados retornados pelas views de projecao.

### FA02 - Exportacao da projecao

A exportacao para CSV esta planejada, mas ainda nao faz parte da interface atual.

## Fluxos de excecao

### FE01 - Nenhum ou varios contratos selecionados

O sistema informa que exatamente um registro deve ser selecionado.

### FE02 - Projecao indisponivel

O sistema informa a falha de consulta ou apresenta uma projecao sem registros,
conforme o resultado retornado pelo banco.

## Regras de negocio

- O calculo e executado exclusivamente no PostgreSQL.
- Dias uteis consideram fins de semana e a tabela `financiamento.feriados`.
- A Selic e obtida conforme os triggers e views definidos no banco.
- Antecipacoes podem alterar a projecao quando registradas no banco.
