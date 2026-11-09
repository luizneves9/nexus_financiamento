import pandas as pd
import streamlit as st
from services.outros_pagamentos import (
    ROTULOS_MODALIDADE,
    buscar_outros_pagamentos,
    montar_itens_baixa,
    validar_baixa,
    baixar_outros_pagamentos,
    estornar_outros_pagamentos,
    excluir_outros_pagamentos,
)
from tools.funcoes import transformar_float_em_str

COLUNAS_PARCELA = {
    'id': None,
    'modalidade': 'Modalidade',
    'descricao': 'Descrição',
    'data_vencimento': st.column_config.DateColumn('Vencimento', format='DD/MM/YYYY'),
    'valor': st.column_config.NumberColumn('Valor', format='localized'),
    'data_pagamento': st.column_config.DateColumn('Data pagamento', format='DD/MM/YYYY'),
    'valor_pago': st.column_config.NumberColumn('Valor pago', format='localized'),
}

def _carregar(ids, situacao):
    '''Parcelas atuais do banco, conferindo se ainda estão na situação esperada.'''

    df = buscar_outros_pagamentos(ids)
    if df.empty:
        st.error('Parcelas não encontradas.')
        return None
    if (df['situacao'] != situacao).any():
        st.error('A situação de alguma parcela mudou. Feche e atualize a tela.')
        return None
    df['modalidade'] = df['modalidade'].map(ROTULOS_MODALIDADE)
    return df

def _botoes(acao, rotulo_erro):
    '''Confirmar (executa `acao`) / Cancelar.'''

    col_confirmar, col_cancelar = st.columns(2)
    with col_confirmar:
        if st.button('Confirmar', type='primary', use_container_width=True):
            if acao():
                st.rerun()
            else:
                st.error(st.session_state.pop('mensagem_erro', rotulo_erro))
    with col_cancelar:
        if st.button('Cancelar', use_container_width=True):
            st.rerun()

@st.dialog('Baixar parcelas', width='large', dismissible=False)
def modal_outros_pagamentos_baixar(ids):
    '''Baixa das parcelas em aberto selecionadas (data e valor pago editáveis).'''

    df = _carregar(ids, 'ABERTA')
    if df is None:
        return

    # valores padrão: pagamento no vencimento, pelo valor lançado
    df = df[['id', 'modalidade', 'descricao', 'data_vencimento', 'valor']].copy()
    df['data_pagamento'] = pd.to_datetime(df['data_vencimento'])
    df['valor_pago'] = df['valor'].astype(float)

    st.markdown('*Informe a data e o valor pago de cada parcela.*')

    df_editado = st.data_editor(
        df,
        key=f'fop_baixar_{abs(hash(tuple(ids)))}',
        hide_index=True,
        disabled=['modalidade', 'descricao', 'data_vencimento', 'valor'],
        column_config={
            **COLUNAS_PARCELA,
            'data_pagamento': st.column_config.DateColumn('Data pagamento', format='DD/MM/YYYY', required=True),
            'valor_pago': st.column_config.NumberColumn('Valor pago', format='localized', min_value=0.01, step=0.01, required=True),
        }
    )

    st.caption(
        f"**Parcelas:** {len(df_editado)}&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"**Lançado:** R\\$ {transformar_float_em_str(float(df_editado['valor'].sum()))}&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"**Pago:** R\\$ {transformar_float_em_str(float(df_editado['valor_pago'].fillna(0).sum()))}",
        unsafe_allow_html=True
    )

    def baixar():
        itens = montar_itens_baixa(df_editado)
        mensagem = validar_baixa(itens)
        if mensagem:
            st.session_state['mensagem_erro'] = mensagem
            return False
        return baixar_outros_pagamentos(itens)

    _botoes(baixar, 'Erro ao baixar as parcelas.')

@st.dialog('Estornar baixa', width='large', dismissible=False)
def modal_outros_pagamentos_estornar(ids):
    '''Estorno da baixa das parcelas pagas selecionadas (volta para em aberto).'''

    df = _carregar(ids, 'PAGA')
    if df is None:
        return

    st.markdown('*A baixa das parcelas abaixo será desfeita (data e valor pago ficam em branco); o log guarda a baixa estornada.*')
    st.dataframe(df[list(COLUNAS_PARCELA)], hide_index=True, column_config=COLUNAS_PARCELA)
    st.caption(f"**Parcelas:** {len(df)}&nbsp;&nbsp;|&nbsp;&nbsp;"
               f"**Pago estornado:** R\\$ {transformar_float_em_str(float(df['valor_pago'].sum()))}", unsafe_allow_html=True)

    _botoes(lambda: estornar_outros_pagamentos(ids), 'Erro ao estornar as baixas.')

@st.dialog('Excluir parcelas', width='large', dismissible=False)
def modal_outros_pagamentos_excluir(ids):
    '''Exclusão das parcelas em aberto selecionadas.'''

    df = _carregar(ids, 'ABERTA')
    if df is None:
        return

    st.markdown('*As parcelas abaixo serão excluídas; o log guarda a cópia de cada registro.*')
    st.dataframe(df[['id', 'modalidade', 'descricao', 'data_vencimento', 'valor']], hide_index=True, column_config=COLUNAS_PARCELA)
    st.caption(f"**Parcelas:** {len(df)}&nbsp;&nbsp;|&nbsp;&nbsp;"
               f"**Valor:** R\\$ {transformar_float_em_str(float(df['valor'].sum()))}", unsafe_allow_html=True)

    _botoes(lambda: excluir_outros_pagamentos(ids), 'Erro ao excluir as parcelas.')
