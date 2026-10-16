from queries.queries_contas_a_pagar import CTE_POSICAO_DATA_BASE

# Indicadores (Painel > Indicadores): mesma posição na data base de Contas a Pagar e Endividamento (RN24),
# consultada duas vezes (período atual e o mesmo período um ano antes, com a data base também recuada).
# - Saldo devedor: principal das parcelas projetadas A VENCER (vencimento útil a partir da data base); as
#   parcelas antigas nunca baixadas no Nexus (liquidação controlada só a partir de 2026) não inflam o saldo.
# - Fluxo de pagamentos: valor considerado (pago, se liquidado até a data base; senão projetado) das parcelas,
#   antecipações e quitações com vencimento útil no período; comparável entre anos mesmo sem baixas antigas.
# - Só entram contratos emitidos até a data base (na data base do ano anterior os mais novos não existiam).

# Posição agregada numa única passada (a posição de data base passada refaz contratos e é cara):
# GROUPING SETS devolve uma linha por contrato (mes nulo) e uma por mês do vencimento útil (numero_contrato nulo).
SELECT_INDICADORES_POSICAO = CTE_POSICAO_DATA_BASE + '''
	SELECT
		p.numero_contrato,
		date_trunc('month', p.vencimento_util)::date AS mes,
		SUM(p.valor_principal) FILTER (WHERE p.situacao = 'Projetado' AND p.vencimento_util >= :data_base) AS saldo_devedor,
		SUM(p.valor_considerado) FILTER (WHERE (:data_ini IS NULL OR p.vencimento_util >= :data_ini)
			AND (:data_fim IS NULL OR p.vencimento_util <= :data_fim)) AS servico_periodo,
		SUM(p.valor_juros) FILTER (WHERE p.situacao IN ('Liquidado', 'Projetado')
			AND (:data_ini IS NULL OR p.vencimento_util >= :data_ini)
			AND (:data_fim IS NULL OR p.vencimento_util <= :data_fim)) AS juros_periodo
	FROM posicao p
	INNER JOIN financiamento.contratos c ON c.numero_contrato = p.numero_contrato
	WHERE c.data_emissao <= :data_base
	AND (:empresa IS NULL OR p.nome_empresa = :empresa)
	AND (:banco IS NULL OR p.banco = :banco)
	GROUP BY GROUPING SETS ((p.numero_contrato), (date_trunc('month', p.vencimento_util)))
'''

# Contratos emitidos até a data base (inclusive os sem parcela na posição, para as contratações do período)
SELECT_INDICADORES_CONTRATOS = '''
	SELECT
		c.id AS id_contrato,
		e.razao_social AS nome_empresa,
		b.razao_social AS banco,
		c.numero_contrato,
		CASE c.tipo_contrato WHEN 'BNDES FINAME SELIC' THEN 'SELIC' WHEN 'BNDES FINAME TFC' THEN 'TFC' ELSE c.tipo_contrato END AS tipo_contrato,
		c.data_emissao,
		c.valor_financiado,
		c.taxa_juros_efetiva
	FROM financiamento.contratos c
	INNER JOIN financiamento.empresas e ON e.id = c.id_empresa
	INNER JOIN financiamento.bancos b ON b.id = c.id_banco
	WHERE c.data_emissao <= :data_base
	AND (:empresa IS NULL OR e.razao_social = :empresa)
	AND (:banco IS NULL OR b.razao_social = :banco)
	ORDER BY e.razao_social, c.numero_contrato
'''
