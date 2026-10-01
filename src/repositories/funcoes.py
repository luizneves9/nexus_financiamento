import pandas as pd

def ler_query(query, conn, parametros=None):
    '''Função criada para retornar um df com a QUERY, CONEXÃO e PARÂMETROS (opcional).'''
    return pd.read_sql(query, conn, params=parametros)
