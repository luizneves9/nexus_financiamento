# Decisoes Arquiteturais

## DA01 - PostgreSQL como motor financeiro

**Status:** Aceita  
**Decisao:** Funcoes, triggers, views e materialized views do PostgreSQL sao
responsaveis pelos calculos financeiros.  
**Motivo:** Centralizar formulas, calendario, Selic e arredondamentos em uma
unica fonte de verdade.  
**Consequencia:** Alteracoes no calculo exigem versionamento e testes no banco.

## DA02 - Exclusao fisica inicial

**Status:** Aceita  
**Decisao:** A primeira versao utiliza exclusao fisica de contratos.  
**Motivo:** E o comportamento atualmente implementado e ainda nao existe
politica aprovada de exclusao logica.  
**Consequencia:** Integridade referencial pode impedir a exclusao e historico
precisa ser tratado em evolucao futura.

## DA03 - API da Selic posterior

**Status:** Planejada  
**Decisao:** A integracao automatica da Selic sera desenvolvida posteriormente.
  
**Consequencia:** No estado atual, os dados precisam estar previamente
carregados no banco.

## DA04 - Autenticacao posterior

**Status:** Planejada  
**Decisao:** Autenticacao e perfis pertencem ao escopo da versao 1.0.  
**Consequencia:** O ambiente atual nao deve ser tratado como pronto para
exposicao sem controle de acesso adicional.
