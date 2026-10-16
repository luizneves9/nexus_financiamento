# Decisões Arquiteturais

## DA01 - PostgreSQL como motor financeiro

**Status:** Aceita  
**Decisão:** Funções, triggers e views do PostgreSQL são responsáveis pelos
cálculos financeiros. Desde a DA08 a projeção é gravada em tabela
(`projecao_parcelas`), recalculada por contrato pelas funções do banco.  
**Motivo:** Centralizar fórmulas, calendário, Selic e arredondamentos em uma
única fonte de verdade.  
**Consequência:** Alterações no cálculo exigem versionamento e testes no banco.

## DA02 - Exclusão física inicial

**Status:** Aceita  
**Decisão:** A primeira versão utiliza exclusão física de contratos.  
**Motivo:** E o comportamento atualmente implementado e ainda não existe
política aprovada de exclusão lógica.  
**Consequência:** Integridade referencial pode impedir a exclusão e histórico
precisa ser tratado em evolução futura.

## DA05 - Projeção temporária por função PostgreSQL

**Status:** Aceita  
**Decisão:** A projeção acionada durante a inclusão será executada por uma
função PostgreSQL que receberá os parâmetros do contrato e retornará o cálculo
final sem persistir o contrato.  
**Motivo:** Manter o cálculo financeiro no banco e evitar efeitos colaterais de
uma inserção seguida de rollback.  
**Consequência:** A função deverá possuir contrato de entrada e saída, testes
próprios e alinhamento com a regra de cálculo da projeção persistida
(`calcular_projecao_contrato`, DA08). Unificar as duas está no backlog.

## DA03 - API da Selic posterior

**Status:** Substituída pela DA11  
**Decisão original:** A integração automática da Selic seria desenvolvida
posteriormente; até lá os dados eram carregados manualmente no banco.

## DA04 - Autenticação própria com sessão em cookie assinado

**Status:** Aceita (autenticação implementada; perfis planejados para a versão 1.0)  
**Decisão:** A autenticação é feita pela própria aplicação, sem provedor
externo:

- usuários em `financiamento.usuarios`, criados somente pelo desenvolvedor,
  sem senha; o próprio usuário cadastra a senha no primeiro acesso;
- senha armazenada somente como hash `scrypt` (biblioteca padrão do Python,
  `hashlib.scrypt`, N=2^14, r=8, p=1, salt aleatório de 16 bytes), no formato
  `scrypt$n$r$p$salt$hash` — os parâmetros ficam gravados, permitindo
  aumentá-los depois sem invalidar senhas;
- sessão mantida por cookie `nexus_sessao` com usuário e expiração assinados
  por HMAC-SHA256 com a chave `AUTH_SECRET` (variável de ambiente), válido
  por 30 minutos deslizantes; o cookie é gravado via JavaScript
  (`st.html(..., unsafe_allow_javascript=True)`) e lido por
  `st.context.cookies`, pois o Streamlit não grava cookies nativamente;
- sem login, a navegação registra apenas a página de login.

**Motivo:** A imagem base `fin-base:1.0` não traz bibliotecas de hash
(bcrypt/argon2) nem de cookies, e o controle de usuários é interno e de baixo
volume.  
**Consequência:** O cookie não pode ser `HttpOnly` (gravado por JS) e um
cookie copiado vale até expirar; o vazamento do `AUTH_SECRET` permite forjar
login. Pendências registradas em BL-014 a BL-018. Perfis e permissões
(RF10.4) continuam planejados para a versão 1.0.

## DA06 - Log de auditoria no banco, na mesma transação e somente inserção

**Status:** Aceita  
**Decisão:** Toda operação de escrita e todo evento de acesso são registrados
em `financiamento.log_auditoria` por `services/log.py`:

- escritas gravam o log **na mesma transação** da operação
  (`registrar_log(..., conn=conn)`): sem log, sem operação;
- falhas são gravadas em transação própria (`registrar_log_falha`), com
  `sucesso = false` e o erro, sem esconder a mensagem original ao usuário;
- inclusões usam `RETURNING id` e exclusões `DELETE ... RETURNING *`, guardando
  a cópia do registro excluído em `detalhes` (jsonb);
- a tabela é somente inserção: triggers bloqueiam UPDATE, DELETE e TRUNCATE;
- consultas e relatórios somente leitura não são registrados;
- senha, hash, token e segredos nunca vão para o log.

Ações do catálogo: `LOGIN`, `LOGIN_FALHA`, `LOGOUT`, `SESSAO_ENCERRADA`,
`CADASTRO_SENHA`, `CONTRATO_INCLUIR`, `CONTRATO_EXCLUIR`,
`ANTECIPACAO_INCLUIR`, `QUITACAO_INCLUIR`, `ANTECIPACAO_EXCLUIR`,
`LIQUIDACAO_INCLUIR`, `LIQUIDACAO_ESTORNAR`, `CONCILIACAO_ERP` (um registro
por lote), `VINCULO_ERP_INCLUIR`, `VINCULO_ERP_EXCLUIR`, `SELIC_IMPORTAR`
(e, com os perfis, `ACESSO_NEGADO`). O recálculo automático da projeção não
gera log próprio (é consequência de uma ação já registrada).

**Motivo:** Rastrear quem fez o quê, quando e com qual resultado (RNF08),
inclusive o conteúdo de registros excluídos fisicamente (DA02), garantindo
que nenhuma operação fique sem registro.  
**Consequência:** Toda funcionalidade nova deve avaliar a necessidade de log
(regra registrada no `CLAUDE.md`). Como não há banco de testes, testes de
escrita devem rodar em blocos que se desfazem sozinhos (ex.: `DO` terminado
por `RAISE EXCEPTION`), pois o log não pode ser apagado. O usuário `fin` é dono da tabela e poderia remover o trigger;
retenção e usuário somente-inserção estão em BL-022.

## DA07 - Identidade visual compartilhada com o Nexus Extrato

**Status:** Aceita
**Decisão:** A interface segue a mesma identidade visual do Nexus Extrato,
aplicada só na camada de apresentação, sem alterar regras, banco ou
autenticação:

- `.streamlit/config.toml` na raiz define apenas a cor de destaque
  (`primaryColor = "#6366F1"`) nos temas claro e escuro; o usuário continua
  trocando o tema em ⋮ > Settings;
- `src/main.py` aplica, depois do login, o ícone da aba, o About, a logo no
  menu lateral (`src/assets/`), o CSS geral (realce índigo em botões, links
  e campos; recuo do menu) e o rodapé fixo com usuário e **Sair**; os grupos
  do menu têm ícone Material e começam recolhidos, menos o da página atual;
- componentes em `src/views/components/`: `cabecalho.py` (título de toda
  tela, com o ícone do grupo do menu), `botao_principal.py` (estilo de
  `type='primary'`, usado só na ação principal: Entrar/Cadastrar senha e
  Confirmar dos modais) e `cartao_clicavel.py` (para telas em cartões);
- a barra do topo roda em `--client.toolbarMode=viewer` (sem Deploy e opções
  de desenvolvedor).

**Motivo:** Padronizar a experiência entre os sistemas Nexus do Grupo GBS e
remover estilos fixos por tela (ex.: cinza `#666`, pouco legível no tema
escuro).
**Consequência:** Os seletores CSS dependem da estrutura interna do Streamlit
1.63.0; atualizar o Streamlit exige revalidar o visual. O Streamlit deve ser
executado a partir da raiz do repositório para ler o `config.toml` (local e
Docker). Confirmar a versão da imagem `fin-base:1.0` está em BL-025.

## DA08 - Projeção persistida por contrato (substitui as materialized views)

**Status:** Aceita (implantada em 15-16/10/2026)  
**Decisão:** A projeção deixa de ser calculada pelas materialized views
`mv_projecao_moeda`, `mv_projecao_moeda_final` e `mv_projecao_tfc` (removidas)
e passa a ser gravada em `projecao_parcelas` (uma linha por parcela, chave
estável `(id_contrato, parcela)`) com controle em `projecao_controle`:

- `calcular_projecao_contrato(id, data_base opcional)` calcula um contrato com
  a mesma regra das antigas MVs (validada com diferença zero na migração);
- `recalcular_projecao_contrato(id, motivo)` grava o resultado, nunca altera
  parcelas LIQUIDADAS e marca como `CANCELADA_QUITACAO` as parcelas depois da
  quitação (em vez de excluí-las);
- triggers por linha recalculam só o contrato afetado na inclusão/alteração de
  contrato e na inclusão/alteração/exclusão de antecipação; a inclusão de Selic
  recalcula, uma vez por comando, os contratos com parcelas abertas afetadas.

**Motivo:** O refresh das MVs recalculava toda a base a cada inclusão, não
acompanhava exclusões nem a Selic e não tinha chave estável para vincular
pagamentos.  
**Consequência:** Estrutura documentada em `database/projecao_persistida.sql`.
Os bugs herdados das MVs (TFC sem antecipação, uma antecipação por contrato,
parcela do dia da quitação) foram reproduzidos de propósito e estão no backlog.

## DA09 - Liquidação e conciliação com o ERP sem guardar o relatório

**Status:** Aceita  
**Decisão:** A baixa de parcelas fica em `liquidacao` (manual ou por
conciliação), com `valor_ajuste = valor_pago - valor_projetado` calculado pelo
banco; a parcela liquidada não é alterada pelo recálculo; liquidação só pode
ser estornada (exclusão e TRUNCATE bloqueados). O CSV do ERP é lido em memória
e carregado numa tabela temporária (`ON COMMIT DROP`) a cada prévia (transação
desfeita) e na confirmação (conciliação refeita na mesma transação); só as
liquidações são gravadas. Códigos do ERP diferentes do número do contrato são
resolvidos por `contrato_erp_vinculo` (um código pode formar um grupo de
contratos, com rateio proporcional do valor pago).  
**Motivo:** A reexecução do Streamlit pode trocar a conexão do pool, o que
impede manter uma tabela temporária entre interações; o relatório do ERP não
precisa ser guardado além do que vira liquidação.  
**Consequência:** Linhas não identificadas e não pagas existem só na prévia; o
resumo do lote fica no log `CONCILIACAO_ERP`.

## DA10 - Posição na data base nos relatórios

**Status:** Aceita  
**Decisão:** Contas a Pagar e Endividamento usam a mesma regra
(`CTE_POSICAO_DATA_BASE`): parcela liquidada até a data base vale o valor
pago; as demais valem o valor projetado, refeito com a Selic conhecida até a
data base; antecipações e quitações pagas depois da data base não entram, e os
contratos que as têm são recalculados como estavam na data base.  
**Motivo:** Permitir consultar posições passadas sem usar informação que não
existia naquela data.  
**Consequência:** O recálculo pela data base acontece só na consulta; a tabela
`projecao_parcelas` continua guardando a projeção atual.

## DA11 - Selic oficial do BNDES

**Status:** Aceita (substitui a DA03)  
**Decisão:** A Selic (fator UM143) é importada de
`https://www.bndes.gov.br/Moedas/um143.txt` pela tela Cadastros > Selic, com
um único INSERT apenas das datas posteriores à última gravada (o recálculo da
projeção roda uma vez por importação).  
**Motivo:** As cargas manuais por planilha gravaram datas com dia e mês
trocados; a série oficial publica inclusive o dia seguinte.  
**Consequência:** O servidor precisa de acesso a `www.bndes.gov.br`; datas
antigas ausentes não são importadas automaticamente (são apenas informadas).
