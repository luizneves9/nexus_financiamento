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

A antecipação registra valor pago e, quando existe Selic aplicável, calcula o
`valor_moeda` pela divisão do valor pago pela Selic. A projeção utiliza esses
dados quando suas estruturas estiverem atualizadas.

## Pontos para validação do negócio

- Arredondamentos e casas decimais.
- Politica quando não existe Selic para uma data.
- Momento de atualização das matérialized views.
- Regras para liquidação total e parcial.
- Regras de carência e pagamento durante carência.
