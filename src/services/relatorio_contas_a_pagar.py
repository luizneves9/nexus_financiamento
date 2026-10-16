import io
import pandas as pd
import streamlit as st
from sqlalchemy import text
from database.connection import ConexaoBancoSQL
from queries.queries_contas_a_pagar import SELECT_CONTAS_A_PAGAR
from repositories.funcoes import ler_query

connect = ConexaoBancoSQL()
engine = connect.conexao_banco()

# rótulos das colunas (tela e exportação)
COLUNAS_CONTAS_A_PAGAR = {
    'nome_empresa': 'Empresa',
    'banco': 'Banco',
    'numero_contrato': 'Contrato',
    'tipo_contrato': 'Tipo de contrato',
    'parcela': 'Parcela',
    'tipo': 'Tipo',
    'situacao': 'Situação',
    'vencimento': 'Vencimento',
    'vencimento_util': 'Vencimento útil',
    'valor_principal': 'Principal',
    'valor_juros': 'Juros',
    'parcela_h': 'Parcela H',
    'valor_projetado': 'Valor projetado',
    'data_pagamento': 'Data pagamento',
    'valor_pago': 'Valor pago',
    'valor_ajuste': 'Ajuste',
    'valor_considerado': 'Valor considerado',
    'origem': 'Origem',
    'doctos_erp': 'Doctos ERP',
}

COLUNAS_VALOR = ['valor_principal', 'valor_juros', 'parcela_h', 'valor_projetado', 'valor_pago', 'valor_ajuste', 'valor_considerado']

def listar_contas_a_pagar(data_base, empresa=None, banco=None, contrato=None, data_vcto_ini=None, data_vcto_fim=None, situacao=None):
    '''Função definida para listar as contas a pagar na posição da data base, com filtros opcionais.'''

    df = pd.DataFrame()
    query = text(SELECT_CONTAS_A_PAGAR)
    parametros = {
        'data_base': data_base,
        'empresa': empresa or None,      # valor exato do selectbox (razão social)
        'banco': banco or None,
        'contrato': f"%{contrato}%" if contrato else None,
        'data_vcto_ini': data_vcto_ini,
        'data_vcto_fim': data_vcto_fim,
        'situacao': situacao
    }

    try:
        with engine.begin() as conn:
            df = ler_query(query, conn, parametros)
    except Exception as e:
        st.session_state['mensagem_erro'] = f'Erro ao consultar as contas a pagar. ({e})'

    return df

def resumir_contas_a_pagar(df):
    '''Função definida para resumir as contas a pagar filtradas (valor considerado por situação), antes da formatação.'''

    def total(*situacoes):
        return float(df.loc[df['situacao'].isin(situacoes), 'valor_considerado'].fillna(0).sum())

    return {
        'contratos': df['numero_contrato'].nunique(),
        'linhas': len(df),
        'liquidado': total('Liquidado'),
        'antecipacoes': total('Antecipação', 'Quitação'),
        'projetado': total('Projetado'),
        'total': float(df['valor_considerado'].fillna(0).sum())
    }

def exportar_contas_a_pagar(df, data_base):
    '''Gera o arquivo de exportação (Excel; CSV se o ambiente não tiver o openpyxl).

    Devolve (conteúdo, nome do arquivo, tipo MIME).
    '''

    df_exportacao = df.rename(columns=COLUNAS_CONTAS_A_PAGAR)
    nome = f"contas_a_pagar_base_{data_base:%d-%m-%Y}"

    try:
        import openpyxl  # noqa: F401 (disponibilidade do motor do Excel)
        arquivo = io.BytesIO()
        with pd.ExcelWriter(arquivo, engine='openpyxl', date_format='DD/MM/YYYY', datetime_format='DD/MM/YYYY') as escritor:
            df_exportacao.to_excel(escritor, index=False, sheet_name='Contas a Pagar')
        return arquivo.getvalue(), f'{nome}.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    except ImportError:
        conteudo = df_exportacao.to_csv(index=False, sep=';', decimal=',', date_format='%d/%m/%Y')
        return conteudo.encode('utf-8-sig'), f'{nome}.csv', 'text/csv'
