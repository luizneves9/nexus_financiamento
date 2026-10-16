-- =====================================================================
-- Retrato documental do schema financiamento (não é instalador).
-- Atualizado em 16/10/2026: removidos as materialized views mv_projecao_moeda,
-- mv_projecao_moeda_final e mv_projecao_tfc, a função refresh_views_contratos()
-- e os triggers trg_after_insert_contratos / trg_after_insert_antecipacao
-- (excluídos do banco). Tabelas, funções e triggers da projeção persistida,
-- liquidação e vínculo ERP estão em database/projecao_persistida.sql;
-- usuarios e log_auditoria em database/usuarios.sql e database/log_auditoria.sql.
-- =====================================================================
-- DROP SCHEMA financiamento;

CREATE SCHEMA financiamento AUTHORIZATION fin;

-- DROP SEQUENCE financiamento.antecipacao_id_seq;

CREATE SEQUENCE financiamento.antecipacao_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;

-- Permissions

ALTER SEQUENCE financiamento.antecipacao_id_seq OWNER TO fin;
GRANT ALL ON SEQUENCE financiamento.antecipacao_id_seq TO fin;

-- DROP SEQUENCE financiamento.bancos_id_seq;

CREATE SEQUENCE financiamento.bancos_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;

-- Permissions

ALTER SEQUENCE financiamento.bancos_id_seq OWNER TO fin;
GRANT ALL ON SEQUENCE financiamento.bancos_id_seq TO fin;

-- DROP SEQUENCE financiamento.bem_id_seq;

CREATE SEQUENCE financiamento.bem_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;

-- Permissions

ALTER SEQUENCE financiamento.bem_id_seq OWNER TO fin;
GRANT ALL ON SEQUENCE financiamento.bem_id_seq TO fin;

-- DROP SEQUENCE financiamento.contratos_id_seq;

CREATE SEQUENCE financiamento.contratos_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;

-- Permissions

ALTER SEQUENCE financiamento.contratos_id_seq OWNER TO fin;
GRANT ALL ON SEQUENCE financiamento.contratos_id_seq TO fin;

-- DROP SEQUENCE financiamento.empresas_id_seq;

CREATE SEQUENCE financiamento.empresas_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;

-- Permissions

ALTER SEQUENCE financiamento.empresas_id_seq OWNER TO fin;
GRANT ALL ON SEQUENCE financiamento.empresas_id_seq TO fin;

-- DROP SEQUENCE financiamento.feriados_id_seq;

CREATE SEQUENCE financiamento.feriados_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;

-- Permissions

ALTER SEQUENCE financiamento.feriados_id_seq OWNER TO fin;
GRANT ALL ON SEQUENCE financiamento.feriados_id_seq TO fin;

-- DROP SEQUENCE financiamento.fornecedor_id_seq;

CREATE SEQUENCE financiamento.fornecedor_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;

-- Permissions

ALTER SEQUENCE financiamento.fornecedor_id_seq OWNER TO fin;
GRANT ALL ON SEQUENCE financiamento.fornecedor_id_seq TO fin;

-- DROP SEQUENCE financiamento.selic_id_seq;

CREATE SEQUENCE financiamento.selic_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;

-- Permissions

ALTER SEQUENCE financiamento.selic_id_seq OWNER TO fin;
GRANT ALL ON SEQUENCE financiamento.selic_id_seq TO fin;

-- DROP SEQUENCE financiamento.veiculos_id_seq;

CREATE SEQUENCE financiamento.veiculos_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;

-- Permissions

ALTER SEQUENCE financiamento.veiculos_id_seq OWNER TO fin;
GRANT ALL ON SEQUENCE financiamento.veiculos_id_seq TO fin;
-- financiamento.bancos definição

-- Drop table

-- DROP TABLE financiamento.bancos;

CREATE TABLE financiamento.bancos (
	id int4 GENERATED ALWAYS AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE) NOT NULL,
	cnpj varchar(20) NOT NULL,
	razao_social varchar(250) NOT NULL,
	CONSTRAINT bancos_cnpj_key UNIQUE (cnpj),
	CONSTRAINT bancos_pkey PRIMARY KEY (id)
);

-- Permissions

ALTER TABLE financiamento.bancos OWNER TO fin;
GRANT ALL ON TABLE financiamento.bancos TO fin;


-- financiamento.empresas definição

-- Drop table

-- DROP TABLE financiamento.empresas;

CREATE TABLE financiamento.empresas (
	id int4 GENERATED ALWAYS AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE) NOT NULL,
	cnpj varchar(20) NOT NULL,
	razao_social varchar(250) NOT NULL,
	CONSTRAINT empresas_cnpj_key UNIQUE (cnpj),
	CONSTRAINT empresas_pkey PRIMARY KEY (id)
);

-- Permissions

ALTER TABLE financiamento.empresas OWNER TO fin;
GRANT ALL ON TABLE financiamento.empresas TO fin;


-- financiamento.feriados definição

-- Drop table

-- DROP TABLE financiamento.feriados;

CREATE TABLE financiamento.feriados (
	id int4 GENERATED ALWAYS AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE) NOT NULL,
	"data" date NOT NULL,
	feriado varchar(255) NULL,
	CONSTRAINT feriados_pkey PRIMARY KEY (id)
);

-- Permissions

ALTER TABLE financiamento.feriados OWNER TO fin;
GRANT ALL ON TABLE financiamento.feriados TO fin;


-- financiamento.fornecedor definição

-- Drop table

-- DROP TABLE financiamento.fornecedor;

CREATE TABLE financiamento.fornecedor (
	id int4 GENERATED ALWAYS AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE) NOT NULL,
	cnpj varchar(20) NOT NULL,
	razao_social varchar(250) NOT NULL,
	CONSTRAINT fornecedor_cnpj_key UNIQUE (cnpj),
	CONSTRAINT fornecedor_pkey PRIMARY KEY (id)
);

-- Permissions

ALTER TABLE financiamento.fornecedor OWNER TO fin;
GRANT ALL ON TABLE financiamento.fornecedor TO fin;


-- financiamento.selic definição

-- Drop table

-- DROP TABLE financiamento.selic;

CREATE TABLE financiamento.selic (
	id int4 GENERATED ALWAYS AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE) NOT NULL,
	"data" date NULL,
	valor numeric(12, 8) NULL
);

-- Permissions

ALTER TABLE financiamento.selic OWNER TO fin;
GRANT ALL ON TABLE financiamento.selic TO fin;


-- financiamento.contratos definição

-- Drop table

-- DROP TABLE financiamento.contratos;

CREATE TABLE financiamento.contratos (
	id int4 GENERATED ALWAYS AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE) NOT NULL,
	id_empresa int4 NOT NULL,
	id_banco int4 NOT NULL,
	numero_contrato varchar(50) NOT NULL,
	data_emissao date NOT NULL,
	data_bndes date NOT NULL,
	selic numeric(10, 6) NULL,
	tipo_contrato varchar(50) NOT NULL,
	valor_financiado numeric(15, 2) NOT NULL,
	pos_fixado varchar(10) DEFAULT 'NAO'::character varying NOT NULL,
	custo_bndes numeric(6, 2) NOT NULL,
	sobretaxa_bndes numeric(6, 2) NOT NULL,
	percentual_banco numeric(6, 2) NOT NULL,
	taxa_juros_efetiva numeric(10, 5) NOT NULL,
	prazo_total int4 NOT NULL,
	prazo_carencia int4 NOT NULL,
	prazo_final int4 NOT NULL,
	data_primeira_parcela_encargo date NOT NULL,
	data_primeira_parcela_prestacao date NOT NULL,
	data_ultima_parcela date NOT NULL,
	debito_conta_corrente bool DEFAULT false NULL,
	data_referencia date NULL,
	carencia_pagamento int4 NULL,
	registro_cobranca varchar(125) NULL,
	CONSTRAINT contratos_numero_contrato_key UNIQUE (numero_contrato),
	CONSTRAINT contratos_pkey PRIMARY KEY (id),
	CONSTRAINT contratos_id_banco_fkey FOREIGN KEY (id_banco) REFERENCES financiamento.bancos(id),
	CONSTRAINT contratos_id_empresa_fkey FOREIGN KEY (id_empresa) REFERENCES financiamento.empresas(id)
);

-- Table Triggers

create trigger trg_preencher_selic_contrato before
insert
    on
    financiamento.contratos for each row execute function financiamento.preencher_selic_contrato();
create trigger trg_set_data_referencia_contrato before
insert
    on
    financiamento.contratos for each row execute function financiamento.set_data_referencia_contrato();

-- Permissions

ALTER TABLE financiamento.contratos OWNER TO fin;
GRANT ALL ON TABLE financiamento.contratos TO fin;


-- financiamento.antecipacao definição

-- Drop table

-- DROP TABLE financiamento.antecipacao;

CREATE TABLE financiamento.antecipacao (
	id int4 GENERATED ALWAYS AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE) NOT NULL,
	id_contrato int4 NOT NULL,
	data_pagamento date NOT NULL,
	data_tesouraria date NOT NULL,
	selic numeric(10, 6) NULL,
	valor_pago numeric(15, 2) NOT NULL,
	valor_moeda numeric(15, 2) NULL,
	tipo_lancamento varchar(125) NULL,
	data_compensacao date NULL,
	CONSTRAINT antecipacao_pkey PRIMARY KEY (id),
	CONSTRAINT antecipacao_id_contrato_fkey FOREIGN KEY (id_contrato) REFERENCES financiamento.contratos(id)
);

-- Table Triggers

create trigger trg_processar_dados_antecipacao before
insert
    or
update
    on
    financiamento.antecipacao for each row execute function financiamento.processar_dados_antecipacao();

-- Permissions

ALTER TABLE financiamento.antecipacao OWNER TO fin;
GRANT ALL ON TABLE financiamento.antecipacao TO fin;


-- financiamento.bem definição

-- Drop table

-- DROP TABLE financiamento.bem;

CREATE TABLE financiamento.bem (
	id int4 GENERATED ALWAYS AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE) NOT NULL,
	id_fornecedor int4 NOT NULL,
	id_contrato int4 NOT NULL,
	descricao_bem varchar(255) NOT NULL,
	marca_bem varchar(255) NOT NULL,
	modelo_bem varchar(255) NOT NULL,
	ano_fabricacao int4 NOT NULL,
	ano_modelo int4 NOT NULL,
	placa varchar(10) NULL,
	chassi varchar(255) NULL,
	valor_venda numeric(15, 2) NOT NULL,
	CONSTRAINT bem_pkey PRIMARY KEY (id),
	CONSTRAINT bem_id_contrato_fkey FOREIGN KEY (id_contrato) REFERENCES financiamento.contratos(id),
	CONSTRAINT bem_id_fornecedor_fkey FOREIGN KEY (id_fornecedor) REFERENCES financiamento.fornecedor(id)
);

-- Permissions

ALTER TABLE financiamento.bem OWNER TO fin;
GRANT ALL ON TABLE financiamento.bem TO fin;


-- financiamento.veiculos definição

-- Drop table

-- DROP TABLE financiamento.veiculos;

CREATE TABLE financiamento.veiculos (
	id int4 GENERATED ALWAYS AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE) NOT NULL,
	id_bem_chassi int4 NULL,
	id_bem_carroceria int4 NULL,
	CONSTRAINT veiculos_pkey PRIMARY KEY (id),
	CONSTRAINT veiculos_id_bem_carroceria_fkey FOREIGN KEY (id_bem_carroceria) REFERENCES financiamento.bem(id),
	CONSTRAINT veiculos_id_bem_chassi_fkey FOREIGN KEY (id_bem_chassi) REFERENCES financiamento.bem(id)
);

-- Permissions

ALTER TABLE financiamento.veiculos OWNER TO fin;
GRANT ALL ON TABLE financiamento.veiculos TO fin;


-- financiamento.vw_controle_contratos fonte

CREATE OR REPLACE VIEW financiamento.vw_controle_contratos
AS SELECT c.id AS "Id",
    e.razao_social AS "Empresa",
    b.razao_social AS "Banco",
    c.numero_contrato AS "Contrato",
    c.data_emissao AS "Data de Emissão",
    c.valor_financiado AS "Valor",
    c.pos_fixado AS "Pós fixado",
    c.taxa_juros_efetiva AS "Juros",
    c.prazo_final AS "Prazo",
    c.data_ultima_parcela AS "Vencimento final"
   FROM financiamento.contratos c
     LEFT JOIN financiamento.empresas e ON c.id_empresa = e.id
     LEFT JOIN financiamento.bancos b ON c.id_banco = b.id;

-- Permissions

ALTER TABLE financiamento.vw_controle_contratos OWNER TO fin;
GRANT ALL ON TABLE financiamento.vw_controle_contratos TO fin;



-- DROP FUNCTION financiamento.dias_uteis_entre(date, date);

CREATE OR REPLACE FUNCTION financiamento.dias_uteis_entre(p_data1 date, p_data2 date)
 RETURNS integer
 LANGUAGE plpgsql
AS $function$
DECLARE
    v_inicio DATE := LEAST(p_data1, p_data2);
    v_fim    DATE := GREATEST(p_data1, p_data2);
    v_dias   INTEGER;
    v_sinal  INTEGER := CASE WHEN p_data1 > p_data2 THEN -1 ELSE 1 END;
BEGIN
    IF p_data1 IS NULL OR p_data2 IS NULL THEN
        RETURN NULL;
    END IF;

    -- Conta os dias úteis entre a menor e a maior data (inclusive as pontas)
    SELECT COUNT(*)::INTEGER
      INTO v_dias
      FROM generate_series(v_inicio, v_fim, INTERVAL '1 day') AS d(data_atual)
     WHERE EXTRACT(ISODOW FROM d.data_atual) NOT IN (6, 7) -- Remove Sáb/Dom
       AND NOT EXISTS (
           SELECT 1 
             FROM financiamento.feriados f 
            WHERE f.data = d.data_atual::date
       );

    -- Aplica a lógica exata do Excel: (Dias Úteis * Sinal) - 1
    RETURN (v_dias * v_sinal) - 1;
END;
$function$
;

-- Permissions

ALTER FUNCTION financiamento.dias_uteis_entre(date, date) OWNER TO fin;
GRANT ALL ON FUNCTION financiamento.dias_uteis_entre(date, date) TO fin;

-- DROP FUNCTION financiamento.preencher_selic_contrato();

CREATE OR REPLACE FUNCTION financiamento.preencher_selic_contrato()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    IF NEW.selic IS NULL THEN
        SELECT valor INTO NEW.selic
        FROM financiamento.selic
        WHERE data <= NEW.data_bndes
        ORDER BY data DESC
        LIMIT 1;
    END IF;
    
    RETURN NEW;
END;
$function$
;

-- Permissions

ALTER FUNCTION financiamento.preencher_selic_contrato() OWNER TO fin;
GRANT ALL ON FUNCTION financiamento.preencher_selic_contrato() TO fin;

-- DROP FUNCTION financiamento.processar_dados_antecipacao();

CREATE OR REPLACE FUNCTION financiamento.processar_dados_antecipacao()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    -- 1. Preenche a SELIC caso esteja nula, buscando a mais recente até a data_tesouraria
    IF NEW.selic IS NULL THEN
        SELECT valor INTO NEW.selic
        FROM financiamento.selic
        WHERE data <= NEW.data_tesouraria
        ORDER BY data DESC
        LIMIT 1;
    END IF;

    -- 2. Calcula a divisão de valor_pago por selic para preencher valor_moeda
    IF NEW.selic IS NOT NULL AND NEW.selic <> 0 THEN
        NEW.valor_moeda := ROUND((NEW.valor_pago / NEW.selic), 4);
    ELSE
        NEW.valor_moeda := NULL;
    END IF;

    RETURN NEW;
END;
$function$
;

-- Permissions

ALTER FUNCTION financiamento.processar_dados_antecipacao() OWNER TO fin;
GRANT ALL ON FUNCTION financiamento.processar_dados_antecipacao() TO fin;

-- DROP FUNCTION financiamento.projetar_contrato_selic(date, date, numeric, numeric, int4, int4, int4, varchar);

CREATE OR REPLACE FUNCTION financiamento.projetar_contrato_selic(p_data_emissao date, p_data_bndes date, p_valor_financiado numeric, p_taxa_juros_efetiva numeric, p_prazo_carencia integer, p_prazo_final integer, p_carencia_pagamento integer, p_registro_cobranca character varying)
 RETURNS TABLE(parcela numeric, tipo text, dia_util date, data_vencimento date, data_vcto date, dias_uteis integer, fator_juros numeric, saldo_devedor numeric, principal numeric, juros numeric, total_parcela numeric, valor_pagamento numeric)
 LANGUAGE sql
AS $function$
WITH parametros AS (
    SELECT
        p_data_emissao AS data_emissao,
        p_data_bndes AS data_bndes,
        p_valor_financiado AS valor_financiado,
        p_taxa_juros_efetiva AS taxa_juros_efetiva,
        p_prazo_carencia AS prazo_carencia,
        p_prazo_final AS prazo_final,
        COALESCE(p_carencia_pagamento, 0) AS carencia_pagamento,
        p_registro_cobranca AS registro_cobranca,
        CASE
            WHEN EXTRACT(DAY FROM p_data_emissao) <= 15
                THEN date_trunc('month', p_data_emissao)::date + INTERVAL '14 days'
            ELSE (date_trunc('month', p_data_emissao)::date + INTERVAL '1 month 14 days')::date
        END AS data_referencia,
        (
            SELECT valor
            FROM financiamento.selic
            WHERE data <= p_data_bndes
            ORDER BY data DESC
            LIMIT 1
        ) AS selic
), parcelas AS (
    SELECT
        p.*,
        serie.numero_seq AS parcela,
        CASE
            WHEN serie.numero_seq <= p.carencia_pagamento THEN 'CARENCIA'
            ELSE 'AMORTIZACAO'
        END AS tipo,
        CASE
            WHEN serie.numero_seq <= p.carencia_pagamento THEN
                (p.data_referencia + INTERVAL '1 month' * serie.numero_seq
                    * (p.prazo_carencia::numeric / NULLIF(p.carencia_pagamento, 0)))::date
            ELSE
                (p.data_referencia + INTERVAL '1 month' * p.prazo_carencia
                    + INTERVAL '1 month' * (serie.numero_seq - p.carencia_pagamento))::date
        END AS data_vencimento
    FROM parametros p
    CROSS JOIN LATERAL generate_series(
        1::numeric,
        (p.prazo_final + p.carencia_pagamento)::numeric
    ) AS serie(numero_seq)
), calendario AS (
    SELECT
        p.*,
        financiamento.proximo_dia_util(p.data_vencimento) AS data_vcto,
        financiamento.proximo_dia_util(
            date_trunc('month', p.data_vencimento)::date
        ) AS dia_util,
        CASE
            WHEN p.parcela = 1 THEN
                financiamento.dias_uteis_entre(p.data_bndes, financiamento.proximo_dia_util(p.data_vencimento))
            WHEN p.tipo = 'CARENCIA' THEN
                financiamento.dias_uteis_entre(
                    financiamento.proximo_dia_util(
                        (p.data_vencimento - INTERVAL '1 month'
                            * (p.prazo_carencia::numeric / NULLIF(p.carencia_pagamento, 0)))::date
                    ),
                    financiamento.proximo_dia_util(p.data_vencimento)
                )
            ELSE
                financiamento.dias_uteis_entre(
                    financiamento.proximo_dia_util((p.data_vencimento - INTERVAL '1 month')::date),
                    financiamento.proximo_dia_util(p.data_vencimento)
                )
        END AS dias_uteis
    FROM parcelas p
), calculo AS (
    SELECT
        c.*,
        ROUND(POWER(c.taxa_juros_efetiva / 100 + 1, c.dias_uteis::numeric / 252), 6) AS fator_juros,
        ROUND(c.valor_financiado / NULLIF(c.selic, 0), 2) AS saldo_inicial,
        CASE
            WHEN c.tipo = 'CARENCIA' THEN 0.00
            ELSE ROUND(c.valor_financiado / NULLIF(c.selic, 0) / c.prazo_final, 2)
        END AS principal_original
    FROM calendario c
), calculo_base AS (
    SELECT
        c.*,
        CASE
            WHEN c.tipo = 'CARENCIA' THEN c.saldo_inicial
            ELSE ROUND(
                c.saldo_inicial
                - c.principal_original * GREATEST(0, c.parcela - c.carencia_pagamento - 1),
                2
            )
        END AS saldo_devedor,
        c.principal_original AS principal,
        ROUND(
            (
                CASE
                    WHEN c.tipo = 'CARENCIA' THEN c.saldo_inicial
                    ELSE ROUND(
                        c.saldo_inicial
                        - c.principal_original * GREATEST(0, c.parcela - c.carencia_pagamento - 1),
                        2
                    )
                END
            ) * (c.fator_juros - 1),
            2
        ) AS juros,
        ROUND(
            c.principal_original
            + (
                CASE
                    WHEN c.tipo = 'CARENCIA' THEN c.saldo_inicial
                    ELSE ROUND(
                        c.saldo_inicial
                        - c.principal_original * GREATEST(0, c.parcela - c.carencia_pagamento - 1),
                        2
                    )
                END
            ) * (c.fator_juros - 1),
            2
        ) AS total_parcela
    FROM calculo c
), valores_selic AS (
    SELECT
        c.*,
        sdu.valor AS selic_dia_util,
        sdv.valor AS selic_vencimento,
        ultima.valor AS selic_ultima,
        CASE
            WHEN c.registro_cobranca = 'PRIMEIRO_DIA_UTIL' THEN
                ROUND(c.total_parcela * sdu.valor, 2)
            ELSE 0.00
        END AS valor_parcela_primeiro_dia_util,
        ROUND(c.total_parcela * sdv.valor, 2) AS valor_parcela_vencimento
    FROM calculo_base c
    LEFT JOIN financiamento.selic sdu ON c.dia_util = sdu.data
    LEFT JOIN financiamento.selic sdv ON c.data_vcto = sdv.data
    LEFT JOIN LATERAL (
        SELECT valor
        FROM financiamento.selic
        ORDER BY data DESC
        LIMIT 1
    ) ultima ON TRUE
), calcular_parcela_h AS (
    SELECT
        c.*,
        CASE
            WHEN c.parcela = 1
                OR c.registro_cobranca <> 'PRIMEIRO_DIA_UTIL'
            THEN 0.00
            ELSE COALESCE(
                LAG(c.valor_parcela_vencimento - c.valor_parcela_primeiro_dia_util, 1, 0.00)
                OVER (ORDER BY c.parcela),
                0.00
            )
        END AS parcela_h
    FROM valores_selic c
)
SELECT
    parcela,
    tipo,
    dia_util,
    data_vencimento,
    data_vcto,
    dias_uteis,
    fator_juros,
    saldo_devedor,
    principal,
    juros,
    total_parcela,
    CASE
        WHEN registro_cobranca = 'PRIMEIRO_DIA_UTIL' THEN
            ROUND(
                COALESCE(
                    valor_parcela_primeiro_dia_util + parcela_h,
                    total_parcela * selic_ultima
                ),
                2
            )
        ELSE valor_parcela_vencimento
    END AS valor_pagamento
FROM calcular_parcela_h
ORDER BY parcela;
$function$
;

-- Permissions

ALTER FUNCTION financiamento.projetar_contrato_selic(date, date, numeric, numeric, int4, int4, int4, varchar) OWNER TO fin;
GRANT ALL ON FUNCTION financiamento.projetar_contrato_selic(date, date, numeric, numeric, int4, int4, int4, varchar) TO fin;

-- DROP FUNCTION financiamento.projetar_contrato_tfc(date, date, numeric, numeric, int4, int4, int4);

CREATE OR REPLACE FUNCTION financiamento.projetar_contrato_tfc(p_data_emissao date, p_data_bndes date, p_valor_financiado numeric, p_taxa_juros_efetiva numeric, p_prazo_carencia integer, p_prazo_final integer, p_carencia_pagamento integer)
 RETURNS TABLE(parcela numeric, tipo text, dia_util date, data_vencimento date, data_vcto date, dias_corridos integer, fator_juros numeric, saldo_devedor numeric, principal numeric, juros numeric, total_parcela numeric, valor_pagamento numeric)
 LANGUAGE sql
AS $function$
WITH parametros AS (
    SELECT
        p_data_emissao AS data_emissao,
        p_data_bndes AS data_bndes,
        p_valor_financiado AS valor_financiado,
        p_taxa_juros_efetiva AS taxa_juros_efetiva,
        p_prazo_carencia AS prazo_carencia,
        p_prazo_final AS prazo_final,
        COALESCE(p_carencia_pagamento, 0) AS carencia_pagamento,
        CASE
            WHEN EXTRACT(DAY FROM p_data_emissao) <= 15
                THEN date_trunc('month', p_data_emissao)::date + INTERVAL '14 days'
            ELSE (date_trunc('month', p_data_emissao)::date + INTERVAL '1 month 14 days')::date
        END AS data_referencia
), parcelas AS (
    SELECT
        p.*,
        serie.numero_seq AS parcela,
        CASE
            WHEN serie.numero_seq <= p.carencia_pagamento THEN 'CARENCIA'
            ELSE 'AMORTIZACAO'
        END AS tipo,
        CASE
            WHEN serie.numero_seq <= p.carencia_pagamento THEN
                (p.data_referencia + INTERVAL '1 month' * serie.numero_seq
                    * (p.prazo_carencia::numeric / NULLIF(p.carencia_pagamento, 0)))::date
            ELSE
                (p.data_referencia + INTERVAL '1 month' * p.prazo_carencia
                    + INTERVAL '1 month' * (serie.numero_seq - p.carencia_pagamento))::date
        END AS data_vencimento
    FROM parametros p
    CROSS JOIN LATERAL generate_series(
        1::numeric,
        (p.prazo_final + p.carencia_pagamento)::numeric
    ) AS serie(numero_seq)
), calculo AS (
    SELECT
        p.*,
        financiamento.proximo_dia_util(date_trunc('month', p.data_vencimento)::date) AS dia_util,
        financiamento.proximo_dia_util(p.data_vencimento) AS data_vcto,
        CASE
            WHEN p.parcela = 1 THEN p.data_vencimento - p.data_bndes
            WHEN p.tipo = 'CARENCIA' THEN
                financiamento.proximo_dia_util(p.data_vencimento)
                - financiamento.proximo_dia_util(
                    (p.data_vencimento - INTERVAL '1 month'
                        * (p.prazo_carencia::numeric / NULLIF(p.carencia_pagamento, 0)))::date
                )
            ELSE
                financiamento.proximo_dia_util(p.data_vencimento)
                - financiamento.proximo_dia_util((p.data_vencimento - INTERVAL '1 month')::date)
        END AS dias_corridos,
        ROUND(
            POWER(
                p.taxa_juros_efetiva / 100 + 1,
                (
                    CASE
                        WHEN p.parcela = 1 THEN p.data_vencimento - p.data_bndes
                        WHEN p.tipo = 'CARENCIA' THEN
                            financiamento.proximo_dia_util(p.data_vencimento)
                            - financiamento.proximo_dia_util(
                                (p.data_vencimento - INTERVAL '1 month'
                                    * (p.prazo_carencia::numeric / NULLIF(p.carencia_pagamento, 0)))::date
                            )
                        ELSE
                            financiamento.proximo_dia_util(p.data_vencimento)
                            - financiamento.proximo_dia_util((p.data_vencimento - INTERVAL '1 month')::date)
                    END
                )::numeric / 365
            ),
            6
        ) AS fator_juros,
        ROUND(p.valor_financiado, 2) AS saldo_inicial,
        CASE
            WHEN p.tipo = 'CARENCIA' THEN 0.00
            ELSE ROUND(p.valor_financiado / p.prazo_final, 2)
        END AS principal_original
    FROM parcelas p
), calculo_saldo AS (
    SELECT
        c.*,
        CASE
            WHEN c.tipo = 'CARENCIA' THEN c.saldo_inicial
            ELSE ROUND(
                c.saldo_inicial
                - c.principal_original * GREATEST(0, c.parcela - c.carencia_pagamento - 1),
                2
            )
        END AS saldo_devedor
    FROM calculo c
)
SELECT
    parcela,
    tipo,
    dia_util,
    data_vencimento,
    data_vcto,
    dias_corridos,
    fator_juros,
    saldo_devedor,
    principal_original AS principal,
    ROUND(saldo_devedor * (fator_juros - 1), 2) AS juros,
    ROUND(principal_original + saldo_devedor * (fator_juros - 1), 2) AS total_parcela,
    ROUND(principal_original + saldo_devedor * (fator_juros - 1), 2) AS valor_pagamento
FROM calculo_saldo
ORDER BY parcela;
$function$
;

-- Permissions

ALTER FUNCTION financiamento.projetar_contrato_tfc(date, date, numeric, numeric, int4, int4, int4) OWNER TO fin;
GRANT ALL ON FUNCTION financiamento.projetar_contrato_tfc(date, date, numeric, numeric, int4, int4, int4) TO fin;

-- DROP FUNCTION financiamento.proximo_dia_util(date);

CREATE OR REPLACE FUNCTION financiamento.proximo_dia_util(p_data date)
 RETURNS date
 LANGUAGE plpgsql
AS $function$
DECLARE
    v_data DATE := p_data;
BEGIN
    -- Loop avança enquanto for sábado (6), domingo (7) ou constar na tabela de feriados
    WHILE EXTRACT(ISODOW FROM v_data) IN (6, 7) 
       OR EXISTS (SELECT 1 FROM financiamento.feriados WHERE data = v_data) 
    LOOP
        v_data := v_data + 1;
    END LOOP;

    RETURN v_data;
END;
$function$
;

-- Permissions

ALTER FUNCTION financiamento.proximo_dia_util(date) OWNER TO fin;
GRANT ALL ON FUNCTION financiamento.proximo_dia_util(date) TO fin;

-- DROP FUNCTION financiamento.set_data_referencia_contrato();

CREATE OR REPLACE FUNCTION financiamento.set_data_referencia_contrato()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    NEW.data_referencia := CASE
        WHEN EXTRACT(DAY FROM NEW.data_emissao) <= 15 THEN 
            (date_trunc('month', NEW.data_emissao)::date + INTERVAL '14 days')::date
        ELSE
            (date_trunc('month', NEW.data_emissao)::date + INTERVAL '1 month + 14 days')::date
    END;

    RETURN NEW;
END;
$function$
;

-- Permissions

ALTER FUNCTION financiamento.set_data_referencia_contrato() OWNER TO fin;
GRANT ALL ON FUNCTION financiamento.set_data_referencia_contrato() TO fin;


-- Permissions

GRANT ALL ON SCHEMA financiamento TO fin;