SELECT_EMPRESAS = '''
    SELECT
        id AS "Id",
        cnpj AS "CNPJ",
        razao_social AS "Nome da Empresa"
    FROM financiamento.empresas
    ORDER BY id
'''