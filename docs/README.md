# Nexus - Documentacao do Projeto

Esta pasta contem a documentacao consolidada do projeto para leitura, revisao
e validacao antes da substituicao da documentacao atualmente mantida em `docs/`.

O conteudo foi organizado conforme praticas de engenharia de software e
separado por requisitos, arquitetura, dados, operacao, seguranca, testes e
casos de uso.

## Objetivo do projeto

O Nexus - Gestao de Financiamentos tem como objetivo centralizar a gestao e o
controle dos contratos de financiamento do Grupo GBS, incluindo seus dados
financeiros, empresas, bancos, fornecedores e bens vinculados.

O sistema deve apoiar o ciclo operacional dos contratos, desde a inclusao e
consulta dos dados ate a projecao de parcelas, o acompanhamento de
antecipacoes e a liquidacao total ou parcial. Os calculos financeiros devem
considerar as regras do contrato, a Selic, os dias uteis e o calendario de
feriados mantido no PostgreSQL.

Na evolucao planejada, o Nexus tambem devera permitir o cadastro e vinculo de
bens e veiculos, atualizacao automatica da Selic, controle de acesso, filtros
operacionais, detalhamento dos registros e rastreabilidade das operacoes
financeiras.

## Objetivo da documentacao

Consolidar os requisitos, regras de negocio, arquitetura, modelo de dados,
casos de uso, procedimentos operacionais, seguranca e testes do Nexus,
alinhando a documentacao ao estado real da aplicacao e ao roadmap do projeto.

## Status dos Use Cases

| ID | Caso de uso | Status |
| --- | --- | --- |
| UC01 | Inclusao de contratos | Parcialmente implementado |
| UC02 | Consulta de contratos | Implementado |
| UC03 | Visualizacao de projecao | Parcialmente implementado |
| UC04 | Exclusao fisica de contrato | Implementado, sujeito a dependencias |
| UC05 | Cadastro de bens e veiculos | Banco preparado; interface planejada para a versao 1.0 |
| UC06 | Registro de antecipacao | Banco preparado; interface planejada para a versao 1.0 |
| UC07 | Liquidacao de contrato | Planejado para a versao 1.0 |
| UC08 | Atualizacao da Selic | Dados no banco; integracao por API planejada |

## Estrutura da documentacao

| Pasta ou arquivo | Conteudo |
| --- | --- |
| `requirements/` | Requisitos funcionais, regras de negocio, requisitos nao funcionais, premissas e rastreabilidade. |
| `architecture/` | Visao da solucao, modelo de dados, calculos financeiros e decisoes arquiteturais. |
| `use_cases/` | Fluxos funcionais do sistema, seus atores, excecoes e pos-condicoes. |
| `operations/` | Instalacao, configuracao, execucao, monitoramento e procedimentos operacionais. |
| `security/` | Autenticacao, autorizacao, segredos, auditoria e riscos conhecidos. |
| `testing/` | Estrategia, niveis, cenarios e criterios de aceite de testes. |
| `architecture/integrations.md` | Integracoes atuais e contrato futuro da API da Selic. |
| `architecture/data-dictionary.md` | Significado dos campos principais do banco. |
| `operations/release-management.md` | Checklist de versoes, ambientes e rollback. |
| `security/threat-model.md` | Ameacas, impactos e mitigacoes. |
| `glossary.md` | Termos de negocio e tecnologia utilizados no projeto. |
| `roadmap.md` | Escopo atual, versao 1.0 e evolucoes posteriores. |

## Convencoes

Cada caso de uso apresenta objetivo, atores, pre-condicoes, pos-condicoes,
fluxo principal, fluxos alternativos, excecoes, regras de negocio, dados
persistidos e status da implementacao.

Os status significam:

- **Implementado:** existe fluxo funcional na aplicacao.
- **Parcialmente implementado:** parte do fluxo existe, mas ha etapas ou
	recursos pendentes.
- **Planejado:** o fluxo esta definido para desenvolvimento futuro.

Os Use Cases descrevem o comportamento funcional. Detalhes do modelo
PostgreSQL, triggers, views e materialized views devem ser mantidos na
documentacao de arquitetura.

Os documentos distinguem o estado atual da aplicacao, o que ja existe no
banco de dados e o que esta planejado. Uma funcionalidade planejada nao deve
ser considerada entregue apenas porque sua tabela ou trigger ja existe.