# Requisitos Nao Funcionais

Os requisitos abaixo orientam a qualidade, seguranca, operacao e manutencao do
sistema. Os itens sem implementacao atual representam criterios para a versao
1.0 ou evolucoes posteriores.

| ID | Categoria | Requisito | Status |
| --- | --- | --- | --- |
| RNF01 | Arquitetura | A aplicacao deve utilizar Streamlit e acessar PostgreSQL por SQLAlchemy. | Atual |
| RNF02 | Calculo | Calculos financeiros devem ser executados exclusivamente no banco de dados. | Atual |
| RNF03 | Configuracao | Credenciais do banco devem ser fornecidas por variaveis de ambiente, nunca por codigo-fonte. | Atual |
| RNF04 | Seguranca | O sistema deve possuir autenticacao e perfis de acesso. | Planejado para a versao 1.0 |
| RNF05 | Seguranca | Segredos nao devem ser versionados no Git nem exibidos em logs. | Obrigatorio |
| RNF06 | Integridade | Operacoes de escrita devem utilizar transacoes e respeitar chaves estrangeiras. | Parcialmente implementado |
| RNF07 | Observabilidade | Falhas de aplicacao e banco devem possuir mensagens e logs suficientes para diagnostico. | Parcial |
| RNF08 | Auditoria | Operacoes financeiras devem permitir rastrear usuario, data, operacao e resultado. | Planejado |
| RNF09 | Disponibilidade | A aplicacao deve iniciar por container e expor a porta configurada para o servico. | Atual |
| RNF10 | Desempenho | Consultas de listagem e projecao devem possuir tempo de resposta aceitavel para o volume operacional. | A medir |
| RNF11 | Recuperacao | Devem existir procedimentos de backup, restauracao e validacao do banco. | Planejado |
| RNF12 | Manutenibilidade | Codigo, SQL e documentacao devem permanecer versionados e rastreaveis. | Atual |
| RNF13 | Privacidade | Dados cadastrais e financeiros devem observar politicas internas e requisitos aplicaveis da LGPD. | A definir |
| RNF14 | Compatibilidade | A interface deve funcionar em navegador suportado pelo ambiente corporativo. | A validar |

## Criterios de aceite

Os valores de desempenho, disponibilidade, retencao, RTO e RPO devem ser
preenchidos pelo responsavel operacional antes da entrada em producao.
