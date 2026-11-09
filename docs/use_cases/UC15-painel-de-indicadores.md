# UC15 - Painel de Indicadores

**Status:** Implementado (em calibração — selo BETA no menu)
**Ator principal:** Usuario responsável pelo setor financeiro
**Requisitos associados:** RF07.8, RN02, RN24, RN27, RN28

**Rastreamento detalhado:** [Registro de Status e Pendências](../requirements/status-register.md#uc15---painel-de-indicadores)

## Objetivo

Dar uma visão de decisão da dívida em uma única tela (**Painel > Indicadores**):
os principais indicadores na posição de uma data base, sempre comparando
dois anos escolhidos (**Data X** × **Data Y**), o fluxo de pagamentos mês a
mês e a composição desse fluxo por empresa, banco e tipo de contrato.

## Pre-condicoes

1. O usuário está autenticado (UC12).
2. A projeção está disponível em `financiamento.projecao_parcelas` (DA08).

## Pos-condicoes

O usuário visualiza os indicadores da Data Y comparados aos da Data X.
Nenhum dado é alterado.

## Fluxo principal

1. O usuário acessa **Painel > Indicadores**, a página inicial após o login
   (primeiro grupo do menu).
2. O sistema aplica os filtros padrão, por **ano** (prefixo `fi_`): **Data
   base** = ano atual, **Data X** = ano anterior, **Data Y** = ano atual,
   **Empresa** e **Banco** = Todos.
3. O sistema monta as datas de cada lado (RN27): o período de X e de Y é o ano
   inteiro (01/01 a 31/12); se X ou Y for o ano atual, os dois vão até o
   dia/mês de hoje (acumulado no ano). A posição de Y é hoje (Data base = ano
   atual) ou 31/12 do ano da Data base; a de X é a mesma data deslocada pela
   diferença de anos entre X e Y. Uma legenda abaixo do filtro mostra as datas.
4. O sistema consulta a posição na data base (RN24) para os dois lados; só
   entram contratos contabilizados até cada data base (RN28).
5. O sistema exibe cinco cartões com o valor de Y e a variação sobre X:
   - **Saldo devedor** — principal das parcelas a vencer na data base;
   - **Fluxo de pagamentos** — parcelas, antecipações e quitações com
     vencimento útil no período (pago, se liquidado; senão, projetado);
   - **Juros no período** — juros das parcelas com vencimento no período;
   - **Contratado no período** — valor financiado dos contratos com data de
     contabilização no período (RN28);
   - **Taxa média ponderada** — `taxa_juros_efetiva` dos contratos ativos,
     ponderada pelo saldo devedor (variação em pontos percentuais).
6. Abaixo, lado a lado e alinhados:
   - **Fluxo de pagamentos por mês** — barras de X e de Y para cada mês;
   - **Composição da dívida** — barras horizontais do fluxo de pagamentos de
     X e de Y, com valor, participação e variação no rótulo.

## Fluxos alternativos

### FA01 - Filtrar

O usuário altera os anos da Data base, Data X e Data Y (de 2021 até cinco
anos à frente; a Data X deve ser anterior à Data Y), Empresa e/ou Banco
(seleção entre os cadastros, com **Todos**) e aciona **Filtrar**. Os filtros
permanecem ao trocar de página.

### FA02 - Agrupar a composição

O seletor **Empresas | Bancos | Tipo de contrato**, na linha do título da
composição, troca o agrupamento sem consultar o banco de novo.

### FA03 - Sem base de comparação

Quando o valor de X é zero (ex.: nenhum contrato contabilizado), o cartão mostra
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
  Data X × Data Y.
- Valores em milhões com 3 casas decimais (R$ 248,165 Mi), como no
  Endividamento; valores exatos no "?" de cada cartão e no balão dos gráficos.
- Na variação, queda de saldo, juros e taxa aparece em verde; fluxo e
  contratado não têm juízo de valor (cinza).
- Consultas não são registradas no log de auditoria (RN12).

## Implementação

- `src/views/indicadores.py` (filtros, cartões, gráficos em Altair).
- `src/services/indicadores.py` (`periodos_comparados`, consulta dos dois períodos, resumo dos
  cartões, agrupamento e série mensal).
- `src/queries/queries_indicadores.py` (`SELECT_INDICADORES_POSICAO`, com
  `GROUPING SETS` sobre `CTE_POSICAO_DATA_BASE`, e
  `SELECT_INDICADORES_CONTRATOS`).

## Dados persistidos

Nenhum — somente leitura.
