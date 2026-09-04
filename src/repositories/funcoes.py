import pandas as pd

def ler_query(query, conn):
    '''Função criada para retornar um df com a QUERY e CONEXÃO de parâmetro.'''
    return pd.read_sql(query, conn)
