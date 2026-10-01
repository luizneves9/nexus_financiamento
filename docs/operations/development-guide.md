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
- **Avaliar log de auditoria em toda funcionalidade nova** (DA06): escritas e
  eventos de acesso gravam `registrar_log(...)` na mesma transação da
  operação; falhas usam `registrar_log_falha(...)`; consultas não são
  registradas. Nunca gravar senha, hash, token ou segredos.
- Testes que escrevem no banco de desenvolvimento devem rodar dentro de uma
  transação desfeita no final, pois o log de auditoria não pode ser apagado.
- Filtros de tela: widgets com `key` própria inicializada do filtro salvo,
  nunca `value=st.session_state...` (ver CLAUDE.md, "Filtros de tela").

## Fluxo de alteração

1. Atualizar requisito ou regra quando houver mudanca de comportamento.
2. Atualizar Use Case e matriz de rastreabilidade.
3. Alterar código e/ou DDL.
4. Avaliar e implementar o log de auditoria da funcionalidade.
5. Executar verificacoes de sintaxe e testes.
6. Revisar documentação e impacto operacional.
7. Submeter a alteração para revisão.
