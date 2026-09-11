# Matriz de Rastreabilidade

A matriz relaciona requisitos, regras, Use Cases e estado da implementação. Para
ver o motivo de cada status, as lacunas e a próxima ação, consulte o
[Registro de Status e Pendências](status-register.md).

| Requisito | Regras relacionadas | Use Case | Status | Pendência principal |
| --- | --- | --- | --- | --- |
| RF01 | RN04, RN05 | UC08 | Banco preparado | Implementar API ou job da Selic. |
| RF02, RF02.1 | RN01, RN06 | UC01 | Parcial | Completar fluxo de contrato e recursos planejados. |
| RF02.2 | RN08 | UC05 | Planejado | Implementar vínculo de bens e veículos. |
| RF03 | - | UC02 | Implementado | Validar tratamento de erros e desempenho. |
| RF03.1 | - | UC02 | Planejado | Implementar filtros. |
| RF04, RF04.1 | RN01, RN08 | UC05 | Planejado | Implementar consulta e filtros de veículos. |
| RF05 | RN07, RN08 | UC04 | Parcial | Formalizar dependências e procedimento operacional. |
| RF06 | RN08 | UC05 | Planejado | Definir e implementar exclusão de veículos. |
| RF07 | RN02, RN03 | UC03 | Parcial | Validar cálculos e completar recursos de consulta. |
| RF07.1 | RN05, RN09 | UC06 | Banco preparado | Implementar tela e validar refresh da projeção. |
| RF07.2 | RN10 | UC07 | Planejado | Definir modelo e implementar liquidação. |
| RF08 | RN12 | UC02, UC04 | Planejado | Definir auditoria e histórico. |
| RF09 | RN11, RN12 | UC07 | Planejado | Definir ajustes e autorização. |
| RF10 | RN11 | Todos os casos protegidos | Planejado | Implementar autenticação e perfis. |
| RNF01-RNF03 | - | Todos | Atual | Manter padrão arquitetural e configuração segura. |
| RNF04-RNF05 | RN11 | Todos | Planejado | Implementar controle de acesso e segredos operacionais. |
| RNF06-RNF12 | RN02, RN08, RN12 | UC01, UC03, UC04, UC06 | Parcial | Completar transacoes, logs, auditoria e recuperação. |

## Critério de cobertura

Um requisito será considerado coberto quando possuir descricao aprovada, caso
 de uso aplicável, critério de aceite e teste executavel ou procedimento de
 validação documentado.
