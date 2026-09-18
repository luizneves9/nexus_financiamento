# Calculo Financeiro

## Principio

Todos os cálculos financeiros são realizados no PostgreSQL. A aplicação
consulta os resultados das views e matérialized views e não replica as
fórmulas em Python.

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

A matérialized view TFC utiliza dias corridos e base anual de 365 dias,
conforme a implementação atual do banco.

## Antecipação

A antecipação registra valor pago, data de pagamento, Selic e, quando existe 
Selic aplicável, calcula o `valor_moeda` pela divisão do valor pago pela Selic.

Cada antecipação possui um `tipo_lancamento` que pode ser:
- **ANTECIPACAO**: pagamento parcial que reduz o saldo devedor, mas mantém as 
  demais parcelas na projeção.
- **QUITACAO**: pagamento que liquida o contrato totalmente. A projeção é 
  truncada na parcela da quitação; parcelas posteriores não são exibidas.

A view `mv_projecao_moeda` detecta quitações através da CTE `parcela_quitada` 
e filtra a projeção com `WHERE q.parcela_quitacao IS NULL OR cs.parcela <= q.parcela_quitacao`.

A consulta `SELECT_PROJECAO` (UC03) retorna três blocos:
1. **Parcelas**: dados de `mv_projecao_moeda_final` (saldo, principal, juros, total).
2. **Projeção TFC**: dados da view TFC quando aplicável.
3. **Antecipações**: registros de `financiamento.antecipacao` com tipo e valor pago.

## Pontos para validação do negócio

- Arredondamentos e casas decimais.
- Politica quando não existe Selic para uma data.
- Momento de atualização das matérialized views.
- Regras para liquidação total e parcial.
- Regras de carência e pagamento durante carência.

## Tratamento de Quitação na Projeção

Quando `tipo_lancamento = 'QUITACAO'`:
1. A CTE `parcela_quitada` identifica a parcela em que ocorreu a quitação 
   (`MAX(parcela) WHERE tipo_lancamento = 'QUITACAO'`).
2. O filtro WHERE retém apenas as parcelas até a quitação (`cs.parcela <= q.parcela_quitacao`).
3. Parcelas posteriores à quitação **não são retornadas** da view.
4. O resultado reflete o final do contrato na data de quitação.

**Casos tratados:**
- Contrato sem antecipação: `parcela_quitada` vazio, todas as parcelas são exibidas.
- Antecipação parcial (tipo ANTECIPACAO): `parcela_quitada` vazio, projeção continua completa.
- Quitação total (tipo QUITACAO): `parcela_quitada` preenchida, projeção truncada.

## Validação do UC03

A projeção exibida pelo UC03 foi comparada com os resultados das materialized
views utilizadas pelo banco. Os cálculos foram considerados corretos e
coerentes com o padrão implementado nos MVs.

Essa validação cobre a equivalência do cálculo entre a consulta utilizada pela
interface e o cálculo oficial do PostgreSQL. Novos cenários financeiros devem
continuar sendo registrados na estratégia de testes.
