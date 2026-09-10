SELECT_BANCOS = '''
    SELECT
        id AS "Id",
        cnpj AS "CNPJ",
        razao_social AS "Nome da Empresa"
    FROM financiamento.bancos
    ORDER BY id
'''