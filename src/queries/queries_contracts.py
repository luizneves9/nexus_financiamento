SELECT_PROJECAO = '''
WITH selic AS (
	SELECT valor
	FROM financiamento.selic
	ORDER BY data DESC
	LIMIT 1
)

SELECT
    parcela AS "Parcela",
    data_vcto AS "Data de Vencimento",
    ROUND(COALESCE(valor_pagamento, total_parcela * s.valor), 2) AS "Valor"
FROM financiamento.mv_projecao_real
CROSS JOIN selic s
WHERE id_contrato = :id
'''

DELETE_CONTRATO = '''
	DELETE FROM financiamento.contratos
	WHERE id = :id
'''