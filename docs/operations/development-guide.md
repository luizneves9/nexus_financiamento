# Guia de Desenvolvimento

## Estrutura do codigo

- Views e componentes de interface ficam em `src/views`.
- Orquestracao fica em `src/services`.
- Acesso ao banco fica em `src/repositories`.
- SQL fica em `src/queries`.
- Conexao e configuracao ficam em `src/database` e `src/config`.

## Convencoes

- Preservar as camadas existentes ao criar funcionalidades.
- Manter SQL em arquivos de queries, evitando SQL espalhado nas views.
- Usar transacoes para operacoes de escrita.
- Nao ocultar excecoes de banco sem registrar ou apresentar contexto.
- Atualizar Use Cases, requisitos e matriz de rastreabilidade quando o fluxo
  funcional mudar.
- Adicionar testes para novas regras de negocio e calculos.

## Fluxo de alteracao

1. Atualizar requisito ou regra quando houver mudanca de comportamento.
2. Atualizar Use Case e matriz de rastreabilidade.
3. Alterar codigo e/ou DDL.
4. Executar verificacoes de sintaxe e testes.
5. Revisar documentacao e impacto operacional.
6. Submeter a alteracao para revisao.
