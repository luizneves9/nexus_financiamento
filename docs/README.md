# Nexus - Documentação do Projeto

Esta pasta contém a documentação oficial do projeto. Ela reúne os requisitos,
as regras de negócio, a arquitetura, os casos de uso, os procedimentos
operacionais, a segurança e os testes do Nexus.

O conteúdo foi organizado conforme práticas de engenharia de software e
separado por requisitos, arquitetura, dados, operação, segurança, testes e
casos de uso.

## Objetivo do projeto

O Nexus - Gestão de Financiamentos tem como objetivo centralizar a gestão e o
controle dos contratos de financiamento do Grupo GBS, incluindo seus dados
financeiros, empresas, bancos, fornecedores e bens vinculados.

O sistema deve apoiar o ciclo operacional dos contratos, desde a inclusão e
consulta dos dados até a projeção de parcelas, o acompanhamento de
antecipações e a liquidação total ou parcial. Os cálculos financeiros devem
considerar as regras do contrato, a Selic, os dias úteis e o calendário de
feriados mantido no PostgreSQL.

Na evolução planejada, o Nexus também deverá permitir o cadastro e vínculo de
bens e veículos, atualização automática da Selic, controle de acesso, filtros
operacionais, detalhamento dos registros e rastreabilidade das operações
financeiras.

## Objetivo da documentação

Consolidar os requisitos, regras de negócio, arquitetura, modelo de dados,
casos de uso, procedimentos operacionais, segurança e testes do Nexus,
alinhando a documentação ao estado real da aplicação e ao roadmap do projeto.

## Status dos Use Cases

| ID | Caso de uso | Status |
| --- | --- | --- |
| UC01 | Inclusão de contratos | Parcialmente implementado |
| UC02 | Consulta de contratos | Implementado |
| UC03 | Visualização de projeção | Parcialmente implementado |
| UC04 | Exclusão física de contrato | Implementado |
| UC05 | Cadastro de bens e veículos | Banco preparado |
| UC06 | Registro de antecipação | Banco preparado |
| UC07 | Liquidação de contrato | Planejado para a versão 1.0 |
| UC08 | Atualização da Selic | Dados no banco; integração por API planejada |

## Estrutura da documentação

| Pasta ou arquivo | Conteúdo |
| --- | --- |
| `requirements/` | Requisitos funcionais, regras de negócio, requisitos não funcionais, premissas, rastreabilidade, painel de pendências e templaté de novas funcionalidades. |
| `architecture/` | Visão da solução, modelo de dados, cálculos financeiros e decisões arquiteturais. |
| `use_cases/` | Fluxos funcionais do sistema, seus atores, exceções e pós-condições. |
| `operations/` | Instalação, configuração, execução, monitoramento e procedimentos operacionais. |
| `security/` | Autenticação, autorização, segredos, auditoria e riscos conhecidos. |
| `testing/` | Estratégia, níveis, cenários e critérios de aceite de testes. |
| `architecture/integrations.md` | Integrações atuais e contrato futuro da API da Selic. |
| `architecture/data-dictionary.md` | Significado dos campos principais do banco. |
| `operations/release-management.md` | Checklist de versões, ambientes e rollback. |
| `security/threat-model.md` | Ameaças, impactos e mitigações. |
| `glossary.md` | Termos de negócio e tecnologia utilizados no projeto. |
| `roadmap.md` | Escopo atual, versão 1.0 e evoluções posteriores. |

Para incluir uma nova funcionalidade, use o [Templaté de Rastreabilidade de
Nova Funcionalidade](requirements/feature-traceability-templaté.md).

## Como saber o que falta

Consulte primeiro o [Registro de Status e Pendências](requirements/status-register.md).
Ele é a fonte de consulta rápida para identificar o que está implementado,
parcial, preparado somente no banco, planejado ou bloqueado.

Para cada item, o registro informa o motivo do status, o que já foi entregue,
o que está pendente, a evidência no código ou no banco, a próxima ação e o
critério de conclusão. A [Matriz de Rastreabilidade](requirements/traceability-matrix.md)
relaciona o item aos requisitos, regras e Use Cases.

## Convenções

Cada caso de uso apresenta objetivo, atores, pré-condições, pós-condições,
fluxo principal, fluxos alternativos, exceções, regras de negócio, dados
persistidos e status da implementação.

Os status resumidos significam:

- **Implementado:** existe fluxo funcional na aplicação.
- **Parcialmente implementado:** parte do fluxo existe, mas há etapas ou
	recursos pendentes.
- **Planejado:** o fluxo está definido para desenvolvimento futuro.

- **Banco preparado:** existem objetos no PostgreSQL, mas falta o fluxo
	completo na aplicação.
- **Bloqueado:** uma dependência impede a conclusão.
- **A validar:** existe implementação, mas falta validação técnica ou do
	negócio.
- **Concluído:** implementação, persistência, testes e validação foram
	aprovados.

Os Use Cases descrevem o comportamento funcional. Detalhes do modelo
PostgreSQL, triggers, views e matérialized views devem ser mantidos na
documentação de arquitetura.

Os documentos distinguem o estado atual da aplicação, o que já existe no
banco de dados e o que está planejado. Uma funcionalidade planejada não deve
ser considerada entregue apenas porque sua tabela ou trigger já existe.

## Critério de promoção

Uma alteração deve ser considerada concluída quando o fluxo estiver validado
pelo responsável do negócio, os requisitos associados estiverem coerentes com
a implementação e as evidências estiverem registradas no painel de status.
