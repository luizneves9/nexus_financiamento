# Premissas, Restricoes e Dependencias

## Premissas

- O banco de dados oficial e PostgreSQL.
- O schema utilizado pela aplicacao é `financiamento`.
- O banco é a fonte de verdade dos calculos financeiros.
- Empresas, bancos e fornecedores existem antes da inclusao de contratos.
- A tabela de feriados e mantida com dados necessarios para as projecoes.
- A integracao com a API da Selic sera definida em etapa posterior.

## Restricoes atuais

- A aplicacao atual nao possui autenticacao ou autorizacao formal.
- A exclusao de contratos é fisica.
- O modulo de veiculos ainda nao possui interface.
- A tela de antecipacao ainda nao esta implementada.
- Auditoria completa ainda nao esta disponivel.
- A aplicacao depende de objetos previamente criados no PostgreSQL.
- O container depende da imagem base `fin-base:1.0`.

## Dependencias externas

- PostgreSQL e seus objetos do schema `financiamento`.
- Variaveis `DB_USER`, `DB_PASS`, `DB_HOST`, `DB_PORT` e `DB_NAME`.
- Docker e Docker Compose.
- Rede Docker externa `rede-proxy`, quando utilizada no ambiente atual.
- Fonte oficial da Selic, quando a integracao for implementada.

## Decisoes pendentes

- Perfis e matriz de autorizacao.
- Politica de backup, restauracao, RTO e RPO.
- Regras de chassi, placa e bens ativos.
- Politica de ausencia de Selic.
- Modelo definitivo para liquidacao.
