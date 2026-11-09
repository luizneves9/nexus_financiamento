import pandas as pd
import streamlit as st
from datetime import timedelta
from sqlalchemy import text
from database.connection import ConexaoBancoSQL
from queries.queries_relatorio_endividamento import (
    SELECT_PROJECAO_ENDIVIDAMENTO,
    SELECT_CREDITO_ENDIVIDAMENTO,
    SELECT_RESUMO_ENDIVIDAMENTO,
)
from repositories.funcoes import ler_query

connect = ConexaoBancoSQL()
engine = connect.conexao_banco()

def listar_projecao_endividamento(data_base, data_corte=None):
    '''Endividamento na posição da data base (financiamentos, Compra Santo Anjo, consórcios e tributário),
    agrupado por ano, mês e modalidade.'''

    df = pd.DataFrame()
    parametros = {'data_base': data_base, 'data_corte': data_corte}

    try:
        with engine.begin() as conn:
            df = ler_query(text(SELECT_PROJECAO_ENDIVIDAMENTO), conn, parametros)
    except Exception as e:
        st.session_state['mensagem_erro'] = f'Erro ao consultar o endividamento. ({e})'

    return df


def buscar_credito_endividamento(data_base):
    '''Créditos de consórcio da competência da data base ou da última anterior (dict ou None).'''

    try:
        with engine.begin() as conn:
            df = ler_query(text(SELECT_CREDITO_ENDIVIDAMENTO), conn, {'data_base': data_base})
    except Exception as e:
        st.session_state['mensagem_erro'] = f'Erro ao consultar os créditos de consórcio. ({e})'
        return None

    return None if df.empty else df.iloc[0].to_dict()


def _pct(valor, total):
    '''Percentual no formato brasileiro (ex.: 12,34%).'''

    pct = (valor / total * 100) if total else 0
    return f'{pct:,.2f}%'.replace(',', 'X').replace('.', ',').replace('X', '.')


def transformar_dados_para_relatorio(df):
    '''Transforma o dataframe em estrutura esperada pelo template HTML.

    - Saldo Acumulado: uma linha por modalidade, % sobre o total geral;
    - anos: linhas das modalidades do ano, % sobre o total da própria modalidade;
    - Sub Total: uma linha por modalidade + Total Geral, com pago e a pagar.'''

    if df.empty:
        return [], 0, {}, []

    # Garantir tipos de dado
    df['ano'] = df['ano'].astype(int)
    df['mes'] = df['mes'].astype(int)
    df['ordem'] = df['ordem'].astype(int)
    for coluna in ('valor', 'valor_pago', 'valor_a_pagar'):
        df[coluna] = df[coluna].astype(float)

    # modalidades na ordem do relatório (Financiamentos, Compra Santo Anjo, Consórcios, Tributário)
    categorias = df.sort_values('ordem')['categoria'].unique().tolist()
    total_categoria = df.groupby('categoria')['valor'].sum().to_dict()

    # Saldo acumulado (todos os anos/meses exibidos) por modalidade
    valor_total_grupo = df['valor'].sum()
    saldo = [
        {
            'modalidade': categoria,
            'total': total_categoria[categoria],
            'pct': _pct(total_categoria[categoria], valor_total_grupo)
        }
        for categoria in categorias
    ]

    # Dados por ano
    anos = {}
    for ano in sorted(df['ano'].unique()):
        df_ano = df[df['ano'] == ano]

        linhas_agrupadas = []
        for categoria in categorias:
            df_cat = df_ano[df_ano['categoria'] == categoria]
            if df_cat.empty:
                continue

            valores_por_mes = [0.0] * 12
            status_por_mes = [None] * 12   # 'pago' (mês todo pago) / 'parcial' (parte paga) / None (projetado)

            for _, row in df_cat.iterrows():
                mes = int(row['mes']) - 1  # 0-indexed
                valores_por_mes[mes] = float(row['valor'])
                if row.get('mes_pago'):
                    status_por_mes[mes] = 'pago'
                elif row.get('mes_com_pagamento'):
                    status_por_mes[mes] = 'parcial'

            total_cat = df_cat['valor'].sum()
            linhas_agrupadas.append({
                'modalidade': categoria,
                'valores': valores_por_mes,
                'status': status_por_mes,
                'total': total_cat,
                'pct': _pct(total_cat, total_categoria[categoria])
            })

        anos[ano] = {
            'total_grupo': df_ano['valor'].sum(),
            'linhas': linhas_agrupadas
        }

    # Sub Total: uma linha por modalidade (meses somados em todos os anos exibidos) + Total Geral,
    # com o total pago até a data base e o total a pagar
    def linha_subtotal(modalidade, df_linha):
        return {
            'modalidade': modalidade,
            'valores': [df_linha.loc[df_linha['mes'] == mes, 'valor'].sum() for mes in range(1, 13)],
            'total': df_linha['valor'].sum(),
            'total_pago': df_linha['valor_pago'].sum(),
            'total_a_pagar': df_linha['valor_a_pagar'].sum()
        }

    subtotal = [linha_subtotal(categoria, df[df['categoria'] == categoria]) for categoria in categorias]
    subtotal.append(linha_subtotal('Total Geral', df))

    return saldo, valor_total_grupo, anos, subtotal


def montar_rodape(subtotal, credito):
    '''Créditos de consórcio (em milhões) e Dívida Líquida = total a pagar geral - créditos.'''

    total_a_pagar = subtotal[-1]['total_a_pagar'] if subtotal else 0.0
    cotas = float(credito['credito_cotas_contempladas']) / 1000000 if credito else 0.0
    nao_contempladas = float(credito['credito_parcelas_nao_contempladas']) / 1000000 if credito else 0.0

    return {
        'competencia': credito['competencia'] if credito else None,
        'credito_cotas_contempladas': cotas,
        'credito_parcelas_nao_contempladas': nao_contempladas,
        'total_a_pagar': total_a_pagar,
        'divida_liquida': total_a_pagar - cotas - nao_contempladas
    }


MESES_EXTENSO = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']


def consultar_resumo_mes(data_base, data_corte=None):
    '''Posição por modalidade no último dia do mês anterior (saldo inicial) e na data base (saldo final).

    Devolve (df_inicial, df_final, base_inicial) ou None em caso de erro (mensagem em session_state).'''

    inicio_mes = data_base.replace(day=1)
    base_inicial = inicio_mes - timedelta(days=1)

    try:
        with engine.begin() as conn:
            df_inicial = ler_query(text(SELECT_RESUMO_ENDIVIDAMENTO), conn,
                                   {'data_base': base_inicial, 'data_corte': data_corte, 'inicio_mes': inicio_mes})
            df_final = ler_query(text(SELECT_RESUMO_ENDIVIDAMENTO), conn,
                                 {'data_base': data_base, 'data_corte': data_corte, 'inicio_mes': inicio_mes})
    except Exception as e:
        st.session_state['mensagem_erro'] = f'Erro ao consultar o resumo do mês. ({getattr(e, "orig", e)})'
        return None

    return df_inicial, df_final, base_inicial


def montar_resumo_mes(df_inicial, df_final, base_inicial, data_base, rodape):
    '''Linhas do resumo do mês (variação do endividamento), em milhões, por modalidade:

    - Saldo Inicial: a pagar no último dia do mês anterior; Saldo Final: a pagar na data base;
    - Contrato Quitado: antecipações e quitações pagas no mês;
    - Contrato Novo: a pagar, na data base, dos contratos contabilizados no mês;
    - Pgto Mês: pagamentos registrados entre as duas posições, sem as quitações e sem os contratos novos;
    - Juros: o que sobra (Saldo Final - Saldo Inicial + Pgto Mês + Contrato Quitado - Contrato Novo),
      ou seja, a correção pela Selic e os reajustes/novas contemplações dos consórcios.'''

    def por_categoria(df):
        if df is None or df.empty:
            return {}
        return {linha['categoria']: {coluna: float(linha[coluna] or 0) for coluna in
                                     ('ordem', 'pago', 'a_pagar', 'quitado', 'novo_pago', 'novo_a_pagar')}
                for _, linha in df.iterrows()}

    inicial, final = por_categoria(df_inicial), por_categoria(df_final)
    vazio = {'ordem': 99, 'pago': 0.0, 'a_pagar': 0.0, 'quitado': 0.0, 'novo_pago': 0.0, 'novo_a_pagar': 0.0}
    categorias = sorted(set(inicial) | set(final), key=lambda c: (final.get(c) or inicial.get(c))['ordem'])

    linhas = []
    for categoria in categorias:
        ini, fim = inicial.get(categoria, vazio), final.get(categoria, vazio)
        quitado = fim['quitado']
        novo = fim['novo_a_pagar']
        # arredondado em 3 casas (+ 0.0 evita "-0.000" por resíduo de ponto flutuante)
        pgto = round((fim['pago'] - fim['novo_pago']) - ini['pago'] - quitado, 3) + 0.0
        linhas.append({
            'modalidade': categoria,
            'saldo_inicial': ini['a_pagar'],
            'juros': round(fim['a_pagar'] - ini['a_pagar'] + pgto + quitado - novo, 3) + 0.0,
            'pgto_mes': pgto,
            'quitado': quitado,
            'novo': novo,
            'saldo_final': fim['a_pagar'],
        })

    colunas = ('saldo_inicial', 'juros', 'pgto_mes', 'quitado', 'novo', 'saldo_final')
    total = {'modalidade': 'Total', **{coluna: sum(linha[coluna] for linha in linhas) for coluna in colunas}}

    if base_inicial.year == data_base.year:
        periodo = f'{MESES_EXTENSO[base_inicial.month - 1]} x {MESES_EXTENSO[data_base.month - 1]}'
    else:
        periodo = (f'{MESES_EXTENSO[base_inicial.month - 1]}/{base_inicial.year} x '
                   f'{MESES_EXTENSO[data_base.month - 1]}/{data_base.year}')

    cotas = rodape['credito_cotas_contempladas'] if rodape else 0.0
    nao_contempladas = rodape['credito_parcelas_nao_contempladas'] if rodape else 0.0

    return {
        'periodo': periodo,
        'linhas': linhas,
        'total': total,
        'competencia': rodape['competencia'] if rodape else None,
        'credito_cotas_contempladas': cotas,
        'credito_parcelas_nao_contempladas': nao_contempladas,
        'divida_liquida': total['saldo_final'] - cotas - nao_contempladas,
    }
