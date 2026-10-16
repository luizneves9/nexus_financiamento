import streamlit as st
from services.include_antecipation import excluir_antecipacao_banco

@st.dialog('Excluir lançamento', dismissible=False)
def modal_excluir_antecipacao(linha):
    '''Modal de confirmação da exclusão de antecipação/quitação.'''
    st.markdown('*Tem certeza que deseja excluir o lançamento abaixo? A projeção do contrato será recalculada.*')

    # visualização de informações
    c1, c2, c3 = st.columns([1, 1, 1])
    c4, c5 = st.columns([1, 1])
    c6, c7 = st.columns([1, 1])
    c1.text_input('Id', value=linha['id'], disabled=True)
    c2.text_input('Contrato', value=linha['numero_contrato'], disabled=True)
    c3.text_input('Tipo', value=linha['tipo_lancamento'], disabled=True)
    c4.text_input('Empresa', value=linha['nome_empresa'], disabled=True)
    c5.text_input('Banco', value=linha['banco'], disabled=True)
    c6.text_input('Data de pagamento', value=linha['data_pagamento'].strftime('%d/%m/%Y'), disabled=True)
    c7.text_input('Valor', value=linha['valor_pago'], disabled=True)

    # botão de confirmação ou cancelamento
    col_confirmar, col_cancelar = st.columns(2)

    with col_confirmar:
        if st.button('Confirmar', type='primary', use_container_width=True):
            excluir_antecipacao_banco(int(linha['id']))
            st.rerun()

    with col_cancelar:
        if st.button('Cancelar', use_container_width=True):
            st.rerun()
