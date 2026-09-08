import pandas as pd

def listar_projecao(query, conn, parametros):
    '''Interação com o banco de dados para importar dataframe com projeção dos valores.'''
    return pd.read_sql(sql=query, con=conn, params=parametros)
