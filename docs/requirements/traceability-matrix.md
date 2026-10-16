# Matriz de Rastreabilidade

A matriz relaciona requisitos, regras, Use Cases e estado da implementação. Para
ver o motivo de cada status, as lacunas e a próxima ação, consulte o
[Registro de Status e Pendências](status-register.md).

| Requisito | Regras relacionadas | Use Case | Status | Pendência principal |
| --- | --- | --- | --- | --- |
| RF01 | RN04, RN05, RN25 | UC08 | Implementado | Agendar a importação; confirmar acesso do servidor ao site do BNDES. |
| RF02, RF02.1 | RN01, RN06 | UC01 | Parcial | Completar fluxo de contrato e recursos planejados. |
| RF02.3 | RN02.1 | UC01 | Implementado | Funções PostgreSQL, queries, service e exibição no modal concluídos. |
| RF02.2 | RN08 | UC05 | Planejado | Implementar vínculo de bens e veículos. |
| RF03 | - | UC02 | Implementado | Validar tratamento de erros e desempenho. |
| RF03.1 | RN26 | UC02, UC14 | Parcial | Empresa, banco, contrato e "Somente sem anexos" entregues; demais filtros planejados. |
| RF03.2 | RN12, RN26 | UC14 | Implementado | Novas abas no detalhe conforme evolução. |
| RF04, RF04.1 | RN01, RN08 | UC05 | Planejado | Implementar consulta e filtros de veículos. |
| RF05 | RN07, RN08, RN21 | UC04 | Implementado | Bloqueio com mensagem para liquidação e antecipação; exclusão lógica em avaliação. |
| RF06 | RN08 | UC05 | Planejado | Definir e implementar exclusão de veículos. |
| RF07 | RN02, RN03 | UC03 | Implementado | Projeção persistida (DA08); corrigir bugs herdados das MVs (BL-027). |
| RF07.1 | RN02, RN05, RN09, RN13, RN14, RN15, RN19 | UC06 | Implementado | Suportar modalidades além de BNDES FINAME SELIC; validar cálculo com o financeiro. |
| RF07.2 | RN19, RN20, RN21 | UC07 | Implementado | Perfis para liquidar/estornar (BL-005). |
| RF07.3 | RN02, RN03, RN20, RN24 | UC09 | Implementado | Contas a Pagar com data base e exportação; validar com o financeiro. |
| RF07.4 | RN02, RN03, RN24 | UC10 | Implementado | Demais modalidades (consórcios, tributário) fora do Nexus. |
| RF07.5 | RN08, RN10 | UC11 | Implementado | Validar com o financeiro; avaliar exportação. |
| RF07.6 | RN19, RN20, RN22, RN23 | UC13 | Implementado | Tratar antecipações vindas no CSV do ERP (BL-028). |
| RF07.7 | RN23 | UC13 | Implementado | Tela de cadastro de vínculos (BL-029). |
| RF08 | RN12 | UC02, UC04 | Parcial | Registro implementado (RF08.1); falta consulta na interface (RF08.2). |
| RF08.1 | RN12 | UC01, UC04, UC06, UC07, UC08, UC12, UC13 | Implementado | Retenção do log e usuário de banco somente-inserção (BL-022). |
| RF08.2 | RN12 | A definir | Planejado | Definir tela de histórico (BL-021). |
| RF09 | RN20 | UC07, UC13 | Implementado | Ajuste gravado na liquidação; autorização por perfil (BL-005). |
| RF10 | RN11 | Todos os casos protegidos | Parcial | Autenticação entregue; implementar perfis (RF10.4). |
| RF10.1, RF10.2, RF10.3 | RN11, RN12, RN16, RN17, RN18 | UC12 | Implementado | Pendências de segurança BL-014 a BL-018. |
| RF10.4 | RN11 | Todos os casos protegidos | Planejado | Definir matriz de perfis e permissões (BL-005). |
| RNF01-RNF03 | - | Todos | Atual | Manter padrão arquitetural e configuração segura. |
| RNF04-RNF05 | RN11, RN17 | Todos | Parcial | Perfis pendentes; remover `.env` do Git e rotacionar segredos (BL-014). |
| RNF06-RNF12 | RN02, RN08, RN12 | UC01, UC03, UC04, UC06 | Parcial | Auditoria registrada; completar logs técnicos, consulta do histórico e recuperação. |
| RNF15 | - | Todos | Implementado | Confirmar Streamlit 1.63.0 na imagem `fin-base:1.0` (BL-025). |

## Critério de cobertura

Um requisito será considerado coberto quando possuir descricao aprovada, caso
 de uso aplicável, critério de aceite e teste executavel ou procedimento de
 validação documentado.
