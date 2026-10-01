import pandas as pd
from sqlalchemy import text
from database.connection import ConexaoBancoSQL
from queries.queries_antecipacao import SELECT_ANTECIPACOES
from repositories.funcoes import ler_query

connect = ConexaoBancoSQL()
engine = connect.conexao_banco()

def listar_antecipacoes(empresa=None, banco=None, contrato=None, data_pagamento_ini=None, data_pagamento_fim=None):
    '''Função definida para listar as antecipações/quitações registradas com filtros opcionais.'''

    df = pd.DataFrame()
    query = text(SELECT_ANTECIPACOES)
    parametros = {
        'empresa': f"%{empresa}%" if empresa else None,
        'banco': f"%{banco}%" if banco else None,
        'contrato': f"%{contrato}%" if contrato else None,
        'data_pagamento_ini': data_pagamento_ini,
        'data_pagamento_fim': data_pagamento_fim
    }

    try:
        with engine.begin() as conn:
            df = ler_query(query, conn, parametros)
    except:
        pass

    return df

def resumir_antecipacoes(df):
    '''Função definida para resumir as antecipações filtradas (quantidades e total pago).'''

    return {
        'empresas': df['nome_empresa'].nunique(),
        'bancos': df['banco'].nunique(),
        'contratos': df['numero_contrato'].nunique(),
        'valor_pago': float(df['valor_pago'].sum())
    }
