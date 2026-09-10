# Modelo de Ameacas

## Escopo

O modelo considera a aplicacao Streamlit, o container, o PostgreSQL, as
variaveis de ambiente e os dados financeiros.

## Ameacas principais

| Ameaca | Impacto | Mitigacao atual ou planejada |
| --- | --- | --- |
| Acesso sem autenticacao | Exposicao ou alteracao indevida | Restringir ambiente atual; implementar autenticacao e perfis. |
| Credencial exposta | Acesso ao banco | Usar `.env` fora do Git e secret manager em producao. |
| SQL indevido | Alteracao ou vazamento de dados | Usar parametros SQLAlchemy e revisar queries. |
| Exclusao sem rastreio | Perda de historico | Confirmacao atual; auditoria e exclusao logica futuras. |
| DDL incorreto | Erro financeiro ou indisponibilidade | Versionar, testar e revisar alteracoes do banco. |
| Selic incorreta | Projecao financeira incorreta | Validar fonte, data, duplicidade e carga da Selic. |
| Log com dados sensiveis | Vazamento de informacao | Reduzir dados em logs e revisar mensagens de erro. |
| Container vulneravel | Comprometimento da aplicacao | Atualizar imagem base e verificar dependencias. |

## Responsabilidades

O responsavel tecnico deve revisar riscos a cada mudanca relevante. O
responsavel do negocio deve validar impacto de alteracoes em calculos,
liquidacoes e regras financeiras.
