import pandas as pd
from sqlalchemy import text
from database.connection import ConexaoBancoSQL
from queries.queries_projection import SELECT_PROJECAO_PAGAMENTOS
from repositories.funcoes import ler_query

connect = ConexaoBancoSQL()
engine = connect.conexao_banco()

def listar_projecao_pagamentos(empresa=None, banco=None, contrato=None, data_vcto_ini=None, data_vcto_fim=None):
    '''Função definida para listar o agrupamento da projeção de pagamentos com filtros opcionais.'''

    df = pd.DataFrame()
    query = text(SELECT_PROJECAO_PAGAMENTOS)
    parametros = {
        'empresa': f"%{empresa}%" if empresa else None,
        'banco': f"%{banco}%" if banco else None,
        'contrato': f"%{contrato}%" if contrato else None,
        'data_vcto_ini': data_vcto_ini,
        'data_vcto_fim': data_vcto_fim
    }

    try:
        with engine.begin() as conn:
            df = ler_query(query, conn, parametros)
    except:
        pass

    return df

def resumir_projecao_pagamentos(df):
    '''Função definida para resumir a projeção de pagamentos filtrada (quantidades e total das parcelas).'''

    return {
        'empresas': df['nome_empresa'].nunique(),
        'bancos': df['banco'].nunique(),
        'contratos': df['numero_contrato'].nunique(),
        'total_parcela': float(df['total_parcela'].sum())
    }
