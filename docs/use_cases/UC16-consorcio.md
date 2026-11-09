# UC16 - Consórcio

**Status:** Implementado
**Ator principal:** Usuario responsável pelo setor financeiro
**Requisitos associados:** RF07.9, RF08.1, RN12, RN29, RN32

**Rastreamento detalhado:** [Registro de Status e Pendências](../requirements/status-register.md#uc16---consórcio)

## Objetivo

Manter no Nexus os pagamentos e as parcelas a pagar das cotas de consórcio
(importados dos CSVs dos bancos) e os créditos de consórcio do fechamento do
mês, que compõem a modalidade Consórcios e a Dívida Líquida do Endividamento
(UC10).

## Pre-condicoes

1. O usuário está autenticado (UC12).
2. O usuário tem os CSVs do banco: "pago" (pagamentos) e/ou "a pagar"
   (parcelas das cotas contempladas), um arquivo por banco e consorciado.

## Pos-condicoes

- Pagamentos gravados em `financiamento.consorcio_pago`.
- Parcelas a pagar gravadas em `financiamento.consorcio_a_pagar`, por
  competência, banco e consorciado.
- Créditos gravados em `financiamento.consorcio_credito`, um por competência.
- Cada operação registrada no log de auditoria.

## Fluxo principal

1. O usuário acessa **Operacional > Consórcio**.
2. O sistema exibe as abas **Pago** (filtros: pagamento de/até — padrão do
   início do ano até hoje —, banco, consorciado, proposta), **A pagar**
   (filtros: data base — padrão hoje —, banco, consorciado, proposta) e
   **Créditos** (lançamentos por competência), com prefixo `fco_`.
3. O usuário aciona **Importar pago** ou **Importar a pagar** e seleciona o
   CSV (`;`, formato brasileiro). No a pagar, informa também a data base
   (competência = mês da data base) e o consorciado (o CSV não traz a coluna).
4. O sistema lê e valida o arquivo e mostra a prévia, com a quantidade e o
   total já gravados que serão substituídos (RN32).
5. O usuário confirma; o sistema apaga o que o arquivo substitui e insere as
   linhas numa única transação, com o log.

## Fluxos alternativos

### FA01 - Créditos do fechamento

O usuário aciona **Créditos**, informa a competência, o Crédito Cotas
Contempladas e o Crédito Parcelas pagas e não contempladas e confirma. Se já
houver lançamento para a competência, o sistema avisa e a confirmação
atualiza os valores (o log guarda os valores anteriores).

### FA02 - Consultar

O usuário altera os filtros de uma aba e aciona **Filtrar**; a filtragem é
feita no banco (texto por busca parcial).

## Fluxos de exceção

### FE01 - Arquivo inválido

Coluna obrigatória ausente, data ou valor inválido: o sistema informa o erro
e não grava nada.

### FE02 - Falha na gravação

A transação é desfeita, a mensagem é exibida e a falha é registrada no log.

## Regras de negócio

- RN32: o que cada importação substitui; um crédito por competência.
- RN29: uso dos dados no Endividamento (pago pela coluna Total, a pagar pela
  última competência até o mês da data base).
- RN12: log `CONSORCIO_IMPORTAR_PAGO`, `CONSORCIO_IMPORTAR_A_PAGAR` e
  `CONSORCIO_CREDITO_SALVAR`.

## Implementação

- `src/views/consorcio.py`, `src/views/components/modal_consorcio_importar.py`,
  `src/views/components/modal_consorcio_credito.py`
- `src/services/consorcio.py`, `src/queries/queries_consorcio.py`
- `database/consorcio_outros_pagamentos.sql`

## Dados persistidos

`consorcio_pago`, `consorcio_a_pagar`, `consorcio_credito` e
`log_auditoria`.
