# Calculo Financeiro

## Principio

Todos os cálculos financeiros são realizados no PostgreSQL. A projeção é
calculada por contrato (`calcular_projecao_contrato`) e gravada em
`projecao_parcelas` (DA08); a aplicação consulta os resultados e não replica
as fórmulas em Python.

## Recálculo automático

- Inclusão/alteração de contrato e inclusão/alteração/exclusão de antecipação:
  recalcula só o contrato afetado (`trg_projecao_contratos`,
  `trg_projecao_antecipacao`).
- Nova Selic: recalcula, uma vez por comando, os contratos com parcelas
  abertas afetadas (`trg_projecao_selic_*`).
- Parcelas LIQUIDADAS nunca são alteradas; o estorno reabre a parcela e
  recalcula o contrato.

## Posição na data base (relatórios)

Contas a Pagar e Endividamento usam a mesma consulta (`CTE_POSICAO_DATA_BASE`,
DA10): parcela liquidada até a data base = valor pago; demais = valor
projetado refeito com a Selic conhecida até a data base (Selic da própria data
se ela for até a data base, senão a última até a data base); antecipações e
quitações pagas depois da data base não entram, e os contratos que as têm são
recalculados com `calcular_projecao_contrato(id, data_base)`.

## Projeção durante a inclusão

A projeção solicitada antes da inclusão definitiva será executada por uma
função PostgreSQL parametrizada. A função receberá os dados necessários do
contrato e retornará as parcelas calculadas, sem inserir o contrato em
`financiamento.contratos` e sem alterar dados permanentes.

O resultado será exibido no mesmo modal do formulário de inclusão. A função
deverá reutilizar as regras financeiras aprovadas para o tipo de contrato,
incluindo Selic, dias úteis, feriados, carência, amortização e arredondamentos,
conforme aplicável.

Os parâmetros e o formato de retorno serão definidos antes da implementação
da função e deverão ser cobertos por testes de banco.

## Tipos de contrato

- **BNDES FINAME SELIC:** utiliza taxa efetiva, Selic, dias úteis e feriados.
- **BNDES FINAME TFC:** utiliza taxa efetiva e dias corridos conforme a view
  especifica.

## Dias úteis

A função `próximo_dia_util` desloca a data para o próximo dia que não seja
sabado, domingo ou feriado cadastrado. A função `dias_úteis_entre` considera o
calendário de dias úteis do schema `financiamento`.

## Data de referencia

A função `set_data_referencia_contrato` define a data de referencia conforme o
dia da emissão: contratos emitidos até o dia 15 usam a referencia no mesmo
mes; contratos posteriores usam a referencia no mes seguinte.

## Selic

A função `preencher_selic_contrato` procura a última Selic cujá data seja
menor ou igual a `data_bndes`. Na antecipação, a busca considera a
`data_tesouraria`.

## Projeção Selic

A matérialized view calcula fator de juros, saldo devedor, principal, juros e
total da parcela. O cálculo considera carência, amortização, dias úteis e
valores antecipados.

## Projeção TFC

O cálculo TFC utiliza dias corridos e base anual de 365 dias,
conforme a implementação atual do banco.

## Antecipação

A antecipação registra valor pago, data de pagamento, Selic e, quando existe
Selic aplicável, calcula o `valor_moeda` pela divisão do valor pago pela Selic.

Cada antecipação possui um `tipo_lancamento` que pode ser:
- **ANTECIPACAO**: pagamento parcial que reduz o saldo devedor, mas mantém as
  demais parcelas na projeção.
- **QUITACAO**: pagamento que quita o contrato. As parcelas a partir da
  parcela da quitação ficam como `CANCELADA_QUITACAO` e não são exibidas.

O cálculo identifica a quitação pela CTE `parcela_quitada` (primeira parcela
com vencimento maior ou igual à data de compensação).

A consulta `SELECT_PROJECAO` (UC03) retorna três blocos:
1. **Parcelas**: `projecao_parcelas` sem as canceladas por quitação (SELIC e TFC).
2. **Antecipações**: registros de `financiamento.antecipacao` com tipo e valor pago.

O registro de antecipação/quitação pela interface (UC06) exibe, antes da
confirmação, um saldo devedor pré-calculado: busca em `projecao_parcelas` a
parcela com vencimento mais próximo da data de pagamento informada, busca a
Selic exata dessa data (ou a próxima disponível, com fallback para a mais
recente cadastrada) e multiplica o saldo devedor da parcela pela Selic
encontrada. Esse cálculo pré-confirmação só atende contratos do tipo
`BNDES FINAME SELIC`.

## Pontos para validação do negócio

- Arredondamentos e casas decimais.
- Politica quando não existe Selic para uma data.
- Regras de carência e pagamento durante carência.

## Tratamento de Quitação na Projeção

Quando `tipo_lancamento = 'QUITACAO'`:
1. A CTE `parcela_quitada` identifica a primeira parcela com vencimento maior
   ou igual à data de compensação da quitação.
2. Essa parcela e as posteriores ficam com `situacao = CANCELADA_QUITACAO`
   (inclusive a do mesmo dia da quitação — ponto a validar, BL-027).
3. As parcelas canceladas não são exibidas nem somadas.
4. O resultado reflete o final do contrato na data de quitação.

**Casos tratados:**
- Contrato sem antecipação: `parcela_quitada` vazio, todas as parcelas são exibidas.
- Antecipação parcial (tipo ANTECIPACAO): `parcela_quitada` vazio, projeção continua completa.
- Quitação total (tipo QUITACAO): `parcela_quitada` preenchida, projeção truncada.

## Validação do UC03

Na migração de 15/10/2026, `calcular_projecao_contrato` foi comparada com as
antigas materialized views para todos os contratos (valores em moeda e em R$,
SELIC e TFC): diferença zero.

Essa validação cobre a equivalência do cálculo entre a consulta utilizada pela
interface e o cálculo oficial do PostgreSQL. Novos cenários financeiros devem
continuar sendo registrados na estratégia de testes.
