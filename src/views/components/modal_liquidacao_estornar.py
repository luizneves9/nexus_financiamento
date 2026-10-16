import streamlit as st
from services.liquidacao import estornar_liquidacoes

@st.dialog('Estornar liquidação', width='large', dismissible=False)
def modal_liquidacao_estornar(linhas):
    '''Modal de estorno das liquidações selecionadas (motivo obrigatório).'''

    st.markdown('*As parcelas abaixo voltarão a ABERTA e os contratos serão recalculados.*')

    # visualização das liquidações selecionadas (valores já formatados na tela)
    st.dataframe(
        linhas[['numero_contrato', 'parcela', 'data_pagamento', 'valor_pago', 'valor_ajuste', 'origem']],
        hide_index=True,
        column_config={
            'numero_contrato': 'Contrato',
            'parcela': 'Parcela',
            'data_pagamento': st.column_config.DateColumn('Data pagamento', format='DD/MM/YYYY'),
            'valor_pago': 'Valor pago',
            'valor_ajuste': 'Ajuste',
            'origem': 'Origem',
        }
    )

    motivo = st.text_area('Motivo do estorno', max_chars=500)

    # botão de confirmação ou cancelamento
    col_confirmar, col_cancelar = st.columns(2)

    with col_confirmar:
        if st.button('Confirmar', type='primary', use_container_width=True):
            if not motivo.strip():
                st.error('Informe o motivo do estorno.')
            else:
                estornar_liquidacoes([int(i) for i in linhas['id_liquidacao']], motivo.strip())
                st.rerun()

    with col_cancelar:
        if st.button('Cancelar', use_container_width=True):
            st.rerun()
