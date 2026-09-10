# UC02 - Consulta de Contratos

**Status:** Implementado  
**Ator principal:** Usuario responsavel pelo setor financeiro  
**Requisitos associados:** RF03

## Objetivo

Exibir os contratos cadastrados para consulta operacional.

## Pre-condicoes

1. A aplicacao esta disponivel.
2. A conexao com o PostgreSQL esta disponivel.

## Pos-condicoes

O usuario visualiza os contratos retornados pela view `financiamento.vw_controle_contratos`.

## Fluxo principal

1. O usuario acessa a pagina **Contratos**.
2. O sistema consulta a view de controle de contratos.
3. O sistema exibe identificador, empresa, banco, numero, data de emissao, valor, tipo de pos-fixacao, juros, prazo e vencimento final.
4. O usuario pode selecionar um registro para executar uma operacao disponivel.

## Fluxos alternativos

### FA01 - Nenhum contrato encontrado

O sistema exibe uma tabela sem registros. O usuario pode retornar a consulta posteriormente.

### FA02 - Filtragem de contratos

Filtros por banco, taxa, periodo, valor e tipo de contrato fazem parte da evolucao planejada.

## Fluxos de excecao

### FE01 - Falha na consulta

O sistema deve informar a indisponibilidade do banco ou da consulta. O
tratamento de erros da consulta sera aprimorado em evolucao futura.

## Regras de negocio

- A consulta utiliza a view de controle do banco.
- A ordenacao atual e feita pelo identificador do contrato.

## Dados consultados

Os campos exibidos sao definidos por `financiamento.vw_controle_contratos`.
