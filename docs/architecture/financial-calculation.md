# Calculo Financeiro

## Principio

Todos os calculos financeiros sao realizados no PostgreSQL. A aplicacao
consulta os resultados das views e materialized views e nao replica as
formulas em Python.

## Tipos de contrato

- **BNDES FINAME SELIC:** utiliza taxa efetiva, Selic, dias uteis e feriados.
- **BNDES FINAME TFC:** utiliza taxa efetiva e dias corridos conforme a view
  especifica.

## Dias uteis

A funcao `proximo_dia_util` desloca a data para o proximo dia que nao seja
sabado, domingo ou feriado cadastrado. A funcao `dias_uteis_entre` considera o
calendario de dias uteis do schema `financiamento`.

## Data de referencia

A funcao `set_data_referencia_contrato` define a data de referencia conforme o
dia da emissao: contratos emitidos ate o dia 15 usam a referencia no mesmo
mes; contratos posteriores usam a referencia no mes seguinte.

## Selic

A funcao `preencher_selic_contrato` procura a ultima Selic cuja data seja
menor ou igual a `data_bndes`. Na antecipacao, a busca considera a
`data_tesouraria`.

## Projecao Selic

A materialized view calcula fator de juros, saldo devedor, principal, juros e
total da parcela. O calculo considera carencia, amortizacao, dias uteis e
valores antecipados.

## Projecao TFC

A materialized view TFC utiliza dias corridos e base anual de 365 dias,
conforme a implementacao atual do banco.

## Antecipacao

A antecipacao registra valor pago e, quando existe Selic aplicavel, calcula o
`valor_moeda` pela divisao do valor pago pela Selic. A projecao utiliza esses
dados quando suas estruturas estiverem atualizadas.

## Pontos para validacao do negocio

- Arredondamentos e casas decimais.
- Politica quando nao existe Selic para uma data.
- Momento de atualizacao das materialized views.
- Regras para liquidacao total e parcial.
- Regras de carencia e pagamento durante carencia.
