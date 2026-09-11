# UC02 - Consulta de Contratos

**Status:** Implementado  
**Ator principal:** Usuario responsável pelo setor financeiro  
**Requisitos associados:** RF03

**Rastreamento detalhado:** [Registro de Status e Pendências](../requirements/status-register.md#uc02---consulta-de-contratos)

## Objetivo

Exibir os contratos cadastrados para consulta operacional.

## Pre-condicoes

1. A aplicação está disponível.
2. A conexão com o PostgreSQL está disponível.

## Pos-condicoes

O usuário visualiza os contratos retornados pela view `financiamento.vw_controle_contratos`.

## Fluxo principal

1. O usuário acessa a página **Contratos**.
2. O sistema consulta a view de controle de contratos.
3. O sistema exibe identificador, empresa, banco, número, data de emissão, valor, tipo de pos-fixação, juros, prazo e vencimento final.
4. O usuário pode selecionar um registro para executar uma operação disponível.

## Fluxos alternativos

### FA01 - Nenhum contrato encontrado

O sistema exibe uma tabela sem registros. O usuário pode retornar a consulta posteriormente.

### FA02 - Filtragem de contratos

Filtros por banco, taxa, período, valor e tipo de contrato fazem parte da evolução planejada.

## Fluxos de exceção

### FE01 - Falha na consulta

O sistema deve informar a indisponibilidade do banco ou da consulta. O
tratamento de erros da consulta será aprimorado em evolução futura.

## Regras de negócio

- A consulta utiliza a view de controle do banco.
- A ordenação atual e feita pelo identificador do contrato.

## Dados consultados

Os campos exibidos são definidos por `financiamento.vw_controle_contratos`.
