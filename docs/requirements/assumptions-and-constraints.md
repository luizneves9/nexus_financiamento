# Premissas, Restricoes e Dependências

## Premissas

- O banco de dados oficial e PostgreSQL.
- O schema utilizado pela aplicação é `financiamento`.
- O banco é a fonte de verdade dos cálculos financeiros.
- Empresas, bancos e fornecedores existem antes da inclusão de contratos.
- A tabela de feriados é mantida com dados necessários para as projeções.
- A integração com a API da Selic será definida em etapa posterior.

## Restricoes atuais

- A aplicação atual não possui autenticação ou autorização formal.
- A exclusão de contratos é física.
- O modulo de veículos ainda não possui interface.
- A tela de antecipação ainda não está implementada.
- Auditoria completa ainda não está disponível.
- A aplicação depende de objetos previamente criados no PostgreSQL.
- O container depende da imagem base `fin-base:1.0`.

## Dependências externas

- PostgreSQL e seus objetos do schema `financiamento`.
- Variaveis `DB_USER`, `DB_PASS`, `DB_HOST`, `DB_PORT` e `DB_NAME`.
- Docker e Docker Compose.
- Rede Docker externa `rede-proxy`, quando utilizada no ambiente atual.
- Fonte oficial da Selic, quando a integração for implementada.

## Decisões pendentes

- Perfis e matriz de autorização.
- Politica de backup, restauração, RTO e RPO.
- Regras de chassi, placa e bens ativos.
- Politica de ausencia de Selic.
- Modelo definitivo para liquidação.
