import pandas as pd
import streamlit as st
from services.liquidacao import buscar_parcelas, montar_itens_liquidacao, validar_liquidacao_manual, liquidar_parcelas_manual
from tools.funcoes import transformar_float_em_str

@st.dialog('Liquidar parcelas', width='large', dismissible=False)
def modal_liquidacao_manual(ids_parcela):
    '''Modal de liquidação manual das parcelas selecionadas (data e valor pago editáveis).'''

    # dados atuais das parcelas (lidos do banco, não da tabela formatada)
    df = buscar_parcelas(ids_parcela)
    if df.empty:
        st.error('Parcelas não encontradas.')
        return

    if (df['situacao'] != 'ABERTA').any():
        st.error('Há parcelas que não estão mais abertas. Feche e atualize a tela.')
        return

    # valores padrão: pagamento no vencimento, pelo valor projetado
    df['data_pagamento'] = df['data_vcto']
    df['valor_pago'] = df['valor_projetado']

    st.markdown('*Informe a data e o valor pago de cada parcela. A diferença para o valor projetado é gravada como ajuste.*')

    # tabela editável (key por seleção, para não reaproveitar edições de outra seleção)
    df_editado = st.data_editor(
        df,
        key=f'fl_liquidar_{abs(hash(tuple(ids_parcela)))}',
        hide_index=True,
        disabled=['numero_contrato', 'parcela', 'data_vcto', 'valor_projetado'],
        column_config={
            'id_parcela': None,
            'situacao': None,
            'numero_contrato': 'Contrato',
            'parcela': 'Parcela',
            'data_vcto': st.column_config.DateColumn('Vencimento', format='DD/MM/YYYY'),
            'valor_projetado': st.column_config.NumberColumn('Valor projetado', format='localized'),
            'data_pagamento': st.column_config.DateColumn('Data pagamento', format='DD/MM/YYYY', required=True),
            'valor_pago': st.column_config.NumberColumn('Valor pago', format='localized', min_value=0.01, step=0.01, required=True),
        }
    )

    # resumo da liquidação
    total_projetado = float(df_editado['valor_projetado'].sum())
    total_pago = float(df_editado['valor_pago'].fillna(0).sum())
    st.caption(
        f"**Parcelas:** {len(df_editado)}&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"**Projetado:** R\\$ {transformar_float_em_str(total_projetado)}&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"**Pago:** R\\$ {transformar_float_em_str(total_pago)}&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"**Ajuste:** R\\$ {transformar_float_em_str(total_pago - total_projetado)}",
        unsafe_allow_html=True
    )

    # botão de confirmação ou cancelamento
    col_confirmar, col_cancelar = st.columns(2)

    with col_confirmar:
        if st.button('Confirmar', type='primary', use_container_width=True):
            itens = montar_itens_liquidacao(df_editado)
            mensagem = validar_liquidacao_manual(itens)
            if mensagem:
                st.error(mensagem)
            else:
                liquidar_parcelas_manual(itens)
                st.rerun()

    with col_cancelar:
        if st.button('Cancelar', use_container_width=True):
            st.rerun()
