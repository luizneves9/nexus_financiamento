SELECT_PROJECAO = '''
	WITH valores_parcelas AS (
		SELECT
			parcela::numeric AS "Parcela",
			'Parcela' AS "Tipo",
			data_vcto AS "Data de Vencimento",
			valor_pagamento AS "Valor"
		FROM financiamento.projecao_parcelas
		WHERE id_contrato = :id
		AND situacao <> 'CANCELADA_QUITACAO'
	),
	valores_antecipacao AS (
		SELECT
			0 AS "Parcela",
			INITCAP(tipo_lancamento) AS "Tipo",
			data_pagamento AS "Data de Vencimento",
			ROUND(valor_pago, 2) AS "Valor"
		FROM financiamento.antecipacao
		WHERE id_contrato = :id
	)
	SELECT "Parcela", "Tipo", "Data de Vencimento", "Valor" FROM valores_parcelas
	UNION ALL
	SELECT "Parcela", "Tipo", "Data de Vencimento", "Valor" FROM valores_antecipacao
	ORDER BY "Data de Vencimento"
'''

PROJETAR_CONTRATO_SELIC = '''
	SELECT *
	FROM financiamento.projetar_contrato_selic(
		:data_emissao,
		:data_bndes,
		:valor_financiado,
		:taxa_juros_efetiva,
		:prazo_carencia,
		:prazo_final,
		:carencia_pagamento,
		:registro_cobranca
	)
	ORDER BY parcela
'''

PROJETAR_CONTRATO_TFC = '''
	SELECT *
	FROM financiamento.projetar_contrato_tfc(
		:data_emissao,
		:data_bndes,
		:valor_financiado,
		:taxa_juros_efetiva,
		:prazo_carencia,
		:prazo_final,
		:carencia_pagamento
	)
	ORDER BY parcela
'''

DELETE_CONTRATO = '''
	DELETE FROM financiamento.contratos
	WHERE id = :id
	RETURNING *
'''

VERIFICAR_LIQUIDACAO_CONTRATO = '''
	SELECT count(*) AS qtd
	FROM financiamento.liquidacao
	WHERE id_contrato = :id
'''

# Detalhe do contrato (modal com abas): dados do contrato e situação da projeção
SELECT_CONTRATO_DETALHE = '''
	SELECT
		c.id,
		c.numero_contrato,
		e.razao_social AS empresa,
		b.razao_social AS banco,
		c.tipo_contrato,
		c.data_emissao,
		c.data_bndes,
		c.valor_financiado,
		c.selic,
		c.taxa_juros_efetiva,
		c.custo_bndes,
		c.sobretaxa_bndes,
		c.percentual_banco,
		c.pos_fixado,
		c.prazo_total,
		c.prazo_carencia,
		c.prazo_final,
		c.carencia_pagamento,
		c.data_primeira_parcela_encargo,
		c.data_primeira_parcela_prestacao,
		c.data_ultima_parcela,
		c.registro_cobranca,
		c.debito_conta_corrente,
		pc.status_contrato,
		pc.qtd_parcelas,
		pc.qtd_liquidadas
	FROM financiamento.contratos c
	INNER JOIN financiamento.empresas e ON e.id = c.id_empresa
	INNER JOIN financiamento.bancos b ON b.id = c.id_banco
	LEFT JOIN financiamento.projecao_controle pc ON pc.id_contrato = c.id
	WHERE c.id = :id
'''

# Histórico do contrato: ações do log de auditoria do próprio contrato e dos registros ligados a ele
# (antecipações/quitações, liquidações e anexos guardam o id_contrato nos detalhes)
SELECT_HISTORICO_CONTRATO = '''
	SELECT data_hora, usuario, acao, sucesso, detalhes
	FROM financiamento.log_auditoria
	WHERE (entidade = 'contratos' AND id_registro = :id)
	OR detalhes ->> 'id_contrato' = CAST(:id AS text)
	ORDER BY data_hora DESC, id DESC
	LIMIT 300
'''
