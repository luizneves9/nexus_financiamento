import streamlit as st

@st.dialog('Projeção de Valores', width='small')
def modal_projecao_valores(df, linha):
    '''Modal para visualizar a projeção dos valores financiados.'''

    with st.container(horizontal=True):
        st.markdown(f'**Contrato:** {linha['Contrato']}')
        st.markdown(f'**Banco:** {linha['Banco']}'.title())

    st.dataframe(df, hide_index=True)
