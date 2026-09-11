# UC05 - Cadastro de Bens e Veículos

**Status:** Planejado para a versão 1.0; estruturas de banco disponíveis  
**Ator principal:** Usuario responsável pelo setor financeiro  
**Requisitos associados:** RF02.2, RF04, RF04.1, RN01

**Rastreamento detalhado:** [Registro de Status e Pendências](../requirements/status-register.md#uc05---cadastro-de-bens-e-veículos)

## Objetivo

Cadastrar bens, associar fornecedores e contratos e formar veículos a partir de bens de chassi e carroceria.

## Pre-condicoes

1. O contrato está cadastrado.
2. O fornecedor está cadastrado.
3. O usuário possui permissão de escrita conforme o controle de acesso que
	será implementado na versão 1.0.

## Pos-condicoes

- O bem e persistido em `financiamento.bem`.
- O bem e associado a fornecedor e contrato.
- Quando aplicável, a associação de chassi e carroceria é persistida em `financiamento.veiculos`.

## Fluxo principal

1. O usuário informa contrato, fornecedor, descricao, marca, modelo, anos, placa, chassi e valor de venda.
2. O sistema valida os dados obrigatórios.
3. O sistema grava o bem.
4. O usuário associa os bens de chassi e carroceria.
5. O sistema grava o veiculo.

## Fluxos alternativos

### FA01 - Bem sem veiculo completo

O bem pode ser cadastrado antes da associação final de chassi e carroceria,
conforme regra que será definida durante a implementação da versão 1.0.

## Fluxos de exceção

### FE01 - Contrato ou fornecedor inexistente

A chave estrangeira impede a gravação.

### FE02 - Chassi ou placa duplicados

A regra de duplicidade será definida e implementada durante o desenvolvimento dos veículos.

## Regras de negócio

- A tabela `bem` referencia contrato e fornecedor.
- A tabela `veiculos` associa dois registros de `bem`.
- As regras de unicidade de chassi, placa e situação ativa seráo definidas
	durante a implementação do modulo.
