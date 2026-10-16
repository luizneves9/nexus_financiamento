import calendar
import pandas as pd
import streamlit as st
from datetime import date
from services.liquidacao import listar_parcelas_liquidacao, resumir_parcelas_liquidacao
from tools.funcoes import transformar_float_em_str, listar_empresas, listar_bancos
from views.components.cabecalho import cabecalho
from views.components.modal_liquidacao_manual import modal_liquidacao_manual
from views.components.modal_liquidacao_estornar import modal_liquidacao_estornar
from views.components.modal_liquidacao_importar import modal_liquidacao_importar

# opções do filtro de situação (rótulo na tela -> valor no banco)
SITUACOES = {'Todas': None, 'Aberta': 'ABERTA', 'Liquidada': 'LIQUIDADA'}

def liquidar_parcelas(linhas_selecionadas):
    '''Funcionalidade de controle para liquidar manualmente as parcelas selecionadas (abertas).'''

    if linhas_selecionadas.empty:
        st.session_state['mensagem_erro'] = 'Selecione ao menos uma parcela!'
        return

    if (linhas_selecionadas['situacao'] != 'ABERTA').any():
        st.session_state['mensagem_erro'] = 'Selecione apenas parcelas abertas para liquidar.'
        return

    modal_liquidacao_manual([int(i) for i in linhas_selecionadas['id_parcela']])

def estornar_parcelas(linhas_selecionadas):
    '''Funcionalidade de controle para estornar a liquidação das parcelas selecionadas (liquidadas).'''

    if linhas_selecionadas.empty:
        st.session_state['mensagem_erro'] = 'Selecione ao menos uma parcela!'
        return

    if (linhas_selecionadas['situacao'] != 'LIQUIDADA').any():
        st.session_state['mensagem_erro'] = 'Selecione apenas parcelas liquidadas para estornar.'
        return

    modal_liquidacao_estornar(linhas_selecionadas)

def importar_erp(df_visual):
    '''Funcionalidade de controle para importar o relatório do ERP: contratos marcados ou, sem marcação, todos os filtrados.'''

    selecionadas = df_visual[df_visual['sel'] == True]
    if selecionadas.empty:
        base, descricao = df_visual, 'todos os contratos filtrados'
    else:
        base, descricao = selecionadas, 'contratos das parcelas marcadas'

    modal_liquidacao_importar(sorted({int(i) for i in base['id_contrato']}), descricao)

def main():

    # cabeçalho padrão da tela (ícone do grupo no menu)
    cabecalho('Liquidação', 'Baixa das parcelas por conciliação com o ERP ou lançamento manual.', 'request_quote')

    # inicializar session_states dos filtros (FL = Filtro Liquidação); padrão: vencimentos do mês atual
    hoje = date.today()
    if 'fl_empresa' not in st.session_state:
        st.session_state['fl_empresa'] = None
    if 'fl_banco' not in st.session_state:
        st.session_state['fl_banco'] = None
    if 'fl_contrato' not in st.session_state:
        st.session_state['fl_contrato'] = None
    if 'fl_data_vcto_ini' not in st.session_state:
        st.session_state['fl_data_vcto_ini'] = hoje.replace(day=1)
    if 'fl_data_vcto_fim' not in st.session_state:
        st.session_state['fl_data_vcto_fim'] = hoje.replace(day=calendar.monthrange(hoje.year, hoje.month)[1])
    if 'fl_situacao' not in st.session_state:
        st.session_state['fl_situacao'] = 'Todas'

    # opções dos filtros de seleção (mesmo cache de cadastros usado no modal de inclusão de contrato)
    if st.session_state.get('df_lista_empresas') is None:
        st.session_state['df_lista_empresas'] = listar_empresas()
    if st.session_state.get('df_lista_bancos') is None:
        st.session_state['df_lista_bancos'] = listar_bancos()

    df_empresas = st.session_state['df_lista_empresas']
    df_bancos = st.session_state['df_lista_bancos']
    opcoes_empresas = ['Todos'] + (df_empresas['razao_social'].to_list() if df_empresas is not None and 'razao_social' in df_empresas else [])
    opcoes_bancos = ['Todos'] + (df_bancos['razao_social'].to_list() if df_bancos is not None and 'razao_social' in df_bancos else [])

    # inicializar session_states dos widgets a partir dos filtros salvos
    # (o widget usa key própria; passar value= dinâmico recria o widget e descarta o que foi digitado)
    if st.session_state.get('fl_empresa_input') not in opcoes_empresas:
        st.session_state['fl_empresa_input'] = st.session_state['fl_empresa'] if st.session_state['fl_empresa'] in opcoes_empresas else 'Todos'
    if st.session_state.get('fl_banco_input') not in opcoes_bancos:
        st.session_state['fl_banco_input'] = st.session_state['fl_banco'] if st.session_state['fl_banco'] in opcoes_bancos else 'Todos'
    if 'fl_contrato_input' not in st.session_state:
        st.session_state['fl_contrato_input'] = st.session_state['fl_contrato'] or ''
    if 'fl_data_vcto_ini_input' not in st.session_state:
        st.session_state['fl_data_vcto_ini_input'] = st.session_state['fl_data_vcto_ini']
    if 'fl_data_vcto_fim_input' not in st.session_state:
        st.session_state['fl_data_vcto_fim_input'] = st.session_state['fl_data_vcto_fim']
    if 'fl_situacao_input' not in st.session_state:
        st.session_state['fl_situacao_input'] = st.session_state['fl_situacao']

    # lista de filtros
    with st.form('liquidacao_filtro'):
        with st.container(horizontal=True, vertical_alignment='bottom'):
            empresa = st.selectbox('Empresa', opcoes_empresas, key='fl_empresa_input')
            banco = st.selectbox('Banco', opcoes_bancos, key='fl_banco_input')
            contrato = st.text_input('Contrato', key='fl_contrato_input')
            data_vcto_ini = st.date_input('Vcto de', key='fl_data_vcto_ini_input', format='DD/MM/YYYY')
            data_vcto_fim = st.date_input('Vcto até', key='fl_data_vcto_fim_input', format='DD/MM/YYYY')
            situacao = st.selectbox('Situação', list(SITUACOES), key='fl_situacao_input')
            submitido = st.form_submit_button('Filtrar', use_container_width=True)

        if submitido:
            st.session_state['fl_empresa'] = None if empresa == 'Todos' else empresa
            st.session_state['fl_banco'] = None if banco == 'Todos' else banco
            st.session_state['fl_contrato'] = contrato if contrato else None
            st.session_state['fl_data_vcto_ini'] = data_vcto_ini
            st.session_state['fl_data_vcto_fim'] = data_vcto_fim
            st.session_state['fl_situacao'] = situacao

    # listando parcelas com filtros
    with st.spinner('Consultando parcelas...'):
        df_parcelas = listar_parcelas_liquidacao(
            empresa=st.session_state.get('fl_empresa'),
            banco=st.session_state.get('fl_banco'),
            contrato=st.session_state.get('fl_contrato'),
            data_vcto_ini=st.session_state.get('fl_data_vcto_ini'),
            data_vcto_fim=st.session_state.get('fl_data_vcto_fim'),
            situacao=SITUACOES[st.session_state.get('fl_situacao')]
        )

    if df_parcelas.empty:
        st.warning('Nenhuma parcela encontrada com os filtros aplicados.')

    else:
        # resumo calculado antes da formatação (valores ainda numéricos)
        resumo = resumir_parcelas_liquidacao(df_parcelas)

        # definindo formato (parcelas abertas não têm valor pago/ajuste: ficam em branco)
        for coluna in ('valor_projetado', 'valor_pago', 'valor_ajuste'):
            df_parcelas[coluna] = df_parcelas[coluna].map(lambda v: transformar_float_em_str(v) if pd.notna(v) else None)

        # inclusão da opção de seleção
        df_parcelas.insert(0, 'sel', False)

        # visualização do dataframe
        df_visual = st.data_editor(
            df_parcelas,
            width='content',
            hide_index=True,
            column_config={
                'sel': st.column_config.CheckboxColumn('', default=False),
                'id_parcela': None,
                'id_liquidacao': None,
                'id_contrato': None,
                'nome_empresa': 'Empresa',
                'banco': 'Banco',
                'numero_contrato': 'Contrato',
                'parcela': 'Parcela',
                'data_vcto': st.column_config.DateColumn('Vencimento', format='DD/MM/YYYY'),
                'situacao': 'Situação',
                'valor_projetado': 'Valor projetado',
                'data_pagamento': st.column_config.DateColumn('Data pagamento', format='DD/MM/YYYY'),
                'valor_pago': 'Valor pago',
                'valor_ajuste': 'Ajuste',
                'origem': 'Origem',
            }
        )

        # botões de interação
        with st.container(horizontal=True):
            if st.button('Importar ERP'): importar_erp(df_visual)
            if st.button('Liquidar'): liquidar_parcelas(df_visual[df_visual['sel'] == True])
            if st.button('Estornar'): estornar_parcelas(df_visual[df_visual['sel'] == True])

        # resumo de valores
        st.caption(
            f"**Contratos:** {resumo['contratos']}&nbsp;&nbsp;|&nbsp;&nbsp;"
            f"**Parcelas:** {resumo['parcelas']}&nbsp;&nbsp;|&nbsp;&nbsp;"
            f"**Liquidadas:** {resumo['liquidadas']}&nbsp;&nbsp;|&nbsp;&nbsp;"
            f"**Projetado:** R\\$ {transformar_float_em_str(resumo['valor_projetado'])}&nbsp;&nbsp;|&nbsp;&nbsp;"
            f"**Pago:** R\\$ {transformar_float_em_str(resumo['valor_pago'])}&nbsp;&nbsp;|&nbsp;&nbsp;"
            f"**Ajustes:** R\\$ {transformar_float_em_str(resumo['valor_ajuste'])}",
            unsafe_allow_html=True
        )

    if 'mensagem_sucesso' in st.session_state:
        st.toast(st.session_state.pop('mensagem_sucesso'), icon='✅')

    if 'mensagem_erro' in st.session_state:
        st.toast(st.session_state.pop('mensagem_erro'), icon='⚠️')

if __name__ == '__main__':
    main()
