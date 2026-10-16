# UC10 - Relatório de Endividamento

**Status:** Implementado
**Ator principal:** Usuario responsável pelo setor financeiro
**Requisitos associados:** RF07.4, RN02, RN03, RN24

**Rastreamento detalhado:** [Registro de Status e Pendências](../requirements/status-register.md#uc10---relatório-de-endividamento)

## Objetivo

Exibir o endividamento bancário em formato de fluxo de caixa (ano × mês, em
milhões) na posição de uma data base, com o total pago e o total a pagar.

## Pre-condicoes

1. O usuário está autenticado (UC12).
2. A projeção está disponível em `financiamento.projecao_parcelas` (DA08).

## Pos-condicoes

O usuário visualiza a tabela do endividamento na data base, com os meses
liquidados destacados e o bloco Sub Total.

## Fluxo principal

1. O usuário acessa **Relatórios > Endividamento**.
2. O sistema aplica os filtros padrão: **Data base** = hoje, **Vencimentos a
   partir do mês de** = 01/01/2026, Empresa e Banco vazios (prefixo `fe_`).
3. O sistema consulta a mesma posição na data base do Contas a Pagar (RN24),
   somando o valor considerado por ano e mês do vencimento útil.
4. O sistema exibe a tabela: Saldo Acumulado, um bloco por ano (linha
   Financiamento, 12 meses, Total Anual e %), um espaço e o bloco **Sub Total**
   (linha Financiamentos e Total Geral: meses somados em todos os anos
   exibidos, Total, Total pago e Total a pagar).
5. Meses com parcelas liquidadas até a data base aparecem na cor do cabeçalho
   (legenda "Mês liquidado"); antecipações e quitações não marcam o mês.

## Fluxos alternativos

### FA01 - Filtrar

Data base, Vencimentos a partir do mês de (o mês inteiro da data escolhida),
Empresa e Banco (busca parcial), com o botão **Filtrar**.

### FA02 - Alternância manual de tema

Botões Automático, Claro e Escuro; no automático a tabela segue
`prefers-color-scheme`.

### FA03 - Nenhum registro

O sistema exibe "Nenhum dado disponível para o endividamento.".

## Fluxos de exceção

### FE01 - Falha na consulta

A mensagem de erro do banco é exibida.

## Regras de negócio

- RN24: mesma regra de posição na data base do Contas a Pagar (os dois
  relatórios batem para o mesmo período e data base).
- Total pago = parcelas liquidadas, antecipações e quitações pagas até a data
  base; Total a pagar = projetado.
- Valores em milhões com 3 casas decimais.
- Modalidades além de Financiamentos (Compra Santo Anjo, Tributário,
  Consórcios) não existem no Nexus e não são exibidas.

## Implementação

- `src/views/relatorio_endividamento.py`, `src/services/relatorio_endividamento.py`
- `src/queries/queries_relatorio_endividamento.py` (usa `CTE_POSICAO_DATA_BASE`)

## Dados persistidos

Nenhum — somente leitura.
