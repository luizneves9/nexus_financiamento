# UC01 - Inclusao de Contratos

**Status:** Parcialmente implementado  
**Ator principal:** Usuario responsavel pelo setor financeiro  
**Requisitos associados:** RF02, RF02.1, RN01, RN02, RN05

## Objetivo

Cadastrar um contrato de financiamento com seus dados cadastrais e financeiros, permitindo que o banco de dados gere a projecao correspondente.

## Pre-condicoes

1. A aplicacao esta disponivel.
2. Empresas e bancos necessarios ja estao cadastrados.
3. O usuario possui acesso a aplicacao. Autenticacao e perfis formais estao planejados para a versao 1.0.
4. A conexao com o PostgreSQL esta disponivel.

## Pos-condicoes

- Um contrato valido e persistido em `financiamento.contratos`.
- Triggers do banco preenchem a Selic e a data de referencia quando aplicavel.
- As materialized views de projecao sao atualizadas conforme a configuracao atual do banco.

## Fluxo principal

1. O usuario abre a tela de contratos.
2. O usuario seleciona **Novo**.
3. O sistema apresenta o formulario de inclusao.
4. O usuario informa empresa, banco, numero do contrato, datas, tipo, valor, taxas, prazos e parametros de cobranca.
5. O usuario confirma a inclusao.
6. A aplicacao valida campos obrigatorios, valores positivos e ordem das datas.
7. A aplicacao grava o contrato no PostgreSQL.
8. O banco executa os triggers de preenchimento e atualizacao da projecao.
9. O sistema informa que o contrato foi incluido.

## Fluxos alternativos

### FA01 - Visualizar projecao antes da gravacao (planejado)

O usuario solicita uma projecao antes da inclusao definitiva. O sistema devera apresentar a projecao sem persistir o contrato. Esse fluxo ainda nao esta disponivel no formulario atual.

### FA02 - Cancelar inclusao

O usuario seleciona **Cancelar**. O sistema abandona o formulario sem gravar o contrato.

## Fluxos de excecao

### FE01 - Campo obrigatorio ausente

O sistema interrompe a gravacao e informa os campos que precisam ser preenchidos.

### FE02 - Valor ou prazo invalido

O sistema rejeita valores financiados, taxas ou prazos menores ou iguais a zero, conforme as validacoes atuais.

### FE03 - Datas inconsistentes

O sistema rejeita datas fora da ordem esperada entre emissao, BNDES, primeiro encargo, primeiro principal e ultima parcela.

### FE04 - Contrato duplicado

O banco rejeita a gravacao quando o `numero_contrato` ja existir, conforme a restricao atual de unicidade.

### FE05 - Falha de persistencia

O sistema informa a falha de comunicacao ou gravacao e nao deve considerar o contrato incluido.

## Regras de negocio

- O contrato deve possuir periodo de carencia conforme a regra inicial do negocio.
- A exclusao logica nao faz parte desta fase.
- O calculo financeiro e executado pelo banco de dados.
- O vinculo de bens e veiculos esta previsto para a versao 1.0.

## Dados persistidos

Empresa, banco, numero do contrato, datas, tipo, valor financiado, Selic, taxas, prazos, parametros de cobranca e debito em conta corrente.
