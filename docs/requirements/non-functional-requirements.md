# Requisitos Não Funcionais

Os requisitos abaixo orientam a qualidade, segurança, operação e manutenção do
sistema. Os itens sem implementação atual representam critérios para a versão
1.0 ou evoluções posteriores.

| ID | Catégoria | Requisito | Status |
| --- | --- | --- | --- |
| RNF01 | Arquitetura | A aplicação deve utilizar Streamlit e acessar PostgreSQL por SQLAlchemy. | Atual |
| RNF02 | Calculo | Cálculos financeiros devem ser executados exclusivamente no banco de dados. | Atual |
| RNF03 | Configuração | Credenciais do banco devem ser fornecidas por variaveis de ambiente, nunca por código-fonte. | Atual |
| RNF04 | Segurança | O sistema deve possuir autenticação e perfis de acesso. Senhas armazenadas somente como hash `scrypt` com salt; sessão em cookie assinado (HMAC-SHA256) com a chave `AUTH_SECRET`. | Parcial (autenticação implementada; perfis planejados) |
| RNF05 | Segurança | Segredos não devem ser versionados no Git nem exibidos em logs. | Obrigatorio — **violado**: `.env` versionado desde o commit inicial (ver BL-014) |
| RNF06 | Integridade | Operacoes de escrita devem utilizar transacoes e respeitar chaves estrangeiras. | Parcialmente implementado |
| RNF07 | Observabilidade | Falhas de aplicação e banco devem possuir mensagens e logs suficientes para diagnostico. | Parcial |
| RNF08 | Auditoria | Operacoes financeiras devem permitir rastrear usuário, data, operação e resultado. | Implementado (registro em `log_auditoria`); consulta na interface planejada |
| RNF09 | Disponibilidade | A aplicação deve iniciar por container e expor a porta configurada para o servico. | Atual |
| RNF10 | Desempenho | Consultas de listagem e projeção devem possuir tempo de resposta aceitavel para o volume operacional. | A medir |
| RNF11 | Recuperação | Devem existir procedimentos de backup, restauração e validação do banco. | Planejado |
| RNF12 | Manutenibilidade | Codigo, SQL e documentação devem permanecer versionados e rastreaveis. | Atual |
| RNF13 | Privacidade | Dados cadastrais e financeiros devem observar políticas internas e requisitos aplicaveis da LGPD. | A definir |
| RNF14 | Compatibilidade | A interface deve funcionar em navegador suportado pelo ambiente corporativo. | A validar |

## Critérios de aceite

Os valores de desempenho, disponibilidade, retenção, RTO e RPO devem ser
preenchidos pelo responsável operacional antes da entrada em producao.
