# Estrategia de Testes

## Objetivo

Validar regras de negocio, calculos financeiros, integridade dos dados e
fluxos da aplicacao antes da promocao para ambientes superiores.

## Niveis

### Testes unitarios

Validar funcoes Python de validacao, transformacao de valores, selecao de
registros e tratamento de estados da interface.

### Testes de integracao

Validar services, repositories, queries, conexao SQLAlchemy e transacoes com
um PostgreSQL de teste contendo o schema `financiamento`.

### Testes de banco

Validar funcoes, triggers, views, materialized views, chaves estrangeiras,
unicidades, dias uteis, feriados, Selic, carencia e antecipacao.

### Testes de aceitacao

Executar os fluxos dos Use Cases com um usuario do setor financeiro e dados
representativos, verificando resultado funcional e mensagens.

## Cenários prioritarios

| ID | Cenario | Resultado esperado |
| --- | --- | --- |
| T01 | Incluir contrato valido | Contrato persistido e projecao disponivel. |
| T02 | Campo obrigatorio ausente | Inclusao rejeitada com mensagem. |
| T03 | Valor, taxa ou prazo invalido | Inclusao rejeitada. |
| T04 | Datas fora de ordem | Inclusao rejeitada. |
| T05 | Numero de contrato repetido | Banco rejeita a operacao. |
| T06 | Consultar contratos | View retorna dados esperados. |
| T07 | Visualizar projecao | Parcelas e valores sao apresentados. |
| T08 | Excluir contrato sem dependencias | Registro removido. |
| T09 | Excluir contrato com dependencias | Integridade impede ou procedimento trata o caso. |
| T10 | Selic e feriado | Dias e valores seguem o calendario cadastrado. |
| T11 | Registrar antecipacao | Selic e valor em moeda sao calculados. |
| T12 | Falha de banco | Operacao nao e confirmada e erro e informado. |

## Dados de teste

Os testes devem utilizar dados ficticios ou anonimizados. Dados financeiros
reais nao devem ser usados em ambiente de desenvolvimento sem autorizacao.

## Criterio de entrada

Ambiente configurado, schema atualizado, dados de teste carregados e versao
identificada.

## Criterio de saida

Cenarios prioritarios aprovados, sem defeitos criticos abertos e resultados
registrados para a versao avaliada.
