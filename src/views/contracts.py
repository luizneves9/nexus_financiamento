import streamlit as st
from services.contracts import listar_contratos, visualizar_projecao
from views.components.modal_contracts_incluir import modal_incluir_contrato
from views.components.modal_contracts_excluir import modal_excluir_contrato
from views.components.modal_quitacao_antecipacao import modal_quitacao_antecipacao
from views.components.modal_contracts_detalhe import modal_detalhe_contrato
from views.components.cabecalho import cabecalho

def excluir_contrato(linha_selecionada):
    '''Funcionalidade de controle para excluir um contrato do banco de dados.'''

    # validando quantidade selecionada (deve ser um)
    if len(linha_selecionada) != 1:
        st.session_state['mensagem_erro'] = 'Selecione um registro!'
        return

    # selecionando registro
    linha = linha_selecionada.iloc[0].copy()

    # abrindo o modal de confirmação
    modal_excluir_contrato(linha)

def abrir_modal_antecipacao(linha_selecionada):
    '''Funcionalidade para abrir o modal de quitação/antecipação.'''

    # validando quantidade selecionada (deve ser um)
    if len(linha_selecionada) != 1:
        st.session_state['mensagem_erro'] = 'Selecione um registro!'
        return

    # selecionando registro
    linha = linha_selecionada.iloc[0].copy()

    # abrindo o modal de quitação/antecipação
    modal_quitacao_antecipacao(linha)

def abrir_detalhe(linha_selecionada):
    '''Funcionalidade para abrir o detalhe do contrato (abas Dados, Contrato, Ficha Financeira e Histórico).'''

    # validando quantidade selecionada (deve ser um)
    if len(linha_selecionada) != 1:
        st.session_state['mensagem_erro'] = 'Selecione um registro!'
        return

    # abrindo o detalhe do contrato
    modal_detalhe_contrato(linha_selecionada.iloc[0].copy())

def transformar_float_em_str(valor):
    '''Função para transformar valores em formato brasileiro.'''

    if isinstance(valor, str):
        return str

    if isinstance(valor, (float, int)):
        return f'{valor:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.')

def main():

    # cabeçalho padrão da tela (ícone do grupo no menu)
    cabecalho('Gestão de Contratos', 'Controle detalhado dos contratos de financiamento.', 'request_quote')

    # inicializar session_states dos filtros (FC = Filtro Contratos)
    if 'fc_empresa' not in st.session_state:
        st.session_state['fc_empresa'] = None
    if 'fc_banco' not in st.session_state:
        st.session_state['fc_banco'] = None
    if 'fc_contrato' not in st.session_state:
        st.session_state['fc_contrato'] = None
    if 'fc_sem_anexos' not in st.session_state:
        st.session_state['fc_sem_anexos'] = False

    # inicializar session_states dos widgets a partir dos filtros salvos
    # (o widget usa key própria; passar value= dinâmico recria o widget e descarta o que foi digitado)
    if 'fc_empresa_input' not in st.session_state:
        st.session_state['fc_empresa_input'] = st.session_state['fc_empresa'] or ''
    if 'fc_banco_input' not in st.session_state:
        st.session_state['fc_banco_input'] = st.session_state['fc_banco'] or ''
    if 'fc_contrato_input' not in st.session_state:
        st.session_state['fc_contrato_input'] = st.session_state['fc_contrato'] or ''
    if 'fc_sem_anexos_input' not in st.session_state:
        st.session_state['fc_sem_anexos_input'] = st.session_state['fc_sem_anexos']

    # lista de filtros
    with st.form('gestao_contratos_filtro'):
        with st.container(horizontal=True, vertical_alignment='bottom'):
            empresa = st.text_input('Empresa', key='fc_empresa_input')
            banco = st.text_input('Banco', key='fc_banco_input')
            contrato = st.text_input('Contrato', key='fc_contrato_input')
            sem_anexos = st.checkbox('Somente sem anexos', key='fc_sem_anexos_input',
                                     help='Contratos sem anexo de contrato ou sem anexo de ficha financeira.')
            submitido = st.form_submit_button('Filtrar', use_container_width=True)

        if submitido:
            st.session_state['fc_empresa'] = empresa if empresa else None
            st.session_state['fc_banco'] = banco if banco else None
            st.session_state['fc_contrato'] = contrato if contrato else None
            st.session_state['fc_sem_anexos'] = sem_anexos

    # listando contratos com filtros
    with st.spinner('Consultando contratos...'):
        df_contratos = listar_contratos(
            empresa=st.session_state.get('fc_empresa'),
            banco=st.session_state.get('fc_banco'),
            contrato=st.session_state.get('fc_contrato'),
            sem_anexos=st.session_state.get('fc_sem_anexos')
        )

    if df_contratos.empty:
        if 'mensagem_erro' in st.session_state:
            st.error(st.session_state.pop('mensagem_erro'))
        else:
            st.warning('Nenhum contrato encontrado com os filtros aplicados.')
        return

    # definindo formato
    if 'Juros' in df_contratos.columns:
        df_contratos['Juros'] = df_contratos['Juros'].astype(str).str.replace('.', ',').str.ljust(4, '0') + '%'
    if 'Valor' in df_contratos.columns:
        df_contratos['Valor'] = df_contratos['Valor'].map(transformar_float_em_str)

    # inclusão da opção de seleção
    df_contratos.insert(0, 'sel', False)

    # visualização do dataframe
    df_visual = st.data_editor(
        df_contratos,
        hide_index=True,
        column_config={
            'Data de Emissão': st.column_config.DateColumn('Data', format='DD/MM/YYYY'),
            'Vencimento final': st.column_config.DateColumn('Vencimento', format='DD/MM/YYYY'),
            'anexo_contrato': st.column_config.CheckboxColumn('Anexo contrato', help='Possui PDF do contrato', disabled=True),
            'anexo_ficha': st.column_config.CheckboxColumn('Anexo ficha', help='Possui PDF da ficha financeira', disabled=True),
            'sel': st.column_config.CheckboxColumn('', default=False)
        }
    )

    # botões de interação
    with st.container(horizontal=True):
        if st.button('Novo'): modal_incluir_contrato()
        if st.button('Detalhes'): abrir_detalhe(df_visual[df_visual['sel'] == True])
        if st.button('Projeção'): visualizar_projecao(df_visual[df_visual['sel'] == True])
        if st.button('Quitação/Antecipação'): abrir_modal_antecipacao(df_visual[df_visual['sel'] == True])
        if st.button('Excluir'): excluir_contrato(df_visual[df_visual['sel'] == True])

    if 'mensagem_sucesso' in st.session_state:
        st.toast(st.session_state.pop('mensagem_sucesso'), icon='✅')

    if 'mensagem_erro' in st.session_state:
        st.toast(st.session_state.pop('mensagem_erro'), icon='⚠️')

if __name__ == '__main__':
    main()