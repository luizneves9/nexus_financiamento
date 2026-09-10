# Runbook Operacional

## Diagnostico inicial

1. Verificar se o container esta em execucao.
2. Verificar conectividade com o host e a porta do PostgreSQL.
3. Conferir as variaveis do `.env` sem expor a senha.
4. Consultar os logs da aplicacao e do banco.
5. Confirmar a existencia do schema `financiamento`.

## Falhas comuns

### Aplicacao nao inicia

Verificar a imagem `fin-base:1.0`, dependencias Python, porta 8502 e sintaxe
dos arquivos Python.

### Falha ao carregar cadastros

Verificar credenciais, conectividade, permissoes do usuario e existencia das
tabelas `empresas`, `bancos` e `fornecedor`.

### Projecao vazia ou desatualizada

Verificar contrato, dados da tabela `selic`, feriados, materialized views e
rotinas de refresh.

### Exclusao rejeitada

Verificar registros dependentes em `bem` e `antecipacao`. A integridade
referencial pode impedir a exclusao fisica.

## Operacoes de banco

Atualizacoes, refresh de materialized views, cargas de Selic e correcoes devem
ser executados por procedimento controlado, com registro da alteracao e
backup quando aplicavel.

## Backup e restauracao

O procedimento oficial de backup, retencao, restauracao, RTO e RPO ainda deve
ser definido pelo responsavel de infraestrutura. Nenhuma restauracao deve ser
executada em producao sem validacao e autorizacao.
