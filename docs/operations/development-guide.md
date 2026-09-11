# Guia de Desenvolvimento

## Estrutura do código

- Views e componentes de interface ficam em `src/views`.
- Orquestração fica em `src/services`.
- Acesso ao banco fica em `src/repositories`.
- SQL fica em `src/queries`.
- Conexao e configuração ficam em `src/database` e `src/config`.

## Convenções

- Preservar as camadas existentes ao criar funcionalidades.
- Manter SQL em arquivos de queries, evitando SQL espalhado nas views.
- Usar transacoes para operações de escrita.
- Não ocultar exceções de banco sem registrar ou apresentar contexto.
- Atualizar Use Cases, requisitos e matriz de rastreabilidade quando o fluxo
  funcional mudar.
- Adicionar testes para novas regras de negócio e cálculos.

## Fluxo de alteração

1. Atualizar requisito ou regra quando houver mudanca de comportamento.
2. Atualizar Use Case e matriz de rastreabilidade.
3. Alterar código e/ou DDL.
4. Executar verificacoes de sintaxe e testes.
5. Revisar documentação e impacto operacional.
6. Submeter a alteração para revisão.
