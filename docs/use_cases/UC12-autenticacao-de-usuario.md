# UC12 - Autenticação de Usuário

**Status:** Implementado (perfis e permissões planejados)  
**Ator principal:** Usuário do sistema  
**Ator secundário:** Administrador do portal Nexus (cria usuários, dá acesso ao módulo, reseta senha e bloqueia na tela Administração do `nexus_portal`)  
**Requisitos associados:** RF10, RF10.1, RF10.2, RF10.3, RF08.1, RN11, RN12, RN16, RN17, RN18

**Rastreamento detalhado:** [Registro de Status e Pendências](../requirements/status-register.md#uc12---autenticação-de-usuário)

## Objetivo

Garantir que somente usuários cadastrados acessem o sistema, permitindo que
cada usuário cadastre a própria senha no primeiro acesso, mantendo o login
por um período limitado e registrando cada evento de acesso no log de
auditoria.

## Pre-condicoes

1. O schema `nexus` do portal existe (`nexus_portal/database/01_nexus.sql`):
   cadastro único de usuários `nexus.usuarios` e acesso por módulo
   `nexus.usuario_modulos`.
2. A tabela `financiamento.log_auditoria` existe
   (`database/log_auditoria.sql`), com a FK de `id_usuario` para
   `nexus.usuarios` (`database/usuarios_nexus.sql`).
3. O usuário existe em `nexus.usuarios` (criado sem senha pelo portal) e tem
   acesso ao módulo: linha em `nexus.usuario_modulos` com
   `modulo = 'financiamento'`.
4. A variável `AUTH_SECRET` está configurada no `.env` (sem ela o login
   funciona, mas não persiste ao fechar o navegador).

## Pos-condicoes

- Usuário autenticado vê o menu completo, seu nome e o botão **Sair** fixos
  no rodapé da barra lateral.
- Cookie `nexus_sessao` assinado grava o login no navegador por 30 minutos.
- O evento é registrado em `financiamento.log_auditoria`.

## Fluxo principal - Login

1. O usuário acessa o sistema; sem sessão válida, apenas a tela de login é
   exibida (nenhuma aba é registrada na navegação), com a logo do sistema
   acima do formulário e, abaixo, a orientação "Esqueceu a senha ou ainda
   não tem acesso? Fale com o administrador do sistema.".
2. O usuário informa **Usuário** e **Senha** e aciona **Entrar**.
3. O sistema busca o usuário em `nexus.usuarios`, confere se ele tem acesso
   ao Financiamento (`nexus.usuario_modulos`) e confere a senha contra o hash
   gravado.
4. O sistema registra `LOGIN` (`origem: senha`) no log, guarda o usuário na
   sessão e exibe o sistema.
5. O sistema grava o cookie de sessão, renovado enquanto o usuário usa o
   sistema (no máximo a cada 5 minutos).

## Fluxos alternativos

### FA01 - Primeiro acesso (cadastro de senha)

1. O usuário informa o nome e deixa a senha **vazia**.
2. O sistema identifica que o usuário está ativo e sem senha cadastrada e
   exibe "Primeiro acesso de **usuário**. Cadastre sua senha." com os campos
   **Nova senha** e **Confirmar senha**.
3. O usuário informa e confirma a senha e aciona **Cadastrar senha**.
4. O sistema valida mínimo de 8 caracteres e confirmação igual (RN17).
5. O sistema grava somente o hash `scrypt` em `nexus.usuarios` e registra
   `CADASTRO_SENHA` no log na mesma transação. O cadastro só ocorre se a
   senha ainda estiver vazia no banco (`WHERE senha_hash IS NULL`) e o
   usuário tiver acesso ao Financiamento. A senha vale para o portal e todos
   os módulos (cadastro único).
6. O usuário entra no sistema e vê "Senha cadastrada com sucesso!".

O texto **Voltar/cancelar**, abaixo do formulário, retorna à tela de login.

### FA02 - Retorno com sessão válida

1. O usuário fecha o navegador e o reabre em até 30 minutos após o último
   uso.
2. O sistema valida a assinatura e a expiração do cookie e confere no banco
   se o usuário continua ativo, com acesso ao Financiamento e com senha.
3. O sistema registra `LOGIN` (`origem: cookie`) e entra direto, sem pedir
   senha.

### FA03 - Sair

1. O usuário aciona **Sair** na barra lateral.
2. O sistema registra `LOGOUT`, encerra a sessão, apaga o cookie e recarrega
   a página, zerando filtros e estado. A tela de login é exibida.

## Fluxos de exceção

### FE01 - Dados incorretos

Usuário inexistente, bloqueado, sem acesso ao Financiamento em
`nexus.usuario_modulos` (motivo `sem_permissao`), senha errada, senha vazia
de usuário que já tem senha, ou senha preenchida de usuário que ainda não
cadastrou senha: o
sistema exibe a notificação "Usuário ou senha incorretos." (sem revelar qual
foi o caso) e registra `LOGIN_FALHA` com o motivo real em `detalhes`.

### FE02 - Senha inválida no cadastro

Menos de 8 caracteres ou confirmação diferente: o sistema exibe a
notificação correspondente e não grava a senha.

### FE03 - Senha cadastrada por outra sessão

Se a senha foi cadastrada (ou o usuário bloqueado) entre o login e o
cadastro, o sistema informa "Não foi possível cadastrar a senha. Faça o login
novamente." e volta para o login.

### FE04 - Usuário bloqueado, sem acesso ou com senha resetada durante a sessão

Na renovação da sessão (no máximo a cada 5 minutos), o sistema confere o
usuário no banco; se não estiver mais ativo, com acesso ao Financiamento ou
com senha, registra
`SESSAO_ENCERRADA` e volta para a tela de login.

### FE05 - Banco indisponível

O sistema informa "Não foi possível acessar o banco de dados." e não
autentica.

## Regras de negócio

- Acesso somente autenticado (RN11).
- Usuários criados apenas pelo administrador (portal Nexus); primeiro acesso
  com senha vazia (RN16).
- Senha mínima de 8 caracteres, armazenada só como hash (RN17).
- Sessão de 30 minutos deslizantes; Sair encerra imediatamente (RN18).
- Todos os eventos de acesso são registrados no log, sem senha, hash ou
  token (RN12).

## Operações do administrador

Na tela **Administração** do portal Nexus (`nexus_portal`, com log no
`nexus.log_auditoria`), ou pelos SQLs do fim de
`nexus_portal/database/01_nexus.sql`:

- **Criar usuário** (sem senha) e **dar/retirar acesso ao Financiamento**
  (`nexus.usuario_modulos`, `modulo = 'financiamento'`).
- **Resetar senha** (vale para todos os módulos) e **bloquear**
  (`nexus.usuarios.ativo = false`, bloqueia o portal e todos os módulos).

Até 11/2026 os usuários ficavam em `financiamento.usuarios`
(`database/usuarios.sql`); a troca está em `database/usuarios_nexus.sql`
(senha copiada para quem não tinha no `nexus`; FK do log para
`nexus.usuarios` com `NOT VALID` — logs anteriores guardam o id antigo, vale
a coluna `usuario`).

## Limitações conhecidas

- Enquanto o usuário não cadastra a senha, quem souber o nome dele pode
  cadastrar primeiro; o usuário deve cadastrar logo após ser criado (em caso
  de problema, resetar a senha).
- Um cookie copiado continua válido até expirar, mesmo após **Sair**
  (BL-017).
- Sem limite de tentativas de login (BL-016) e sem HTTPS garantido (BL-015).
- Perfis e permissões por aba/ação ainda não existem (RF10.4); o acesso é
  por módulo (`nexus.usuario_modulos`).
- O login ainda é próprio do módulo (cookie `nexus_sessao`, porta 8502); o
  login único do portal (cookie `nexus_acesso`, rota `/financiamento`) é a
  etapa 2 da publicação.

## Dados persistidos

- `nexus.usuarios`: `senha_hash` e `senha_definida_em` no cadastro de
  senha.
- `financiamento.log_auditoria`: um registro por evento de acesso.

## Evidência

- `src/main.py` (bloqueio da navegação sem login, rodapé da barra lateral com
  usuário e Sair).
- `src/views/login.py` (tela de login e cadastro de senha).
- `src/services/login.py` (hash, autenticação, sessão e cookie).
- `src/queries/queries_login.py` e `src/repositories/login.py`.
- `src/services/log.py` (registro dos eventos).
- `database/usuarios_nexus.sql` (troca para `nexus.usuarios`) e
  `database/usuarios.sql` (tabela antiga).
