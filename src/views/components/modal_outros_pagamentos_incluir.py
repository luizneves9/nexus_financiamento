import pandas as pd
import streamlit as st
from datetime import date
from services.outros_pagamentos import (
    MODALIDADES,
    ROTULOS_MODALIDADE,
    gerar_parcelas,
    montar_itens_inclusao,
    validar_inclusao,
    incluir_outros_pagamentos,
    validar_alteracao,
    alterar_outro_pagamento,
)
from tools.funcoes import transformar_float_em_str

@st.dialog('Incluir outros pagamentos', width='large', dismissible=False)
def modal_outros_pagamentos_incluir():
    '''Inclusão de parcelas mensais (Compra Santo Anjo / Tributário) com prévia editável antes de gravar.'''

    st.markdown('*Informe o 1º vencimento, o valor e a quantidade: as parcelas são geradas mês a mês (mesmo dia; '
                'último dia do mês quando o dia não existe). Ajuste valores, vencimentos e marque as já pagas na prévia.*')

    with st.container(horizontal=True, vertical_alignment='bottom'):
        modalidade = st.selectbox('Modalidade', list(MODALIDADES), index=None, placeholder='Selecione', key='fop_inc_modalidade')
        descricao = st.text_input('Descrição', key='fop_inc_descricao')
    with st.container(horizontal=True, vertical_alignment='bottom'):
        vencimento = st.date_input('1º vencimento', value=date.today(), key='fop_inc_vencimento', format='DD/MM/YYYY')
        valor = st.number_input('Valor da parcela (R$)', min_value=0.0, step=0.01, format='%.2f', key='fop_inc_valor')
        quantidade = st.number_input('Quantidade de parcelas', min_value=1, max_value=360, value=1, step=1, format='%d',
                                     key='fop_inc_quantidade')

    # prévia (tipos de data/valor compatíveis com a edição no data_editor)
    df = gerar_parcelas(descricao, vencimento, valor, quantidade)
    df['data_vencimento'] = pd.to_datetime(df['data_vencimento'])
    df['data_pagamento'] = pd.to_datetime(df['data_pagamento'])
    df['valor_pago'] = df['valor_pago'].astype(float)

    # key pelos parâmetros: mudar a geração descarta as edições da prévia anterior
    df_editado = st.data_editor(
        df,
        key=f'fop_inc_previa_{abs(hash((descricao, vencimento, valor, quantidade)))}',
        hide_index=True,
        disabled=['parcela'],
        column_config={
            'parcela': 'Parcela',
            'descricao': st.column_config.TextColumn('Descrição', max_chars=255),
            'data_vencimento': st.column_config.DateColumn('Vencimento', format='DD/MM/YYYY', required=True),
            'valor': st.column_config.NumberColumn('Valor', format='localized', min_value=0.01, step=0.01, required=True),
            'pago': st.column_config.CheckboxColumn('Já pago', default=False),
            'data_pagamento': st.column_config.DateColumn('Data pagamento', format='DD/MM/YYYY'),
            'valor_pago': st.column_config.NumberColumn('Valor pago', format='localized', min_value=0.01, step=0.01),
        }
    )

    itens = montar_itens_inclusao(df_editado)
    total = sum(item['valor'] or 0 for item in itens)
    pagas = [item for item in itens if item['pago']]
    st.caption(
        f"**Parcelas:** {len(itens)}&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"**Total:** R\\$ {transformar_float_em_str(float(total))}&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"**Já pagas:** {len(pagas)} (R\\$ {transformar_float_em_str(float(sum(item['valor_pago'] or 0 for item in pagas)))})",
        unsafe_allow_html=True
    )

    col_confirmar, col_cancelar = st.columns(2)

    with col_confirmar:
        if st.button('Confirmar', type='primary', use_container_width=True):
            codigo = MODALIDADES.get(modalidade)
            mensagem = validar_inclusao(codigo, itens)
            if mensagem:
                st.error(mensagem)
            elif incluir_outros_pagamentos(codigo, itens):
                st.rerun()
            else:
                st.error(st.session_state.pop('mensagem_erro', 'Erro ao incluir as parcelas.'))

    with col_cancelar:
        if st.button('Cancelar', use_container_width=True):
            st.rerun()

@st.dialog('Editar parcela', dismissible=False)
def modal_outros_pagamentos_editar(anterior):
    '''Alteração de uma parcela em aberto (modalidade, descrição, vencimento e valor).'''

    rotulos = list(MODALIDADES)
    rotulo_atual = ROTULOS_MODALIDADE.get(anterior['modalidade'])
    sufixo = int(anterior['id'])

    modalidade = st.selectbox('Modalidade', rotulos, index=rotulos.index(rotulo_atual) if rotulo_atual in rotulos else None,
                              key=f'fop_edt_modalidade_{sufixo}')
    descricao = st.text_input('Descrição', value=anterior['descricao'] or '', max_chars=255, key=f'fop_edt_descricao_{sufixo}')
    vencimento = st.date_input('Vencimento', value=anterior['data_vencimento'], key=f'fop_edt_vencimento_{sufixo}', format='DD/MM/YYYY')
    valor = st.number_input('Valor (R$)', min_value=0.0, step=0.01, format='%.2f', value=float(anterior['valor']),
                            key=f'fop_edt_valor_{sufixo}')

    col_confirmar, col_cancelar = st.columns(2)

    with col_confirmar:
        if st.button('Confirmar', type='primary', use_container_width=True):
            codigo = MODALIDADES.get(modalidade)
            mensagem = validar_alteracao(codigo, vencimento, valor)
            if mensagem:
                st.error(mensagem)
            elif alterar_outro_pagamento(anterior, codigo, descricao, vencimento, valor):
                st.rerun()
            else:
                st.error(st.session_state.pop('mensagem_erro', 'Erro ao alterar a parcela.'))

    with col_cancelar:
        if st.button('Cancelar', use_container_width=True):
            st.rerun()
