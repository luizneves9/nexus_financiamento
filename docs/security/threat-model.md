# Modelo de Ameaças

## Escopo

O modelo considera a aplicação Streamlit, o container, o PostgreSQL, as
variaveis de ambiente e os dados financeiros.

## Ameaças principais

| Ameaca | Impacto | Mitigação atual ou planejada |
| --- | --- | --- |
| Acesso sem autenticação | Exposicao ou alteração indevida | Login obrigatório (UC12); perfis planejados (BL-005). |
| Credencial exposta | Acesso ao banco | **`.env` hoje versionado** — remover do Git, rotacionar senha e usar secret manager em producao (BL-014). |
| Cookie de sessão forjado | Login como qualquer usuário | Assinatura HMAC com `AUTH_SECRET` fora do Git (BL-014). |
| Cookie roubado / tráfego interceptado | Sequestro de sessão ou da senha | HTTPS e cookie `Secure` (BL-015); invalidação de sessões (BL-017). |
| Força bruta de senha | Acesso indevido e carga no servidor | Hash `scrypt`; limite de tentativas (BL-016). |
| Senha do banco de usuários vazada | Quebra offline de senhas | Hash `scrypt` com salt por usuário; avaliar N=2^15 (BL-018). |
| Adulteração do log | Perda de rastreabilidade | Trigger somente inserção; usuário de banco restrito (BL-022). |
| SQL indevido | Alteração ou vazamento de dados | Usar parâmetros SQLAlchemy e revisar queries. |
| Exclusão sem rastreio | Perda de histórico | Cópia do registro excluído no log de auditoria (DA06); exclusão lógica futura. |
| DDL incorreto | Erro financeiro ou indisponibilidade | Versionar, testar e revisar alterações do banco. |
| Selic incorreta | Projeção financeira incorreta | Validar fonte, data, duplicidade e carga da Selic. |
| Log com dados sensiveis | Vazamento de informação | Log de auditoria nunca grava senha, hash ou token; mensagens de login genéricas. |
| Container vulneravel | Comprometimento da aplicação | Atualizar imagem base e verificar dependências. |

## Responsabilidades

O responsável tecnico deve revisar riscos a cada mudanca relevante. O
responsável do negócio deve validar impacto de alterações em cálculos,
liquidacoes e regras financeiras.
