-- Anexos (PDF) dos contratos: uma tabela por tipo (Contrato e Ficha Financeira).
-- Cria tabelas NOVAS; não altera tabelas existentes. Já executado em 16/10/2026.
-- Vários arquivos por contrato; o mesmo PDF (hash) não se repete no mesmo contrato;
-- máximo de 20 MB por arquivo; anexos são excluídos junto com o contrato (CASCADE).

CREATE TABLE financiamento.anexo_contrato (
	id int4 GENERATED ALWAYS AS IDENTITY NOT NULL,
	id_contrato int4 NOT NULL,
	nome_arquivo varchar(255) NOT NULL,
	tamanho_bytes int4 NOT NULL,
	hash_sha256 char(64) NOT NULL,
	conteudo bytea NOT NULL,
	usuario varchar(100) NULL,
	data_registro timestamp DEFAULT now() NOT NULL,
	CONSTRAINT anexo_contrato_pkey PRIMARY KEY (id),
	CONSTRAINT anexo_contrato_id_contrato_fkey FOREIGN KEY (id_contrato)
		REFERENCES financiamento.contratos(id) ON DELETE CASCADE,
	CONSTRAINT anexo_contrato_arquivo_key UNIQUE (id_contrato, hash_sha256),
	CONSTRAINT anexo_contrato_tamanho_ck CHECK (tamanho_bytes > 0 AND tamanho_bytes <= 20971520)
);
CREATE INDEX anexo_contrato_contrato_idx ON financiamento.anexo_contrato (id_contrato);

CREATE TABLE financiamento.anexo_ficha_financeira (
	id int4 GENERATED ALWAYS AS IDENTITY NOT NULL,
	id_contrato int4 NOT NULL,
	nome_arquivo varchar(255) NOT NULL,
	tamanho_bytes int4 NOT NULL,
	hash_sha256 char(64) NOT NULL,
	conteudo bytea NOT NULL,
	usuario varchar(100) NULL,
	data_registro timestamp DEFAULT now() NOT NULL,
	CONSTRAINT anexo_ficha_financeira_pkey PRIMARY KEY (id),
	CONSTRAINT anexo_ficha_financeira_id_contrato_fkey FOREIGN KEY (id_contrato)
		REFERENCES financiamento.contratos(id) ON DELETE CASCADE,
	CONSTRAINT anexo_ficha_financeira_arquivo_key UNIQUE (id_contrato, hash_sha256),
	CONSTRAINT anexo_ficha_financeira_tamanho_ck CHECK (tamanho_bytes > 0 AND tamanho_bytes <= 20971520)
);
CREATE INDEX anexo_ficha_financeira_contrato_idx ON financiamento.anexo_ficha_financeira (id_contrato);

COMMENT ON TABLE financiamento.anexo_contrato IS 'PDFs do contrato (vários por contrato).';
COMMENT ON TABLE financiamento.anexo_ficha_financeira IS 'PDFs da ficha financeira (vários por contrato).';

ALTER TABLE financiamento.anexo_contrato OWNER TO fin;
GRANT ALL ON TABLE financiamento.anexo_contrato TO fin;
ALTER TABLE financiamento.anexo_ficha_financeira OWNER TO fin;
GRANT ALL ON TABLE financiamento.anexo_ficha_financeira TO fin;
