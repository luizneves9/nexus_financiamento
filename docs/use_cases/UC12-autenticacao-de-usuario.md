# UC12 - Autenticação de Usuário

**Status:** Implementado (perfis e permissões planejados)  
**Ator principal:** Usuário do sistema  
**Ator secundário:** Desenvolvedor (cria, reseta e bloqueia usuários no banco)  
**Requisitos associados:** RF10, RF10.1, RF10.2, RF10.3, RF08.1, RN11, RN12, RN16, RN17, RN18

**Rastreamento detalhado:** [Registro de Status e Pendências](../requirements/status-register.md#uc12---autenticação-de-usuário)

## Objetivo

Garantir que somente usuários cadastrados acessem o sistema, permitindo que
cada usuário cadastre a própria senha no primeiro acesso, mantendo o login
por um período limitado e registrando cada evento de acesso no log de
auditoria.

## Pre-condicoes

1. A tabela `financiamento.usuarios` existe (`database/usuarios.sql`).
2. A tabela `financiamento.log_auditoria` existe
   (`database/log_auditoria.sql`).
3. O desenvolvedor criou o usuário no banco, sem senha:
   `INSERT INTO financiamento.usuarios (usuario) VALUES ('<usuario>');`
4. A variável `AUTH_SECRET` está configurada no `.env` (sem ela o login
   funciona, mas não persiste ao fechar o navegador).

## Pos-condicoes

- Usuário autenticado vê o menu completo, seu nome e o botão **Sair** na
  barra lateral.
- Cookie `nexus_sessao` assinado grava o login no navegador por 30 minutos.
- O evento é registrado em `financiamento.log_auditoria`.

## Fluxo principal - Login

1. O usuário acessa o sistema; sem sessão válida, apenas a tela de login é
   exibida (nenhuma aba é registrada na navegação).
2. O usuário informa **Usuário** e **Senha** e aciona **Entrar**.
3. O sistema busca o usuário em `financiamento.usuarios` e confere a senha
   contra o hash gravado.
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
5. O sistema grava somente o hash `scrypt` e registra `CADASTRO_SENHA` no log
   na mesma transação. O cadastro só ocorre se a senha ainda estiver vazia no
   banco (`WHERE senha_hash IS NULL`).
6. O usuário entra no sistema e vê "Senha cadastrada com sucesso!".

O texto **Voltar/cancelar**, abaixo do formulário, retorna à tela de login.

### FA02 - Retorno com sessão válida

1. O usuário fecha o navegador e o reabre em até 30 minutos após o último
   uso.
2. O sistema valida a assinatura e a expiração do cookie e confere no banco
   se o usuário continua ativo e com senha.
3. O sistema registra `LOGIN` (`origem: cookie`) e entra direto, sem pedir
   senha.

### FA03 - Sair

1. O usuário aciona **Sair** na barra lateral.
2. O sistema registra `LOGOUT`, encerra a sessão, apaga o cookie e recarrega
   a página, zerando filtros e estado. A tela de login é exibida.

## Fluxos de exceção

### FE01 - Dados incorretos

Usuário inexistente, bloqueado, senha errada, senha vazia de usuário que já
tem senha, ou senha preenchida de usuário que ainda não cadastrou senha: o
sistema exibe a notificação "Usuário ou senha incorretos." (sem revelar qual
foi o caso) e registra `LOGIN_FALHA` com o motivo real em `detalhes`.

### FE02 - Senha inválida no cadastro

Menos de 8 caracteres ou confirmação diferente: o sistema exibe a
notificação correspondente e não grava a senha.

### FE03 - Senha cadastrada por outra sessão

Se a senha foi cadastrada (ou o usuário bloqueado) entre o login e o
cadastro, o sistema informa "Não foi possível cadastrar a senha. Faça o login
novamente." e volta para o login.

### FE04 - Usuário bloqueado ou senha resetada durante a sessão

Na renovação da sessão (no máximo a cada 5 minutos), o sistema confere o
usuário no banco; se não estiver mais ativo ou com senha, registra
`SESSAO_ENCERRADA` e volta para a tela de login.

### FE05 - Banco indisponível

O sistema informa "Não foi possível acessar o banco de dados." e não
autentica.

## Regras de negócio

- Acesso somente autenticado (RN11).
- Usuários criados apenas pelo desenvolvedor; primeiro acesso com senha
  vazia (RN16).
- Senha mínima de 8 caracteres, armazenada só como hash (RN17).
- Sessão de 30 minutos deslizantes; Sair encerra imediatamente (RN18).
- Todos os eventos de acesso são registrados no log, sem senha, hash ou
  token (RN12).

## Operações do desenvolvedor

Comandos em `database/usuarios.sql`:

- **Criar usuário:** `INSERT INTO financiamento.usuarios (usuario) VALUES ('...');`
- **Resetar senha:** `UPDATE ... SET senha_hash = NULL, senha_definida_em = NULL WHERE usuario = '...';`
- **Bloquear:** `UPDATE ... SET ativo = false WHERE usuario = '...';`
- **Conferir:** consulta que mostra se a senha foi cadastrada sem exibir o hash.

## Limitações conhecidas

- Enquanto o usuário não cadastra a senha, quem souber o nome dele pode
  cadastrar primeiro; o usuário deve cadastrar logo após ser criado (em caso
  de problema, resetar a senha).
- Um cookie copiado continua válido até expirar, mesmo após **Sair**
  (BL-017).
- Sem limite de tentativas de login (BL-016) e sem HTTPS garantido (BL-015).
- Perfis e permissões por aba/ação ainda não existem (RF10.4).

## Dados persistidos

- `financiamento.usuarios`: `senha_hash` e `senha_definida_em` no cadastro de
  senha.
- `financiamento.log_auditoria`: um registro por evento de acesso.

## Evidência

- `src/main.py` (bloqueio da navegação sem login, barra lateral com Sair).
- `src/views/login.py` (tela de login e cadastro de senha).
- `src/services/login.py` (hash, autenticação, sessão e cookie).
- `src/queries/queries_login.py` e `src/repositories/login.py`.
- `src/services/log.py` (registro dos eventos).
- `database/usuarios.sql`.
