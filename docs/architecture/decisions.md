# Decisões Arquiteturais

## DA01 - PostgreSQL como motor financeiro

**Status:** Aceita  
**Decisão:** Funções, triggers, views e matérialized views do PostgreSQL são
responsáveis pelos cálculos financeiros.  
**Motivo:** Centralizar fórmulas, calendário, Selic e arredondamentos em uma
única fonte de verdade.  
**Consequência:** Alterações no cálculo exigem versionamento e testes no banco.

## DA02 - Exclusão física inicial

**Status:** Aceita  
**Decisão:** A primeira versão utiliza exclusão física de contratos.  
**Motivo:** E o comportamento atualmente implementado e ainda não existe
política aprovada de exclusão lógica.  
**Consequência:** Integridade referencial pode impedir a exclusão e histórico
precisa ser tratado em evolução futura.

## DA05 - Projeção temporária por função PostgreSQL

**Status:** Aceita  
**Decisão:** A projeção acionada durante a inclusão será executada por uma
função PostgreSQL que receberá os parâmetros do contrato e retornará o cálculo
final sem persistir o contrato.  
**Motivo:** Manter o cálculo financeiro no banco e evitar efeitos colaterais de
uma inserção seguida de rollback.  
**Consequência:** A função deverá possuir contrato de entrada e saída, testes
próprios e alinhamento com as regras das materialized views.

## DA03 - API da Selic posterior

**Status:** Planejada  
**Decisão:** A integração automática da Selic será desenvolvida posteriormente.
  
**Consequência:** No estado atual, os dados precisam estár previamente
carregados no banco.

## DA04 - Autenticação posterior

**Status:** Planejada  
**Decisão:** Autenticação e perfis pertencem ao escopo da versão 1.0.  
**Consequência:** O ambiente atual não deve ser tratado como pronto para
exposicao sem controle de acesso adicional.
