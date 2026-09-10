import pandas as pd

def consultar_empresas(query, conn):
    '''Interação com o banco de dados para retornar um select.'''
    return pd.read_sql(query, conn)