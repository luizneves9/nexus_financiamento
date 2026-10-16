# UC15 - Painel de Indicadores

**Status:** Implementado
**Ator principal:** Usuario responsável pelo setor financeiro
**Requisitos associados:** RF07.8, RN02, RN24, RN27

**Rastreamento detalhado:** [Registro de Status e Pendências](../requirements/status-register.md#uc15---painel-de-indicadores)

## Objetivo

Dar uma visão de decisão da dívida em uma única tela (**Painel > Indicadores**):
os principais indicadores na posição de uma data base, sempre comparados ao
mesmo período do ano anterior, o fluxo de pagamentos mês a mês e a composição
desse fluxo por empresa, banco e tipo de contrato.

## Pre-condicoes

1. O usuário está autenticado (UC12).
2. A projeção está disponível em `financiamento.projecao_parcelas` (DA08).

## Pos-condicoes

O usuário visualiza os indicadores do período escolhido e do mesmo período do
ano anterior. Nenhum dado é alterado.

## Fluxo principal

1. O usuário acessa **Painel > Indicadores** (primeiro grupo do menu; a página
   inicial após o login continua sendo Contratos).
2. O sistema aplica os filtros padrão: **Data base** = hoje, **Período de** =
   01/01 do ano atual, **Período até** = hoje, **Empresa** e **Banco** = Todos
   (prefixo `fi_`).
3. O sistema consulta a posição na data base (RN24) duas vezes: para o período
   escolhido e para o mesmo período um ano antes, com a data base também
   recuada um ano (RN27).
4. O sistema exibe cinco cartões, cada um com a variação sobre o ano anterior:
   - **Saldo devedor** — principal das parcelas a vencer na data base;
   - **Fluxo de pagamentos** — parcelas, antecipações e quitações com
     vencimento útil no período (pago, se liquidado; senão, projetado);
   - **Juros no período** — juros das parcelas com vencimento no período;
   - **Contratado no período** — valor financiado dos contratos emitidos no
     período;
   - **Taxa média ponderada** — `taxa_juros_efetiva` dos contratos ativos,
     ponderada pelo saldo devedor (variação em pontos percentuais).
5. Abaixo, lado a lado e alinhados:
   - **Fluxo de pagamentos por mês** — barras do ano atual e do ano anterior
     para cada mês do período;
   - **Composição da dívida** — barras horizontais do fluxo de pagamentos do
     ano anterior e do atual, com valor, participação e variação no rótulo.

## Fluxos alternativos

### FA01 - Filtrar

O usuário altera Data base, Período de/até, Empresa e/ou Banco (seleção entre
os cadastros, com **Todos**) e aciona **Filtrar**. O ano anterior acompanha o
novo recorte. Os filtros permanecem ao trocar de página.

### FA02 - Agrupar a composição

O seletor **Empresas | Bancos | Tipo de contrato**, na linha do título da
composição, troca o agrupamento sem consultar o banco de novo.

### FA03 - Sem base de comparação

Quando o ano anterior é zero (ex.: nenhum contrato emitido), o cartão mostra
"sem base" em cinza no lugar da variação.

### FA04 - Nenhum contrato

O sistema exibe "Nenhum contrato encontrado com os filtros aplicados.".

## Fluxos de exceção

### FE01 - Falha na consulta

A mensagem de erro do banco é exibida e a tela não mostra os indicadores.

## Regras de negócio

- RN24: mesma posição na data base de Contas a Pagar e Endividamento; o
  fluxo de pagamentos do período bate com o total considerado de Contas a
  Pagar para o mesmo período, data base e filtros.
- RN27: definições do saldo devedor, do fluxo de pagamentos e da comparação
  com o ano anterior.
- Valores em milhões com 3 casas decimais (R$ 248,165 Mi), como no
  Endividamento; valores exatos no "?" de cada cartão e no balão dos gráficos.
- Na variação, queda de saldo, juros e taxa aparece em verde; fluxo e
  contratado não têm juízo de valor (cinza).
- Consultas não são registradas no log de auditoria (RN12).

## Implementação

- `src/views/indicadores.py` (filtros, cartões, gráficos em Altair).
- `src/services/indicadores.py` (consulta dos dois períodos, resumo dos
  cartões, agrupamento e série mensal).
- `src/queries/queries_indicadores.py` (`SELECT_INDICADORES_POSICAO`, com
  `GROUPING SETS` sobre `CTE_POSICAO_DATA_BASE`, e
  `SELECT_INDICADORES_CONTRATOS`).

## Dados persistidos

Nenhum — somente leitura.
