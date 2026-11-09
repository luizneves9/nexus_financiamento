import pandas as pd
import streamlit as st
from datetime import date
from services.outros_pagamentos import MODALIDADES, ROTULOS_MODALIDADE, listar_outros_pagamentos, resumir_outros_pagamentos
from tools.funcoes import transformar_float_em_str
from views.components.cabecalho import cabecalho
from views.components.modal_outros_pagamentos_incluir import modal_outros_pagamentos_incluir, modal_outros_pagamentos_editar
from views.components.modal_outros_pagamentos_baixar import (
    modal_outros_pagamentos_baixar,
    modal_outros_pagamentos_estornar,
    modal_outros_pagamentos_excluir,
)

# opções dos filtros (rótulo na tela -> valor no banco)
OPCOES_MODALIDADE = {'Todas': None, **MODALIDADES}
SITUACOES = {'Todas': None, 'Aberta': 'ABERTA', 'Paga': 'PAGA'}
ROTULOS_SITUACAO = {'ABERTA': 'Aberta', 'PAGA': 'Paga'}

def selecionadas_na_situacao(linhas, situacao, rotulo):
    '''Ids das linhas marcadas, todas na situação exigida (senão grava a mensagem de erro e devolve None).'''

    if linhas.empty:
        st.session_state['mensagem_erro'] = 'Selecione ao menos uma parcela!'
        return None
    if (linhas['situacao'] != situacao).any():
        st.session_state['mensagem_erro'] = f'Selecione apenas parcelas {rotulo}.'
        return None
    return [int(i) for i in linhas['id']]

def editar(linhas, df_original):
    '''Funcionalidade de controle para editar uma única parcela em aberto.'''

    if len(linhas) != 1:
        st.session_state['mensagem_erro'] = 'Selecione uma única parcela para editar.'
        return
    if linhas.iloc[0]['situacao'] != 'ABERTA':
        st.session_state['mensagem_erro'] = 'Só parcelas em aberto podem ser editadas (estorne a baixa antes).'
        return

    # dados não formatados da parcela
    modal_outros_pagamentos_editar(df_original[df_original['id'] == linhas.iloc[0]['id']].iloc[0].to_dict())

def main():

    # cabeçalho padrão da tela (ícone do grupo no menu)
    cabecalho('Outros Pagamentos', 'Parcelas de Compra Santo Anjo e Tributário lançadas manualmente, com baixa e estorno.',
              'request_quote')

    # inicializar session_states dos filtros (FOP = Filtro Outros Pagamentos); padrão: vencimentos do ano atual
    hoje = date.today()
    padroes = {
        'fop_modalidade': 'Todas',
        'fop_data_vcto_ini': hoje.replace(month=1, day=1),
        'fop_data_vcto_fim': hoje.replace(month=12, day=31),
        'fop_situacao': 'Todas',
    }
    for chave, valor in padroes.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor

    # inicializar session_states dos widgets a partir dos filtros salvos
    # (o widget usa key própria; passar value= dinâmico recria o widget e descarta o que foi digitado)
    for chave in padroes:
        if f'{chave}_input' not in st.session_state:
            st.session_state[f'{chave}_input'] = st.session_state[chave]

    # lista de filtros
    with st.form('outros_pagamentos_filtro'):
        with st.container(horizontal=True, vertical_alignment='bottom'):
            modalidade = st.selectbox('Modalidade', list(OPCOES_MODALIDADE), key='fop_modalidade_input')
            data_vcto_ini = st.date_input('Vcto de', key='fop_data_vcto_ini_input', format='DD/MM/YYYY')
            data_vcto_fim = st.date_input('Vcto até', key='fop_data_vcto_fim_input', format='DD/MM/YYYY')
            situacao = st.selectbox('Situação', list(SITUACOES), key='fop_situacao_input')
            submitido = st.form_submit_button('Filtrar', use_container_width=True)

        if submitido:
            st.session_state['fop_modalidade'] = modalidade
            st.session_state['fop_data_vcto_ini'] = data_vcto_ini
            st.session_state['fop_data_vcto_fim'] = data_vcto_fim
            st.session_state['fop_situacao'] = situacao

    # listando parcelas com filtros
    with st.spinner('Consultando outros pagamentos...'):
        df = listar_outros_pagamentos(
            modalidade=OPCOES_MODALIDADE[st.session_state['fop_modalidade']],
            data_vcto_ini=st.session_state['fop_data_vcto_ini'],
            data_vcto_fim=st.session_state['fop_data_vcto_fim'],
            situacao=SITUACOES[st.session_state['fop_situacao']]
        )

    if df.empty:
        st.warning('Nenhuma parcela encontrada com os filtros aplicados.')
        if st.button('Incluir'): modal_outros_pagamentos_incluir()

    else:
        df_original = df.copy()

        # resumo calculado antes da formatação (valores ainda numéricos)
        resumo = resumir_outros_pagamentos(df)

        # definindo formato (parcela em aberto não tem valor pago: fica em branco)
        for coluna in ('valor', 'valor_pago'):
            df[coluna] = df[coluna].map(lambda v: transformar_float_em_str(float(v)) if pd.notna(v) else None)
        df['modalidade'] = df['modalidade'].map(ROTULOS_MODALIDADE)
        df['situacao_rotulo'] = df['situacao'].map(ROTULOS_SITUACAO)

        # inclusão da opção de seleção
        df.insert(0, 'sel', False)

        # visualização do dataframe (só a seleção é editável)
        df_visual = st.data_editor(
            df,
            width='content',
            hide_index=True,
            disabled=[coluna for coluna in df.columns if coluna != 'sel'],
            column_order=['sel', 'modalidade', 'descricao', 'data_vencimento', 'valor', 'situacao_rotulo', 'data_pagamento',
                          'valor_pago', 'usuario', 'data_registro', 'usuario_baixa', 'data_registro_baixa',
                          'usuario_alteracao', 'data_alteracao'],
            column_config={
                'sel': st.column_config.CheckboxColumn('', default=False),
                'modalidade': 'Modalidade',
                'descricao': 'Descrição',
                'data_vencimento': st.column_config.DateColumn('Vencimento', format='DD/MM/YYYY'),
                'valor': 'Valor',
                'situacao_rotulo': 'Situação',
                'data_pagamento': st.column_config.DateColumn('Data pagamento', format='DD/MM/YYYY'),
                'valor_pago': 'Valor pago',
                'usuario': 'Lançado por',
                'data_registro': st.column_config.DatetimeColumn('Lançado em', format='DD/MM/YYYY HH:mm'),
                'usuario_baixa': 'Baixado por',
                'data_registro_baixa': st.column_config.DatetimeColumn('Baixado em', format='DD/MM/YYYY HH:mm'),
                'usuario_alteracao': 'Alterado por',
                'data_alteracao': st.column_config.DatetimeColumn('Alterado em', format='DD/MM/YYYY HH:mm'),
            }
        )
        marcadas = df_visual[df_visual['sel'] == True]

        # botões de interação
        with st.container(horizontal=True):
            if st.button('Incluir'): modal_outros_pagamentos_incluir()
            if st.button('Editar'): editar(marcadas, df_original)
            if st.button('Baixar'):
                ids = selecionadas_na_situacao(marcadas, 'ABERTA', 'em aberto para baixar')
                if ids: modal_outros_pagamentos_baixar(ids)
            if st.button('Estornar'):
                ids = selecionadas_na_situacao(marcadas, 'PAGA', 'pagas para estornar')
                if ids: modal_outros_pagamentos_estornar(ids)
            if st.button('Excluir'):
                ids = selecionadas_na_situacao(marcadas, 'ABERTA', 'em aberto para excluir (estorne a baixa antes)')
                if ids: modal_outros_pagamentos_excluir(ids)

        # resumo de valores
        st.caption(
            f"**Parcelas:** {resumo['parcelas']} (abertas: {resumo['abertas']}, pagas: {resumo['pagas']})&nbsp;&nbsp;|&nbsp;&nbsp;"
            f"**Lançado:** R\\$ {transformar_float_em_str(resumo['valor'])}&nbsp;&nbsp;|&nbsp;&nbsp;"
            f"**Pago:** R\\$ {transformar_float_em_str(resumo['valor_pago'])}&nbsp;&nbsp;|&nbsp;&nbsp;"
            f"**Em aberto:** R\\$ {transformar_float_em_str(resumo['valor_aberto'])}",
            unsafe_allow_html=True
        )

    if 'mensagem_sucesso' in st.session_state:
        st.toast(st.session_state.pop('mensagem_sucesso'), icon='✅')

    if 'mensagem_erro' in st.session_state:
        st.toast(st.session_state.pop('mensagem_erro'), icon='⚠️')

if __name__ == '__main__':
    main()
