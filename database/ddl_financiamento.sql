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
create trigger trg_after_insert_contratos after
insert
    on
    financiamento.contratos for each statement execute function financiamento.refresh_views_contratos();

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


-- financiamento.mv_projecao_moeda fonte

CREATE MATERIALIZED VIEW financiamento.mv_projecao_moeda
TABLESPACE pg_default
AS WITH dados_parcelado AS (
         SELECT c.id AS id_contrato,
            p.numero_seq AS parcela,
            c.carencia_pagamento,
                CASE
                    WHEN p.numero_seq <= COALESCE(c.carencia_pagamento, 0)::numeric THEN 'CARENCIA'::text
                    ELSE 'AMORTIZACAO'::text
                END AS tipo,
            c.data_emissao,
            c.data_referencia,
            c.data_bndes,
            c.taxa_juros_efetiva,
            c.valor_financiado,
            c.selic,
            c.prazo_carencia,
            c.prazo_final,
                CASE
                    WHEN p.numero_seq <= COALESCE(c.carencia_pagamento, 0)::numeric THEN c.data_referencia + '1 mon'::interval * p.numero_seq::double precision * (c.prazo_carencia::double precision / NULLIF(c.carencia_pagamento, 0)::double precision)
                    ELSE c.data_referencia + '1 mon'::interval * c.prazo_carencia::double precision + '1 mon'::interval * (p.numero_seq - COALESCE(c.carencia_pagamento, 0)::numeric)::double precision
                END::date AS data_vencimento
           FROM financiamento.contratos c
             CROSS JOIN LATERAL generate_series(1::numeric, (c.prazo_final + COALESCE(c.carencia_pagamento, 0))::numeric) p(numero_seq)
          WHERE c.tipo_contrato::text = 'BNDES FINAME SELIC'::text
        ), dados_dias_uteis AS (
         SELECT dp.id_contrato,
            dp.parcela,
            dp.carencia_pagamento,
            dp.tipo,
            dp.data_emissao,
            dp.data_referencia,
            dp.data_bndes,
            dp.taxa_juros_efetiva,
            dp.valor_financiado,
            dp.selic,
            dp.prazo_carencia,
            dp.prazo_final,
            dp.data_vencimento,
            financiamento.proximo_dia_util(date_trunc('month'::text, dp.data_vencimento::timestamp with time zone)::date) AS data_primeiro_dia,
            financiamento.proximo_dia_util(dp.data_vencimento) AS data_vencimento_real,
                CASE
                    WHEN dp.parcela = 1::numeric THEN financiamento.dias_uteis_entre(dp.data_bndes, financiamento.proximo_dia_util(dp.data_vencimento))
                    WHEN dp.tipo = 'CARENCIA'::text THEN financiamento.dias_uteis_entre(financiamento.proximo_dia_util((dp.data_vencimento - '1 mon'::interval * (dp.prazo_carencia::double precision / NULLIF(dp.carencia_pagamento, 0)::double precision))::date), financiamento.proximo_dia_util(dp.data_vencimento))
                    ELSE financiamento.dias_uteis_entre(financiamento.proximo_dia_util((dp.data_vencimento - '1 mon'::interval)::date), financiamento.proximo_dia_util(dp.data_vencimento))
                END AS dias_uteis,
            a.data_pagamento AS data_antec,
            a.selic AS selic_antec,
            a.valor_pago AS liq_antec,
            COALESCE(a.valor_moeda, 0::numeric) AS valor_em_moeda
           FROM dados_parcelado dp
             LEFT JOIN financiamento.antecipacao a ON dp.id_contrato = a.id_contrato AND date_trunc('month'::text, a.data_pagamento::timestamp with time zone) = date_trunc('month'::text, dp.data_vencimento::timestamp with time zone)
        ), calculo_base AS (
         SELECT dados_dias_uteis.id_contrato,
            dados_dias_uteis.parcela,
            dados_dias_uteis.carencia_pagamento,
            dados_dias_uteis.tipo,
            dados_dias_uteis.data_emissao,
            dados_dias_uteis.data_referencia,
            dados_dias_uteis.data_bndes,
            dados_dias_uteis.taxa_juros_efetiva,
            dados_dias_uteis.valor_financiado,
            dados_dias_uteis.selic,
            dados_dias_uteis.prazo_carencia,
            dados_dias_uteis.prazo_final,
            dados_dias_uteis.data_vencimento,
            dados_dias_uteis.data_primeiro_dia,
            dados_dias_uteis.data_vencimento_real,
            dados_dias_uteis.dias_uteis,
            dados_dias_uteis.data_antec,
            dados_dias_uteis.selic_antec,
            dados_dias_uteis.liq_antec,
            dados_dias_uteis.valor_em_moeda,
            round(power(dados_dias_uteis.taxa_juros_efetiva::numeric / 100::numeric + 1::numeric, dados_dias_uteis.dias_uteis::numeric / 252::numeric), 6) AS fator_juros,
            round(dados_dias_uteis.valor_financiado / dados_dias_uteis.selic, 2) AS saldo_inicial,
                CASE
                    WHEN dados_dias_uteis.tipo = 'CARENCIA'::text THEN 0.00
                    ELSE round(dados_dias_uteis.valor_financiado / dados_dias_uteis.selic / dados_dias_uteis.prazo_final::numeric, 2)
                END AS principal_original,
            max(
                CASE
                    WHEN dados_dias_uteis.valor_em_moeda > 0::numeric THEN dados_dias_uteis.parcela
                    ELSE NULL::numeric
                END) OVER (PARTITION BY dados_dias_uteis.id_contrato) AS parcela_antecipacao,
            max(dados_dias_uteis.valor_em_moeda) OVER (PARTITION BY dados_dias_uteis.id_contrato) AS total_antecipado,
            GREATEST(0::numeric, dados_dias_uteis.parcela - COALESCE(dados_dias_uteis.carencia_pagamento, 0)::numeric - 1::numeric) AS qtd_amortizacoes_anteriores
           FROM dados_dias_uteis
        ), calculo_novo_principal AS (
         SELECT calculo_base.id_contrato,
            calculo_base.parcela,
            calculo_base.carencia_pagamento,
            calculo_base.tipo,
            calculo_base.data_emissao,
            calculo_base.data_referencia,
            calculo_base.data_bndes,
            calculo_base.taxa_juros_efetiva,
            calculo_base.valor_financiado,
            calculo_base.selic,
            calculo_base.prazo_carencia,
            calculo_base.prazo_final,
            calculo_base.data_vencimento,
            calculo_base.data_primeiro_dia,
            calculo_base.data_vencimento_real,
            calculo_base.dias_uteis,
            calculo_base.data_antec,
            calculo_base.selic_antec,
            calculo_base.liq_antec,
            calculo_base.valor_em_moeda,
            calculo_base.fator_juros,
            calculo_base.saldo_inicial,
            calculo_base.principal_original,
            calculo_base.parcela_antecipacao,
            calculo_base.total_antecipado,
            calculo_base.qtd_amortizacoes_anteriores,
            round(calculo_base.saldo_inicial - calculo_base.principal_original * GREATEST(0::numeric, COALESCE(calculo_base.parcela_antecipacao, 0::numeric) - COALESCE(calculo_base.carencia_pagamento, 0)::numeric - 1::numeric), 2) AS saldo_mes_antecipacao,
            calculo_base.prazo_final::numeric - GREATEST(0::numeric, COALESCE(calculo_base.parcela_antecipacao, 0::numeric) - COALESCE(calculo_base.carencia_pagamento, 0)::numeric) AS parcelas_restantes_pos_antec
           FROM calculo_base
        ), calculo_final_estruturado AS (
         SELECT calculo_novo_principal.id_contrato,
            calculo_novo_principal.parcela,
            calculo_novo_principal.carencia_pagamento,
            calculo_novo_principal.tipo,
            calculo_novo_principal.data_emissao,
            calculo_novo_principal.data_referencia,
            calculo_novo_principal.data_bndes,
            calculo_novo_principal.taxa_juros_efetiva,
            calculo_novo_principal.valor_financiado,
            calculo_novo_principal.selic,
            calculo_novo_principal.prazo_carencia,
            calculo_novo_principal.prazo_final,
            calculo_novo_principal.data_vencimento,
            calculo_novo_principal.data_primeiro_dia,
            calculo_novo_principal.data_vencimento_real,
            calculo_novo_principal.dias_uteis,
            calculo_novo_principal.data_antec,
            calculo_novo_principal.selic_antec,
            calculo_novo_principal.liq_antec,
            calculo_novo_principal.valor_em_moeda,
            calculo_novo_principal.fator_juros,
            calculo_novo_principal.saldo_inicial,
            calculo_novo_principal.principal_original,
            calculo_novo_principal.parcela_antecipacao,
            calculo_novo_principal.total_antecipado,
            calculo_novo_principal.qtd_amortizacoes_anteriores,
            calculo_novo_principal.saldo_mes_antecipacao,
            calculo_novo_principal.parcelas_restantes_pos_antec,
                CASE
                    WHEN calculo_novo_principal.tipo = 'CARENCIA'::text THEN 0.00
                    WHEN calculo_novo_principal.parcela_antecipacao IS NOT NULL AND calculo_novo_principal.parcela > calculo_novo_principal.parcela_antecipacao THEN round((calculo_novo_principal.saldo_mes_antecipacao - calculo_novo_principal.principal_original - calculo_novo_principal.total_antecipado) / calculo_novo_principal.parcelas_restantes_pos_antec, 2)
                    ELSE calculo_novo_principal.principal_original
                END AS principal_efetivo
           FROM calculo_novo_principal
        ), calculo_saldo AS (
         SELECT calculo_final_estruturado.id_contrato,
            calculo_final_estruturado.parcela,
            calculo_final_estruturado.carencia_pagamento,
            calculo_final_estruturado.tipo,
            calculo_final_estruturado.data_emissao,
            calculo_final_estruturado.data_referencia,
            calculo_final_estruturado.data_bndes,
            calculo_final_estruturado.taxa_juros_efetiva,
            calculo_final_estruturado.valor_financiado,
            calculo_final_estruturado.selic,
            calculo_final_estruturado.prazo_carencia,
            calculo_final_estruturado.prazo_final,
            calculo_final_estruturado.data_vencimento,
            calculo_final_estruturado.data_primeiro_dia,
            calculo_final_estruturado.data_vencimento_real,
            calculo_final_estruturado.dias_uteis,
            calculo_final_estruturado.data_antec,
            calculo_final_estruturado.selic_antec,
            calculo_final_estruturado.liq_antec,
            calculo_final_estruturado.valor_em_moeda,
            calculo_final_estruturado.fator_juros,
            calculo_final_estruturado.saldo_inicial,
            calculo_final_estruturado.principal_original,
            calculo_final_estruturado.parcela_antecipacao,
            calculo_final_estruturado.total_antecipado,
            calculo_final_estruturado.qtd_amortizacoes_anteriores,
            calculo_final_estruturado.saldo_mes_antecipacao,
            calculo_final_estruturado.parcelas_restantes_pos_antec,
            calculo_final_estruturado.principal_efetivo,
                CASE
                    WHEN calculo_final_estruturado.tipo = 'CARENCIA'::text THEN calculo_final_estruturado.saldo_inicial
                    WHEN calculo_final_estruturado.parcela_antecipacao IS NOT NULL AND calculo_final_estruturado.parcela > calculo_final_estruturado.parcela_antecipacao THEN round(calculo_final_estruturado.saldo_mes_antecipacao - calculo_final_estruturado.principal_original - calculo_final_estruturado.total_antecipado - calculo_final_estruturado.principal_efetivo * (calculo_final_estruturado.parcela - calculo_final_estruturado.parcela_antecipacao - 1::numeric), 2)
                    ELSE round(calculo_final_estruturado.saldo_inicial - calculo_final_estruturado.principal_original * calculo_final_estruturado.qtd_amortizacoes_anteriores, 2)
                END AS saldo_devedor
           FROM calculo_final_estruturado
        )
 SELECT row_number() OVER (ORDER BY id_contrato, parcela) AS id,
    id_contrato,
    parcela,
    tipo,
    data_primeiro_dia AS dia_util,
    data_vencimento AS data,
    data_vencimento_real AS data_vcto,
    dias_uteis,
    fator_juros,
    saldo_devedor,
    valor_em_moeda AS antecipacao,
    principal_efetivo AS principal,
    round(saldo_devedor * (fator_juros - 1::numeric), 2) AS juros,
    round(principal_efetivo + saldo_devedor * (fator_juros - 1::numeric), 2) AS total_parcela
   FROM calculo_saldo
  ORDER BY id_contrato, parcela
WITH DATA;

-- View indexes:
CREATE UNIQUE INDEX idx_projecao_moeda_id ON financiamento.mv_projecao_moeda USING btree (id);


-- Permissions

ALTER TABLE financiamento.mv_projecao_moeda OWNER TO fin;
GRANT ALL ON TABLE financiamento.mv_projecao_moeda TO fin;


-- financiamento.mv_projecao_moeda_final fonte

CREATE MATERIALIZED VIEW financiamento.mv_projecao_moeda_final
TABLESPACE pg_default
AS WITH calculo_base AS (
         SELECT m.id AS id_projecao_moeda,
            m.id_contrato,
            m.parcela,
            m.dia_util,
            m.data_vcto,
            m.total_parcela,
            c.registro_cobranca,
            sdu.valor AS selic_dia_util,
            sdv.valor AS selic_vencimento,
                CASE
                    WHEN c.registro_cobranca::text = 'PRIMEIRO_DIA_UTIL'::text THEN round(m.total_parcela * sdu.valor, 2)
                    ELSE 0::numeric
                END AS valor_parcela_primeiro_dia_util,
            round(m.total_parcela * sdv.valor, 2) AS valor_parcela_vencimento
           FROM financiamento.mv_projecao_moeda m
             LEFT JOIN financiamento.selic sdu ON m.dia_util = sdu.data
             LEFT JOIN financiamento.selic sdv ON m.data_vcto = sdv.data
             LEFT JOIN financiamento.contratos c ON m.id_contrato = c.id
          ORDER BY m.id
        ), calcular_parcela_h AS (
         SELECT calculo_base.id_projecao_moeda,
            calculo_base.id_contrato,
            calculo_base.parcela,
            calculo_base.dia_util,
            calculo_base.data_vcto,
            calculo_base.total_parcela,
            calculo_base.registro_cobranca,
            calculo_base.selic_dia_util,
            calculo_base.selic_vencimento,
            calculo_base.valor_parcela_primeiro_dia_util,
            calculo_base.valor_parcela_vencimento,
                CASE
                    WHEN calculo_base.parcela = 1::numeric OR NOT calculo_base.registro_cobranca::text = 'PRIMEIRO_DIA_UTIL'::text THEN 0.00
                    ELSE COALESCE(lag(calculo_base.valor_parcela_vencimento - calculo_base.valor_parcela_primeiro_dia_util, 1, 0::numeric) OVER (PARTITION BY calculo_base.id_contrato ORDER BY calculo_base.parcela), 0::numeric)
                END AS parcela_h
           FROM calculo_base
        )
 SELECT id_projecao_moeda,
    id_contrato,
    parcela,
    dia_util,
    data_vcto,
    total_parcela,
    selic_dia_util,
    selic_vencimento,
    valor_parcela_primeiro_dia_util,
    valor_parcela_vencimento,
    parcela_h,
        CASE
            WHEN registro_cobranca::text = 'PRIMEIRO_DIA_UTIL'::text THEN round(COALESCE(valor_parcela_primeiro_dia_util + parcela_h, total_parcela * (( SELECT selic.valor
               FROM financiamento.selic
              ORDER BY selic.data DESC
             LIMIT 1))), 2)
            ELSE valor_parcela_vencimento
        END AS valor_pagamento
   FROM calcular_parcela_h
WITH DATA;

-- Permissions

ALTER TABLE financiamento.mv_projecao_moeda_final OWNER TO fin;
GRANT ALL ON TABLE financiamento.mv_projecao_moeda_final TO fin;


-- financiamento.mv_projecao_tfc fonte

CREATE MATERIALIZED VIEW financiamento.mv_projecao_tfc
TABLESPACE pg_default
AS WITH dados_parcelado AS (
         SELECT c.id AS id_contrato,
            p.numero_seq AS parcela,
            c.carencia_pagamento,
                CASE
                    WHEN p.numero_seq <= COALESCE(c.carencia_pagamento, 0)::numeric THEN 'CARENCIA'::text
                    ELSE 'AMORTIZACAO'::text
                END AS tipo,
            c.data_emissao,
            c.data_referencia,
            c.data_bndes,
            c.taxa_juros_efetiva,
            c.valor_financiado,
            c.prazo_carencia,
            c.prazo_final,
                CASE
                    WHEN p.numero_seq <= COALESCE(c.carencia_pagamento, 0)::numeric THEN c.data_referencia + '1 mon'::interval * p.numero_seq::double precision * (c.prazo_carencia::double precision / NULLIF(c.carencia_pagamento, 0)::double precision)
                    ELSE c.data_referencia + '1 mon'::interval * c.prazo_carencia::double precision + '1 mon'::interval * (p.numero_seq - COALESCE(c.carencia_pagamento, 0)::numeric)::double precision
                END::date AS data_vencimento
           FROM financiamento.contratos c
             CROSS JOIN LATERAL generate_series(1::numeric, (c.prazo_final + COALESCE(c.carencia_pagamento, 0))::numeric) p(numero_seq)
          WHERE c.tipo_contrato::text = 'BNDES FINAME TFC'::text
        ), dados_dias_uteis AS (
         SELECT dp.id_contrato,
            dp.parcela,
            dp.carencia_pagamento,
            dp.tipo,
            dp.data_emissao,
            dp.data_referencia,
            dp.taxa_juros_efetiva,
            dp.valor_financiado,
            dp.prazo_carencia,
            dp.prazo_final,
            dp.data_vencimento,
            financiamento.proximo_dia_util(date_trunc('month'::text, dp.data_vencimento::timestamp with time zone)::date) AS data_primeiro_dia,
            financiamento.proximo_dia_util(dp.data_vencimento) AS data_vencimento_real,
                CASE
                    WHEN dp.parcela = 1::numeric THEN dp.data_vencimento - dp.data_bndes
                    WHEN dp.tipo = 'CARENCIA'::text THEN financiamento.proximo_dia_util(dp.data_vencimento) - financiamento.proximo_dia_util((dp.data_vencimento - '1 mon'::interval * (dp.prazo_carencia::double precision / NULLIF(dp.carencia_pagamento, 0)::double precision))::date)
                    ELSE financiamento.proximo_dia_util(dp.data_vencimento) - financiamento.proximo_dia_util((dp.data_vencimento - '1 mon'::interval)::date)
                END AS dias_corridos,
            a.data_pagamento AS data_antec,
            a.valor_pago AS liq_antec
           FROM dados_parcelado dp
             LEFT JOIN financiamento.antecipacao a ON dp.id_contrato = a.id_contrato AND date_trunc('month'::text, a.data_pagamento::timestamp with time zone) = date_trunc('month'::text, dp.data_vencimento::timestamp with time zone)
        ), calculo_base AS (
         SELECT dados_dias_uteis.id_contrato,
            dados_dias_uteis.parcela,
            dados_dias_uteis.carencia_pagamento,
            dados_dias_uteis.tipo,
            dados_dias_uteis.data_emissao,
            dados_dias_uteis.data_referencia,
            dados_dias_uteis.taxa_juros_efetiva,
            dados_dias_uteis.valor_financiado,
            dados_dias_uteis.prazo_carencia,
            dados_dias_uteis.prazo_final,
            dados_dias_uteis.data_vencimento,
            dados_dias_uteis.data_primeiro_dia,
            dados_dias_uteis.data_vencimento_real,
            dados_dias_uteis.dias_corridos,
            dados_dias_uteis.data_antec,
            dados_dias_uteis.liq_antec,
            round(power(dados_dias_uteis.taxa_juros_efetiva::numeric / 100::numeric + 1::numeric, dados_dias_uteis.dias_corridos::numeric / 365::numeric), 6) AS fator_juros,
            round(dados_dias_uteis.valor_financiado, 2) AS saldo_inicial,
                CASE
                    WHEN dados_dias_uteis.tipo = 'CARENCIA'::text THEN 0.00
                    ELSE round(dados_dias_uteis.valor_financiado / dados_dias_uteis.prazo_final::numeric, 2)
                END AS principal_original,
            GREATEST(0::numeric, dados_dias_uteis.parcela - COALESCE(dados_dias_uteis.carencia_pagamento, 0)::numeric - 1::numeric) AS qtd_amortizacoes_anteriores
           FROM dados_dias_uteis
        ), calculo_saldo AS (
         SELECT calculo_base.id_contrato,
            calculo_base.parcela,
            calculo_base.carencia_pagamento,
            calculo_base.tipo,
            calculo_base.data_emissao,
            calculo_base.data_referencia,
            calculo_base.taxa_juros_efetiva,
            calculo_base.valor_financiado,
            calculo_base.prazo_carencia,
            calculo_base.prazo_final,
            calculo_base.data_vencimento,
            calculo_base.data_primeiro_dia,
            calculo_base.data_vencimento_real,
            calculo_base.dias_corridos,
            calculo_base.data_antec,
            calculo_base.liq_antec,
            calculo_base.fator_juros,
            calculo_base.saldo_inicial,
            calculo_base.principal_original,
            calculo_base.qtd_amortizacoes_anteriores,
                CASE
                    WHEN calculo_base.tipo = 'CARENCIA'::text THEN calculo_base.saldo_inicial
                    ELSE round(calculo_base.saldo_inicial - calculo_base.principal_original * calculo_base.qtd_amortizacoes_anteriores, 2)
                END AS saldo_devedor
           FROM calculo_base
        )
 SELECT row_number() OVER (ORDER BY id_contrato, parcela) AS id,
    id_contrato,
    parcela,
    tipo,
    data_primeiro_dia AS dia_util,
    data_vencimento AS data,
    data_vencimento_real AS data_vcto,
    dias_corridos,
    fator_juros,
    saldo_devedor,
    principal_original AS principal,
    round(saldo_devedor * (fator_juros - 1::numeric), 2) AS juros,
    round(principal_original + saldo_devedor * (fator_juros - 1::numeric), 2) AS total_parcela
   FROM calculo_saldo
  ORDER BY id_contrato, parcela
WITH DATA;

-- Permissions

ALTER TABLE financiamento.mv_projecao_tfc OWNER TO fin;
GRANT ALL ON TABLE financiamento.mv_projecao_tfc TO fin;


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

-- DROP FUNCTION financiamento.refresh_views_contratos();

CREATE OR REPLACE FUNCTION financiamento.refresh_views_contratos()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
	REFRESH MATERIALIZED VIEW financiamento.mv_projecao_moeda;
	REFRESH MATERIALIZED VIEW financiamento.mv_projecao_moeda_final;
	REFRESH MATERIALIZED VIEW financiamento.mv_projecao_tfc;
	RETURN NEW;
END;
$function$
;

-- Permissions

ALTER FUNCTION financiamento.refresh_views_contratos() OWNER TO fin;
GRANT ALL ON FUNCTION financiamento.refresh_views_contratos() TO fin;

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