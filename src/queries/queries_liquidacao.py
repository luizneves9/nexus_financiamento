SELECT_PARCELAS_LIQUIDACAO = '''
	SELECT
		p.id AS id_parcela,
		l.id AS id_liquidacao,
		p.id_contrato,
		e.razao_social AS nome_empresa,
		b.razao_social AS banco,
		c.numero_contrato,
		p.parcela,
		p.data_vcto,
		p.situacao,
		p.valor_pagamento AS valor_projetado,
		l.data_pagamento,
		l.valor_pago,
		l.valor_ajuste,
		l.origem
	FROM financiamento.projecao_parcelas p
	INNER JOIN financiamento.contratos c ON c.id = p.id_contrato
	INNER JOIN financiamento.empresas e ON e.id = c.id_empresa
	INNER JOIN financiamento.bancos b ON b.id = c.id_banco
	LEFT JOIN financiamento.liquidacao l ON l.id_parcela = p.id AND NOT l.estornado
	WHERE p.situacao <> 'CANCELADA_QUITACAO'
	AND (:empresa IS NULL OR e.razao_social = :empresa)
	AND (:banco IS NULL OR b.razao_social = :banco)
	AND (:contrato IS NULL OR c.numero_contrato ILIKE :contrato)
	AND (:data_vcto_ini IS NULL OR p.data_vcto >= :data_vcto_ini)
	AND (:data_vcto_fim IS NULL OR p.data_vcto <= :data_vcto_fim)
	AND (:situacao IS NULL OR p.situacao = :situacao)
	ORDER BY p.data_vcto, c.numero_contrato, p.parcela
'''

SELECT_PARCELAS_POR_ID = '''
	SELECT
		p.id AS id_parcela,
		c.numero_contrato,
		p.parcela,
		p.data_vcto,
		p.situacao,
		p.valor_pagamento AS valor_projetado
	FROM financiamento.projecao_parcelas p
	INNER JOIN financiamento.contratos c ON c.id = p.id_contrato
	WHERE p.id = ANY(:ids)
	ORDER BY p.data_vcto, c.numero_contrato, p.parcela
'''

# id_contrato e valor_projetado são preenchidos pelo trigger a partir da parcela
INSERIR_LIQUIDACAO_MANUAL = '''
	INSERT INTO financiamento.liquidacao
		(id_parcela, id_contrato, data_pagamento, valor_projetado, valor_pago, origem, usuario)
	VALUES (:id_parcela, 0, :data_pagamento, 0, :valor_pago, 'MANUAL', :usuario)
	RETURNING *
'''

ESTORNAR_LIQUIDACAO = '''
	UPDATE financiamento.liquidacao
	SET estornado = true, motivo_estorno = :motivo, usuario_estorno = :usuario
	WHERE id = :id AND NOT estornado
	RETURNING *
'''

# Conciliação com o ERP: o relatório fica numa tabela temporária, apagada ao final da transação
CRIAR_TMP_CONCILIACAO_ERP = '''
	CREATE TEMP TABLE tmp_conciliacao_erp (
		linha int4,
		filial varchar(20),
		data_pagamento date,
		fornecedor varchar(255),
		docto varchar(100),
		vencimento date,
		valor_pago numeric(15, 2)
	) ON COMMIT DROP
'''

INSERIR_TMP_CONCILIACAO_ERP = '''
	INSERT INTO tmp_conciliacao_erp (linha, filial, data_pagamento, fornecedor, docto, vencimento, valor_pago)
	VALUES (:linha, :filial, :data_pagamento, :fornecedor, :docto, :vencimento, :valor_pago)
'''

# Conciliação: cada linha do ERP é identificada pelo código (Docto antes do 1º '-') e resolvida para um
# GRUPO de contratos: o(s) contrato(s) vinculado(s) manualmente ao código (contrato_erp_vinculo) ou o
# contrato de mesmo número (no grupo de vínculo dele, se houver). ERP e parcelas são somados por
# (grupo, mês/ano): do vencimento no ERP e de data na projeção.
CTE_CONCILIACAO_ERP = '''
	WITH linhas AS (
		SELECT
			t.*,
			trim(split_part(t.docto, '-', 1)) AS codigo_erp,
			date_trunc('month', t.vencimento)::date AS competencia
		FROM tmp_conciliacao_erp t
	),
	vinculos AS (
		SELECT codigo_erp, array_agg(id_contrato ORDER BY id_contrato) AS grupo
		FROM financiamento.contrato_erp_vinculo
		GROUP BY codigo_erp
	),
	resolvidas AS (
		SELECT
			l.*,
			COALESCE(v.grupo, gc.grupo, CASE WHEN c.id IS NOT NULL THEN ARRAY[c.id] END) AS grupo,
			(v.codigo_erp IS NOT NULL) AS vinculo_manual
		FROM linhas l
		LEFT JOIN vinculos v ON v.codigo_erp = l.codigo_erp
		LEFT JOIN financiamento.contratos c ON c.numero_contrato = l.codigo_erp
		LEFT JOIN LATERAL (
			SELECT vv.grupo FROM vinculos vv WHERE c.id = ANY(vv.grupo) ORDER BY vv.grupo LIMIT 1
		) gc ON true
	),
	erp AS (
		SELECT
			grupo,
			CASE WHEN grupo IS NULL THEN codigo_erp END AS codigo_nao_identificado,
			competencia,
			string_agg(DISTINCT codigo_erp, ', ') AS codigos_erp,
			bool_or(vinculo_manual) AS vinculo_manual,
			sum(valor_pago) AS valor_erp,
			count(*) AS qtd_linhas,
			array_agg(docto ORDER BY linha) AS doctos,
			max(data_pagamento) AS data_pagamento,
			count(DISTINCT data_pagamento) > 1 AS datas_diferentes
		FROM resolvidas
		GROUP BY grupo, CASE WHEN grupo IS NULL THEN codigo_erp END, competencia
	),
	nexus AS (
		SELECT
			p.id AS id_parcela,
			p.id_contrato,
			c.numero_contrato,
			p.parcela,
			date_trunc('month', p.data)::date AS competencia,
			p.valor_pagamento AS valor_nexus,
			p.situacao
		FROM financiamento.projecao_parcelas p
		INNER JOIN financiamento.contratos c ON c.id = p.id_contrato
		WHERE p.situacao IN ('ABERTA', 'LIQUIDADA')
		AND date_trunc('month', p.data)::date IN (SELECT competencia FROM erp)
	),
	nexus_parcela_grupo AS (
		-- grupo de cada parcela: o grupo do ERP que contém o contrato no mês, senão o grupo de vínculo, senão o próprio contrato
		SELECT
			n.*,
			COALESCE(g.grupo, gc.grupo, ARRAY[n.id_contrato]) AS grupo,
			count(g.grupo) OVER (PARTITION BY n.id_parcela) > 1 AS conflito
		FROM nexus n
		LEFT JOIN (SELECT DISTINCT grupo, competencia FROM erp WHERE grupo IS NOT NULL) g
			ON n.id_contrato = ANY(g.grupo) AND g.competencia = n.competencia
		LEFT JOIN LATERAL (
			SELECT vv.grupo FROM vinculos vv WHERE n.id_contrato = ANY(vv.grupo) ORDER BY vv.grupo LIMIT 1
		) gc ON true
	),
	nexus_grupo AS (
		SELECT
			grupo,
			competencia,
			array_agg(id_parcela ORDER BY numero_contrato, parcela) AS parcelas,
			string_agg(numero_contrato, ' + ' ORDER BY numero_contrato, parcela) AS contratos,
			string_agg(parcela::text, ' + ' ORDER BY numero_contrato, parcela) AS parcela,
			sum(valor_nexus) AS valor_nexus,
			bool_or(situacao = 'LIQUIDADA') AS alguma_liquidada,
			bool_or(conflito) AS conflito
		FROM nexus_parcela_grupo
		GROUP BY grupo, competencia
	),
	cruzamento AS (
		SELECT
			COALESCE(
				n.contratos,
				(SELECT string_agg(c.numero_contrato, ' + ' ORDER BY c.numero_contrato)
				 FROM financiamento.contratos c WHERE c.id = ANY(e.grupo)),
				e.codigo_nao_identificado
			) AS contrato,
			COALESCE(e.competencia, n.competencia) AS competencia,
			e.codigos_erp,
			e.codigo_nao_identificado,
			CASE
				WHEN e.vinculo_manual THEN 'Manual'
				WHEN e.grupo IS NOT NULL THEN 'Automático'
			END AS vinculo,
			COALESCE(e.grupo, n.grupo) AS grupo,
			n.parcelas,
			n.parcela,
			e.doctos,
			e.qtd_linhas,
			e.data_pagamento,
			e.datas_diferentes,
			e.valor_erp,
			n.valor_nexus,
			e.valor_erp - n.valor_nexus AS diferenca,
			CASE
				WHEN e.competencia IS NULL AND n.alguma_liquidada THEN 'JA_LIQUIDADA'      -- só no Nexus, já liquidada
				WHEN e.competencia IS NULL THEN 'NAO_PAGO_ERP'                           -- só no Nexus
				WHEN e.grupo IS NULL THEN 'NAO_IDENTIFICADO'                             -- código desconhecido
				WHEN NOT (e.grupo && CAST(:contratos AS int4[])) THEN 'FORA_SELECAO'     -- nenhum contrato do grupo considerado
				WHEN n.grupo IS NULL THEN 'NAO_IDENTIFICADO'                             -- contrato(s) sem parcela no mês
				WHEN n.conflito THEN 'CONFLITO'                                          -- parcela em mais de um grupo
				WHEN n.alguma_liquidada THEN 'JA_LIQUIDADA'
				WHEN e.valor_erp = n.valor_nexus THEN 'CONCILIADO'
				ELSE 'DIFERENCA'
			END AS status
		FROM erp e
		FULL JOIN nexus_grupo n ON n.grupo = e.grupo AND n.competencia = e.competencia
		WHERE NOT (e.competencia IS NULL AND NOT (n.grupo && CAST(:contratos AS int4[])))
	)
'''

SELECT_CONCILIACAO_ERP = CTE_CONCILIACAO_ERP + '''
	SELECT *
	FROM cruzamento
	ORDER BY
		CASE status
			WHEN 'DIFERENCA' THEN 1
			WHEN 'CONCILIADO' THEN 2
			WHEN 'CONFLITO' THEN 3
			WHEN 'NAO_IDENTIFICADO' THEN 4
			WHEN 'NAO_PAGO_ERP' THEN 5
			WHEN 'JA_LIQUIDADA' THEN 6
			ELSE 7
		END,
		contrato,
		competencia
'''

# grava as linhas marcadas que continuam CONCILIADO/DIFERENCA na conciliação refeita: uma liquidação por
# parcela do grupo, com o valor do ERP rateado pelo valor projetado (sobra do arredondamento na maior parcela)
INSERIR_LIQUIDACAO_CONCILIACAO = CTE_CONCILIACAO_ERP + ''',
	marcadas AS (
		SELECT
			cz.grupo,
			cz.competencia,
			cz.data_pagamento,
			cz.valor_erp,
			cz.valor_nexus,
			cz.doctos,
			cz.qtd_linhas,
			unnest(cz.parcelas) AS id_parcela
		FROM cruzamento cz
		WHERE cz.status IN ('CONCILIADO', 'DIFERENCA')
		AND cz.parcelas <@ CAST(:parcelas_marcadas AS int4[])
	),
	rateio AS (
		SELECT
			m.*,
			COALESCE(round(m.valor_erp * p.valor_pagamento / NULLIF(m.valor_nexus, 0), 2), 0) AS valor_rateado,
			row_number() OVER (PARTITION BY m.grupo, m.competencia ORDER BY p.valor_pagamento DESC, p.id) AS ordem
		FROM marcadas m
		INNER JOIN financiamento.projecao_parcelas p ON p.id = m.id_parcela
	),
	rateio_final AS (
		SELECT
			r.*,
			r.valor_rateado + CASE
				WHEN r.ordem = 1 THEN r.valor_erp - sum(r.valor_rateado) OVER (PARTITION BY r.grupo, r.competencia)
				ELSE 0
			END AS valor_pago_parcela
		FROM rateio r
	)
	INSERT INTO financiamento.liquidacao
		(id_parcela, id_contrato, data_pagamento, valor_projetado, valor_pago, origem,
		 lote_conciliacao, nome_arquivo, doctos_erp, qtd_linhas_erp, usuario)
	SELECT id_parcela, 0, data_pagamento, 0, valor_pago_parcela, 'ERP',
		CAST(:lote AS uuid), :nome_arquivo, doctos, qtd_linhas, :usuario
	FROM rateio_final
	RETURNING id, id_parcela, valor_projetado, valor_pago, valor_ajuste
'''

SELECT_CONTRATOS_VINCULO = '''
	SELECT c.id, c.numero_contrato, e.razao_social AS nome_empresa, b.razao_social AS banco
	FROM financiamento.contratos c
	INNER JOIN financiamento.empresas e ON e.id = c.id_empresa
	INNER JOIN financiamento.bancos b ON b.id = c.id_banco
	ORDER BY c.numero_contrato
'''

INSERIR_VINCULO_ERP = '''
	INSERT INTO financiamento.contrato_erp_vinculo (codigo_erp, id_contrato, usuario)
	VALUES (:codigo_erp, :id_contrato, :usuario)
	RETURNING *
'''

EXCLUIR_VINCULO_ERP = '''
	DELETE FROM financiamento.contrato_erp_vinculo
	WHERE codigo_erp = :codigo_erp
	AND id_contrato = :id_contrato
	RETURNING *
'''

SELECT_VINCULOS_ERP = '''
	SELECT v.codigo_erp, v.id_contrato, c.numero_contrato, e.razao_social AS nome_empresa, b.razao_social AS banco
	FROM financiamento.contrato_erp_vinculo v
	INNER JOIN financiamento.contratos c ON c.id = v.id_contrato
	INNER JOIN financiamento.empresas e ON e.id = c.id_empresa
	INNER JOIN financiamento.bancos b ON b.id = c.id_banco
	WHERE v.codigo_erp = ANY(:codigos)
	ORDER BY v.codigo_erp, c.numero_contrato
'''
