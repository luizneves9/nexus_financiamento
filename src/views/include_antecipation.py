import calendar
from datetime import date
import streamlit as st
from services.include_antecipation import listar_antecipacoes, resumir_antecipacoes
from tools.funcoes import transformar_float_em_str, listar_empresas, listar_bancos
from views.components.cabecalho import cabecalho
from views.components.modal_antecipacao_excluir import modal_excluir_antecipacao

def excluir_antecipacao(linha_selecionada):
    '''Funcionalidade de controle para excluir uma antecipação/quitação.'''

    # validando quantidade selecionada (deve ser um)
    if len(linha_selecionada) != 1:
        st.session_state['mensagem_erro'] = 'Selecione um registro!'
        return

    # selecionando registro
    linha = linha_selecionada.iloc[0].copy()

    # abrindo o modal de confirmação
    modal_excluir_antecipacao(linha)

def main():

    # cabeçalho padrão da tela (ícone do grupo no menu)
    cabecalho('Antecipações', 'Visualização das antecipações e quitações registradas nos contratos.', 'request_quote')

    # inicializar session_states dos filtros (FA = Filtro Antecipação)
    if 'fa_empresa' not in st.session_state:
        st.session_state['fa_empresa'] = None
    if 'fa_banco' not in st.session_state:
        st.session_state['fa_banco'] = None
    if 'fa_contrato' not in st.session_state:
        st.session_state['fa_contrato'] = None
    # período de pagamento começa no mês atual
    hoje = date.today()
    if 'fa_data_pagamento_ini' not in st.session_state:
        st.session_state['fa_data_pagamento_ini'] = hoje.replace(day=1)
    if 'fa_data_pagamento_fim' not in st.session_state:
        st.session_state['fa_data_pagamento_fim'] = hoje.replace(day=calendar.monthrange(hoje.year, hoje.month)[1])

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
    if st.session_state.get('fa_empresa_input') not in opcoes_empresas:
        st.session_state['fa_empresa_input'] = st.session_state['fa_empresa'] if st.session_state['fa_empresa'] in opcoes_empresas else 'Todos'
    if st.session_state.get('fa_banco_input') not in opcoes_bancos:
        st.session_state['fa_banco_input'] = st.session_state['fa_banco'] if st.session_state['fa_banco'] in opcoes_bancos else 'Todos'
    if 'fa_contrato_input' not in st.session_state:
        st.session_state['fa_contrato_input'] = st.session_state['fa_contrato'] or ''
    if 'fa_data_pagamento_ini_input' not in st.session_state:
        st.session_state['fa_data_pagamento_ini_input'] = st.session_state['fa_data_pagamento_ini']
    if 'fa_data_pagamento_fim_input' not in st.session_state:
        st.session_state['fa_data_pagamento_fim_input'] = st.session_state['fa_data_pagamento_fim']

    # lista de filtros
    with st.form('antecipacoes_filtro'):
        with st.container(horizontal=True, vertical_alignment='bottom'):
            empresa = st.selectbox('Empresa', opcoes_empresas, key='fa_empresa_input')
            banco = st.selectbox('Banco', opcoes_bancos, key='fa_banco_input')
            contrato = st.text_input('Contrato', key='fa_contrato_input')
            data_pagamento_ini = st.date_input('Pagamento de', key='fa_data_pagamento_ini_input', format='DD/MM/YYYY')
            data_pagamento_fim = st.date_input('Pagamento até', key='fa_data_pagamento_fim_input', format='DD/MM/YYYY')
            submitido = st.form_submit_button('Filtrar', use_container_width=True)

        if submitido:
            st.session_state['fa_empresa'] = None if empresa == 'Todos' else empresa
            st.session_state['fa_banco'] = None if banco == 'Todos' else banco
            st.session_state['fa_contrato'] = contrato if contrato else None
            st.session_state['fa_data_pagamento_ini'] = data_pagamento_ini
            st.session_state['fa_data_pagamento_fim'] = data_pagamento_fim

    # listando antecipações com filtros
    with st.spinner('Consultando antecipações...'):
        df_antecipacoes = listar_antecipacoes(
            empresa=st.session_state.get('fa_empresa'),
            banco=st.session_state.get('fa_banco'),
            contrato=st.session_state.get('fa_contrato'),
            data_pagamento_ini=st.session_state.get('fa_data_pagamento_ini'),
            data_pagamento_fim=st.session_state.get('fa_data_pagamento_fim')
        )

    if df_antecipacoes.empty:
        st.warning('Nenhuma antecipação encontrada com os filtros aplicados.')
        return

    # resumo calculado antes da formatação (valores ainda numéricos)
    resumo = resumir_antecipacoes(df_antecipacoes)

    # definindo formato
    df_antecipacoes['valor_pago'] = df_antecipacoes['valor_pago'].map(transformar_float_em_str)

    # inclusão da opção de seleção
    df_antecipacoes.insert(0, 'sel', False)

    # visualização do dataframe
    df_visual = st.data_editor(
        df_antecipacoes,
        width='content',
        hide_index=True,
        column_config={
            'sel': st.column_config.CheckboxColumn('', default=False),
            'data_pagamento': st.column_config.DateColumn(format='DD/MM/YYYY'),
        }
    )

    # botões de interação
    with st.container(horizontal=True):
        if st.button('Excluir'): excluir_antecipacao(df_visual[df_visual['sel'] == True])

    # resumo de valores
    st.caption(
        f"**Empresas:** {resumo['empresas']}&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"**Bancos:** {resumo['bancos']}&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"**Contratos:** {resumo['contratos']}&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"**Total pago:** R$ {transformar_float_em_str(resumo['valor_pago'])}",
        unsafe_allow_html=True
    )

    if 'mensagem_sucesso' in st.session_state:
        st.toast(st.session_state.pop('mensagem_sucesso'), icon='✅')

    if 'mensagem_erro' in st.session_state:
        st.toast(st.session_state.pop('mensagem_erro'), icon='⚠️')

if __name__ == '__main__':
    main()
