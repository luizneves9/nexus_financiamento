SELECT_SELIC_LISTA = '''
	SELECT id, data, valor
	FROM financiamento.selic
	WHERE (:data_ini IS NULL OR data >= :data_ini)
	AND (:data_fim IS NULL OR data <= :data_fim)
	ORDER BY data DESC, id DESC
'''

SELECT_DATAS_SELIC = '''
	SELECT DISTINCT data
	FROM financiamento.selic
	WHERE data IS NOT NULL
'''

# um único comando: o trigger da SELIC (por comando) recalcula os contratos uma vez por importação
INSERIR_SELIC_LOTE = '''
	INSERT INTO financiamento.selic (data, valor)
	SELECT t.data, t.valor
	FROM unnest(CAST(:datas AS date[]), CAST(:valores AS numeric[])) AS t(data, valor)
	ORDER BY t.data
	RETURNING id
'''

# contratos recalculados pelo trigger da SELIC nesta transação
CONTAR_RECALCULADOS_SELIC = '''
	SELECT count(*)
	FROM financiamento.projecao_controle
	WHERE motivo_ultimo_calculo = 'SELIC'
	AND data_ultimo_calculo = now()
'''
