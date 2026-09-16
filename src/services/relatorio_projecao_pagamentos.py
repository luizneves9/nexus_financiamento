import pandas as pd
from database.connection import ConexaoBancoSQL
from queries.queries_projection import SELECT_PROJECAO_PAGAMENTOS
from repositories.funcoes import ler_query

connect = ConexaoBancoSQL()
engine = connect.conexao_banco()

def listar_projecao_pagamentos():
    '''Função definida para listar o agrupamento da projeção de pagamentos.'''

    df = pd.DataFrame()
    query = SELECT_PROJECAO_PAGAMENTOS

    try:
        with engine.begin() as conn:
            df = ler_query(query, conn)
    except:
        pass

    return df
