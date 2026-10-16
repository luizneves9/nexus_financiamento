import altair as alt
import pandas as pd
import streamlit as st
from datetime import date
from services.indicadores import (
    consultar_indicadores,
    resumir_indicadores,
    agrupar_indicadores,
    servico_mensal_comparado,
)
from tools.funcoes import transformar_float_em_str, listar_empresas, listar_bancos
from views.components.cabecalho import cabecalho

MESES = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']
CORES_ANOS = ['#94A3B8', '#6366F1']        # ano anterior (cinza), ano atual (índigo da identidade visual)

# cartões: (chave do resumo, título, cor do delta, definição)
# delta 'inverse': queda aparece em verde (saldo, juros e taxa menores são melhores); 'off': sem juízo de valor
CARTOES = [
    ('saldo_devedor', 'Saldo devedor', 'inverse', 'Principal das parcelas a vencer na data base.'),
    ('servico_periodo', 'Fluxo de pagamentos', 'off', 'Parcelas, antecipações e quitações com vencimento útil no período: valor pago, se liquidado até a data base; senão, o projetado.'),
    ('juros_periodo', 'Juros no período', 'inverse', 'Juros das parcelas com vencimento útil no período.'),
    ('contratado_periodo', 'Contratado no período', 'off', 'Valor financiado dos contratos emitidos no período.'),
]

# cartões compactos (só nesta tela, pelo container key='fi_cartoes'): valor e título menores, faixa índigo à
# esquerda para destacar, valor sem reticências
ESTILO_CARTOES = '''
    <style>
        .st-key-fi_cartoes [data-testid="stMetric"] { padding: 0; border-left: 3px solid #6366F1 !important; }
        .st-key-fi_cartoes [data-testid="stMetric"] > div { padding: 0.55rem 0.9rem; }
        .st-key-fi_cartoes [data-testid="stMetricLabel"] p { font-size: 0.8rem; }
        .st-key-fi_cartoes [data-testid="stMetricValue"] { font-size: 1.35rem; }
        .st-key-fi_cartoes [data-testid="stMetricValue"] > div { overflow: visible; text-overflow: clip; }
        .st-key-fi_cartoes [data-testid="stMetricDelta"] { font-size: 0.75rem; }
    </style>
'''

# rótulo do agrupamento da composição (balão do gráfico) e opções do seletor
ROTULOS_AGRUPAMENTO = {'nome_empresa': 'Empresa', 'banco': 'Banco', 'tipo_contrato': 'Tipo'}
AGRUPAMENTOS = {'Empresas': 'nome_empresa', 'Bancos': 'banco', 'Tipo de contrato': 'tipo_contrato'}

# gráficos lado a lado: título numa linha de altura fixa, a mesma legenda e a mesma altura de gráfico nos
# dois, para alinharem em cima e embaixo
ALTURA_TITULO = 52
ALTURA_GRAFICO = 380

def numero_br(valor, casas):
    return f'{valor:,.{casas}f}'.replace(',', 'v').replace('.', ',').replace('v', '.')

def milhoes(valor):
    '''Valor em milhões com 3 casas (padrão do relatório de Endividamento): R$ 248,165 Mi.'''
    return f'R$ {numero_br(valor / 1_000_000, 3)} Mi'

def percentual(valor):
    return '—' if valor is None or pd.isna(valor) else f'{numero_br(valor, 2)}%'

def variacao_txt(valor):
    return '—' if valor is None or pd.isna(valor) else f'{valor:+.1f}%'.replace('.', ',')

def cartoes(resumo, ano, ano_anterior):
    '''Linha de cartões com o valor atual e a variação sobre o mesmo período do ano anterior.'''

    # colunas fixas (os cinco na mesma linha); todo cartão tem a linha de variação (sem base de comparação,
    # mostra "sem base" em cinza), então todos ficam com a mesma altura
    st.html(ESTILO_CARTOES)
    colunas = st.container(key='fi_cartoes').columns(len(CARTOES) + 1)
    comparacao = f'vs {ano_anterior}'

    for coluna, (chave, titulo, cor, definicao) in zip(colunas, CARTOES):
        c = resumo['cartoes'][chave]
        sem_base = c['variacao'] is None
        anterior_mi = milhoes(c['anterior']).replace('$', r'\$')      # dois "$" no help viram fórmula LaTeX
        coluna.metric(
            titulo, milhoes(c['atual']),
            delta='sem base' if sem_base else variacao_txt(c['variacao']), delta_description=comparacao,
            delta_color='off' if sem_base else cor, delta_arrow='off' if sem_base else 'auto',
            border=True,
            help=f"{definicao}  \n{ano}: R\\$ {transformar_float_em_str(c['atual'])}  \n"
                 f"{ano_anterior}: R\\$ {transformar_float_em_str(c['anterior'])} ({anterior_mi})"
        )

    t = resumo['cartoes']['taxa_media']
    sem_base = t['variacao'] is None
    colunas[-1].metric(
        'Taxa média ponderada', percentual(t['atual']),
        delta='sem base' if sem_base else f"{t['variacao']:+.2f}".replace('.', ',') + ' p.p.', delta_description=comparacao,
        delta_color='off' if sem_base else 'inverse', delta_arrow='off' if sem_base else 'auto',
        border=True,
        help=f"Taxa de juros efetiva dos contratos ativos, ponderada pelo saldo devedor.  \n"
             f"{ano}: {percentual(t['atual'])}  \n{ano_anterior}: {percentual(t['anterior'])}"
    )

def grafico_servico(dados):
    '''Fluxo de pagamentos por mês: ano atual x ano anterior, barras lado a lado (eixo em R$ Mi, formato brasileiro).'''

    df, series = servico_mensal_comparado(dados)
    if df.empty:
        st.info('Sem parcelas no período.')
        return

    df['valor_mi'] = df['servico'] / 1_000_000
    df['valor_txt'] = df['servico'].map(milhoes)
    df['rotulo'] = df['mes'].map(lambda m: MESES[int(m[5:7]) - 1])
    if df['mes'].str[:4].nunique() > 1:          # período com mais de um ano: mostra o ano no rótulo
        df['rotulo'] = df['rotulo'] + '/' + df['mes'].str[2:4]
    ordem = df.sort_values('mes')['rotulo'].drop_duplicates().to_list()

    grafico = alt.Chart(df).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
        x=alt.X('rotulo:N', sort=ordem, title=None, axis=alt.Axis(labelAngle=0)),
        xOffset=alt.XOffset('serie:N', sort=series),
        y=alt.Y('valor_mi:Q', title='R$ Mi', axis=alt.Axis(labelExpr="replace(format(datum.value, ',.0f'), /,/g, '.')")),
        color=alt.Color('serie:N', sort=series, scale=alt.Scale(domain=series, range=CORES_ANOS), legend=None),
        tooltip=[alt.Tooltip('rotulo:N', title='Mês'), alt.Tooltip('serie:N', title='Ano'), alt.Tooltip('valor_txt:N', title='Fluxo de pagamentos')],
    ).properties(height=ALTURA_GRAFICO)

    legenda(series)
    st.altair_chart(grafico, width='stretch')

def grafico_composicao(df, coluna, series):
    '''Barras horizontais por empresa/banco/tipo: fluxo de pagamentos do ano anterior x ano atual.

    Rótulo da barra do ano atual: valor, participação no fluxo e variação; saldo e taxa no balão.
    '''

    ano_anterior, ano = series
    ordem = df.sort_values('servico_periodo', ascending=False)[coluna].to_list()

    linhas = []
    for _, g in df.iterrows():
        comum = {
            'nome': g[coluna],
            'saldo_txt': milhoes(g['saldo_devedor']),
            'var_saldo_txt': variacao_txt(g['var_saldo']),
            'var_fluxo_txt': variacao_txt(g['var_servico']),
            'taxa_txt': percentual(g['taxa_media']),
        }
        anterior, atual = g['servico_periodo_anterior'], g['servico_periodo']
        linhas.append({**comum, 'serie': ano_anterior, 'valor_mi': anterior / 1_000_000,
                       'valor_txt': milhoes(anterior), 'rotulo': f"{numero_br(anterior / 1_000_000, 3)} Mi"})
        linhas.append({**comum, 'serie': ano, 'valor_mi': atual / 1_000_000, 'valor_txt': milhoes(atual),
                       'rotulo': f"{numero_br(atual / 1_000_000, 3)} Mi · {numero_br(g['participacao_servico'], 1)}% · {variacao_txt(g['var_servico'])}"})
    dados_grafico = pd.DataFrame(linhas)

    # folga à direita para os rótulos não serem cortados
    maximo = max(dados_grafico['valor_mi'].max(), 0.001) * 1.7

    base = alt.Chart(dados_grafico).encode(
        y=alt.Y('nome:N', sort=ordem, title=None, axis=alt.Axis(labelLimit=170)),
        yOffset=alt.YOffset('serie:N', sort=series),
        x=alt.X('valor_mi:Q', title=None, axis=None, scale=alt.Scale(domain=[0, maximo])),
        tooltip=[
            alt.Tooltip('nome:N', title=ROTULOS_AGRUPAMENTO[coluna]),
            alt.Tooltip('serie:N', title='Ano'),
            alt.Tooltip('valor_txt:N', title='Fluxo de pagamentos'),
            alt.Tooltip('var_fluxo_txt:N', title='Δ fluxo'),
            alt.Tooltip('saldo_txt:N', title=f'Saldo devedor {ano}'),
            alt.Tooltip('var_saldo_txt:N', title='Δ saldo'),
            alt.Tooltip('taxa_txt:N', title='Taxa média'),
        ],
    )
    barras = base.mark_bar(cornerRadiusTopRight=3, cornerRadiusBottomRight=3).encode(
        color=alt.Color('serie:N', sort=series, scale=alt.Scale(domain=series, range=CORES_ANOS), legend=None),
    )
    rotulos = base.mark_text(align='left', dx=4, fontSize=12, color='#94A3B8').encode(text='rotulo:N')

    # mesma altura do gráfico do fluxo (no Streamlit a altura já inclui os eixos); muitas categorias só afinam as barras
    legenda(series)
    st.altair_chart((barras + rotulos).properties(height=ALTURA_GRAFICO), width='stretch')

def legenda(series):
    '''Legenda dos anos em HTML, igual nos dois gráficos: a legenda interna do Altair ocupava alturas diferentes
    em cada gráfico e desalinhava as áreas de dados.'''

    itens = ''.join(
        f"<span style='display:inline-flex; align-items:center; gap:0.35rem; margin-right:1rem;'>"
        f"<span style='width:0.7rem; height:0.7rem; border-radius:2px; background:{cor};'></span>{rotulo}</span>"
        for rotulo, cor in zip(series, CORES_ANOS)
    )
    st.markdown(f"<div style='font-size:0.85rem; line-height:1.2rem;'>{itens}</div>", unsafe_allow_html=True)

def linha_titulo(titulo):
    '''Linha de título de altura fixa (alinha os dois gráficos lado a lado); devolve o container para controles.'''

    # 'distribute': título à esquerda e controle (se houver) encostado à direita; sem quebra de linha
    linha = st.container(horizontal=True, horizontal_alignment='distribute', vertical_alignment='center',
                         wrap=False, height=ALTURA_TITULO, border=False)
    linha.subheader(titulo, anchor=False)
    return linha

@st.fragment
def composicao(dados, series):
    '''Composição da dívida: fluxo de pagamentos por empresa, banco ou tipo de contrato.

    Fragmento: trocar o agrupamento redesenha só este bloco, sem consultar o banco de novo.
    '''

    if st.session_state.get('fi_agrupamento') not in AGRUPAMENTOS:
        st.session_state['fi_agrupamento'] = 'Empresas'

    # seletor na linha do título (no lugar de abas): o gráfico começa na mesma altura do gráfico do fluxo
    linha = linha_titulo('Composição da dívida')
    with linha:
        agrupamento = st.segmented_control('Agrupar por', list(AGRUPAMENTOS), key='fi_agrupamento',
                                           required=True, label_visibility='collapsed')

    coluna = AGRUPAMENTOS[agrupamento]
    df = agrupar_indicadores(dados, coluna)
    if df.empty:
        st.info('Sem dados para os filtros aplicados.')
        return
    grafico_composicao(df, coluna, series)

def main():

    # cabeçalho padrão da tela (ícone do grupo no menu)
    cabecalho('Indicadores', 'Posição da dívida na data base, comparada ao mesmo período do ano anterior.', 'dashboard')

    # inicializar session_states dos filtros (FI = Filtro Indicadores); padrão: do início do ano até hoje
    hoje = date.today()
    if 'fi_data_base' not in st.session_state:
        st.session_state['fi_data_base'] = hoje
    if 'fi_data_ini' not in st.session_state:
        st.session_state['fi_data_ini'] = date(hoje.year, 1, 1)
    if 'fi_data_fim' not in st.session_state:
        st.session_state['fi_data_fim'] = hoje
    if 'fi_empresa' not in st.session_state:
        st.session_state['fi_empresa'] = None
    if 'fi_banco' not in st.session_state:
        st.session_state['fi_banco'] = None

    # opções dos filtros de seleção (mesmo cache de cadastros usado no modal de inclusão de contrato)
    if st.session_state.get('df_lista_empresas') is None:
        st.session_state['df_lista_empresas'] = listar_empresas()
    if st.session_state.get('df_lista_bancos') is None:
        st.session_state['df_lista_bancos'] = listar_bancos()

    df_empresas = st.session_state['df_lista_empresas']
    df_bancos = st.session_state['df_lista_bancos']
    opcoes_empresas = ['Todos'] + (df_empresas['razao_social'].to_list() if df_empresas is not None and 'razao_social' in df_empresas else [])
    opcoes_bancos = ['Todos'] + (df_bancos['razao_social'].to_list() if df_bancos is not None and 'razao_social' in df_bancos else [])

    # inicializar session_states dos widgets a partir dos filtros salvos
    # (o widget usa key própria; passar value= dinâmico recria o widget e descarta o que foi digitado)
    if 'fi_data_base_input' not in st.session_state:
        st.session_state['fi_data_base_input'] = st.session_state['fi_data_base']
    if 'fi_data_ini_input' not in st.session_state:
        st.session_state['fi_data_ini_input'] = st.session_state['fi_data_ini']
    if 'fi_data_fim_input' not in st.session_state:
        st.session_state['fi_data_fim_input'] = st.session_state['fi_data_fim']
    if st.session_state.get('fi_empresa_input') not in opcoes_empresas:
        st.session_state['fi_empresa_input'] = st.session_state['fi_empresa'] if st.session_state['fi_empresa'] in opcoes_empresas else 'Todos'
    if st.session_state.get('fi_banco_input') not in opcoes_bancos:
        st.session_state['fi_banco_input'] = st.session_state['fi_banco'] if st.session_state['fi_banco'] in opcoes_bancos else 'Todos'

    # lista de filtros
    with st.form('indicadores_filtro'):
        with st.container(horizontal=True, vertical_alignment='bottom'):
            data_base = st.date_input('Data base', key='fi_data_base_input', format='DD/MM/YYYY')
            data_ini = st.date_input('Período de', key='fi_data_ini_input', format='DD/MM/YYYY')
            data_fim = st.date_input('Período até', key='fi_data_fim_input', format='DD/MM/YYYY')
            empresa = st.selectbox('Empresa', opcoes_empresas, key='fi_empresa_input')
            banco = st.selectbox('Banco', opcoes_bancos, key='fi_banco_input')
            submitido = st.form_submit_button('Filtrar', use_container_width=True)

        if submitido:
            st.session_state['fi_data_base'] = data_base or hoje
            st.session_state['fi_data_ini'] = data_ini
            st.session_state['fi_data_fim'] = data_fim
            st.session_state['fi_empresa'] = None if empresa == 'Todos' else empresa
            st.session_state['fi_banco'] = None if banco == 'Todos' else banco

    # consultando o período atual e o mesmo período do ano anterior
    with st.spinner('Consultando indicadores...'):
        dados = consultar_indicadores(
            st.session_state['fi_data_base'],
            data_ini=st.session_state['fi_data_ini'],
            data_fim=st.session_state['fi_data_fim'],
            empresa=st.session_state.get('fi_empresa'),
            banco=st.session_state.get('fi_banco')
        )

    if dados is None:
        st.error(st.session_state.pop('mensagem_erro', 'Erro ao consultar os indicadores.'))
        return
    if dados['atual']['contratos'].empty:
        st.warning('Nenhum contrato encontrado com os filtros aplicados.')
        return

    atual, anterior = dados['atual'], dados['anterior']
    ano, ano_anterior = atual['data_base'].year, anterior['data_base'].year

    # indicadores calculados antes da formatação (valores ainda numéricos)
    resumo = resumir_indicadores(dados)

    # 1. cartões comparados ao ano anterior
    cartoes(resumo, ano, ano_anterior)

    # 2 e 3 lado a lado: fluxo de pagamentos por mês (ano atual x anterior) e composição; mesmo espaçamento das
    # colunas dos cartões, para as bordas externas dos gráficos alinharem com as dos cartões
    col_fluxo, col_composicao = st.columns(2)

    with col_fluxo:
        linha_titulo('Fluxo de pagamentos por mês')
        grafico_servico(dados)

    with col_composicao:
        composicao(dados, [str(ano_anterior), str(ano)])

    if 'mensagem_erro' in st.session_state:
        st.toast(st.session_state.pop('mensagem_erro'), icon='⚠️')

if __name__ == '__main__':
    main()
