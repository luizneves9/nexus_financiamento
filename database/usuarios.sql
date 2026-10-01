-- =====================================================================
-- financiamento.usuarios — autenticação da aplicação (DA04)
-- =====================================================================
-- Usuários são criados apenas pelo desenvolvedor, sem senha (senha_hash NULL).
-- No primeiro acesso o usuário entra com a senha vazia e cadastra a própria
-- senha pela tela de login; a aplicação grava somente o hash (scrypt + salt),
-- nunca a senha em texto.
--
-- Executar uma única vez no banco (desenvolvimento e depois produção).
-- =====================================================================

CREATE TABLE financiamento.usuarios (
	id int4 GENERATED ALWAYS AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE) NOT NULL,
	usuario varchar(100) NOT NULL,
	senha_hash varchar(255) NULL,
	ativo bool DEFAULT true NOT NULL,
	criado_em timestamp DEFAULT now() NOT NULL,
	senha_definida_em timestamp NULL,
	CONSTRAINT usuarios_pkey PRIMARY KEY (id),
	CONSTRAINT usuarios_usuario_key UNIQUE (usuario)
);

-- Permissions

ALTER TABLE financiamento.usuarios OWNER TO fin;
GRANT ALL ON TABLE financiamento.usuarios TO fin;


-- =====================================================================
-- Operações do desenvolvedor (executar manualmente quando necessário)
-- =====================================================================

-- Conferir usuários (sem expor o hash):
-- SELECT id, usuario, ativo, (senha_hash IS NOT NULL) AS senha_cadastrada, criado_em, senha_definida_em
-- FROM financiamento.usuarios ORDER BY id;

-- Criar usuário (primeiro acesso: entra com senha vazia e cadastra a senha):
-- INSERT INTO financiamento.usuarios (usuario) VALUES ('luiz.neves');

-- Resetar a senha (usuário volta a cadastrar no próximo login):
-- UPDATE financiamento.usuarios SET senha_hash = NULL, senha_definida_em = NULL WHERE usuario = 'luiz.neves';

-- Bloquear o acesso (também derruba o login automático pelo cookie):
-- UPDATE financiamento.usuarios SET ativo = false WHERE usuario = 'luiz.neves';
