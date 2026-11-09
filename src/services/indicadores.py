import pandas as pd
import streamlit as st
from datetime import date
from sqlalchemy import text
from database.connection import ConexaoBancoSQL
from queries.queries_indicadores import SELECT_INDICADORES_CONTRATOS, SELECT_INDICADORES_POSICAO
from repositories.funcoes import ler_query

connect = ConexaoBancoSQL()
engine = connect.conexao_banco()

# colunas de valor do retorno por contrato (vêm como Decimal/objeto do banco)
COLUNAS_VALOR_CONTRATO = ['valor_financiado', 'taxa_juros_efetiva', 'saldo_devedor', 'servico_periodo', 'juros_periodo']

def trocar_ano(data, ano):
    '''Mesma data (dia e mês) em outro ano (29/02 vira 28/02).'''

    if data is None:
        return None
    try:
        return data.replace(year=ano)
    except ValueError:
        return data.replace(year=ano, day=28)

def periodos_comparados(ano_x, ano_y, ano_base, hoje):
    '''Data base e período de cada lado da comparação Data X (anterior) x Data Y (atual).

    - período: ano inteiro (01/01 a 31/12); se um dos anos for o atual, os dois vão até o dia/mês de hoje
      (acumulado no ano, comparável entre os anos);
    - data base do lado Y: hoje se o ano da data base for o atual, senão 31/12; a do lado X é a mesma data
      deslocada pela diferença entre X e Y (as duas posições ficam à mesma distância de cada período).
    Devolve {'atual': (base, ini, fim), 'anterior': (base, ini, fim)}.'''

    parcial = hoje.year in (ano_x, ano_y)
    fim = (lambda ano: trocar_ano(hoje, ano)) if parcial else (lambda ano: date(ano, 12, 31))
    base_y = hoje if ano_base == hoje.year else date(ano_base, 12, 31)
    base_x = trocar_ano(base_y, base_y.year - (ano_y - ano_x))
    return {
        'atual': (base_y, date(ano_y, 1, 1), fim(ano_y)),
        'anterior': (base_x, date(ano_x, 1, 1), fim(ano_x)),
    }

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
    df_contratos['data_contabilizacao'] = pd.to_datetime(df_contratos['data_contabilizacao']).dt.date
    df_contratos['ativo'] = df_contratos['saldo_devedor'] > 0
    df_mensal['servico'] = pd.to_numeric(df_mensal['servico'], errors='coerce').fillna(0.0)

    return df_contratos, df_mensal

def consultar_indicadores(periodos, empresa=None, banco=None):
    '''Consulta o painel nos dois lados da comparação (periodos_comparados: 'atual' = Data Y, 'anterior' = Data X).

    Devolve um dicionário com 'atual' e 'anterior' (cada um: contratos, mensal, data_base, data_ini, data_fim);
    ou None em caso de erro (mensagem em session_state).
    '''

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
    '''Valor financiado dos contratos contabilizados no período.'''

    filtro = pd.Series(True, index=df.index)
    if data_ini:
        filtro &= df['data_contabilizacao'] >= data_ini
    if data_fim:
        filtro &= df['data_contabilizacao'] <= data_fim
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
    '''Indicadores dos cartões: valor de Y (atual), de X (anterior) e variação (valores numéricos, antes da formatação).'''

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
    '''Indicadores por empresa/banco/tipo (coluna) com a variação de Y sobre X, ordenados pelo saldo.'''

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
    '''Fluxo de pagamentos por mês: Data Y x mesmo mês de Data X (formato longo para o gráfico).

    `mes` = mês do período de Y (AAAA-MM); X é alinhado somando a diferença de anos entre Y e X.
    '''

    atual, anterior = dados['atual'], dados['anterior']
    rotulo_atual = str(atual['data_ini'].year)
    rotulo_anterior = str(anterior['data_ini'].year)
    diferenca = atual['data_ini'].year - anterior['data_ini'].year

    partes = []
    for posicao, rotulo, deslocamento in ((anterior, rotulo_anterior, diferenca), (atual, rotulo_atual, 0)):
        df = posicao['mensal']
        if df.empty:
            continue
        meses = pd.to_datetime(df['mes']) + pd.DateOffset(years=deslocamento)
        partes.append(pd.DataFrame({'mes': meses.dt.strftime('%Y-%m'), 'serie': rotulo, 'servico': df['servico'].values}))

    if not partes:
        return pd.DataFrame(columns=['mes', 'serie', 'servico']), [rotulo_anterior, rotulo_atual]
    return pd.concat(partes, ignore_index=True), [rotulo_anterior, rotulo_atual]
