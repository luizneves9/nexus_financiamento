import streamlit as st
from services.contracts import deletar_contrato_banco

@st.dialog('Excluir contrato', dismissible=False)
def modal_excluir_contrato(linha):
    '''Modal de confirmação da exclusão de contrato.'''
    st.markdown('*Tem certeza que deseja excluir o contrato abaixo?*')

    # visualização de informações
    c1, c2, c3 = st.columns([1, 1, 1])
    c4, c5 = st.columns([1, 1])
    c1.text_input('Id', value=linha['Id'], disabled=True)
    c2.text_input('Empresa', value=linha['Empresa'], disabled=True)
    c3.text_input('Valor', value=linha['Valor'], disabled=True)
    c4.text_input('Banco', value=linha['Banco'], disabled=True)
    c5.text_input('Contrato', value=linha['Contrato'], disabled=True)

    # botão de confirmação ou exclusão
    col_confirmar, col_cancelar = st.columns(2)

    with col_confirmar:
        if st.button('Confirmar', type='primary', use_container_width=True):
            try:
                deletar_contrato_banco(int(linha['Id']))
                st.rerun()
            except Exception as e:
                st.session_state['mensagem_erro'] = e
                st.rerun()

        with col_cancelar:
            if st.button('Cancelar', use_container_width=True):
                st.rerun()