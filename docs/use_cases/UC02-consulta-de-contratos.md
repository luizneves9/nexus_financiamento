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
2. (Opcional) O usuário preenche um ou mais filtros: Empresa, Banco ou Contrato.
3. O usuário clica em **Filtrar** para aplicar os filtros (filtros ILIKE, busca parcial).
4. O sistema consulta a view `vw_controle_contratos` com as cláusulas WHERE parametrizadas.
5. O sistema exibe identificador, empresa, banco, número, data de emissão, valor, tipo de pos-fixação, juros, prazo e vencimento final.
6. O usuário pode selecionar um registro para executar uma operação disponível (Projeção, Excluir, Novo).

## Fluxos alternativos

### FA01 - Nenhum contrato encontrado

O sistema exibe um aviso "Nenhum contrato encontrado com os filtros aplicados." O usuário pode modificar os filtros ou limpar o formulário para voltar a listar todos os registros.

### FA02 - Sem filtros

Quando nenhum filtro é preenchido, o sistema lista todos os contratos cadastrados ordenados por identificador.

## Fluxos de exceção

### FE01 - Falha na consulta

O sistema deve informar a indisponibilidade do banco ou da consulta. O
tratamento de erros da consulta será aprimorado em evolução futura.

## Regras de negócio

- A consulta utiliza a view de controle do banco.
- A ordenação atual e feita pelo identificador do contrato.

## Dados consultados

Os campos exibidos são definidos por `financiamento.vw_controle_contratos`.
