# UC09 - Relatório Contas a Pagar

**Status:** Implementado
**Ator principal:** Usuario responsável pelo setor financeiro
**Requisitos associados:** RF07.3, RN02, RN03, RN20, RN24

**Rastreamento detalhado:** [Registro de Status e Pendências](../requirements/status-register.md#uc09---relatório-contas-a-pagar)

> Até 10/2026 este relatório se chamava "Projeção de Pagamentos" e lia a
> view `vw_agrupamento_projecao` (removida).

## Objetivo

Exibir a posição das contas a pagar em uma data base: o que foi pago até ela
(pelo valor pago) e o que está projetado (pelo valor da projeção), incluindo
antecipações e quitações, com exportação completa.

## Pre-condicoes

1. O usuário está autenticado (UC12).
2. A projeção está disponível em `financiamento.projecao_parcelas` (DA08).

## Pos-condicoes

O usuário visualiza (e pode exportar) as linhas filtradas na posição da data
base, com o resumo por situação.

## Fluxo principal

1. O usuário acessa **Relatórios > Contas a Pagar**.
2. O sistema aplica os filtros padrão: **Data base** = hoje, **Vcto de / até**
   = mês atual, **Situação** = Todas (prefixo `fcp_`).
3. O sistema consulta a posição na data base (`CTE_POSICAO_DATA_BASE`, RN24) e
   exibe: Empresa, Banco, Contrato, Tipo de contrato, Parcela, Tipo, Situação,
   Vencimento, Vencimento útil, Principal, Juros, Parcela H, Valor projetado,
   Data pagamento, Valor pago, Ajuste, Valor considerado, Origem e Doctos ERP.
4. Abaixo da tabela, o resumo: data base, contratos, linhas, Liquidado,
   Antecipações/Quitações, Projetado e Total considerado.
5. O botão **Exportar** baixa as linhas filtradas
   (`contas_a_pagar_base_dd-mm-aaaa.xlsx`).

## Fluxos alternativos

### FA01 - Filtrar

Data base, Empresa, Banco, Contrato (busca parcial), Vcto de/até (vencimento
útil) e Situação (Todas, Liquidado, Projetado, Antecipação, Quitação), com o
botão **Filtrar**; a filtragem é feita no banco.

### FA02 - Data base passada

Parcelas liquidadas depois da data base aparecem como Projetado; antecipações
e quitações pagas depois da data base não aparecem, e o contrato é
considerado como estava na data base (parcelas que a quitação posterior
cancelou voltam como Projetado); a Selic usada é a conhecida até a data base.

### FA03 - Ambiente sem `openpyxl`

A exportação gera CSV (`;`, vírgula decimal) em vez de Excel.

### FA04 - Nenhum registro

O sistema exibe "Nenhuma conta a pagar encontrada com os filtros aplicados.".

## Fluxos de exceção

### FE01 - Falha na consulta

A mensagem de erro do banco é exibida.

## Regras de negócio

- RN24: Liquidado = parcela paga até a data base (valor pago, já com o ajuste);
  Projetado = demais parcelas (valor projetado na Selic da data base);
  Antecipação/Quitação = lançamentos pagos até a data base (valor pago).
- O Valor considerado segue a situação e é o que soma no resumo.
- RN02 / RN03: cálculo no PostgreSQL, dias úteis.
- Consulta e exportação não são registradas no log (RN12).

## Implementação

- `src/views/relatorio_contas_a_pagar.py`, `src/services/relatorio_contas_a_pagar.py`
- `src/queries/queries_contas_a_pagar.py` (`CTE_POSICAO_DATA_BASE`, compartilhada
  com o UC10)
