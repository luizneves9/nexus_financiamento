# UC01 - Inclusão de Contratos

**Status:** Parcialmente implementado  
**Ator principal:** Usuario responsável pelo setor financeiro  
**Requisitos associados:** RF02, RF02.1, RF02.3, RF03.2, RN01, RN02, RN02.1, RN05, RN26

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
- A projeção do contrato é gravada em `projecao_parcelas` pelo trigger de recálculo (DA08).
- Os PDFs anexados na inclusão (opcionais) ficam em `anexo_contrato` / `anexo_ficha_financeira`, gravados na mesma transação do contrato.

## Fluxo principal

1. O usuário abre a tela de contratos.
2. O usuário seleciona **Novo**.
3. O sistema apresenta o modal de inclusão com as abas **Dados**, **Contrato**,
   **Ficha Financeira** e **Projeção** (as mesmas do Detalhe do contrato, UC14).
4. Na aba Dados, o usuário informa empresa, banco, número do contrato, datas,
   tipo, valor, taxas, prazos (inteiros) e parâmetros de cobrança. A taxa de
   juros efetiva aceita até 6 casas decimais (ex.: 13,125974).
5. Opcionalmente, nas abas Contrato e Ficha Financeira, o usuário seleciona
   PDFs (a linha "Anexos selecionados" mostra a quantidade).
6. O usuário aciona **Confirmar**.
7. A aplicação valida campos obrigatórios, valores positivos, ordem das datas
   e os PDFs (RN26).
8. A aplicação grava, numa única transação, o contrato, os anexos e os logs —
   se algo falhar, nada é gravado.
9. O banco executa os triggers de preenchimento e de recálculo da projeção.
10. O sistema informa a inclusão e a quantidade de anexos.

## Fluxos alternativos

### FA01 - Projeção antes da gravação (automática)

1. O usuário abre a aba **Projeção**.
2. Se faltar algum dado, a aba lista o que falta ou está inválido (ex.: "Data
   BNDES", "Prazo final (maior que zero)", "Data BNDES (maior ou igual à Data
   Emissão)").
3. Com os dados completos, o sistema envia os parâmetros para a função
   PostgreSQL de projeção temporária e exibe a projeção na aba, sem botão.
4. O usuário volta à aba Dados para ajustar ou confirma a inclusão.

O fluxo não insere o contrato nem altera dados permanentes. A projeção só é
calculada com a aba Projeção aberta.

### FA02 - Cancelar inclusão

O usuário seleciona **Cancelar**. O sistema fecha o modal sem gravar o contrato e limpa os PDFs selecionados.

## Fluxos de exceção

### FE01 - Campo obrigatório ausente

O sistema interrompe a gravação e informa os campos que precisam ser preenchidos.

### FE02 - Valor ou prazo inválido

O sistema rejeita valores financiados, taxas ou prazos menores ou iguais a
zero. O pagamento de carência pode ser zero, mas não pode ser negativo.

### FE03 - Datas inconsistentes

O sistema rejeita datas fora da ordem esperada entre emissão, BNDES, primeiro encargo, primeiro principal e última parcela.

### FE04 - Contrato duplicado

O banco rejeita a gravação quando o `número_contrato` já existir, conforme a restrição atual de unicidade.

### FE05 - Falha de persistência

O sistema informa a falha de comúnicação ou gravação e não deve considerar o contrato incluído.

### FE06 - Banco indisponível

O sistema informa que não foi possível acessar o banco de dados e não confirma
a inclusão do contrato.

### FE07 - Falha na projeção temporária

A aba Projeção informa que não foi possível calcular a projeção, com o motivo
retornado pelo banco, e o contrato continua sem persistência.

### FE08 - Anexo inválido

PDF inválido, acima de 20 MB ou repetido no mesmo envio: nada é gravado e o
sistema informa o arquivo e a aba (RN26).

## Regras de negócio

- O contrato deve possuir período de carência conforme a regra inicial do negócio.
- A exclusão lógica não faz parte destá fase.
- O cálculo financeiro e executado pelo banco de dados.
- O vínculo de bens e veículos está previsto para a versão 1.0.
- A taxa de juros efetiva é informada com até 6 casas decimais e usada assim
  na projeção temporária (FA01); a coluna `contratos.taxa_juros_efetiva`
  (`numeric(10, 5)`) ainda grava só 5 casas e arredonda a sexta (`BL-024`).

## Dados persistidos

Empresa, banco, número do contrato, datas, tipo, valor financiado, Selic, taxas, prazos, parâmetros de cobrança e debito em conta corrente.

## Auditoria

A inclusão registra `CONTRATO_INCLUIR` (e um `ANEXO_INCLUIR` por PDF anexado) em `financiamento.log_auditoria` na mesma transação do contrato (número, empresa, banco, tipo, valor e emissão em `detalhes`). Falhas, como número duplicado, são registradas com `sucesso = false` e o erro (RF08.1, RN12).
