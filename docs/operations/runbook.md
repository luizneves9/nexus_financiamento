# Runbook Operacional

## Diagnostico inicial

1. Verificar se o container está em execução.
2. Verificar conectividade com o host e a porta do PostgreSQL.
3. Conferir as variaveis do `.env` sem expor a senha.
4. Consultar os logs da aplicação e do banco.
5. Confirmar a existência do schema `financiamento`.

## Falhas comuns

### Aplicação não inicia

Verificar a imagem `fin-base:1.0`, dependências Python, porta 8502 e sintaxe
dos arquivos Python.

### Falha ao carregar cadastros

Verificar credenciais, conectividade, permissões do usuário e existência das
tabelas `empresas`, `bancos` e `fornecedor`.

### Projeção vazia ou desatualizada

Verificar contrato, dados da tabela `selic`, feriados, matérialized views e
rotinas de refresh.

### Exclusão rejeitada

Verificar registros dependentes em `bem` e `antecipacao`. A integridade
referencial pode impedir a exclusão física.

## Operacoes de banco

Atualizacoes, refresh de matérialized views, cargas de Selic e correcoes devem
ser executados por procedimento controlado, com registro da alteração e
backup quando aplicável.

## Backup e restauração

O procedimento oficial de backup, retenção, restauração, RTO e RPO ainda deve
ser definido pelo responsável de infraestrutura. Nenhuma restauração deve ser
executada em producao sem validação e autorização.
