# Segurança

## Estado atual

- **Autenticação:** implementada (UC12, DA04). Usuários em
  `financiamento.usuarios`, senha em hash `scrypt` com salt, sessão em cookie
  assinado por HMAC-SHA256 (`AUTH_SECRET`) válido por 30 minutos
  deslizantes. Mensagem de erro genérica para não revelar quais usuários
  existem.
- **Auditoria:** implementada (RF08.1, DA06). Escritas e eventos de acesso
  gravados em `financiamento.log_auditoria`, somente inserção.
- **Autorização por perfil:** ainda não existe (RF10.4); todo usuário
  autenticado acessa todas as abas e ações.

O acesso deve permanecer restrito ao ambiente controlado até que as
pendências críticas abaixo sejam resolvidas.

## Avaliação do hash de senha

`scrypt` com N=2^14, r=8, p=1 custa cerca de 68 ms e 16 MiB por tentativa
(medido em desenvolvimento), o que encarece ataques de força bruta em massa,
principalmente em GPU. É o mínimo clássico; a OWASP recomenda N=2^17
(cerca de 543 ms e 128 MiB, pesado para logins simultâneos). O meio-termo
avaliado é N=2^15 (cerca de 135 ms, 32 MiB) — BL-018. O hash protege bem
senhas boas; senhas fracas caem por lista de palavras com qualquer
algoritmo.

## Requisitos de segurança

- Credenciais devem ser fornecidas por variaveis de ambiente.
- Arquivos `.env` não devem ser versionados.
- Senhas, tokens e dados sensiveis não devem aparecer em logs.
- O usuário do banco deve possuir apenas as permissões necessárias.
- Operacoes financeiras devem ser protegidas por perfil quando a autenticação
  for implementada.
- Exclusões, liquidações e eventos de acesso são rastreados no log de
  auditoria (DA06); o log nunca contém senha, hash ou token.
- Comúnicação com o banco deve utilizar canal protegido no ambiente de
  producao.

## Perfis previstos

A matriz definitiva ainda não foi aprovada. Como referencia inicial, podem ser
considerados:

- **Consulta:** visualiza dados e projeções.
- **Operacional:** inclui contratos e registra operações permitidas.
- **Financeiro:** executa operações financeiras.
- **Administrador:** administra cadastros, acessos e configuracoes.

## Dados e LGPD

O sistema trata dados cadastrais de empresas, bancos, fornecedores e dados
financeiros. Devem ser definidos finalidade, acesso, retenção, descarte,
backup e aténdimento a solicitacoes aplicaveis da LGPD.

## Riscos conhecidos

| Gravidade | Risco | Pendência |
| --- | --- | --- |
| Crítica | `.env` versionado no Git desde o commit inicial e enviado ao servidor Git (senha do banco no histórico); `AUTH_SECRET` iria no próximo commit; `Dockerfile` copia `.env` e `.git` para a imagem (sem `.dockerignore`). Com o `AUTH_SECRET`, é possível forjar cookie de login de qualquer usuário. | BL-014 |
| Alta | Sem HTTPS garantido e cookie sem `Secure`: senha e cookie podem trafegar em texto puro. | BL-015 |
| Alta | Sem limite de tentativas de login (força bruta e carga de CPU/memória do scrypt). | BL-016 |
| Média | Cookie copiado continua válido até expirar, mesmo após **Sair**; renovado indefinidamente com uso; volta a valer após reset e novo cadastro de senha. | BL-017 |
| Média | Cookie legível por JavaScript (sem `HttpOnly`); nenhum ponto de XSS identificado. | — |
| Média | Primeiro acesso pode ser tomado por quem souber o nome do usuário antes do cadastro da senha; o fluxo revela que o usuário existe. | Mitigação operacional (cadastrar logo após criar) |
| Média | Usuário `fin` é dono do log e poderia remover o trigger de imutabilidade; sem política de retenção. | BL-022 |
| Baixa | Diferença de tempo de resposta revela usuário sem senha cadastrada; regra de senha só exige 8 caracteres. | BL-018 |
| — | Ausência de perfis: todo usuário autenticado executa todas as ações. | BL-005 |
| — | Ausência de política formal de backup e restauração. | BL-009 |

## O que não é brecha (verificado)

- Acessar uma aba pela URL sem login: sem login, só a página de login é
  registrada.
- Alterar o `session_state`: fica no servidor.
- Cookie editado ou expirado: recusado pela assinatura/expiração.
- SQL injection: todas as queries usam parâmetros.
