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

## DA04 - Autenticação própria com sessão em cookie assinado

**Status:** Aceita (autenticação implementada; perfis planejados para a versão 1.0)  
**Decisão:** A autenticação é feita pela própria aplicação, sem provedor
externo:

- usuários em `financiamento.usuarios`, criados somente pelo desenvolvedor,
  sem senha; o próprio usuário cadastra a senha no primeiro acesso;
- senha armazenada somente como hash `scrypt` (biblioteca padrão do Python,
  `hashlib.scrypt`, N=2^14, r=8, p=1, salt aleatório de 16 bytes), no formato
  `scrypt$n$r$p$salt$hash` — os parâmetros ficam gravados, permitindo
  aumentá-los depois sem invalidar senhas;
- sessão mantida por cookie `nexus_sessao` com usuário e expiração assinados
  por HMAC-SHA256 com a chave `AUTH_SECRET` (variável de ambiente), válido
  por 30 minutos deslizantes; o cookie é gravado via JavaScript
  (`st.html(..., unsafe_allow_javascript=True)`) e lido por
  `st.context.cookies`, pois o Streamlit não grava cookies nativamente;
- sem login, a navegação registra apenas a página de login.

**Motivo:** A imagem base `fin-base:1.0` não traz bibliotecas de hash
(bcrypt/argon2) nem de cookies, e o controle de usuários é interno e de baixo
volume.  
**Consequência:** O cookie não pode ser `HttpOnly` (gravado por JS) e um
cookie copiado vale até expirar; o vazamento do `AUTH_SECRET` permite forjar
login. Pendências registradas em BL-014 a BL-018. Perfis e permissões
(RF10.4) continuam planejados para a versão 1.0.

## DA06 - Log de auditoria no banco, na mesma transação e somente inserção

**Status:** Aceita  
**Decisão:** Toda operação de escrita e todo evento de acesso são registrados
em `financiamento.log_auditoria` por `services/log.py`:

- escritas gravam o log **na mesma transação** da operação
  (`registrar_log(..., conn=conn)`): sem log, sem operação;
- falhas são gravadas em transação própria (`registrar_log_falha`), com
  `sucesso = false` e o erro, sem esconder a mensagem original ao usuário;
- inclusões usam `RETURNING id` e exclusões `DELETE ... RETURNING *`, guardando
  a cópia do registro excluído em `detalhes` (jsonb);
- a tabela é somente inserção: triggers bloqueiam UPDATE, DELETE e TRUNCATE;
- consultas e relatórios somente leitura não são registrados;
- senha, hash, token e segredos nunca vão para o log.

Ações do catálogo: `LOGIN`, `LOGIN_FALHA`, `LOGOUT`, `SESSAO_ENCERRADA`,
`CADASTRO_SENHA`, `CONTRATO_INCLUIR`, `CONTRATO_EXCLUIR`,
`ANTECIPACAO_INCLUIR`, `QUITACAO_INCLUIR` (e, com os perfis, `ACESSO_NEGADO`).

**Motivo:** Rastrear quem fez o quê, quando e com qual resultado (RNF08),
inclusive o conteúdo de registros excluídos fisicamente (DA02), garantindo
que nenhuma operação fique sem registro.  
**Consequência:** Toda funcionalidade nova deve avaliar a necessidade de log
(regra registrada no `CLAUDE.md`). Testes de escrita no banco de
desenvolvimento devem rodar dentro de transação desfeita, pois o log não pode
ser apagado. O usuário `fin` é dono da tabela e poderia remover o trigger;
retenção e usuário somente-inserção estão em BL-022.
