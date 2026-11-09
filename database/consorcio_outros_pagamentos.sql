-- =====================================================================
-- Consórcios e outros pagamentos (Compra Santo Anjo, Tributário)
-- Modalidades do relatório de Endividamento além dos financiamentos.
-- =====================================================================
-- Cria tabelas NOVAS; não altera tabelas existentes. Executar uma única vez.
--
-- Competência = mês de referência da importação/lançamento, sempre gravada
-- como o 1º dia do mês (ex.: 2026-10-01 = outubro/2026).
--
-- Regras (definidas em 06/11/2026):
--   consorcio_pago      histórico pela data de pagamento, um arquivo por banco e
--                       consorciado (só o mês ou o histórico completo). Importar
--                       substitui os pagamentos do banco + consorciado entre a
--                       menor e a maior data de
--                       pagamento do arquivo; competencia é só referência (mês da
--                       maior data do arquivo). No relatório entra tudo com
--                       data_pagamento <= data base, no mês da data_pagamento,
--                       pela coluna total.
--   consorcio_a_pagar   foto por competência (data base informada na importação)
--                       , banco e consorciado (informado na importação); só cotas
--                       contempladas (o arquivo já vem filtrado). Reimportar troca
--                       competência + banco + consorciado. O relatório usa, por
--                       banco + consorciado, a competência do mês da data base ou,
--                       se não houver, a última anterior.
--   consorcio_credito   um lançamento manual por competência (mesma regra).
--   outros_pagamentos   lançamento manual por parcela, com baixa e estorno;
--                       a parcela fica no mês do vencimento (paga ou não).
-- =====================================================================


-- ---------------------------------------------------------------------
-- Consórcio: pagamentos (CSV "pago")
-- ---------------------------------------------------------------------
CREATE TABLE financiamento.consorcio_pago (
	id int4 GENERATED ALWAYS AS IDENTITY NOT NULL,
	competencia date NOT NULL,
	banco varchar(100) NOT NULL,
	nome_consorciado varchar(255) NULL,
	numero_proposta varchar(30) NOT NULL,
	data_adesao date NULL,
	id_cota varchar(30) NULL,
	movimento varchar(100) NOT NULL,
	data_pagamento date NOT NULL,
	valor_fundo_comum numeric(15, 2) NULL,
	valor_fundo_reserva numeric(15, 2) NULL,
	valor_taxa_administracao numeric(15, 2) NULL,
	valor_multa_juros numeric(15, 2) NULL,
	valor_outros numeric(15, 2) NULL,
	valor_total numeric(15, 2) NOT NULL,
	nome_arquivo varchar(255) NULL,
	usuario varchar(100) NULL,
	data_registro timestamp DEFAULT now() NOT NULL,
	CONSTRAINT consorcio_pago_pkey PRIMARY KEY (id),
	CONSTRAINT consorcio_pago_competencia_ck CHECK (competencia = date_trunc('month', competencia)::date)
);
CREATE INDEX consorcio_pago_competencia_idx ON financiamento.consorcio_pago (competencia);
CREATE INDEX consorcio_pago_data_pagamento_idx ON financiamento.consorcio_pago (data_pagamento);

COMMENT ON TABLE financiamento.consorcio_pago IS 'Pagamentos de consórcio importados do CSV (um arquivo por banco e consorciado; importar substitui os pagamentos do banco + consorciado no período de datas do arquivo).';
COMMENT ON COLUMN financiamento.consorcio_pago.competencia IS 'Referência da importação: mês da maior data de pagamento do arquivo (1º dia do mês); não é usada no relatório.';
COMMENT ON COLUMN financiamento.consorcio_pago.movimento IS 'Nome Código Movimento Financeiro (ex.: RECBTO. PARCELA, RECBTO LANCE DILUIDO).';
COMMENT ON COLUMN financiamento.consorcio_pago.valor_total IS 'Coluna Total do CSV; é o valor usado no Endividamento (todos os movimentos).';


-- ---------------------------------------------------------------------
-- Consórcio: parcelas a pagar (CSV "a pagar"), foto por competência
-- ---------------------------------------------------------------------
CREATE TABLE financiamento.consorcio_a_pagar (
	id int4 GENERATED ALWAYS AS IDENTITY NOT NULL,
	competencia date NOT NULL,
	banco varchar(100) NOT NULL,
	numero_proposta varchar(30) NOT NULL,
	valor_parcela numeric(15, 2) NOT NULL,
	nome_consorciado varchar(255) NOT NULL,         -- incluída em 06/11/2026 (ALTER TABLE ... ADD COLUMN)
	data_pagamento date NOT NULL,
	data_emissao date NULL,
	nome_arquivo varchar(255) NULL,
	usuario varchar(100) NULL,
	data_registro timestamp DEFAULT now() NOT NULL,
	CONSTRAINT consorcio_a_pagar_pkey PRIMARY KEY (id),
	CONSTRAINT consorcio_a_pagar_competencia_ck CHECK (competencia = date_trunc('month', competencia)::date)
);
CREATE INDEX consorcio_a_pagar_competencia_idx ON financiamento.consorcio_a_pagar (competencia);
CREATE INDEX consorcio_a_pagar_chave_idx ON financiamento.consorcio_a_pagar (competencia, banco, nome_consorciado);

COMMENT ON TABLE financiamento.consorcio_a_pagar IS 'Parcelas a pagar das cotas contempladas, importadas do CSV; foto por competência, banco e consorciado (reimportar troca competência + banco + consorciado).';
COMMENT ON COLUMN financiamento.consorcio_a_pagar.nome_consorciado IS 'Consorciado informado na importação (o CSV a pagar não traz a coluna); reimportar troca competência + banco + consorciado.';
COMMENT ON COLUMN financiamento.consorcio_a_pagar.competencia IS 'Mês da data base informada na importação (1º dia do mês).';
COMMENT ON COLUMN financiamento.consorcio_a_pagar.data_pagamento IS 'Data Pagamento do CSV (vencimento previsto da parcela).';


-- ---------------------------------------------------------------------
-- Consórcio: créditos do fechamento do mês (lançamento manual)
-- ---------------------------------------------------------------------
CREATE TABLE financiamento.consorcio_credito (
	id int4 GENERATED ALWAYS AS IDENTITY NOT NULL,
	competencia date NOT NULL,
	credito_cotas_contempladas numeric(15, 2) DEFAULT 0 NOT NULL,
	credito_parcelas_nao_contempladas numeric(15, 2) DEFAULT 0 NOT NULL,
	usuario varchar(100) NULL,
	data_registro timestamp DEFAULT now() NOT NULL,
	data_alteracao timestamp NULL,
	CONSTRAINT consorcio_credito_pkey PRIMARY KEY (id),
	CONSTRAINT consorcio_credito_competencia_key UNIQUE (competencia),
	CONSTRAINT consorcio_credito_competencia_ck CHECK (competencia = date_trunc('month', competencia)::date)
);

COMMENT ON TABLE financiamento.consorcio_credito IS 'Créditos de consórcio no fechamento do mês (um lançamento por competência), abatidos na Dívida Líquida do Endividamento.';
COMMENT ON COLUMN financiamento.consorcio_credito.credito_cotas_contempladas IS 'Crédito Cotas Consórcios Contempladas (R$).';
COMMENT ON COLUMN financiamento.consorcio_credito.credito_parcelas_nao_contempladas IS 'Crédito Parcelas pagas e não contempladas (R$).';


-- ---------------------------------------------------------------------
-- Outros pagamentos: Compra Santo Anjo e Tributário (lançamento manual)
-- ---------------------------------------------------------------------
CREATE TABLE financiamento.outros_pagamentos (
	id int4 GENERATED ALWAYS AS IDENTITY NOT NULL,
	modalidade varchar(30) NOT NULL,
	descricao varchar(255) NULL,
	data_vencimento date NOT NULL,
	valor numeric(15, 2) NOT NULL,
	data_pagamento date NULL,                       -- baixa: vazio = não pago
	valor_pago numeric(15, 2) NULL,
	usuario varchar(100) NULL,
	data_registro timestamp DEFAULT now() NOT NULL,
	usuario_alteracao varchar(100) NULL,
	data_alteracao timestamp NULL,
	usuario_baixa varchar(100) NULL,
	data_registro_baixa timestamp NULL,
	CONSTRAINT outros_pagamentos_pkey PRIMARY KEY (id),
	CONSTRAINT outros_pagamentos_modalidade_ck CHECK (modalidade IN ('COMPRA_SANTO_ANJO', 'TRIBUTARIO')),
	CONSTRAINT outros_pagamentos_valor_ck CHECK (valor > 0),
	CONSTRAINT outros_pagamentos_baixa_ck CHECK ((data_pagamento IS NULL) = (valor_pago IS NULL)),
	CONSTRAINT outros_pagamentos_valor_pago_ck CHECK (valor_pago IS NULL OR valor_pago > 0)
);
CREATE INDEX outros_pagamentos_vencimento_idx ON financiamento.outros_pagamentos (modalidade, data_vencimento);

COMMENT ON TABLE financiamento.outros_pagamentos IS 'Parcelas de Compra Santo Anjo e Tributário lançadas manualmente, com baixa (data e valor pago) e estorno (limpa a baixa; histórico no log de auditoria).';
COMMENT ON COLUMN financiamento.outros_pagamentos.modalidade IS 'COMPRA_SANTO_ANJO / TRIBUTARIO.';
COMMENT ON COLUMN financiamento.outros_pagamentos.data_pagamento IS 'Data da baixa; NULL = não pago. No Endividamento a parcela fica no mês do vencimento.';


-- Permissões
ALTER TABLE financiamento.consorcio_pago OWNER TO fin;
GRANT ALL ON TABLE financiamento.consorcio_pago TO fin;
ALTER TABLE financiamento.consorcio_a_pagar OWNER TO fin;
GRANT ALL ON TABLE financiamento.consorcio_a_pagar TO fin;
ALTER TABLE financiamento.consorcio_credito OWNER TO fin;
GRANT ALL ON TABLE financiamento.consorcio_credito TO fin;
ALTER TABLE financiamento.outros_pagamentos OWNER TO fin;
GRANT ALL ON TABLE financiamento.outros_pagamentos TO fin;


-- =====================================================================
-- Verificação (executar depois da criação)
-- =====================================================================

-- 1) As 4 tabelas existem e estão vazias (esperado: 4 linhas, qtd = 0):
-- SELECT 'consorcio_pago' AS tabela, count(*) AS qtd FROM financiamento.consorcio_pago
-- UNION ALL SELECT 'consorcio_a_pagar', count(*) FROM financiamento.consorcio_a_pagar
-- UNION ALL SELECT 'consorcio_credito', count(*) FROM financiamento.consorcio_credito
-- UNION ALL SELECT 'outros_pagamentos', count(*) FROM financiamento.outros_pagamentos;

-- 2) Teste das regras, que se desfaz sozinho (esperado: ERRO "TESTE DESFEITO: ok"):
-- DO $$
-- BEGIN
-- 	INSERT INTO financiamento.consorcio_credito (competencia, credito_cotas_contempladas) VALUES ('2026-10-01', 29420000);
-- 	BEGIN
-- 		INSERT INTO financiamento.consorcio_credito (competencia) VALUES ('2026-10-15');   -- não é dia 1
-- 		RAISE EXCEPTION 'FALHOU: competência fora do dia 1 foi aceita';
-- 	EXCEPTION WHEN check_violation THEN NULL;
-- 	END;
-- 	BEGIN
-- 		INSERT INTO financiamento.outros_pagamentos (modalidade, data_vencimento, valor, data_pagamento)
-- 		VALUES ('TRIBUTARIO', '2026-10-10', 1000, '2026-10-10');                          -- baixa sem valor pago
-- 		RAISE EXCEPTION 'FALHOU: baixa sem valor pago foi aceita';
-- 	EXCEPTION WHEN check_violation THEN NULL;
-- 	END;
-- 	BEGIN
-- 		INSERT INTO financiamento.outros_pagamentos (modalidade, data_vencimento, valor)
-- 		VALUES ('OUTRA', '2026-10-10', 1000);                                              -- modalidade inválida
-- 		RAISE EXCEPTION 'FALHOU: modalidade inválida foi aceita';
-- 	EXCEPTION WHEN check_violation THEN NULL;
-- 	END;
-- 	RAISE EXCEPTION 'TESTE DESFEITO: ok';
-- END $$;
