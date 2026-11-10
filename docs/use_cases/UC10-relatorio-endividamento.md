# UC10 - Relatório de Endividamento

**Status:** Implementado (em calibração — selo BETA no menu)
**Ator principal:** Usuario responsável pelo setor financeiro
**Requisitos associados:** RF07.4, RF07.4.1, RN02, RN03, RN24, RN28, RN29, RN30

**Rastreamento detalhado:** [Registro de Status e Pendências](../requirements/status-register.md#uc10---relatório-de-endividamento)

## Objetivo

Exibir o endividamento do grupo em formato de fluxo de caixa (ano × mês, em
milhões) na posição de uma data base, por modalidade (Financiamentos, Compra
Santo Anjo, Consórcios e Tributário), com o total pago, o total a pagar, os
créditos de consórcio, a Dívida Líquida e o resumo da variação do mês.

## Pre-condicoes

1. O usuário está autenticado (UC12).
2. A projeção está disponível em `financiamento.projecao_parcelas` (DA08).
3. Para as demais modalidades: pagamentos e parcelas a pagar de consórcio
   importados e créditos lançados (UC16); parcelas de Compra Santo Anjo e
   Tributário lançadas e baixadas (UC17).

## Pos-condicoes

O usuário visualiza a tabela do endividamento na data base, com os meses
liquidados destacados, o bloco Sub Total, os créditos, a Dívida Líquida e o
resumo do mês.

## Fluxo principal

1. O usuário acessa **Relatórios > Endividamento**.
2. O sistema aplica os filtros padrão: **Data base** = hoje e **Vencimentos a
   partir do mês de** = 01/01/2026 (prefixo `fe_`).
3. O sistema consulta a posição na data base por modalidade (RN29):
   Financiamentos pela mesma regra do Contas a Pagar (RN24), só com contratos
   contabilizados até a data base (RN28); Compra Santo Anjo e Tributário pelo
   vencimento; Consórcios pelo pago importado e pela última competência a
   pagar.
4. O sistema exibe a tabela: Saldo Acumulado por modalidade, um bloco por ano
   (uma linha por modalidade, 12 meses, Total Anual e %), um espaço e o bloco
   **Sub Total** (uma linha por modalidade e o Total Geral: meses somados em
   todos os anos exibidos, Total, Total pago e Total a pagar).
5. Abaixo, os créditos de consórcio da competência da data base (ou da última
   anterior) e a **Dívida Líquida** (Total a pagar − créditos).
6. Meses com parcelas liquidadas até a data base aparecem na cor do cabeçalho
   (legenda "Mês liquidado"); antecipações e quitações não marcam o mês.
7. O sistema consulta a posição também no último dia do mês anterior e exibe
   o **Resumo do mês - variação do endividamento** (RN30): Período (mês
   anterior × mês da data base), por modalidade Saldo Inicial, Juros, Pgto
   Mês, Contrato Quitado, Contrato Novo e Saldo Final, a linha Total, os
   créditos e a Dívida Líquida.

## Fluxos alternativos

### FA01 - Filtrar

Data base e Vencimentos a partir do mês de (o mês inteiro da data
escolhida), com o botão **Filtrar**. O mesmo filtro vale para o relatório e
para o resumo do mês.

### FA02 - Alternância manual de tema

Botões Automático, Claro e Escuro; no automático a tabela segue
`prefers-color-scheme`.

### FA03 - Nenhum registro

O sistema exibe "Nenhum dado disponível para o endividamento.".

## Fluxos de exceção

### FE01 - Falha na consulta

A mensagem de erro do banco é exibida (relatório, créditos ou resumo do mês).

## Regras de negócio

- RN24: Financiamentos com a mesma regra de posição na data base do Contas a
  Pagar.
- RN28: o contrato entra a partir da data de contabilização (não da emissão).
- RN29: regras de Compra Santo Anjo, Tributário, Consórcios, créditos e
  Dívida Líquida.
- RN30: colunas do resumo do mês; o Saldo Final é igual ao Total a pagar do
  Sub Total.
- Valores em milhões com 3 casas decimais; os totais (anos, Saldo Acumulado,
  Sub Total, resumo e Dívida Líquida) somam o valor exato e só o resultado é
  arredondado — batem com a tela Consórcio, mas a soma das células exibidas
  pode diferir 0,001 do total.

## Implementação

- `src/views/relatorio_endividamento.py`, `src/services/relatorio_endividamento.py`
- `src/queries/queries_relatorio_endividamento.py`: `CTE_MOVIMENTOS_ENDIVIDAMENTO`
  (usa `CTE_POSICAO_DATA_BASE`) compartilhado por `SELECT_PROJECAO_ENDIVIDAMENTO`
  e `SELECT_RESUMO_ENDIVIDAMENTO`; `SELECT_CREDITO_ENDIVIDAMENTO`.

## Dados persistidos

Nenhum — somente leitura (sem log de auditoria).
