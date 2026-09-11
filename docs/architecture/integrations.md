# Integracoes

## Estado atual

A aplicação não possui integrações HTTP ou API externas implementadas. Ela
acessa diretamente o PostgreSQL configurado no ambiente.

## Integração futura da Selic

A atualização automática da Selic está planejada. A solução deverá definir:

- fonte oficial e endpoint;
- autenticação, caso exigida;
- periodicidade da coleta;
- formato de data e valor;
- tratamento de duplicidade por data;
- retry e comportamento offline;
- logs sem exposicao de credenciais;
- validação dos dados antes da persistência;
- política para indisponibilidade da fonte;
- atualização das estruturas de projeção.

## Contrato de integração a definir

Quando a API for escolhida, este documento deverá registrar request, response,
códigos de erro, limites, timeout, versionamento, idempotência e responsável
operacional. Ate essa definicao, a tabela `financiamento.selic` deve ser
considerada uma dependência de dados previamente carregados.
