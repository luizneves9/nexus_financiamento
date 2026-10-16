import pandas as pd
import streamlit as st
from sqlalchemy import text
from database.connection import ConexaoBancoSQL
from queries.queries_indicadores import SELECT_INDICADORES_CONTRATOS, SELECT_INDICADORES_POSICAO
from repositories.funcoes import ler_query

connect = ConexaoBancoSQL()
engine = connect.conexao_banco()

# colunas de valor do retorno por contrato (vêm como Decimal/objeto do banco)
COLUNAS_VALOR_CONTRATO = ['valor_financiado', 'taxa_juros_efetiva', 'saldo_devedor', 'servico_periodo', 'juros_periodo']

def menos_um_ano(data):
    '''Mesma data no ano anterior (29/02 vira 28/02).'''

    if data is None:
        return None
    try:
        return data.replace(year=data.year - 1)
    except ValueError:
        return data.replace(year=data.year - 1, day=28)

def _consultar_posicao(conn, data_base, data_ini, data_fim, empresa, banco):
    '''Contratos e fluxo de pagamentos mensal na posição de uma data base (valores numéricos).'''

    parametros = {'data_base': data_base, 'data_ini': data_ini, 'data_fim': data_fim, 'empresa': empresa, 'banco': banco}
    df_contratos = ler_query(text(SELECT_INDICADORES_CONTRATOS), conn, parametros)
    df_posicao = ler_query(text(SELECT_INDICADORES_POSICAO), conn, parametros)

    # linhas por contrato (mes nulo) e por mês (numero_contrato nulo) do GROUPING SETS
    por_contrato = df_posicao[df_posicao['numero_contrato'].notna()].drop(columns=['mes'])
    df_contratos = df_contratos.merge(por_contrato, on='numero_contrato', how='left')
    df_mensal = (df_posicao[df_posicao['numero_contrato'].isna() & df_posicao['mes'].notna() & df_posicao['servico_periodo'].notna()]
                 [['mes', 'servico_periodo']].rename(columns={'servico_periodo': 'servico'})
                 .sort_values('mes'))

    for coluna in COLUNAS_VALOR_CONTRATO:
        df_contratos[coluna] = pd.to_numeric(df_contratos[coluna], errors='coerce').fillna(0.0)
    df_contratos['data_emissao'] = pd.to_datetime(df_contratos['data_emissao']).dt.date
    df_contratos['ativo'] = df_contratos['saldo_devedor'] > 0
    df_mensal['servico'] = pd.to_numeric(df_mensal['servico'], errors='coerce').fillna(0.0)

    return df_contratos, df_mensal

def consultar_indicadores(data_base, data_ini=None, data_fim=None, empresa=None, banco=None):
    '''Consulta o painel no período atual e no mesmo período do ano anterior (data base também recuada).

    Devolve um dicionário com 'atual' e 'anterior' (cada um: contratos, mensal, data_base, data_ini, data_fim);
    ou None em caso de erro (mensagem em session_state).
    '''

    periodos = {
        'atual': (data_base, data_ini, data_fim),
        'anterior': (menos_um_ano(data_base), menos_um_ano(data_ini), menos_um_ano(data_fim)),
    }
    resultado = {}

    try:
        with engine.begin() as conn:
            for chave, (base, ini, fim) in periodos.items():
                df_contratos, df_mensal = _consultar_posicao(conn, base, ini, fim, empresa or None, banco or None)
                resultado[chave] = {'contratos': df_contratos, 'mensal': df_mensal, 'data_base': base, 'data_ini': ini, 'data_fim': fim}
    except Exception as e:
        st.session_state['mensagem_erro'] = f'Erro ao consultar os indicadores. ({getattr(e, "orig", e)})'
        return None

    return resultado

def taxa_ponderada(df, peso):
    '''Média da taxa_juros_efetiva ponderada pela coluna `peso` (None se o peso total for zero).'''

    total = df[peso].sum()
    if df.empty or total <= 0:
        return None
    return float((df['taxa_juros_efetiva'] * df[peso]).sum() / total)

def _contratado(df, data_ini, data_fim):
    '''Valor financiado dos contratos emitidos no período.'''

    filtro = pd.Series(True, index=df.index)
    if data_ini:
        filtro &= df['data_emissao'] >= data_ini
    if data_fim:
        filtro &= df['data_emissao'] <= data_fim
    return df[filtro]

def variacao(atual, anterior):
    '''Variação percentual do atual sobre o anterior (None se não houver base de comparação).'''

    if atual is None or anterior is None or anterior == 0:
        return None
    return (atual - anterior) / abs(anterior) * 100

def _resumo(posicao):
    df = posicao['contratos']
    novos = _contratado(df, posicao['data_ini'], posicao['data_fim'])
    return {
        'saldo_devedor': float(df['saldo_devedor'].sum()),
        'servico_periodo': float(df['servico_periodo'].sum()),
        'juros_periodo': float(df['juros_periodo'].sum()),
        'contratado_periodo': float(novos['valor_financiado'].sum()),
        'taxa_media': taxa_ponderada(df[df['ativo']], 'saldo_devedor'),
    }

def resumir_indicadores(dados):
    '''Indicadores dos cartões: valor atual, do ano anterior e variação (valores numéricos, antes da formatação).'''

    atual, anterior = _resumo(dados['atual']), _resumo(dados['anterior'])

    cartoes = {}
    for chave in ['saldo_devedor', 'servico_periodo', 'juros_periodo', 'contratado_periodo']:
        cartoes[chave] = {'atual': atual[chave], 'anterior': anterior[chave], 'variacao': variacao(atual[chave], anterior[chave])}

    # taxa: diferença em pontos percentuais
    ta, tb = atual['taxa_media'], anterior['taxa_media']
    cartoes['taxa_media'] = {'atual': ta, 'anterior': tb, 'variacao': None if ta is None or tb is None else ta - tb}

    return {'cartoes': cartoes}

def _agrupar(df, coluna):
    linhas = {
        chave: {
            'saldo_devedor': float(grupo['saldo_devedor'].sum()),
            'servico_periodo': float(grupo['servico_periodo'].sum()),
            'taxa_media': taxa_ponderada(grupo[grupo['ativo']], 'saldo_devedor'),
        }
        for chave, grupo in df.groupby(coluna)
    }
    return pd.DataFrame.from_dict(linhas, orient='index', columns=['saldo_devedor', 'servico_periodo', 'taxa_media']).rename_axis(coluna)

def agrupar_indicadores(dados, coluna):
    '''Indicadores por empresa/banco/tipo (coluna) com a variação sobre o ano anterior, ordenados pelo saldo.'''

    atual = _agrupar(dados['atual']['contratos'], coluna)
    anterior = _agrupar(dados['anterior']['contratos'], coluna)
    if atual.empty:
        return pd.DataFrame()

    df = atual.join(anterior, rsuffix='_anterior', how='left')
    df[['saldo_devedor_anterior', 'servico_periodo_anterior']] = df[['saldo_devedor_anterior', 'servico_periodo_anterior']].fillna(0.0)
    saldo_total, servico_total = df['saldo_devedor'].sum(), df['servico_periodo'].sum()
    df['participacao'] = df['saldo_devedor'] / saldo_total * 100 if saldo_total > 0 else 0.0
    df['participacao_servico'] = df['servico_periodo'] / servico_total * 100 if servico_total > 0 else 0.0
    df['var_saldo'] = [variacao(a, b) for a, b in zip(df['saldo_devedor'], df['saldo_devedor_anterior'])]
    df['var_servico'] = [variacao(a, b) for a, b in zip(df['servico_periodo'], df['servico_periodo_anterior'])]

    return (df.reset_index()
            .sort_values('saldo_devedor', ascending=False)
            [[coluna, 'saldo_devedor', 'var_saldo', 'participacao', 'servico_periodo', 'var_servico', 'taxa_media',
              'saldo_devedor_anterior', 'servico_periodo_anterior', 'participacao_servico']])

def servico_mensal_comparado(dados):
    '''Fluxo de pagamentos por mês: período atual x mesmo mês do ano anterior (formato longo para o gráfico).

    `mes` = mês do período atual (AAAA-MM); o ano anterior é alinhado somando um ano.
    '''

    atual, anterior = dados['atual'], dados['anterior']
    mesmo_ano = atual['data_ini'] and atual['data_fim'] and atual['data_ini'].year == atual['data_fim'].year
    rotulo_atual = str(atual['data_ini'].year) if mesmo_ano else 'Período atual'
    rotulo_anterior = str(anterior['data_ini'].year) if mesmo_ano else 'Ano anterior'

    partes = []
    for posicao, rotulo, deslocamento in ((anterior, rotulo_anterior, 1), (atual, rotulo_atual, 0)):
        df = posicao['mensal']
        if df.empty:
            continue
        meses = pd.to_datetime(df['mes']) + pd.DateOffset(years=deslocamento)
        partes.append(pd.DataFrame({'mes': meses.dt.strftime('%Y-%m'), 'serie': rotulo, 'servico': df['servico'].values}))

    if not partes:
        return pd.DataFrame(columns=['mes', 'serie', 'servico']), [rotulo_anterior, rotulo_atual]
    return pd.concat(partes, ignore_index=True), [rotulo_anterior, rotulo_atual]
