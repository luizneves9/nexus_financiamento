from queries.queries_contas_a_pagar import CTE_POSICAO_DATA_BASE

# Endividamento na posição da data base, por ano/mês e modalidade, em milhões:
# - Financiamentos: mesma regra do Contas a Pagar (CTE_POSICAO_DATA_BASE): pago até a data base
#   e projetado depois; o mês é marcado como pago só por parcelas liquidadas (antecipações e quitações não marcam);
#   só entram contratos contabilizados até a data base (data_contabilizacao; o Painel usa a mesma regra e o
#   Contas a Pagar não filtra);
# - Compra Santo Anjo / Tributário (outros_pagamentos): no mês do vencimento; baixada até a data base entra pelo
#   valor pago, as demais (inclusive vencidas sem baixa) como a pagar pelo valor lançado;
# - Consórcios: pago = consorcio_pago com data de pagamento até a data base (mês do pagamento, coluna Total);
#   a pagar = parcelas da última competência até o mês da data base, por banco + consorciado, com
#   vencimento depois da data base ou num mês até a data base ainda sem pagamento importado
#   (o banco + consorciado não tem consorcio_pago naquele mês);
# filtro opcional de data de corte (a partir do mês). `ordem` define a sequência das modalidades no relatório.
# Trecho comum (termina no CTE movimentos) do relatório e do resumo do mês: `quitacao` marca antecipações/quitações
# e `data_contabilizacao` vem só nos financiamentos (contrato novo no resumo).
CTE_MOVIMENTOS_ENDIVIDAMENTO = CTE_POSICAO_DATA_BASE + ''',
	competencia_consorcio AS (
		-- última importação do a pagar até o mês da data base, por banco + consorciado
		SELECT banco, nome_consorciado, max(competencia) AS competencia
		FROM financiamento.consorcio_a_pagar
		WHERE competencia <= date_trunc('month', CAST(:data_base AS date))::date
		GROUP BY banco, nome_consorciado
	),
	meses_pagos_consorcio AS (
		-- meses com pagamento importado até a data base, por banco + consorciado
		SELECT DISTINCT banco, nome_consorciado, date_trunc('month', data_pagamento)::date AS mes
		FROM financiamento.consorcio_pago
		WHERE data_pagamento <= :data_base
	),
	movimentos AS (
		SELECT 1 AS ordem, 'Financiamentos' AS categoria, p.vencimento_util AS data_referencia,
			p.valor_considerado AS valor, p.situacao <> 'Projetado' AS pago, p.situacao = 'Liquidado' AS liquidado,
			p.situacao IN ('Quitação', 'Antecipação') AS quitacao, c.data_contabilizacao
		FROM posicao p
		INNER JOIN financiamento.contratos c ON c.numero_contrato = p.numero_contrato
		WHERE c.data_contabilizacao <= :data_base   -- contrato já contabilizado na data base
		UNION ALL
		SELECT
			CASE o.modalidade WHEN 'COMPRA_SANTO_ANJO' THEN 2 ELSE 4 END,
			CASE o.modalidade WHEN 'COMPRA_SANTO_ANJO' THEN 'Compra Santo Anjo' ELSE 'Tributário' END,
			o.data_vencimento,
			CASE WHEN o.data_pagamento <= :data_base THEN o.valor_pago ELSE o.valor END,
			COALESCE(o.data_pagamento <= :data_base, false),
			COALESCE(o.data_pagamento <= :data_base, false),
			false, NULL::date
		FROM financiamento.outros_pagamentos o
		UNION ALL
		SELECT 3, 'Consórcios', cp.data_pagamento, cp.valor_total, true, true, false, NULL::date
		FROM financiamento.consorcio_pago cp
		WHERE cp.data_pagamento <= :data_base
		UNION ALL
		SELECT 3, 'Consórcios', ap.data_pagamento, ap.valor_parcela, false, false, false, NULL::date
		FROM financiamento.consorcio_a_pagar ap
		INNER JOIN competencia_consorcio u
			ON u.banco = ap.banco AND u.nome_consorciado = ap.nome_consorciado AND u.competencia = ap.competencia
		LEFT JOIN meses_pagos_consorcio mp
			ON mp.banco = ap.banco AND mp.nome_consorciado = ap.nome_consorciado
			AND mp.mes = date_trunc('month', ap.data_pagamento)::date
		WHERE ap.data_pagamento > :data_base
		OR mp.mes IS NULL          -- mês até a data base sem pagamento importado: fica o a pagar
	)
'''

SELECT_PROJECAO_ENDIVIDAMENTO = CTE_MOVIMENTOS_ENDIVIDAMENTO + '''
	SELECT
		EXTRACT(YEAR FROM data_referencia)::int AS ano,
		EXTRACT(MONTH FROM data_referencia)::int AS mes,
		ordem,
		categoria,
		ROUND(SUM(valor) / 1000000, 3) AS valor,
		ROUND(SUM(CASE WHEN pago THEN valor ELSE 0 END) / 1000000, 3) AS valor_pago,
		ROUND(SUM(CASE WHEN NOT pago THEN valor ELSE 0 END) / 1000000, 3) AS valor_a_pagar,
		bool_or(liquidado) AND bool_and(pago) AS mes_pago,   -- só o liquidado marca (antecipação/quitação não)
		bool_or(liquidado) AS mes_com_pagamento
	FROM movimentos
	WHERE (CAST(:data_corte AS date) IS NULL OR data_referencia >= date_trunc('month', CAST(:data_corte AS date))::date)   -- a partir do mês da data de corte
	GROUP BY 1, 2, 3, 4
	ORDER BY 1, 2, 3
'''

# Resumo do mês (variação do endividamento): posição por modalidade numa data base, em milhões
# (o service roda na data base e no último dia do mês anterior e calcula as colunas):
# - pago / a_pagar: mesmos totais do Sub Total do relatório (mesmo filtro de data de corte e mesmo
#   arredondamento: cada mês arredondado em 3 casas antes da soma, para o Saldo Final bater com o relatório);
# - quitado: antecipações e quitações pagas no mês da data base (a partir de :inicio_mes);
# - novo_pago / novo_a_pagar: contratos com data de contabilização no mês da data base (a partir de :inicio_mes).
SELECT_RESUMO_ENDIVIDAMENTO = CTE_MOVIMENTOS_ENDIVIDAMENTO + ''',
	resumo_mes AS (
		SELECT
			ordem,
			categoria,
			date_trunc('month', data_referencia) AS mes,
			ROUND(COALESCE(SUM(valor) FILTER (WHERE pago), 0) / 1000000, 3) AS pago,
			ROUND(COALESCE(SUM(valor) FILTER (WHERE NOT pago), 0) / 1000000, 3) AS a_pagar,
			ROUND(COALESCE(SUM(valor) FILTER (WHERE quitacao AND data_referencia >= CAST(:inicio_mes AS date)), 0) / 1000000, 3) AS quitado,
			ROUND(COALESCE(SUM(valor) FILTER (WHERE pago AND data_contabilizacao >= CAST(:inicio_mes AS date)), 0) / 1000000, 3) AS novo_pago,
			ROUND(COALESCE(SUM(valor) FILTER (WHERE NOT pago AND data_contabilizacao >= CAST(:inicio_mes AS date)), 0) / 1000000, 3) AS novo_a_pagar
		FROM movimentos
		WHERE (CAST(:data_corte AS date) IS NULL OR data_referencia >= date_trunc('month', CAST(:data_corte AS date))::date)
		GROUP BY 1, 2, 3
	)
	SELECT ordem, categoria, SUM(pago) AS pago, SUM(a_pagar) AS a_pagar, SUM(quitado) AS quitado,
		SUM(novo_pago) AS novo_pago, SUM(novo_a_pagar) AS novo_a_pagar
	FROM resumo_mes
	GROUP BY 1, 2
	ORDER BY 1
'''

# Créditos de consórcio (lançamento manual por competência): o da competência da data base ou o último anterior
SELECT_CREDITO_ENDIVIDAMENTO = '''
	SELECT competencia, credito_cotas_contempladas, credito_parcelas_nao_contempladas
	FROM financiamento.consorcio_credito
	WHERE competencia <= date_trunc('month', CAST(:data_base AS date))::date
	ORDER BY competencia DESC
	LIMIT 1
'''
