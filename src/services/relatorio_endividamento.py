import pandas as pd
from database.connection import ConexaoBancoSQL
from queries.queries_relatorio_endividamento import SELECT_PROJECAO_ENDIVIDAMENTO
from repositories.funcoes import ler_query

connect = ConexaoBancoSQL()
engine = connect.conexao_banco()

def listar_projecao_endividamento():
    '''Função para buscar a projeção de endividamento agrupada por ano e mês.'''

    df = pd.DataFrame()
    query = SELECT_PROJECAO_ENDIVIDAMENTO

    try:
        with engine.begin() as conn:
            df = ler_query(query, conn)
    except:
        pass

    return df


def transformar_dados_para_relatorio(df):
    '''Transforma o dataframe em estrutura esperada pelo template HTML.'''

    if df.empty:
        return {}, 0, {}

    # Garantir tipos de dado
    df['ano'] = df['ano'].astype(int)
    df['mes'] = df['mes'].astype(int)
    df['valor'] = df['valor'].astype(float)

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

            for idx, row in df_cat.iterrows():
                mes = int(row['mes']) - 1  # 0-indexed
                valor = float(row['valor'])
                if mes < len(valores_por_mes):
                    valores_por_mes[mes] = valor

            total_cat = df_cat['valor'].sum()
            pct = (total_cat / valor_total_grupo * 100) if valor_total_grupo > 0 else 0

            linhas_agrupadas.append({
                'modalidade': categoria,
                'valores': valores_por_mes,
                'total': total_cat,
                'pct': f'{pct:,.2f}%'.replace('.', ',')
            })

        anos[ano] = {
            'total_grupo': total_ano,
            'linhas': linhas_agrupadas
        }

    return saldo, valor_total_grupo, anos
