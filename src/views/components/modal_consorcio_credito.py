import streamlit as st
from services.consorcio import buscar_credito, salvar_credito, competencia_do_mes

@st.dialog('Créditos de consórcio', dismissible=False)
def modal_consorcio_credito(data_base_padrao):
    '''Modal de lançamento dos créditos de consórcio do fechamento do mês (inclui ou atualiza a competência).'''

    st.markdown('*Valores do fechamento do mês, em R$. Abatidos do total a pagar na Dívida Líquida do Endividamento.*')

    data = st.date_input('Competência', value=data_base_padrao, key='fco_cred_data', format='DD/MM/YYYY')
    competencia = competencia_do_mes(data)
    st.caption(f'Competência gravada: **{competencia:%m/%Y}**')

    # valores já lançados (key por competência: trocar o mês recarrega os valores gravados)
    atual = buscar_credito(competencia)
    if atual:
        st.info(f'Já existe lançamento para {competencia:%m/%Y}; confirmar atualiza os valores.')

    cotas = st.number_input(
        'Crédito Cotas Consórcios Contempladas (R$)', min_value=0.0, step=0.01, format='%.2f',
        value=float(atual['credito_cotas_contempladas']) if atual else 0.0, key=f'fco_cred_cotas_{competencia}')
    nao_contempladas = st.number_input(
        'Crédito Parcelas pagas e não contempladas (R$)', min_value=0.0, step=0.01, format='%.2f',
        value=float(atual['credito_parcelas_nao_contempladas']) if atual else 0.0, key=f'fco_cred_nao_cont_{competencia}')

    col_confirmar, col_cancelar = st.columns(2)

    with col_confirmar:
        if st.button('Confirmar', type='primary', use_container_width=True):
            if salvar_credito(competencia, round(cotas, 2), round(nao_contempladas, 2)):
                st.rerun()
            else:
                st.error(st.session_state.pop('mensagem_erro', 'Erro ao salvar os créditos.'))

    with col_cancelar:
        if st.button('Cancelar', use_container_width=True):
            st.rerun()
