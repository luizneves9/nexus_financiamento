# Estratégia de Testes

## Objetivo

Validar regras de negócio, cálculos financeiros, integridade dos dados e
fluxos da aplicação antes da promocao para ambientes superiores.

## Níveis

### Testes unitarios

Validar funções Python de validação, transformação de valores, seleção de
registros e tratamento de estados da interface.

### Testes de integração

Validar services, repositories, queries, conexão SQLAlchemy e transacoes com
um PostgreSQL de teste contendo o schema `financiamento`.

### Testes de banco

Validar funções, triggers, views, matérialized views, chaves estrangeiras,
unicidades, dias úteis, feriados, Selic, carência e antecipação.

### Testes de aceitação

Executar os fluxos dos Use Cases com um usuário do setor financeiro e dados
representativos, verificando resultado funcional e mensagens.

## Cenários prioritários

| ID | Cenario | Resultado esperado |
| --- | --- | --- |
| T01 | Incluir contrato válido | Contrato persistido e projeção disponível. |
| T01.1 | Projetar contrato antes da inclusão | Projeção exibida no mesmo modal sem persistir contrato. |
| T02 | Campo obrigatório ausente | Inclusão rejeitada com mensagem. |
| T03 | Valor, taxa ou prazo inválido | Inclusão rejeitada. |
| T04 | Datas fora de ordem | Inclusão rejeitada. |
| T05 | Numero de contrato repetido | Banco rejeita a operação. |
| T06 | Consultar contratos | View retorna dados esperados. |
| T07 | Visualizar projeção | Parcelas e valores são apresentados. |
| T07.1 | Comparar projeção do UC03 com o MV | Parcelas, datas e valores seguem o mesmo cálculo e arredondamento do PostgreSQL. |
| T07.2 | Projeção sem parcelas | Sistema informa que a projeção não foi encontrada. |
| T07.3 | Falha na consulta da projeção | Sistema informa o erro sem abrir modal vazia. |
| T08 | Excluir contrato sem dependências | Registro removido. |
| T09 | Excluir contrato com dependências | Integridade impede ou procedimento trata o caso. |
| T10 | Selic e feriado | Dias e valores seguem o calendário cadastrado. |
| T11 | Registrar antecipação | Selic e valor em moeda são calculados. |
| T12 | Falha de banco | Operação não e confirmada e erro e informado. |
| T13 | Banco indisponível durante inclusão | Mensagem funcional exibida e contrato não persistido. |
| T14 | Falha na projeção temporária | Mensagem funcional exibida e formulário permanece disponível. |
| T15 | Filtrar Projeção de Pagamentos (cada filtro, combinados, Vcto só de/só até) | Tabela e resumo refletem os filtros; filtro mantido ao trocar de aba; alterar/limpar um filtro aplica na primeira tentativa. |
| T16 | Filtrar Antecipações | Tabela e resumo refletem os filtros (validado contra o banco: 19 lançamentos sem filtro). |
| T17 | Login com usuário inexistente, bloqueado ou senha errada | Notificação "Usuário ou senha incorretos." e `LOGIN_FALHA` com o motivo no log. |
| T18 | Primeiro acesso (senha vazia) | Cadastro de senha exibido; senha curta ou confirmação diferente rejeitadas; banco guarda só `scrypt$...`; `CADASTRO_SENHA` no log. |
| T19 | Sessão | Fechar e reabrir o navegador em até 30 min entra direto (`LOGIN` com origem cookie); **Sair** recarrega a página no login; usuário bloqueado perde o acesso. |
| T20 | Cookie adulterado ou expirado | Recusado; login exigido. |
| T21 | Log das operações de escrita | Inclusão, exclusão (com cópia do contrato) e antecipação registradas na mesma transação; falhas com `sucesso = false`. |
| T22 | Imutabilidade do log | UPDATE, DELETE e TRUNCATE em `log_auditoria` bloqueados pelo trigger. |

## Testes que escrevem no banco

O log de auditoria não pode ser apagado e prende o usuário pela chave
estrangeira. Testes de escrita no banco de desenvolvimento devem usar uma
conexão com transação externa, transformar cada `engine.begin()` dos services
em savepoint e terminar com `ROLLBACK` (padrão usado na validação de T17 a
T22), para não deixar usuários, contratos ou logs de teste.

## Dados de teste

Os testes devem utilizar dados ficticios ou anonimizados. Dados financeiros
reais não devem ser usados em ambiente de desenvolvimento sem autorização.

## Critério de entrada

Ambiente configurado, schema atualizado, dados de teste carregados e versão
identificada.

## Critério de saída

Cenários prioritários aprovados, sem defeitos críticos abertos e resultados
registrados para a versão avaliada.
