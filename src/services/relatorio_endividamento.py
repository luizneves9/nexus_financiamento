import pandas as pd
import streamlit as st
from sqlalchemy import text
from database.connection import ConexaoBancoSQL
from queries.queries_relatorio_endividamento import SELECT_PROJECAO_ENDIVIDAMENTO
from repositories.funcoes import ler_query

connect = ConexaoBancoSQL()
engine = connect.conexao_banco()

def listar_projecao_endividamento(data_base, data_corte=None, empresa=None, banco=None):
    '''Função para buscar o endividamento na posição da data base, agrupado por ano e mês, com filtros opcionais.'''

    df = pd.DataFrame()
    query = text(SELECT_PROJECAO_ENDIVIDAMENTO)
    parametros = {
        'data_base': data_base,
        'data_corte': data_corte,
        'empresa': empresa or None,      # valor exato do selectbox (razão social)
        'banco': banco or None
    }

    try:
        with engine.begin() as conn:
            df = ler_query(query, conn, parametros)
    except Exception as e:
        st.session_state['mensagem_erro'] = f'Erro ao consultar o endividamento. ({e})'

    return df


def transformar_dados_para_relatorio(df):
    '''Transforma o dataframe em estrutura esperada pelo template HTML.'''

    if df.empty:
        return {}, 0, {}, []

    # Garantir tipos de dado
    df['ano'] = df['ano'].astype(int)
    df['mes'] = df['mes'].astype(int)
    for coluna in ('valor', 'valor_pago', 'valor_a_pagar'):
        df[coluna] = df[coluna].astype(float)

    # Dados de saldo acumulado (agregação de todos os anos/meses)
    valor_total_grupo = df['valor'].sum()
    saldo = [
        {
            'modalidade': 'Saldo Acumulado - Financiamentos',
            'total': valor_total_grupo,
            'pct': '100,00%'
        }
    ]

    # Dados por ano
    anos = {}
    for ano in sorted(df['ano'].unique()):
        df_ano = df[df['ano'] == ano]
        total_ano = df_ano['valor'].sum()

        # Agrupar por modalidade (categoria) e calcular totais
        linhas_agrupadas = []
        categorias_unicas = df_ano['categoria'].unique()

        for categoria in categorias_unicas:
            df_cat = df_ano[df_ano['categoria'] == categoria]
            valores_por_mes = [0.0] * 12
            status_por_mes = [None] * 12   # 'pago' (mês todo pago) / 'parcial' (parte paga) / None (projetado)

            for idx, row in df_cat.iterrows():
                mes = int(row['mes']) - 1  # 0-indexed
                valor = float(row['valor'])
                if mes < len(valores_por_mes):
                    valores_por_mes[mes] = valor
                    if row.get('mes_pago'):
                        status_por_mes[mes] = 'pago'
                    elif row.get('mes_com_pagamento'):
                        status_por_mes[mes] = 'parcial'

            total_cat = df_cat['valor'].sum()
            pct = (total_cat / valor_total_grupo * 100) if valor_total_grupo > 0 else 0

            linhas_agrupadas.append({
                'modalidade': categoria,
                'valores': valores_por_mes,
                'status': status_por_mes,
                'total': total_cat,
                'pct': f'{pct:,.2f}%'.replace('.', ',')
            })

        anos[ano] = {
            'total_grupo': total_ano,
            'linhas': linhas_agrupadas
        }

    # Sub Total: uma linha por modalidade (meses somados em todos os anos exibidos) + Total Geral,
    # com o total pago até a data base e o total a pagar (projetado)
    def linha_subtotal(modalidade, df_linha):
        return {
            'modalidade': modalidade,
            'valores': [df_linha.loc[df_linha['mes'] == mes, 'valor'].sum() for mes in range(1, 13)],
            'total': df_linha['valor'].sum(),
            'total_pago': df_linha['valor_pago'].sum(),
            'total_a_pagar': df_linha['valor_a_pagar'].sum()
        }

    subtotal = [linha_subtotal('Financiamentos' if categoria == 'Financiamento' else categoria, df[df['categoria'] == categoria])
                for categoria in df['categoria'].unique()]
    subtotal.append(linha_subtotal('Total Geral', df))

    return saldo, valor_total_grupo, anos, subtotal
