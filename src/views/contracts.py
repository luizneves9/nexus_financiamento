import streamlit as st
from services.contracts import listar_contratos
from views.components.modal_contracts_incluir import modal_incluir_contrato

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

    df_contratos['Juros'] = df_contratos['Juros'].astype(str).str.replace('.', ',').str.ljust(4, '0') + '%'
    df_contratos['Valor'] = df_contratos['Valor'].map(transformar_float_em_str)

    st.data_editor(
        df_contratos,
        hide_index=True,
        column_config={
            'Data de Emissão': st.column_config.DateColumn('Data', format='DD/MM/YYYY'),
            'Vencimento final': st.column_config.DateColumn('Vencimento', format='DD/MM/YYYY')
        }
    )

    # botões de interação
    with st.container(horizontal=True):
        if st.button('Novo'): modal_incluir_contrato()

if __name__ == '__main__':
    main()