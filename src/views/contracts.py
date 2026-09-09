import streamlit as st
from services.contracts import listar_contratos, visualizar_projecao
from views.components.modal_contracts_incluir import modal_incluir_contrato
from views.components.modal_contracts_excluir import modal_excluir_contrato

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

def transformar_float_em_str(valor):
    '''Função para transformar valores em formato brasileiro.'''

    if isinstance(valor, str):
        return str

    if isinstance(valor, (float, int)):
        return f'{valor:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.')

def main():

    # definindo o título da página
    st.markdown('''
        <h2 style='margin-bottom: 0px;'>Gestão de Contratos</h2>
        <p style='margin-top: -15px; color: #666; font-style: italic;'>
            Controle detalhado dos contratos de financiamento.
        </p>
        ''',
        unsafe_allow_html=True
    )

    # listando contratos
    df_contratos = listar_contratos()

    # definindo formato
    df_contratos['Juros'] = df_contratos['Juros'].astype(str).str.replace('.', ',').str.ljust(4, '0') + '%'
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
            'sel': st.column_config.CheckboxColumn('', default=False)
        }
    )

    # botões de interação
    with st.container(horizontal=True):
        if st.button('Novo'): modal_incluir_contrato()
        if st.button('Projeção'): visualizar_projecao(df_visual[df_visual['sel'] == True])
        if st.button('Excluir'): excluir_contrato(df_visual[df_visual['sel'] == True])

    if 'mensagem_sucesso' in st.session_state:
        st.toast(st.session_state.pop('mensagem_sucesso'), icon='✅')

    if 'mensagem_erro' in st.session_state:
        st.toast(st.session_state.pop('mensagem_erro'), icon='⚠️')

if __name__ == '__main__':
    main()