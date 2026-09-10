SELECT_FORNECEDORES = '''
    SELECT
        id AS "Id",
        cnpj AS "CNPJ",
        razao_social AS "Nome da Empresa"
    FROM financiamento.fornecedor
    ORDER BY id
'''