# Gestão de Alterações do Banco

## Princípio

O DDL é parte do contrato da aplicação. Alterações em tabelas, funções,
triggers, views ou materialized views podem alterar resultados financeiros e
devem ser tratadas como mudanças de software.

Os arquivos SQL versionados do banco ficam em `database/`. O DDL completo está
em `database/ddl_financiamento.sql`; as funções de projeção temporária estão
em `database/projection_functions.sql`.

## Procedimento minimo

1. Descrever a necessidade e o impacto.
2. Atualizar o DDL ou script de migração versionado.
3. Atualizar o modelo de dados e o cálculo financeiro quando aplicável.
4. Executar testes em banco isolado.
5. Validar dados de referencia e resultados esperados.
6. Planejar backup e rollback.
7. Registrar a versão aplicada no ambiente.

## Riscos especificos

- Alteração de fórmulas de juros ou arredondamento.
- Refresh incompleto de matérialized views.
- Mudanca em chaves estrangeiras e exclusões.
- Ausencia de Selic ou feriado no calendário.
- Divergencia entre DDL executado e documentação.

## Rollback

Toda alteração que possa afetar dados financeiros deve possuir estratégia de
rollback ou procedimento de restauração validado antes da aplicação em
producao.
