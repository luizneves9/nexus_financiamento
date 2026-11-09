# UC17 - Outros Pagamentos (Compra Santo Anjo e Tributário)

**Status:** Implementado
**Ator principal:** Usuario responsável pelo setor financeiro
**Requisitos associados:** RF07.10, RF08.1, RN12, RN29, RN31

**Rastreamento detalhado:** [Registro de Status e Pendências](../requirements/status-register.md#uc17---outros-pagamentos)

## Objetivo

Lançar e acompanhar as parcelas de Compra Santo Anjo e Tributário, que não
têm projeção calculada, para compor essas modalidades no Endividamento
(UC10).

## Pre-condicoes

1. O usuário está autenticado (UC12).

## Pos-condicoes

- Parcelas gravadas em `financiamento.outros_pagamentos`, com ou sem baixa.
- Cada operação registrada no log de auditoria (um registro por parcela).

## Fluxo principal

1. O usuário acessa **Operacional > Outros Pagamentos**.
2. O sistema aplica os filtros padrão (prefixo `fop_`): Modalidade = Todas,
   vencimento no ano atual e Situação = Todas, e lista as parcelas com o
   resumo (parcelas, lançado, pago e em aberto).
3. O usuário aciona **Incluir**, escolhe a modalidade, a descrição, o 1º
   vencimento, o valor da parcela e a quantidade de parcelas.
4. O sistema gera a prévia das parcelas mensais (mesmo dia; último dia do mês
   quando o dia não existe), que o usuário pode ajustar, inclusive marcando
   parcelas já pagas com data e valor pago.
5. O usuário confirma; o sistema grava as parcelas numa única transação, com
   um log por parcela.

## Fluxos alternativos

### FA01 - Editar

Uma parcela em aberto selecionada: o usuário altera modalidade, descrição,
vencimento e valor; o log guarda os valores anteriores e novos.

### FA02 - Baixar

Parcelas em aberto selecionadas: o usuário informa a data e o valor pago de
cada uma e confirma.

### FA03 - Estornar

Parcelas pagas selecionadas: o estorno limpa data e valor pago; o log guarda
a baixa estornada.

### FA04 - Excluir

Parcelas em aberto selecionadas: o sistema exclui e o log guarda a cópia de
cada registro.

### FA05 - Filtrar

Modalidade, vencimento de/até e situação (Aberta/Paga), com **Filtrar**.

## Fluxos de exceção

### FE01 - Seleção inválida

Editar exige uma única parcela em aberto; baixar e excluir exigem parcelas em
aberto; estornar exige parcelas pagas. O sistema informa o motivo.

### FE02 - Falha na gravação

A transação é desfeita, a mensagem é exibida e a falha é registrada no log.

## Regras de negócio

- RN31: valores, parcelas mensais e situações permitidas para cada ação.
- RN29: no Endividamento, a parcela fica no mês do vencimento, pelo valor
  pago se baixada até a data base, senão pelo valor lançado.
- RN12: log `OUTRO_PAGAMENTO_INCLUIR`, `OUTRO_PAGAMENTO_ALTERAR`,
  `OUTRO_PAGAMENTO_EXCLUIR`, `OUTRO_PAGAMENTO_BAIXAR` e
  `OUTRO_PAGAMENTO_ESTORNAR`.

## Implementação

- `src/views/outros_pagamentos.py`,
  `src/views/components/modal_outros_pagamentos_incluir.py`,
  `src/views/components/modal_outros_pagamentos_baixar.py`
- `src/services/outros_pagamentos.py`, `src/queries/queries_outros_pagamentos.py`
- `database/consorcio_outros_pagamentos.sql`

## Dados persistidos

`outros_pagamentos` e `log_auditoria`.
