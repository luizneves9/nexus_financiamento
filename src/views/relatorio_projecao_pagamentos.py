import streamlit as st
from services.relatorio_projecao_pagamentos import listar_projecao_pagamentos
from tools.funcoes import transformar_float_em_str

def main():

    # definindo o título da página
    st.markdown('''
        <h2 style='margin-bottom: 0px;'>Projeção de Pagamentos</h2>
        <p style='margin-top: -15px; color: #666; font-style: italic;'>
            Agrupamento da projeção de pagamentos dos contratos.
        </p>
        ''',
        unsafe_allow_html=True
    )

    # listando projeção de pagamentos
    df_projecao = listar_projecao_pagamentos()

    # definindo formato
    for coluna in ('valor_principal', 'valor_juros', 'parcela_h', 'total_parcela'):
        df_projecao[coluna] = df_projecao[coluna].map(transformar_float_em_str)

    # inclusão da opção de seleção
    df_projecao.insert(0, 'sel', False)

    # visualização do dataframe
    df_visual = st.data_editor(
        df_projecao,
        width='content',
        hide_index=True,
        column_config={
            'sel': st.column_config.CheckboxColumn('', default=False),
            'data_emissao': st.column_config.DateColumn(format='DD/MM/YYYY'),
            'data': st.column_config.DateColumn(format='DD/MM/YYYY'),
            'data_vcto': st.column_config.DateColumn(format='DD/MM/YYYY'),
        }
    )

    if 'mensagem_sucesso' in st.session_state:
        st.toast(st.session_state.pop('mensagem_sucesso'), icon='✅')

    if 'mensagem_erro' in st.session_state:
        st.toast(st.session_state.pop('mensagem_erro'), icon='⚠️')

if __name__ == '__main__':
    main()
