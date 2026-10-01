# Matriz de Rastreabilidade

A matriz relaciona requisitos, regras, Use Cases e estado da implementação. Para
ver o motivo de cada status, as lacunas e a próxima ação, consulte o
[Registro de Status e Pendências](status-register.md).

| Requisito | Regras relacionadas | Use Case | Status | Pendência principal |
| --- | --- | --- | --- | --- |
| RF01 | RN04, RN05 | UC08 | Banco preparado | Implementar API ou job da Selic. |
| RF02, RF02.1 | RN01, RN06 | UC01 | Parcial | Completar fluxo de contrato e recursos planejados. |
| RF02.3 | RN02.1 | UC01 | Implementado | Funções PostgreSQL, queries, service e exibição no modal concluídos. |
| RF02.2 | RN08 | UC05 | Planejado | Implementar vínculo de bens e veículos. |
| RF03 | - | UC02 | Implementado | Validar tratamento de erros e desempenho. |
| RF03.1 | - | UC02 | Planejado | Implementar filtros. |
| RF04, RF04.1 | RN01, RN08 | UC05 | Planejado | Implementar consulta e filtros de veículos. |
| RF05 | RN07, RN08 | UC04 | Parcial | Formalizar dependências e procedimento operacional. |
| RF06 | RN08 | UC05 | Planejado | Definir e implementar exclusão de veículos. |
| RF07 | RN02, RN03 | UC03 | Parcial | Validar cálculos e completar recursos de consulta. |
| RF07.1 | RN02, RN05, RN09, RN13, RN14, RN15 | UC06 | Implementado | Suportar modalidades além de BNDES FINAME SELIC; validar cálculo com o financeiro. |
| RF07.2 | RN10 | UC07 | Consolidado em RF07.1/UC06 | Nenhuma — funcionalidade absorvida por UC06. |
| RF07.3 | RN02, RN03 | UC09 | Implementado | Filtros e resumo entregues; falta exportação e documentar a view no DDL. |
| RF07.4 | RN02, RN03 | UC10 | Implementado | Adicionar filtros/download e completar documentação da view no DDL. |
| RF07.5 | RN08, RN10 | UC11 | Implementado | Validar com o financeiro; avaliar exportação. |
| RF08 | RN12 | UC02, UC04 | Parcial | Registro implementado (RF08.1); falta consulta na interface (RF08.2). |
| RF08.1 | RN12 | UC01, UC04, UC06, UC12 | Implementado | Retenção do log e usuário de banco somente-inserção (BL-022). |
| RF08.2 | RN12 | A definir | Planejado | Definir tela de histórico (BL-021). |
| RF09 | RN11, RN12 | A definir | Planejado | Definir Use Case, ajustes e autorização. |
| RF10 | RN11 | Todos os casos protegidos | Parcial | Autenticação entregue; implementar perfis (RF10.4). |
| RF10.1, RF10.2, RF10.3 | RN11, RN12, RN16, RN17, RN18 | UC12 | Implementado | Pendências de segurança BL-014 a BL-018. |
| RF10.4 | RN11 | Todos os casos protegidos | Planejado | Definir matriz de perfis e permissões (BL-005). |
| RNF01-RNF03 | - | Todos | Atual | Manter padrão arquitetural e configuração segura. |
| RNF04-RNF05 | RN11, RN17 | Todos | Parcial | Perfis pendentes; remover `.env` do Git e rotacionar segredos (BL-014). |
| RNF06-RNF12 | RN02, RN08, RN12 | UC01, UC03, UC04, UC06 | Parcial | Auditoria registrada; completar logs técnicos, consulta do histórico e recuperação. |

## Critério de cobertura

Um requisito será considerado coberto quando possuir descricao aprovada, caso
 de uso aplicável, critério de aceite e teste executavel ou procedimento de
 validação documentado.
