# UC05 - Cadastro de Bens e Veiculos

**Status:** Planejado para a versao 1.0; estruturas de banco disponiveis  
**Ator principal:** Usuario responsavel pelo setor financeiro  
**Requisitos associados:** RF02.2, RF04, RF04.1, RN01

## Objetivo

Cadastrar bens, associar fornecedores e contratos e formar veiculos a partir de bens de chassi e carroceria.

## Pre-condicoes

1. O contrato esta cadastrado.
2. O fornecedor esta cadastrado.
3. O usuario possui permissao de escrita conforme o controle de acesso que
	sera implementado na versao 1.0.

## Pos-condicoes

- O bem e persistido em `financiamento.bem`.
- O bem e associado a fornecedor e contrato.
- Quando aplicavel, a associacao de chassi e carroceria e persistida em `financiamento.veiculos`.

## Fluxo principal

1. O usuario informa contrato, fornecedor, descricao, marca, modelo, anos, placa, chassi e valor de venda.
2. O sistema valida os dados obrigatorios.
3. O sistema grava o bem.
4. O usuario associa os bens de chassi e carroceria.
5. O sistema grava o veiculo.

## Fluxos alternativos

### FA01 - Bem sem veiculo completo

O bem pode ser cadastrado antes da associacao final de chassi e carroceria,
conforme regra que sera definida durante a implementacao da versao 1.0.

## Fluxos de excecao

### FE01 - Contrato ou fornecedor inexistente

A chave estrangeira impede a gravacao.

### FE02 - Chassi ou placa duplicados

A regra de duplicidade sera definida e implementada durante o desenvolvimento dos veiculos.

## Regras de negocio

- A tabela `bem` referencia contrato e fornecedor.
- A tabela `veiculos` associa dois registros de `bem`.
- As regras de unicidade de chassi, placa e situacao ativa serao definidas
	durante a implementacao do modulo.
