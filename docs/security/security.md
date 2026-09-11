# Segurança

## Estado atual

A aplicação atual não implementa autenticação, autorização por perfil ou
trilha de auditoria. O acesso deve permanecer restrito ao ambiente controlado
até que esses mecanismos sejam implementados.

## Requisitos de segurança

- Credenciais devem ser fornecidas por variaveis de ambiente.
- Arquivos `.env` não devem ser versionados.
- Senhas, tokens e dados sensiveis não devem aparecer em logs.
- O usuário do banco deve possuir apenas as permissões necessárias.
- Operacoes financeiras devem ser protegidas por perfil quando a autenticação
  for implementada.
- Exclusoes e liquidacoes devem ser rastreaveis em evolução futura.
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

- Acesso sem autenticação formal.
- Exclusão física sem trilha de auditoria.
- Credenciais dependentes de configuração externa.
- Ausencia de política formal de backup e restauração.
