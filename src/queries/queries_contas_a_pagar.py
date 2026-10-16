# Posição na data base (usada por Contas a Pagar e Endividamento): parcela paga até a data base ->
# Liquidado (valor pago, já com o ajuste); demais parcelas -> Projetado; antecipações e quitações
# aparecem sempre (valor pago). Valor considerado segue a situação.
# O valor em R$ das parcelas projetadas é refeito com a Selic CONHECIDA ATÉ A DATA BASE: a Selic da
# própria data (1º dia útil / vencimento) se ela for até a data base, senão a última Selic até a data
# base (mesma fórmula da projeção, inclusive parcela H). Contratos TFC não usam Selic.
# Antecipações/quitações pagas depois da data base não entram, e os contratos que as têm são refeitos
# como estavam na data base (calcular_projecao_contrato com a data base).
CTE_POSICAO_DATA_BASE = '''
	WITH selic_ate_base AS (
		SELECT DISTINCT ON (s.data) s.data, s.valor
		FROM financiamento.selic s
		WHERE s.data IS NOT NULL AND s.data <= :data_base
		ORDER BY s.data, s.id DESC
	),
	ultima_selic_base AS (
		SELECT sb.valor FROM selic_ate_base sb ORDER BY sb.data DESC LIMIT 1
	),
	contratos_refazer AS (
		-- contratos com antecipação/quitação paga DEPOIS da data base: a projeção daquela data era outra
		SELECT DISTINCT a.id_contrato
		FROM financiamento.antecipacao a
		WHERE a.data_pagamento > :data_base
	),
	projecao_origem AS (
		-- demais contratos: projeção gravada
		SELECT p.id, p.id_contrato, p.parcela, p.tipo, p.dia_util, p.data, p.data_vcto, p.principal, p.juros,
			p.total_parcela, p.valor_principal, p.valor_juros, p.parcela_h, p.valor_pagamento, p.situacao
		FROM financiamento.projecao_parcelas p
		WHERE p.id_contrato NOT IN (SELECT id_contrato FROM contratos_refazer)
		UNION ALL
		-- contratos refeitos como estavam na data base (só antecipações/quitações pagas até ela)
		SELECT pp.id, r.id_contrato, f.parcela, f.tipo, f.dia_util, f.data, f.data_vcto, f.principal, f.juros,
			f.total_parcela, f.valor_principal, f.valor_juros, f.parcela_h, f.valor_pagamento, f.situacao
		FROM contratos_refazer r
		CROSS JOIN LATERAL financiamento.calcular_projecao_contrato(r.id_contrato, CAST(:data_base AS date)) f
		LEFT JOIN financiamento.projecao_parcelas pp ON pp.id_contrato = r.id_contrato AND pp.parcela = f.parcela
	),
	reais_base AS (
		SELECT
			p.*,
			c.tipo_contrato = 'BNDES FINAME SELIC' AS contrato_selic,
			c.registro_cobranca,
			COALESCE(sdu.valor, u.valor) AS selic_dia_util_base,
			COALESCE(sdv.valor, u.valor) AS selic_vencimento_base
		FROM projecao_origem p
		INNER JOIN financiamento.contratos c ON c.id = p.id_contrato
		LEFT JOIN selic_ate_base sdu ON sdu.data = p.dia_util
		LEFT JOIN selic_ate_base sdv ON sdv.data = p.data_vcto
		LEFT JOIN ultima_selic_base u ON true
	),
	reais_calculo AS (
		SELECT
			r.*,
			round(r.total_parcela * r.selic_vencimento_base, 2) AS parcela_vencimento_base,
			CASE WHEN r.registro_cobranca::text = 'PRIMEIRO_DIA_UTIL'::text
				THEN round(r.total_parcela * r.selic_dia_util_base, 2) ELSE 0::numeric END AS parcela_primeiro_dia_base,
			CASE WHEN r.registro_cobranca::text = 'PRIMEIRO_DIA_UTIL'::text
				THEN round(r.principal * r.selic_dia_util_base, 2) ELSE round(r.principal * r.selic_vencimento_base, 2) END AS principal_base,
			CASE WHEN r.registro_cobranca::text = 'PRIMEIRO_DIA_UTIL'::text
				THEN round(r.juros * r.selic_dia_util_base, 2) ELSE round(r.juros * r.selic_vencimento_base, 2) END AS juros_base
		FROM reais_base r
	),
	reais_parcela_h AS (
		SELECT
			rc.*,
			CASE
				WHEN rc.parcela = 1 OR NOT rc.registro_cobranca::text = 'PRIMEIRO_DIA_UTIL'::text THEN 0.00
				ELSE COALESCE(lag(rc.parcela_vencimento_base - rc.parcela_primeiro_dia_base, 1, 0::numeric)
					OVER (PARTITION BY rc.id_contrato ORDER BY rc.parcela), 0::numeric)
			END AS parcela_h_base
		FROM reais_calculo rc
	),
	projecao_base AS (
		SELECT
			h.id,
			h.id_contrato,
			h.parcela,
			h.tipo,
			h.data,
			h.data_vcto,
			h.situacao,
			CASE WHEN h.contrato_selic THEN h.principal_base ELSE h.valor_principal END AS valor_principal,
			CASE WHEN h.contrato_selic THEN h.juros_base ELSE h.valor_juros END AS valor_juros,
			CASE WHEN h.contrato_selic THEN h.parcela_h_base ELSE h.parcela_h END AS parcela_h,
			CASE
				WHEN NOT h.contrato_selic THEN h.valor_pagamento
				WHEN h.registro_cobranca::text = 'PRIMEIRO_DIA_UTIL'::text THEN round(h.parcela_primeiro_dia_base + h.parcela_h_base, 2)
				ELSE h.parcela_vencimento_base
			END AS valor_pagamento,
			h.valor_principal AS valor_principal_gravado,
			h.valor_juros AS valor_juros_gravado,
			h.parcela_h AS parcela_h_gravada,
			h.valor_pagamento AS valor_pagamento_gravado
		FROM reais_parcela_h h
	),
	parcelas AS (
		SELECT
			p.id_contrato,
			p.parcela,
			CASE p.tipo WHEN 'CARENCIA' THEN 'Carência' ELSE 'Amortização' END AS tipo,
			CASE WHEN l.id IS NOT NULL THEN 'Liquidado' ELSE 'Projetado' END AS situacao,
			p.data AS vencimento,
			p.data_vcto AS vencimento_util,
			-- liquidada: valores da projeção no momento da baixa; projetada: valores na Selic da data base
			CASE WHEN l.id IS NOT NULL THEN p.valor_principal_gravado ELSE p.valor_principal END AS valor_principal,
			CASE WHEN l.id IS NOT NULL THEN p.valor_juros_gravado ELSE p.valor_juros END AS valor_juros,
			CASE WHEN l.id IS NOT NULL THEN p.parcela_h_gravada ELSE p.parcela_h END AS parcela_h,
			CASE WHEN l.id IS NOT NULL THEN l.valor_projetado ELSE p.valor_pagamento END AS valor_projetado,
			l.data_pagamento,
			l.valor_pago,
			l.valor_ajuste,
			CASE l.origem WHEN 'ERP' THEN 'ERP' WHEN 'MANUAL' THEN 'Manual' END AS origem,
			array_to_string(l.doctos_erp, ', ') AS doctos_erp
		FROM projecao_base p
		LEFT JOIN financiamento.liquidacao l
			ON l.id_parcela = p.id
			AND NOT l.estornado
			AND l.data_pagamento <= :data_base
		WHERE p.situacao <> 'CANCELADA_QUITACAO'
	),
	antecipacoes AS (
		SELECT
			a.id_contrato,
			0 AS parcela,
			CASE a.tipo_lancamento WHEN 'QUITACAO' THEN 'Quitação' ELSE 'Antecipação' END AS tipo,
			CASE a.tipo_lancamento WHEN 'QUITACAO' THEN 'Quitação' ELSE 'Antecipação' END AS situacao,
			a.data_pagamento AS vencimento,
			a.data_pagamento AS vencimento_util,
			NULL::numeric AS valor_principal,
			NULL::numeric AS valor_juros,
			NULL::numeric AS parcela_h,
			a.valor_pago AS valor_projetado,
			a.data_pagamento,
			a.valor_pago,
			0::numeric AS valor_ajuste,
			NULL AS origem,
			NULL AS doctos_erp
		FROM financiamento.antecipacao a
		WHERE a.data_pagamento <= :data_base          -- só o que já tinha sido pago na data base
	),
	consolidado AS (
		SELECT * FROM parcelas
		UNION ALL
		SELECT * FROM antecipacoes
	),
	posicao AS (
		SELECT
		e.razao_social AS nome_empresa,
		b.razao_social AS banco,
		c.numero_contrato,
		CASE c.tipo_contrato WHEN 'BNDES FINAME SELIC' THEN 'SELIC' WHEN 'BNDES FINAME TFC' THEN 'TFC' ELSE c.tipo_contrato END AS tipo_contrato,
		x.parcela,
		x.tipo,
		x.situacao,
		x.vencimento,
		x.vencimento_util,
		x.valor_principal,
		x.valor_juros,
		x.parcela_h,
		x.valor_projetado,
		x.data_pagamento,
		x.valor_pago,
		x.valor_ajuste,
		CASE WHEN x.situacao = 'Projetado' THEN x.valor_projetado ELSE x.valor_pago END AS valor_considerado,
		x.origem,
		x.doctos_erp
	FROM consolidado x
	INNER JOIN financiamento.contratos c ON c.id = x.id_contrato
	INNER JOIN financiamento.empresas e ON e.id = c.id_empresa
	INNER JOIN financiamento.bancos b ON b.id = c.id_banco
	)
'''

SELECT_CONTAS_A_PAGAR = CTE_POSICAO_DATA_BASE + '''
	SELECT *
	FROM posicao
	WHERE (:empresa IS NULL OR nome_empresa = :empresa)
	AND (:banco IS NULL OR banco = :banco)
	AND (:contrato IS NULL OR numero_contrato ILIKE :contrato)
	AND (:data_vcto_ini IS NULL OR vencimento_util >= :data_vcto_ini)
	AND (:data_vcto_fim IS NULL OR vencimento_util <= :data_vcto_fim)
	AND (:situacao IS NULL OR situacao = :situacao)
	ORDER BY vencimento_util, numero_contrato, parcela
'''
