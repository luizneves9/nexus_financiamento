# Modelo de Ameaças

## Escopo

O modelo considera a aplicação Streamlit, o container, o PostgreSQL, as
variaveis de ambiente e os dados financeiros.

## Ameaças principais

| Ameaca | Impacto | Mitigação atual ou planejada |
| --- | --- | --- |
| Acesso sem autenticação | Exposicao ou alteração indevida | Restringir ambiente atual; implementar autenticação e perfis. |
| Credencial exposta | Acesso ao banco | Usar `.env` fora do Git e secret manager em producao. |
| SQL indevido | Alteração ou vazamento de dados | Usar parâmetros SQLAlchemy e revisar queries. |
| Exclusão sem rastreio | Perda de histórico | Confirmação atual; auditoria e exclusão lógica futuras. |
| DDL incorreto | Erro financeiro ou indisponibilidade | Versionar, testar e revisar alterações do banco. |
| Selic incorreta | Projeção financeira incorreta | Validar fonte, data, duplicidade e carga da Selic. |
| Log com dados sensiveis | Vazamento de informação | Reduzir dados em logs e revisar mensagens de erro. |
| Container vulneravel | Comprometimento da aplicação | Atualizar imagem base e verificar dependências. |

## Responsabilidades

O responsável tecnico deve revisar riscos a cada mudanca relevante. O
responsável do negócio deve validar impacto de alterações em cálculos,
liquidacoes e regras financeiras.
