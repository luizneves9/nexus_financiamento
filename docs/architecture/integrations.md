# Integracoes

## Estado atual

A aplicacao nao possui integracoes HTTP ou API externas implementadas. Ela
acessa diretamente o PostgreSQL configurado no ambiente.

## Integracao futura da Selic

A atualizacao automatica da Selic esta planejada. A solucao devera definir:

- fonte oficial e endpoint;
- autenticacao, caso exigida;
- periodicidade da coleta;
- formato de data e valor;
- tratamento de duplicidade por data;
- retry e comportamento offline;
- logs sem exposicao de credenciais;
- validacao dos dados antes da persistencia;
- politica para indisponibilidade da fonte;
- atualizacao das estruturas de projecao.

## Contrato de integracao a definir

Quando a API for escolhida, este documento devera registrar request, response,
codigos de erro, limites, timeout, versionamento, idempotencia e responsavel
operacional. Ate essa definicao, a tabela `financiamento.selic` deve ser
considerada uma dependencia de dados previamente carregados.
