-- =====================================================================
-- financiamento.log_auditoria — registro de todas as interações (DA04)
-- =====================================================================
-- Cada ação do sistema grava uma linha. Nas operações de escrita, o log é
-- inserido na MESMA transação da operação: se a ação é gravada, o log existe;
-- se o log falhar, a ação é desfeita.
--
-- A tabela é somente inserção: um trigger bloqueia UPDATE, DELETE e TRUNCATE.
-- Senhas e hashes NUNCA são gravados no log.
--
-- Executar uma única vez no banco (desenvolvimento e depois produção),
-- depois de database/usuarios.sql.
-- =====================================================================

CREATE TABLE financiamento.log_auditoria (
	id int8 GENERATED ALWAYS AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 1 CACHE 1 NO CYCLE) NOT NULL,
	data_hora timestamptz DEFAULT now() NOT NULL,
	id_usuario int4 NULL,
	usuario varchar(100) NULL,
	acao varchar(50) NOT NULL,
	entidade varchar(50) NULL,
	id_registro int4 NULL,
	sucesso bool DEFAULT true NOT NULL,
	detalhes jsonb NULL,
	ip varchar(45) NULL,
	CONSTRAINT log_auditoria_pkey PRIMARY KEY (id),
	CONSTRAINT log_auditoria_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES financiamento.usuarios(id)
);

COMMENT ON TABLE financiamento.log_auditoria IS 'Log de auditoria das interações com o sistema (somente inserção).';
COMMENT ON COLUMN financiamento.log_auditoria.id_usuario IS 'Usuário autenticado; NULL em falha de login de usuário inexistente.';
COMMENT ON COLUMN financiamento.log_auditoria.usuario IS 'Nome do usuário no momento da ação (ou o nome digitado na falha de login).';
COMMENT ON COLUMN financiamento.log_auditoria.acao IS 'Ação executada (LOGIN, LOGIN_FALHA, LOGOUT, CADASTRO_SENHA, CONTRATO_INCLUIR, CONTRATO_EXCLUIR, ANTECIPACAO_INCLUIR, QUITACAO_INCLUIR, ACESSO_NEGADO...).';
COMMENT ON COLUMN financiamento.log_auditoria.entidade IS 'Tabela/objeto afetado (contratos, antecipacao, usuarios...).';
COMMENT ON COLUMN financiamento.log_auditoria.id_registro IS 'Id do registro afetado na entidade (sem FK: o registro pode ter sido excluído).';
COMMENT ON COLUMN financiamento.log_auditoria.detalhes IS 'Dados da ação em JSON (ex.: snapshot do contrato excluído, valores da antecipação).';

-- Índices para as consultas de auditoria mais comuns
CREATE INDEX log_auditoria_data_hora_idx ON financiamento.log_auditoria USING btree (data_hora);
CREATE INDEX log_auditoria_usuario_idx ON financiamento.log_auditoria USING btree (id_usuario, data_hora);
CREATE INDEX log_auditoria_acao_idx ON financiamento.log_auditoria USING btree (acao, data_hora);
CREATE INDEX log_auditoria_registro_idx ON financiamento.log_auditoria USING btree (entidade, id_registro);

-- Permissions

ALTER TABLE financiamento.log_auditoria OWNER TO fin;
GRANT ALL ON TABLE financiamento.log_auditoria TO fin;


-- =====================================================================
-- Imutabilidade: bloqueia UPDATE, DELETE e TRUNCATE no log
-- =====================================================================

CREATE OR REPLACE FUNCTION financiamento.log_auditoria_imutavel()
	RETURNS trigger
	LANGUAGE plpgsql
AS $function$
BEGIN
	RAISE EXCEPTION 'financiamento.log_auditoria é somente inserção (% bloqueado).', TG_OP;
END;
$function$
;

ALTER FUNCTION financiamento.log_auditoria_imutavel() OWNER TO fin;

CREATE TRIGGER trg_log_auditoria_imutavel
	BEFORE UPDATE OR DELETE ON financiamento.log_auditoria
	FOR EACH ROW EXECUTE FUNCTION financiamento.log_auditoria_imutavel();

CREATE TRIGGER trg_log_auditoria_sem_truncate
	BEFORE TRUNCATE ON financiamento.log_auditoria
	FOR EACH STATEMENT EXECUTE FUNCTION financiamento.log_auditoria_imutavel();


-- =====================================================================
-- Consultas úteis (executar manualmente quando necessário)
-- =====================================================================

-- Últimas 100 ações:
-- SELECT data_hora, usuario, acao, entidade, id_registro, sucesso, detalhes, ip
-- FROM financiamento.log_auditoria ORDER BY id DESC LIMIT 100;

-- Histórico de um contrato:
-- SELECT data_hora, usuario, acao, sucesso, detalhes
-- FROM financiamento.log_auditoria WHERE entidade = 'contratos' AND id_registro = 123 ORDER BY id;

-- Falhas de login nas últimas 24h:
-- SELECT data_hora, usuario, ip FROM financiamento.log_auditoria
-- WHERE acao = 'LOGIN_FALHA' AND data_hora >= now() - interval '24 hours' ORDER BY id DESC;
