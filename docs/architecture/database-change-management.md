# Gestao de Alteracoes do Banco

## Principio

O DDL e parte do contrato da aplicacao. Alteracoes em tabelas, funcoes,
triggers, views ou materialized views podem alterar resultados financeiros e
devem ser tratadas como mudancas de software.

## Procedimento minimo

1. Descrever a necessidade e o impacto.
2. Atualizar o DDL ou script de migracao versionado.
3. Atualizar o modelo de dados e o calculo financeiro quando aplicavel.
4. Executar testes em banco isolado.
5. Validar dados de referencia e resultados esperados.
6. Planejar backup e rollback.
7. Registrar a versao aplicada no ambiente.

## Riscos especificos

- Alteracao de formulas de juros ou arredondamento.
- Refresh incompleto de materialized views.
- Mudanca em chaves estrangeiras e exclusoes.
- Ausencia de Selic ou feriado no calendario.
- Divergencia entre DDL executado e documentacao.

## Rollback

Toda alteracao que possa afetar dados financeiros deve possuir estrategia de
rollback ou procedimento de restauracao validado antes da aplicacao em
producao.
