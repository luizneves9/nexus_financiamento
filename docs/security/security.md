# Seguranca

## Estado atual

A aplicacao atual nao implementa autenticacao, autorizacao por perfil ou
trilha de auditoria. O acesso deve permanecer restrito ao ambiente controlado
ate que esses mecanismos sejam implementados.

## Requisitos de seguranca

- Credenciais devem ser fornecidas por variaveis de ambiente.
- Arquivos `.env` nao devem ser versionados.
- Senhas, tokens e dados sensiveis nao devem aparecer em logs.
- O usuario do banco deve possuir apenas as permissoes necessarias.
- Operacoes financeiras devem ser protegidas por perfil quando a autenticacao
  for implementada.
- Exclusoes e liquidacoes devem ser rastreaveis em evolucao futura.
- Comunicacao com o banco deve utilizar canal protegido no ambiente de
  producao.

## Perfis previstos

A matriz definitiva ainda nao foi aprovada. Como referencia inicial, podem ser
considerados:

- **Consulta:** visualiza dados e projecoes.
- **Operacional:** inclui contratos e registra operacoes permitidas.
- **Financeiro:** executa operacoes financeiras.
- **Administrador:** administra cadastros, acessos e configuracoes.

## Dados e LGPD

O sistema trata dados cadastrais de empresas, bancos, fornecedores e dados
financeiros. Devem ser definidos finalidade, acesso, retencao, descarte,
backup e atendimento a solicitacoes aplicaveis da LGPD.

## Riscos conhecidos

- Acesso sem autenticacao formal.
- Exclusao fisica sem trilha de auditoria.
- Credenciais dependentes de configuracao externa.
- Ausencia de politica formal de backup e restauracao.
