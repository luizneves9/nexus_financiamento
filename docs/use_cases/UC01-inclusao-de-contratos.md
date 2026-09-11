# UC01 - Inclusão de Contratos

**Status:** Parcialmente implementado  
**Ator principal:** Usuario responsável pelo setor financeiro  
**Requisitos associados:** RF02, RF02.1, RN01, RN02, RN05

**Rastreamento detalhado:** [Registro de Status e Pendências](../requirements/status-register.md#uc01---inclusão-de-contratos)

## Objetivo

Cadastrar um contrato de financiamento com seus dados cadastrais e financeiros, permitindo que o banco de dados gere a projeção correspondente.

## Pre-condicoes

1. A aplicação está disponível.
2. Empresas e bancos necessários já estão cadastrados.
3. O usuário possui acesso a aplicação. Autenticação e perfis formais estão planejados para a versão 1.0.
4. A conexão com o PostgreSQL está disponível.

## Pos-condicoes

- Um contrato válido e persistido em `financiamento.contratos`.
- Triggers do banco preenchem a Selic e a data de referencia quando aplicável.
- As matérialized views de projeção são atualizadas conforme a configuração atual do banco.

## Fluxo principal

1. O usuário abre a tela de contratos.
2. O usuário seleciona **Novo**.
3. O sistema apresenta o formulario de inclusão.
4. O usuário informa empresa, banco, número do contrato, datas, tipo, valor, taxas, prazos e parâmetros de cobrança.
5. O usuário confirma a inclusão.
6. A aplicação valida campos obrigatórios, valores positivos e ordem das datas.
7. A aplicação grava o contrato no PostgreSQL.
8. O banco executa os triggers de preenchimento e atualização da projeção.
9. O sistema informa que o contrato foi incluído.

## Fluxos alternativos

### FA01 - Visualizar projeção antes da gravação (planejado)

O usuário solicita uma projeção antes da inclusão definitiva. O sistema deverá apresentar a projeção sem persistir o contrato. Esse fluxo ainda não está disponível no formulario atual.

### FA02 - Cancelar inclusão

O usuário seleciona **Cancelar**. O sistema abandona o formulario sem gravar o contrato.

## Fluxos de exceção

### FE01 - Campo obrigatório ausente

O sistema interrompe a gravação e informa os campos que precisam ser preenchidos.

### FE02 - Valor ou prazo inválido

O sistema rejeita valores financiados, taxas ou prazos menores ou iguais a zero, conforme as validações atuais.

### FE03 - Datas inconsistentes

O sistema rejeita datas fora da ordem esperada entre emissão, BNDES, primeiro encargo, primeiro principal e última parcela.

### FE04 - Contrato duplicado

O banco rejeita a gravação quando o `número_contrato` já existir, conforme a restrição atual de unicidade.

### FE05 - Falha de persistência

O sistema informa a falha de comúnicação ou gravação e não deve considerar o contrato incluído.

## Regras de negócio

- O contrato deve possuir período de carência conforme a regra inicial do negócio.
- A exclusão lógica não faz parte destá fase.
- O cálculo financeiro e executado pelo banco de dados.
- O vínculo de bens e veículos está previsto para a versão 1.0.

## Dados persistidos

Empresa, banco, número do contrato, datas, tipo, valor financiado, Selic, taxas, prazos, parâmetros de cobrança e debito em conta corrente.
