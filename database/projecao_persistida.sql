-- =====================================================================
-- Projeção persistida, liquidação e conciliação com o ERP - estado final (schema financiamento)
-- =====================================================================
-- Consolida os scripts da migração executados em 15-16/10/2026 (substituição das materialized views
-- mv_projecao_moeda / mv_projecao_moeda_final / mv_projecao_tfc pela tabela projecao_parcelas).
--
-- ATENÇÃO: o banco de produção JÁ ESTÁ neste estado. Este arquivo é documentação e serve para montar
-- um banco novo (ex.: ambiente de teste) a partir do schema financiamento sem estes objetos.
-- NÃO executar novamente em produção.
--
-- Ordem: 1) tabelas de projeção; 2) função de cálculo; 3) liquidação e recálculo; 4) triggers de
-- recálculo automático; 5) vínculo ERP; 6) carga inicial (uma única vez, depois da SELIC carregada).
-- A SELIC é carregada pela tela Cadastros > Selic (Atualizar Selic - BNDES).
-- =====================================================================

-- #####################################################################
-- 1. Tabelas da projeção (projecao_controle, projecao_parcelas)
-- #####################################################################

CREATE TABLE financiamento.projecao_controle (
	id_contrato int4 NOT NULL,
	status_projecao varchar(20) DEFAULT 'PENDENTE' NOT NULL,
	status_contrato varchar(20) DEFAULT 'ATIVO' NOT NULL,
	motivo_ultimo_calculo varchar(30) NULL,
	data_ultimo_calculo timestamp NULL,
	qtd_parcelas int4 DEFAULT 0 NOT NULL,
	qtd_liquidadas int4 DEFAULT 0 NOT NULL,
	saldo_devedor_atual numeric(15, 2) NULL,
	mensagem_erro text NULL,
	CONSTRAINT projecao_controle_pkey PRIMARY KEY (id_contrato),
	CONSTRAINT projecao_controle_id_contrato_fkey FOREIGN KEY (id_contrato)
		REFERENCES financiamento.contratos(id) ON DELETE CASCADE,
	CONSTRAINT projecao_controle_status_projecao_ck
		CHECK (status_projecao IN ('PENDENTE', 'PROJETADO', 'ERRO')),
	CONSTRAINT projecao_controle_status_contrato_ck
		CHECK (status_contrato IN ('ATIVO', 'QUITADO', 'ENCERRADO'))
);

-- Parcelas projetadas: substitui mv_projecao_moeda, mv_projecao_moeda_final e mv_projecao_tfc
CREATE TABLE financiamento.projecao_parcelas (
	id int4 GENERATED ALWAYS AS IDENTITY NOT NULL,
	id_contrato int4 NOT NULL,
	parcela int4 NOT NULL,
	tipo varchar(15) NOT NULL,                       -- CARENCIA / AMORTIZACAO
	dia_util date NULL,                              -- 1º dia útil do mês
	"data" date NOT NULL,                            -- vencimento teórico (chave da conciliação)
	data_vcto date NULL,                             -- vencimento ajustado para dia útil
	dias_uteis int4 NULL,                            -- SELIC
	dias_corridos int4 NULL,                         -- TFC
	fator_juros numeric(12, 6) NULL,
	saldo_devedor numeric(15, 2) NULL,
	antecipacao numeric(15, 2) NULL,
	tipo_lancamento varchar(125) NULL,
	principal numeric(15, 2) NULL,                   -- em moeda (SELIC) / R$ (TFC)
	juros numeric(15, 2) NULL,
	total_parcela numeric(15, 2) NULL,
	selic_dia_util numeric(12, 8) NULL,
	selic_vencimento numeric(12, 8) NULL,
	valor_parcela_primeiro_dia_util numeric(15, 2) NULL,
	valor_parcela_vencimento numeric(15, 2) NULL,
	valor_principal numeric(15, 2) NULL,             -- R$
	valor_juros numeric(15, 2) NULL,                 -- R$
	parcela_h numeric(15, 2) NULL,
	valor_pagamento numeric(15, 2) NULL,             -- R$ (valor conciliado com o ERP)
	situacao varchar(20) DEFAULT 'ABERTA' NOT NULL,
	atualizado_em timestamp DEFAULT now() NOT NULL,
	CONSTRAINT projecao_parcelas_pkey PRIMARY KEY (id),
	CONSTRAINT projecao_parcelas_contrato_parcela_key UNIQUE (id_contrato, parcela),
	CONSTRAINT projecao_parcelas_id_contrato_fkey FOREIGN KEY (id_contrato)
		REFERENCES financiamento.contratos(id) ON DELETE CASCADE,
	CONSTRAINT projecao_parcelas_situacao_ck
		CHECK (situacao IN ('ABERTA', 'LIQUIDADA', 'CANCELADA_QUITACAO'))
);

CREATE INDEX projecao_parcelas_contrato_data_idx
	ON financiamento.projecao_parcelas USING btree (id_contrato, "data");

-- Comentários
COMMENT ON TABLE financiamento.projecao_controle IS 'Controle da projeção por contrato (recálculo individual; substitui o refresh global das MVs).';
COMMENT ON TABLE financiamento.projecao_parcelas IS 'Parcelas projetadas por contrato (SELIC e TFC). Parcelas LIQUIDADAS não são alteradas pelo recálculo.';

-- Permissões (somente das tabelas novas)
ALTER TABLE financiamento.projecao_controle OWNER TO fin;
GRANT ALL ON TABLE financiamento.projecao_controle TO fin;
ALTER TABLE financiamento.projecao_parcelas OWNER TO fin;
GRANT ALL ON TABLE financiamento.projecao_parcelas TO fin;

-- #####################################################################
-- 2. Cálculo da projeção de um contrato (não grava)
-- #####################################################################

-- =====================================================================
-- Cálculo puro (não grava). Reproduz mv_projecao_moeda + mv_projecao_moeda_final (SELIC)
-- e mv_projecao_tfc (TFC) para um único contrato.
-- p_data_base (opcional): considera só as antecipações/quitações pagas até essa data (posição
-- histórica dos relatórios); NULL = todas (projeção atual, usada pelo recálculo).
-- Diferenças intencionais em relação às MVs:
--   - quitação não exclui as parcelas posteriores: devolve situacao = 'CANCELADA_QUITACAO';
--   - SELIC repetida na mesma data: usa a de maior id; "última SELIC" ignora data nula;
--   - TFC sem o JOIN de antecipação (não entra no cálculo e só poderia duplicar linhas).
-- =====================================================================
CREATE OR REPLACE FUNCTION financiamento.calcular_projecao_contrato(p_id_contrato int4, p_data_base date DEFAULT NULL)
 RETURNS TABLE (
	parcela int4, tipo varchar, dia_util date, "data" date, data_vcto date,
	dias_uteis int4, dias_corridos int4, fator_juros numeric, saldo_devedor numeric,
	antecipacao numeric, tipo_lancamento varchar, principal numeric, juros numeric, total_parcela numeric,
	selic_dia_util numeric, selic_vencimento numeric,
	valor_parcela_primeiro_dia_util numeric, valor_parcela_vencimento numeric,
	valor_principal numeric, valor_juros numeric, parcela_h numeric, valor_pagamento numeric,
	situacao varchar
 )
 LANGUAGE plpgsql
 STABLE
AS $function$
#variable_conflict use_column
DECLARE
	v_tipo_contrato varchar(50);
BEGIN
	SELECT c.tipo_contrato INTO v_tipo_contrato
	FROM financiamento.contratos c
	WHERE c.id = p_id_contrato;

	IF v_tipo_contrato = 'BNDES FINAME SELIC' THEN
		RETURN QUERY
		WITH dados_parcelado AS (               -- = mv_projecao_moeda.dados_parcelado
			SELECT c.id AS id_contrato,
				p.numero_seq AS parcela,
				c.carencia_pagamento,
				CASE WHEN p.numero_seq <= COALESCE(c.carencia_pagamento, 0)::numeric THEN 'CARENCIA'::text ELSE 'AMORTIZACAO'::text END AS tipo,
				c.data_referencia, c.data_bndes, c.taxa_juros_efetiva, c.valor_financiado, c.selic,
				c.prazo_carencia, c.prazo_final, c.registro_cobranca,
				CASE
					WHEN p.numero_seq <= COALESCE(c.carencia_pagamento, 0)::numeric THEN c.data_referencia + '1 mon'::interval * p.numero_seq::double precision * (c.prazo_carencia::double precision / NULLIF(c.carencia_pagamento, 0)::double precision)
					ELSE c.data_referencia + '1 mon'::interval * c.prazo_carencia::double precision + '1 mon'::interval * (p.numero_seq - COALESCE(c.carencia_pagamento, 0)::numeric)::double precision
				END::date AS data_vencimento
			FROM financiamento.contratos c
			CROSS JOIN LATERAL generate_series(1::numeric, (c.prazo_final + COALESCE(c.carencia_pagamento, 0))::numeric) p(numero_seq)
			WHERE c.id = p_id_contrato
		), dados_dias_uteis AS (                -- = mv_projecao_moeda.dados_dias_uteis
			SELECT dp.*,
				financiamento.proximo_dia_util(date_trunc('month'::text, dp.data_vencimento::timestamp with time zone)::date) AS data_primeiro_dia,
				financiamento.proximo_dia_util(dp.data_vencimento) AS data_vencimento_real,
				CASE
					WHEN dp.parcela = 1::numeric THEN financiamento.dias_uteis_entre(dp.data_bndes, financiamento.proximo_dia_util(dp.data_vencimento))
					WHEN dp.tipo = 'CARENCIA'::text THEN financiamento.dias_uteis_entre(financiamento.proximo_dia_util((dp.data_vencimento - '1 mon'::interval * (dp.prazo_carencia::double precision / NULLIF(dp.carencia_pagamento, 0)::double precision))::date), financiamento.proximo_dia_util(dp.data_vencimento))
					ELSE financiamento.dias_uteis_entre(financiamento.proximo_dia_util((dp.data_vencimento - '1 mon'::interval)::date), financiamento.proximo_dia_util(dp.data_vencimento))
				END AS dias_uteis,
				a.tipo_lancamento,
				COALESCE(a.valor_moeda, 0::numeric) AS valor_em_moeda
			FROM dados_parcelado dp
			LEFT JOIN financiamento.antecipacao a
				ON dp.id_contrato = a.id_contrato
				AND date_trunc('month'::text, a.data_compensacao::timestamp with time zone) = date_trunc('month'::text, dp.data_vencimento::timestamp with time zone)
				AND (p_data_base IS NULL OR a.data_pagamento <= p_data_base)
		), calculo_base AS (                    -- = mv_projecao_moeda.calculo_base
			SELECT d.*,
				round(power(d.taxa_juros_efetiva::numeric / 100::numeric + 1::numeric, d.dias_uteis::numeric / 252::numeric), 6) AS fator_juros,
				round(d.valor_financiado / d.selic, 2) AS saldo_inicial,
				CASE WHEN d.tipo = 'CARENCIA'::text THEN 0.00 ELSE round(d.valor_financiado / d.selic / d.prazo_final::numeric, 2) END AS principal_original,
				max(CASE WHEN d.valor_em_moeda > 0::numeric THEN d.parcela ELSE NULL::numeric END) OVER (PARTITION BY d.id_contrato) AS parcela_antecipacao,
				max(d.valor_em_moeda) OVER (PARTITION BY d.id_contrato) AS total_antecipado,
				GREATEST(0::numeric, d.parcela - COALESCE(d.carencia_pagamento, 0)::numeric - 1::numeric) AS qtd_amortizacoes_anteriores
			FROM dados_dias_uteis d
		), calculo_novo_principal AS (          -- = mv_projecao_moeda.calculo_novo_principal
			SELECT b.*,
				round(b.saldo_inicial - b.principal_original * GREATEST(0::numeric, COALESCE(b.parcela_antecipacao, 0::numeric) - COALESCE(b.carencia_pagamento, 0)::numeric - 1::numeric), 2) AS saldo_mes_antecipacao,
				b.prazo_final::numeric - GREATEST(0::numeric, COALESCE(b.parcela_antecipacao, 0::numeric) - COALESCE(b.carencia_pagamento, 0)::numeric) AS parcelas_restantes_pos_antec
			FROM calculo_base b
		), calculo_final_estruturado AS (       -- = mv_projecao_moeda.calculo_final_estruturado
			SELECT n.*,
				CASE
					WHEN n.tipo = 'CARENCIA'::text THEN 0.00
					WHEN n.parcela_antecipacao IS NOT NULL AND n.parcela > n.parcela_antecipacao THEN round((n.saldo_mes_antecipacao - n.principal_original - n.total_antecipado) / n.parcelas_restantes_pos_antec, 2)
					ELSE n.principal_original
				END AS principal_efetivo
			FROM calculo_novo_principal n
		), calculo_saldo AS (                   -- = mv_projecao_moeda.calculo_saldo
			SELECT f.*,
				CASE
					WHEN f.tipo = 'CARENCIA'::text THEN f.saldo_inicial
					WHEN f.parcela_antecipacao IS NOT NULL AND f.parcela > f.parcela_antecipacao THEN round(f.saldo_mes_antecipacao - f.principal_original - f.total_antecipado - f.principal_efetivo * (f.parcela - f.parcela_antecipacao - 1::numeric), 2)
					ELSE round(f.saldo_inicial - f.principal_original * f.qtd_amortizacoes_anteriores, 2)
				END AS saldo_devedor
			FROM calculo_final_estruturado f
		), parcela_quitada AS (                 -- = mv_projecao_moeda.parcela_quitada
			SELECT a.id_contrato,
				(SELECT min(ddu.parcela) FROM dados_dias_uteis ddu
				 WHERE ddu.id_contrato = a.id_contrato AND ddu.data_vencimento >= a.data_compensacao) AS parcela_quitacao
			FROM financiamento.antecipacao a
			WHERE a.tipo_lancamento::text = 'QUITACAO'::text
			  AND a.id_contrato = p_id_contrato
			  AND (p_data_base IS NULL OR a.data_pagamento <= p_data_base)
		), projecao_moeda AS (                  -- = SELECT final de mv_projecao_moeda (quitação vira situação, não filtro)
			SELECT cs.id_contrato, cs.parcela, cs.tipo, cs.registro_cobranca,
				cs.data_primeiro_dia AS dia_util,
				cs.data_vencimento AS data,
				cs.data_vencimento_real AS data_vcto,
				cs.dias_uteis, cs.fator_juros, cs.saldo_devedor,
				cs.valor_em_moeda AS antecipacao,
				cs.tipo_lancamento,
				cs.principal_efetivo AS principal,
				round(cs.saldo_devedor * (cs.fator_juros - 1::numeric), 2) AS juros,
				round(cs.principal_efetivo + cs.saldo_devedor * (cs.fator_juros - 1::numeric), 2) AS total_parcela,
				CASE WHEN q.parcela_quitacao IS NOT NULL AND cs.parcela >= q.parcela_quitacao
					THEN 'CANCELADA_QUITACAO' ELSE 'ABERTA' END AS situacao
			FROM calculo_saldo cs
			LEFT JOIN parcela_quitada q ON cs.id_contrato = q.id_contrato
		), reais_base AS (                      -- = mv_projecao_moeda_final.calculo_base (uma SELIC por data)
			SELECT m.*,
				sdu.valor AS selic_dia_util,
				sdv.valor AS selic_vencimento,
				CASE WHEN m.registro_cobranca::text = 'PRIMEIRO_DIA_UTIL'::text THEN round(m.total_parcela * COALESCE(sdu.valor, ultima.valor), 2) ELSE 0::numeric END AS valor_parcela_primeiro_dia_util,
				CASE WHEN m.registro_cobranca::text = 'PRIMEIRO_DIA_UTIL'::text THEN round(m.principal * COALESCE(sdu.valor, ultima.valor), 2) ELSE round(m.principal * COALESCE(sdv.valor, ultima.valor), 2) END AS valor_principal,
				CASE WHEN m.registro_cobranca::text = 'PRIMEIRO_DIA_UTIL'::text THEN round(m.juros * COALESCE(sdu.valor, ultima.valor), 2) ELSE round(m.juros * COALESCE(sdv.valor, ultima.valor), 2) END AS valor_juros,
				round(m.total_parcela * COALESCE(sdv.valor, ultima.valor), 2) AS valor_parcela_vencimento
			FROM projecao_moeda m
			LEFT JOIN LATERAL (SELECT s.valor FROM financiamento.selic s
			                   WHERE s.data = m.dia_util ORDER BY s.id DESC LIMIT 1) sdu ON true
			LEFT JOIN LATERAL (SELECT s.valor FROM financiamento.selic s
			                   WHERE s.data = m.data_vcto ORDER BY s.id DESC LIMIT 1) sdv ON true
			CROSS JOIN LATERAL (SELECT s.valor FROM financiamento.selic s
			                    WHERE s.data IS NOT NULL ORDER BY s.data DESC, s.id DESC LIMIT 1) ultima
		), reais_parcela_h AS (                 -- = mv_projecao_moeda_final.calcular_parcela_h
			SELECT r.*,
				CASE
					WHEN r.parcela = 1::numeric OR NOT r.registro_cobranca::text = 'PRIMEIRO_DIA_UTIL'::text THEN 0.00
					ELSE COALESCE(lag(r.valor_parcela_vencimento - r.valor_parcela_primeiro_dia_util, 1, 0::numeric) OVER (PARTITION BY r.id_contrato ORDER BY r.parcela), 0::numeric)
				END AS parcela_h
			FROM reais_base r
		)
		SELECT h.parcela::int4, h.tipo::varchar, h.dia_util, h.data, h.data_vcto,
			h.dias_uteis, NULL::int4, h.fator_juros, h.saldo_devedor,
			h.antecipacao, h.tipo_lancamento::varchar, h.principal, h.juros, h.total_parcela,
			h.selic_dia_util, h.selic_vencimento,
			h.valor_parcela_primeiro_dia_util, h.valor_parcela_vencimento,
			h.valor_principal, h.valor_juros, h.parcela_h,
			CASE WHEN h.registro_cobranca::text = 'PRIMEIRO_DIA_UTIL'::text THEN round(h.valor_parcela_primeiro_dia_util + h.parcela_h, 2) ELSE h.valor_parcela_vencimento END,
			h.situacao::varchar
		FROM reais_parcela_h h
		ORDER BY h.parcela;

	ELSIF v_tipo_contrato = 'BNDES FINAME TFC' THEN
		RETURN QUERY
		WITH dados_parcelado AS (               -- = mv_projecao_tfc.dados_parcelado
			SELECT c.id AS id_contrato,
				p.numero_seq AS parcela,
				c.carencia_pagamento,
				CASE WHEN p.numero_seq <= COALESCE(c.carencia_pagamento, 0)::numeric THEN 'CARENCIA'::text ELSE 'AMORTIZACAO'::text END AS tipo,
				c.data_bndes, c.taxa_juros_efetiva, c.valor_financiado, c.prazo_carencia, c.prazo_final,
				CASE
					WHEN p.numero_seq <= COALESCE(c.carencia_pagamento, 0)::numeric THEN c.data_referencia + '1 mon'::interval * p.numero_seq::double precision * (c.prazo_carencia::double precision / NULLIF(c.carencia_pagamento, 0)::double precision)
					ELSE c.data_referencia + '1 mon'::interval * c.prazo_carencia::double precision + '1 mon'::interval * (p.numero_seq - COALESCE(c.carencia_pagamento, 0)::numeric)::double precision
				END::date AS data_vencimento
			FROM financiamento.contratos c
			CROSS JOIN LATERAL generate_series(1::numeric, (c.prazo_final + COALESCE(c.carencia_pagamento, 0))::numeric) p(numero_seq)
			WHERE c.id = p_id_contrato
		), dados_dias_uteis AS (                -- = mv_projecao_tfc.dados_dias_uteis (sem o JOIN de antecipação)
			SELECT dp.*,
				financiamento.proximo_dia_util(date_trunc('month'::text, dp.data_vencimento::timestamp with time zone)::date) AS data_primeiro_dia,
				financiamento.proximo_dia_util(dp.data_vencimento) AS data_vencimento_real,
				CASE
					WHEN dp.parcela = 1::numeric THEN dp.data_vencimento - dp.data_bndes
					WHEN dp.tipo = 'CARENCIA'::text THEN financiamento.proximo_dia_util(dp.data_vencimento) - financiamento.proximo_dia_util((dp.data_vencimento - '1 mon'::interval * (dp.prazo_carencia::double precision / NULLIF(dp.carencia_pagamento, 0)::double precision))::date)
					ELSE financiamento.proximo_dia_util(dp.data_vencimento) - financiamento.proximo_dia_util((dp.data_vencimento - '1 mon'::interval)::date)
				END AS dias_corridos
			FROM dados_parcelado dp
		), calculo_base AS (                    -- = mv_projecao_tfc.calculo_base
			SELECT d.*,
				round(power(d.taxa_juros_efetiva::numeric / 100::numeric + 1::numeric, d.dias_corridos::numeric / 365::numeric), 6) AS fator_juros,
				round(d.valor_financiado, 2) AS saldo_inicial,
				CASE WHEN d.tipo = 'CARENCIA'::text THEN 0.00 ELSE round(d.valor_financiado / d.prazo_final::numeric, 2) END AS principal_original,
				GREATEST(0::numeric, d.parcela - COALESCE(d.carencia_pagamento, 0)::numeric - 1::numeric) AS qtd_amortizacoes_anteriores
			FROM dados_dias_uteis d
		), calculo_saldo AS (                   -- = mv_projecao_tfc.calculo_saldo
			SELECT b.*,
				CASE
					WHEN b.tipo = 'CARENCIA'::text THEN b.saldo_inicial
					ELSE round(b.saldo_inicial - b.principal_original * b.qtd_amortizacoes_anteriores, 2)
				END AS saldo_devedor
			FROM calculo_base b
		)
		SELECT cs.parcela::int4, cs.tipo::varchar,
			cs.data_primeiro_dia, cs.data_vencimento, cs.data_vencimento_real,
			NULL::int4, cs.dias_corridos, cs.fator_juros, cs.saldo_devedor,
			NULL::numeric, NULL::varchar,
			cs.principal_original,
			round(cs.saldo_devedor * (cs.fator_juros - 1::numeric), 2),
			round(cs.principal_original + cs.saldo_devedor * (cs.fator_juros - 1::numeric), 2),
			NULL::numeric, NULL::numeric, NULL::numeric, NULL::numeric,
			cs.principal_original,                                                       -- valor_principal (R$)
			round(cs.saldo_devedor * (cs.fator_juros - 1::numeric), 2),                  -- valor_juros (R$)
			0::numeric,                                                                  -- parcela_h (como na vw_agrupamento_projecao)
			round(cs.principal_original + cs.saldo_devedor * (cs.fator_juros - 1::numeric), 2), -- valor_pagamento (R$)
			'ABERTA'::varchar                                                            -- TFC sem quitação hoje (P4)
		FROM calculo_saldo cs
		ORDER BY cs.parcela;
	END IF;
	-- Outros tipos de contrato: nenhuma parcela (igual às MVs)
END;
$function$;

ALTER FUNCTION financiamento.calcular_projecao_contrato(int4, date) OWNER TO fin;
GRANT ALL ON FUNCTION financiamento.calcular_projecao_contrato(int4, date) TO fin;

-- #####################################################################
-- 3. Liquidação, controle do contrato e recálculo
-- #####################################################################

CREATE TABLE financiamento.liquidacao (
	id int4 GENERATED ALWAYS AS IDENTITY NOT NULL,
	id_parcela int4 NOT NULL,
	id_contrato int4 NOT NULL,                       -- preenchido pelo trigger a partir da parcela
	data_pagamento date NOT NULL,
	valor_projetado numeric(15, 2) NOT NULL,         -- cópia do valor_pagamento da parcela (preenchido pelo trigger)
	valor_pago numeric(15, 2) NOT NULL,
	valor_ajuste numeric(15, 2) GENERATED ALWAYS AS (valor_pago - valor_projetado) STORED,
	origem varchar(10) NOT NULL,                     -- ERP / MANUAL
	lote_conciliacao uuid NULL,                      -- agrupa as liquidações de uma mesma confirmação do ERP
	nome_arquivo varchar(255) NULL,
	doctos_erp text[] NULL,                          -- Doctos do ERP somados nesta parcela
	qtd_linhas_erp int4 NULL,
	usuario varchar(100) NULL,
	data_registro timestamp DEFAULT now() NOT NULL,
	estornado bool DEFAULT false NOT NULL,
	data_estorno timestamp NULL,
	usuario_estorno varchar(100) NULL,
	motivo_estorno varchar(500) NULL,
	CONSTRAINT liquidacao_pkey PRIMARY KEY (id),
	CONSTRAINT liquidacao_id_parcela_fkey FOREIGN KEY (id_parcela)
		REFERENCES financiamento.projecao_parcelas(id),           -- RESTRICT: parcela com liquidação não some
	CONSTRAINT liquidacao_id_contrato_fkey FOREIGN KEY (id_contrato)
		REFERENCES financiamento.contratos(id),                   -- RESTRICT: bloqueia a exclusão do contrato (D11)
	CONSTRAINT liquidacao_origem_ck CHECK (origem IN ('ERP', 'MANUAL')),
	CONSTRAINT liquidacao_origem_lote_ck CHECK ((origem = 'ERP') = (lote_conciliacao IS NOT NULL)),
	CONSTRAINT liquidacao_estorno_ck CHECK (
		(estornado AND data_estorno IS NOT NULL AND motivo_estorno IS NOT NULL)
		OR (NOT estornado AND data_estorno IS NULL AND usuario_estorno IS NULL AND motivo_estorno IS NULL))
);

-- uma liquidação ativa por parcela
CREATE UNIQUE INDEX liquidacao_parcela_ativa_uidx ON financiamento.liquidacao (id_parcela) WHERE NOT estornado;
CREATE INDEX liquidacao_contrato_idx ON financiamento.liquidacao (id_contrato);
CREATE INDEX liquidacao_lote_idx ON financiamento.liquidacao (lote_conciliacao);

COMMENT ON TABLE financiamento.liquidacao IS 'Liquidação (baixa) de parcelas projetadas, manual ou por conciliação com o ERP. Somente inclusão e estorno; exclusão bloqueada.';

ALTER TABLE financiamento.liquidacao OWNER TO fin;
GRANT ALL ON TABLE financiamento.liquidacao TO fin;

-- =====================================================================
-- Controle do contrato: contagens, status (ATIVO / QUITADO / ENCERRADO) e saldo
-- =====================================================================
CREATE OR REPLACE FUNCTION financiamento.atualizar_controle_contrato(p_id_contrato int4)
 RETURNS void LANGUAGE plpgsql AS $function$
BEGIN
	UPDATE financiamento.projecao_controle pc SET
		qtd_parcelas   = s.qtd_parcelas,
		qtd_liquidadas = s.qtd_liquidadas,
		status_contrato = CASE
			WHEN EXISTS (SELECT 1 FROM financiamento.antecipacao a
			             WHERE a.id_contrato = p_id_contrato AND a.tipo_lancamento = 'QUITACAO') THEN 'QUITADO'
			WHEN s.qtd_parcelas > 0 AND s.qtd_liquidadas = s.qtd_parcelas THEN 'ENCERRADO'
			ELSE 'ATIVO' END,
		saldo_devedor_atual = (SELECT p.saldo_devedor FROM financiamento.projecao_parcelas p
		                       WHERE p.id_contrato = p_id_contrato AND p.situacao = 'ABERTA' AND p.data_vcto >= current_date
		                       ORDER BY p.parcela LIMIT 1)
	FROM (SELECT count(*) FILTER (WHERE p.situacao <> 'CANCELADA_QUITACAO') AS qtd_parcelas,
	             count(*) FILTER (WHERE p.situacao = 'LIQUIDADA')            AS qtd_liquidadas
	      FROM financiamento.projecao_parcelas p WHERE p.id_contrato = p_id_contrato) s
	WHERE pc.id_contrato = p_id_contrato;
END;
$function$;

-- =====================================================================
-- Regras da liquidação
-- =====================================================================
CREATE OR REPLACE FUNCTION financiamento.liquidacao_antes_incluir()
 RETURNS trigger LANGUAGE plpgsql AS $function$
DECLARE
	v_parcela record;
BEGIN
	SELECT p.id_contrato, p.parcela, p.situacao, p.valor_pagamento INTO v_parcela
	FROM financiamento.projecao_parcelas p
	WHERE p.id = NEW.id_parcela
	FOR UPDATE;

	IF NOT FOUND THEN
		RAISE EXCEPTION 'Parcela % não encontrada.', NEW.id_parcela;
	END IF;
	IF v_parcela.situacao <> 'ABERTA' THEN
		RAISE EXCEPTION 'Parcela % do contrato % não está aberta (situação: %).',
			v_parcela.parcela, v_parcela.id_contrato, v_parcela.situacao;
	END IF;

	NEW.id_contrato := v_parcela.id_contrato;
	NEW.valor_projetado := v_parcela.valor_pagamento;
	RETURN NEW;
END;
$function$;

CREATE OR REPLACE FUNCTION financiamento.liquidacao_antes_alterar()
 RETURNS trigger LANGUAGE plpgsql AS $function$
BEGIN
	IF OLD.estornado THEN
		RAISE EXCEPTION 'Liquidação % já está estornada e não pode ser alterada.', OLD.id;
	END IF;
	IF NOT NEW.estornado
	   OR (NEW.id_parcela, NEW.id_contrato, NEW.data_pagamento, NEW.valor_projetado, NEW.valor_pago, NEW.origem,
	       NEW.lote_conciliacao, NEW.nome_arquivo, NEW.doctos_erp, NEW.qtd_linhas_erp, NEW.usuario, NEW.data_registro)
	      IS DISTINCT FROM
	      (OLD.id_parcela, OLD.id_contrato, OLD.data_pagamento, OLD.valor_projetado, OLD.valor_pago, OLD.origem,
	       OLD.lote_conciliacao, OLD.nome_arquivo, OLD.doctos_erp, OLD.qtd_linhas_erp, OLD.usuario, OLD.data_registro) THEN
		RAISE EXCEPTION 'Liquidação % só pode ser estornada; demais alterações não são permitidas.', OLD.id;
	END IF;

	NEW.data_estorno := COALESCE(NEW.data_estorno, now());
	RETURN NEW;
END;
$function$;

CREATE OR REPLACE FUNCTION financiamento.liquidacao_antes_excluir()
 RETURNS trigger LANGUAGE plpgsql AS $function$
BEGIN
	RAISE EXCEPTION 'Liquidação não pode ser excluída; use o estorno.';
END;
$function$;

CREATE OR REPLACE FUNCTION financiamento.liquidacao_depois()
 RETURNS trigger LANGUAGE plpgsql AS $function$
BEGIN
	IF TG_OP = 'INSERT' THEN
		UPDATE financiamento.projecao_parcelas
		SET situacao = 'LIQUIDADA', atualizado_em = now()
		WHERE id = NEW.id_parcela;
		PERFORM financiamento.atualizar_controle_contrato(NEW.id_contrato);
	ELSE  -- UPDATE (estorno)
		UPDATE financiamento.projecao_parcelas
		SET situacao = 'ABERTA', atualizado_em = now()
		WHERE id = NEW.id_parcela;
		PERFORM financiamento.recalcular_projecao_contrato(NEW.id_contrato, 'ESTORNO_LIQUIDACAO');
	END IF;
	RETURN NULL;
END;
$function$;

CREATE TRIGGER trg_liquidacao_antes_incluir BEFORE INSERT ON financiamento.liquidacao
	FOR EACH ROW EXECUTE FUNCTION financiamento.liquidacao_antes_incluir();
CREATE TRIGGER trg_liquidacao_antes_alterar BEFORE UPDATE ON financiamento.liquidacao
	FOR EACH ROW EXECUTE FUNCTION financiamento.liquidacao_antes_alterar();
CREATE TRIGGER trg_liquidacao_antes_excluir BEFORE DELETE ON financiamento.liquidacao
	FOR EACH ROW EXECUTE FUNCTION financiamento.liquidacao_antes_excluir();
CREATE TRIGGER trg_liquidacao_depois AFTER INSERT OR UPDATE OF estornado ON financiamento.liquidacao
	FOR EACH ROW EXECUTE FUNCTION financiamento.liquidacao_depois();

-- Bloqueio de TRUNCATE (o trigger de DELETE não alcança o TRUNCATE)
CREATE OR REPLACE FUNCTION financiamento.liquidacao_sem_truncate()
 RETURNS trigger LANGUAGE plpgsql AS $function$
BEGIN
	RAISE EXCEPTION 'Liquidação não pode ser apagada; use o estorno.';
END;
$function$;

CREATE TRIGGER trg_liquidacao_sem_truncate BEFORE TRUNCATE ON financiamento.liquidacao
	FOR EACH STATEMENT EXECUTE FUNCTION financiamento.liquidacao_sem_truncate();

-- =====================================================================
-- recalcular_projecao_contrato:
--   - controle do contrato centralizado em atualizar_controle_contrato (inclui status ENCERRADO);
--   - remove a tabela temporária só se existir (sem o aviso 'esquema "pg_temp" não existe').
-- =====================================================================
CREATE OR REPLACE FUNCTION financiamento.recalcular_projecao_contrato(p_id_contrato int4, p_motivo varchar)
 RETURNS int4
 LANGUAGE plpgsql
AS $function$
DECLARE
	v_qtd int4;
BEGIN
	-- Contrato excluído: o ON DELETE CASCADE já removeu a projeção
	IF NOT EXISTS (SELECT 1 FROM financiamento.contratos WHERE id = p_id_contrato) THEN
		RETURN 0;
	END IF;

	-- Trava o contrato (evita dois recálculos simultâneos)
	INSERT INTO financiamento.projecao_controle (id_contrato) VALUES (p_id_contrato)
	ON CONFLICT (id_contrato) DO NOTHING;
	PERFORM 1 FROM financiamento.projecao_controle WHERE id_contrato = p_id_contrato FOR UPDATE;

	-- Calcula uma única vez
	IF to_regclass('pg_temp.tmp_recalculo_projecao') IS NOT NULL THEN
		DROP TABLE pg_temp.tmp_recalculo_projecao;
	END IF;
	CREATE TEMP TABLE tmp_recalculo_projecao ON COMMIT DROP AS
	SELECT * FROM financiamento.calcular_projecao_contrato(p_id_contrato);

	-- Parcela liquidada não pode ser cancelada nem deixar de existir
	IF EXISTS (
		SELECT 1
		FROM financiamento.projecao_parcelas p
		LEFT JOIN tmp_recalculo_projecao t ON t.parcela = p.parcela
		WHERE p.id_contrato = p_id_contrato
		  AND p.situacao = 'LIQUIDADA'
		  AND (t.parcela IS NULL OR t.situacao = 'CANCELADA_QUITACAO')
	) THEN
		RAISE EXCEPTION 'Contrato %: o recálculo cancelaria parcela já liquidada.', p_id_contrato;
	END IF;

	-- Grava (upsert); parcelas LIQUIDADAS ficam intactas
	INSERT INTO financiamento.projecao_parcelas (
		id_contrato, parcela, tipo, dia_util, "data", data_vcto, dias_uteis, dias_corridos,
		fator_juros, saldo_devedor, antecipacao, tipo_lancamento, principal, juros, total_parcela,
		selic_dia_util, selic_vencimento, valor_parcela_primeiro_dia_util, valor_parcela_vencimento,
		valor_principal, valor_juros, parcela_h, valor_pagamento, situacao, atualizado_em
	)
	SELECT p_id_contrato, t.parcela, t.tipo, t.dia_util, t.data, t.data_vcto, t.dias_uteis, t.dias_corridos,
		t.fator_juros, t.saldo_devedor, t.antecipacao, t.tipo_lancamento, t.principal, t.juros, t.total_parcela,
		t.selic_dia_util, t.selic_vencimento, t.valor_parcela_primeiro_dia_util, t.valor_parcela_vencimento,
		t.valor_principal, t.valor_juros, t.parcela_h, t.valor_pagamento, t.situacao, now()
	FROM tmp_recalculo_projecao t
	ON CONFLICT (id_contrato, parcela) DO UPDATE SET
		tipo = EXCLUDED.tipo, dia_util = EXCLUDED.dia_util, "data" = EXCLUDED."data", data_vcto = EXCLUDED.data_vcto,
		dias_uteis = EXCLUDED.dias_uteis, dias_corridos = EXCLUDED.dias_corridos, fator_juros = EXCLUDED.fator_juros,
		saldo_devedor = EXCLUDED.saldo_devedor, antecipacao = EXCLUDED.antecipacao, tipo_lancamento = EXCLUDED.tipo_lancamento,
		principal = EXCLUDED.principal, juros = EXCLUDED.juros, total_parcela = EXCLUDED.total_parcela,
		selic_dia_util = EXCLUDED.selic_dia_util, selic_vencimento = EXCLUDED.selic_vencimento,
		valor_parcela_primeiro_dia_util = EXCLUDED.valor_parcela_primeiro_dia_util,
		valor_parcela_vencimento = EXCLUDED.valor_parcela_vencimento,
		valor_principal = EXCLUDED.valor_principal, valor_juros = EXCLUDED.valor_juros,
		parcela_h = EXCLUDED.parcela_h, valor_pagamento = EXCLUDED.valor_pagamento,
		situacao = EXCLUDED.situacao, atualizado_em = now()
	WHERE financiamento.projecao_parcelas.situacao <> 'LIQUIDADA';

	-- Remove parcelas que deixaram de existir (ex.: prazo alterado), exceto liquidadas
	DELETE FROM financiamento.projecao_parcelas p
	WHERE p.id_contrato = p_id_contrato
	  AND p.situacao <> 'LIQUIDADA'
	  AND NOT EXISTS (SELECT 1 FROM tmp_recalculo_projecao t WHERE t.parcela = p.parcela);

	-- Atualiza o controle (contagens e status em atualizar_controle_contrato)
	UPDATE financiamento.projecao_controle SET
		status_projecao = 'PROJETADO',
		motivo_ultimo_calculo = p_motivo,
		data_ultimo_calculo = now(),
		mensagem_erro = NULL
	WHERE id_contrato = p_id_contrato;

	PERFORM financiamento.atualizar_controle_contrato(p_id_contrato);

	SELECT qtd_parcelas INTO v_qtd FROM financiamento.projecao_controle WHERE id_contrato = p_id_contrato;

	RETURN v_qtd;
END;
$function$;

-- Permissões (somente das funções novas/atualizadas)
ALTER FUNCTION financiamento.atualizar_controle_contrato(int4) OWNER TO fin;
GRANT ALL ON FUNCTION financiamento.atualizar_controle_contrato(int4) TO fin;
ALTER FUNCTION financiamento.liquidacao_antes_incluir() OWNER TO fin;
GRANT ALL ON FUNCTION financiamento.liquidacao_antes_incluir() TO fin;
ALTER FUNCTION financiamento.liquidacao_antes_alterar() OWNER TO fin;
GRANT ALL ON FUNCTION financiamento.liquidacao_antes_alterar() TO fin;
ALTER FUNCTION financiamento.liquidacao_antes_excluir() OWNER TO fin;
GRANT ALL ON FUNCTION financiamento.liquidacao_antes_excluir() TO fin;
ALTER FUNCTION financiamento.liquidacao_depois() OWNER TO fin;
GRANT ALL ON FUNCTION financiamento.liquidacao_depois() TO fin;
ALTER FUNCTION financiamento.liquidacao_sem_truncate() OWNER TO fin;
GRANT ALL ON FUNCTION financiamento.liquidacao_sem_truncate() TO fin;
ALTER FUNCTION financiamento.recalcular_projecao_contrato(int4, varchar) OWNER TO fin;
GRANT ALL ON FUNCTION financiamento.recalcular_projecao_contrato(int4, varchar) TO fin;

-- #####################################################################
-- 4. Recálculo automático (triggers em contratos, antecipacao e selic)
-- #####################################################################

CREATE OR REPLACE FUNCTION financiamento.recalcular_projecao_selic(p_data_min date)
 RETURNS int4
 LANGUAGE plpgsql
AS $function$
DECLARE
	r record;
	v_qtd int4 := 0;
BEGIN
	FOR r IN
		SELECT DISTINCT p.id_contrato
		FROM financiamento.projecao_parcelas p
		JOIN financiamento.contratos c ON c.id = p.id_contrato
		WHERE c.tipo_contrato = 'BNDES FINAME SELIC'
		  AND p.situacao = 'ABERTA'
		  AND (p.dia_util >= p_data_min
		       OR p.data_vcto >= p_data_min
		       OR p.selic_dia_util IS NULL      -- usou a "última SELIC"
		       OR p.selic_vencimento IS NULL)
		ORDER BY p.id_contrato
	LOOP
		PERFORM financiamento.recalcular_projecao_contrato(r.id_contrato, 'SELIC');
		v_qtd := v_qtd + 1;
	END LOOP;

	RETURN v_qtd;
END;
$function$;

-- =====================================================================
-- contratos: inclusão/alteração recalcula o contrato (exclusão: ON DELETE CASCADE)
-- =====================================================================
CREATE OR REPLACE FUNCTION financiamento.projecao_trigger_contratos()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
	PERFORM financiamento.recalcular_projecao_contrato(
		NEW.id, CASE TG_OP WHEN 'INSERT' THEN 'INCLUSAO' ELSE 'ATUALIZACAO' END);
	RETURN NULL;
END;
$function$;

CREATE TRIGGER trg_projecao_contratos
	AFTER INSERT OR UPDATE ON financiamento.contratos
	FOR EACH ROW EXECUTE FUNCTION financiamento.projecao_trigger_contratos();

-- =====================================================================
-- antecipacao: inclusão/alteração/exclusão recalcula o(s) contrato(s) envolvido(s)
-- =====================================================================
CREATE OR REPLACE FUNCTION financiamento.projecao_trigger_antecipacao()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
	IF TG_OP IN ('INSERT', 'UPDATE') THEN
		PERFORM financiamento.recalcular_projecao_contrato(
			NEW.id_contrato, CASE TG_OP WHEN 'INSERT' THEN 'ANTECIPACAO_INCLUSAO' ELSE 'ANTECIPACAO_ALTERACAO' END);
	END IF;

	-- exclusão, ou alteração que mudou o contrato: recalcula também o contrato antigo
	IF TG_OP = 'DELETE' OR (TG_OP = 'UPDATE' AND OLD.id_contrato <> NEW.id_contrato) THEN
		PERFORM financiamento.recalcular_projecao_contrato(OLD.id_contrato, 'ANTECIPACAO_EXCLUSAO');
	END IF;

	RETURN NULL;
END;
$function$;

CREATE TRIGGER trg_projecao_antecipacao
	AFTER INSERT OR UPDATE OR DELETE ON financiamento.antecipacao
	FOR EACH ROW EXECUTE FUNCTION financiamento.projecao_trigger_antecipacao();

-- =====================================================================
-- selic: um recálculo por comando (carga em lote recalcula uma vez, a partir da menor data)
-- =====================================================================
CREATE OR REPLACE FUNCTION financiamento.projecao_trigger_selic()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE
	v_data_min date;
BEGIN
	IF TG_OP = 'INSERT' THEN
		SELECT min(n.data) INTO v_data_min FROM selic_novas n;
	ELSIF TG_OP = 'UPDATE' THEN
		SELECT min(d.data) INTO v_data_min
		FROM (SELECT n.data FROM selic_novas n UNION ALL SELECT a.data FROM selic_antigas a) d;
	ELSE
		SELECT min(a.data) INTO v_data_min FROM selic_antigas a;
	END IF;

	IF v_data_min IS NOT NULL THEN
		PERFORM financiamento.recalcular_projecao_selic(v_data_min);
	END IF;

	RETURN NULL;
END;
$function$;

-- O PostgreSQL não permite tabela de transição em trigger com mais de um evento: um trigger por evento
CREATE TRIGGER trg_projecao_selic_insert
	AFTER INSERT ON financiamento.selic
	REFERENCING NEW TABLE AS selic_novas
	FOR EACH STATEMENT EXECUTE FUNCTION financiamento.projecao_trigger_selic();

CREATE TRIGGER trg_projecao_selic_update
	AFTER UPDATE ON financiamento.selic
	REFERENCING OLD TABLE AS selic_antigas NEW TABLE AS selic_novas
	FOR EACH STATEMENT EXECUTE FUNCTION financiamento.projecao_trigger_selic();

CREATE TRIGGER trg_projecao_selic_delete
	AFTER DELETE ON financiamento.selic
	REFERENCING OLD TABLE AS selic_antigas
	FOR EACH STATEMENT EXECUTE FUNCTION financiamento.projecao_trigger_selic();

-- Permissões (somente das funções novas)
ALTER FUNCTION financiamento.recalcular_projecao_selic(date) OWNER TO fin;
GRANT ALL ON FUNCTION financiamento.recalcular_projecao_selic(date) TO fin;
ALTER FUNCTION financiamento.projecao_trigger_contratos() OWNER TO fin;
GRANT ALL ON FUNCTION financiamento.projecao_trigger_contratos() TO fin;
ALTER FUNCTION financiamento.projecao_trigger_antecipacao() OWNER TO fin;
GRANT ALL ON FUNCTION financiamento.projecao_trigger_antecipacao() TO fin;
ALTER FUNCTION financiamento.projecao_trigger_selic() OWNER TO fin;
GRANT ALL ON FUNCTION financiamento.projecao_trigger_selic() TO fin;

-- #####################################################################
-- 5. Vínculo código do ERP -> contrato(s) do Nexus
-- #####################################################################

CREATE TABLE financiamento.contrato_erp_vinculo (
	id int4 GENERATED ALWAYS AS IDENTITY NOT NULL,
	codigo_erp varchar(100) NOT NULL,                -- trecho do Docto antes do 1º '-' (ex.: 401758033)
	id_contrato int4 NOT NULL,
	usuario varchar(100) NULL,
	data_registro timestamp DEFAULT now() NOT NULL,
	CONSTRAINT contrato_erp_vinculo_pkey PRIMARY KEY (id),
	CONSTRAINT contrato_erp_vinculo_codigo_contrato_key UNIQUE (codigo_erp, id_contrato),   -- um código pode ter vários contratos (grupo)
	CONSTRAINT contrato_erp_vinculo_id_contrato_fkey FOREIGN KEY (id_contrato)
		REFERENCES financiamento.contratos(id) ON DELETE CASCADE
);

CREATE INDEX contrato_erp_vinculo_contrato_idx ON financiamento.contrato_erp_vinculo (id_contrato);

COMMENT ON TABLE financiamento.contrato_erp_vinculo IS 'De-para permanente: código do contrato no ERP (Docto antes do 1º "-") -> contrato(s) do Nexus. Um código com vários contratos forma um grupo (mesmo contrato dividido no Nexus), conciliado e liquidado em conjunto.';

ALTER TABLE financiamento.contrato_erp_vinculo OWNER TO fin;
GRANT ALL ON TABLE financiamento.contrato_erp_vinculo TO fin;

-- #####################################################################
-- 6. Carga inicial (executar uma única vez)
-- #####################################################################

DO $$
DECLARE
	r record;
	v_ok int4 := 0;
	v_erro int4 := 0;
BEGIN
	FOR r IN SELECT id FROM financiamento.contratos ORDER BY id LOOP
		BEGIN
			PERFORM financiamento.recalcular_projecao_contrato(r.id, 'CARGA_INICIAL');
			v_ok := v_ok + 1;
		EXCEPTION WHEN OTHERS THEN
			-- só este contrato é desfeito; registra o erro e segue para o próximo
			v_erro := v_erro + 1;
			INSERT INTO financiamento.projecao_controle
				(id_contrato, status_projecao, motivo_ultimo_calculo, data_ultimo_calculo, mensagem_erro)
			VALUES (r.id, 'ERRO', 'CARGA_INICIAL', now(), SQLERRM)
			ON CONFLICT (id_contrato) DO UPDATE SET
				status_projecao = 'ERRO',
				motivo_ultimo_calculo = 'CARGA_INICIAL',
				data_ultimo_calculo = now(),
				mensagem_erro = EXCLUDED.mensagem_erro;
		END;
	END LOOP;

	RAISE NOTICE 'Carga inicial concluída: % contratos projetados, % com erro.', v_ok, v_erro;
END $$;
