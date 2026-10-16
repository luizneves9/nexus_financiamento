import pandas as pd
import streamlit as st
from services.liquidacao import (
    ler_csv_erp,
    conciliar_erp,
    resumir_conciliacao,
    confirmar_conciliacao,
    listar_contratos_vinculo,
    listar_vinculos_erp,
    vincular_codigos_erp,
    remover_vinculos_erp,
    STATUS_LIQUIDAVEIS,
)
from tools.funcoes import transformar_float_em_str

# rótulos das situações da conciliação
SITUACOES_CONCILIACAO = {
    'DIFERENCA': 'Diferença',
    'CONCILIADO': 'Conciliado',
    'CONFLITO': 'Vínculo conflitante',
    'NAO_IDENTIFICADO': 'Não identificado no Nexus',
    'NAO_PAGO_ERP': 'Não pago no ERP',
    'JA_LIQUIDADA': 'Já liquidada',
    'FORA_SELECAO': 'Fora da seleção',
}

def limpar_importacao():
    '''Remove do session_state o arquivo, a prévia e os vínculos pendentes da importação.'''
    for chave in [k for k in st.session_state if k.startswith('fl_erp_')]:
        del st.session_state[chave]

def nova_versao_previa():
    '''Nova versão da prévia (após vincular/remover): as marcações da prévia anterior são descartadas.'''
    st.session_state['fl_erp_versao'] = st.session_state.get('fl_erp_versao', 0) + 1

def secao_vinculos(df, linhas):
    '''Vínculo manual (permanente) entre códigos do ERP e contratos do Nexus, montado em lista e gravado de uma vez.'''

    # mensagem do último vínculo/remoção (sobrevive ao rerun do modal)
    if 'fl_erp_msg_vinculo' in st.session_state:
        tipo, texto = st.session_state.pop('fl_erp_msg_vinculo')
        if tipo == 'ok':
            st.success(texto)
        else:
            st.error(texto)

    codigos = sorted(df.loc[df['status'] == 'NAO_IDENTIFICADO', 'codigo_nao_identificado'].dropna().unique())
    pendentes = st.session_state.setdefault('fl_erp_pendentes', [])

    if codigos or pendentes:
        st.markdown('**Vincular códigos do ERP**')

        # contratos: primeiro os "Não pago no ERP" deste arquivo (candidatos mais prováveis), depois os demais
        contratos = listar_contratos_vinculo()
        rotulos = {int(c.id): f'{c.numero_contrato} — {c.nome_empresa} — {c.banco}' for c in contratos.itertuples()}
        candidatos = {int(i) for grupo in df.loc[df['status'] == 'NAO_PAGO_ERP', 'grupo'] for i in grupo}
        opcoes = sorted(rotulos, key=lambda i: (i not in candidatos, rotulos[i]))

        with st.container(horizontal=True, vertical_alignment='bottom'):
            codigo = st.selectbox('Código do ERP', codigos, index=None, placeholder='Selecione', key='fl_erp_vinc_codigo')
            ids_contrato = st.multiselect('Contrato(s) do Nexus', opcoes, placeholder='Digite para buscar',
                                          format_func=lambda i: ('★ ' if i in candidatos else '') + rotulos[i],
                                          key='fl_erp_vinc_contratos')
            if st.button('Adicionar'):
                if codigo is None or not ids_contrato:
                    st.session_state['fl_erp_msg_vinculo'] = ('erro', 'Selecione o código do ERP e ao menos um contrato do Nexus.')
                else:
                    for id_contrato in ids_contrato:
                        if not any(p['codigo_erp'] == codigo and p['id_contrato'] == id_contrato for p in pendentes):
                            pendentes.append({'codigo_erp': codigo, 'id_contrato': id_contrato, 'contrato': rotulos[id_contrato]})
                    st.session_state.pop('fl_erp_vinc_codigo', None)
                    st.session_state.pop('fl_erp_vinc_contratos', None)
                    st.session_state['fl_erp_pend_versao'] = st.session_state.get('fl_erp_pend_versao', 0) + 1
                st.rerun(scope='fragment')
        st.caption('★ contratos que aparecem como *Não pago no ERP* neste arquivo.')

        # vínculos pendentes: podem ser excluídos da lista antes de gravar
        if pendentes:
            st.markdown('*Vínculos pendentes (selecione a linha e exclua para tirar da lista):*')
            df_pendentes = st.data_editor(
                pd.DataFrame(pendentes),
                key=f"fl_erp_pendentes_editor_{st.session_state.get('fl_erp_pend_versao', 0)}",
                hide_index=True,
                num_rows='dynamic',
                disabled=['codigo_erp', 'id_contrato', 'contrato'],
                column_config={
                    'codigo_erp': 'Código do ERP',
                    'id_contrato': None,
                    'contrato': 'Contrato do Nexus',
                }
            )
            pares = [(str(p.codigo_erp), int(p.id_contrato)) for p in df_pendentes.dropna(subset=['codigo_erp', 'id_contrato']).itertuples()]

            if st.button('Vincular'):
                erro = vincular_codigos_erp(pares) if pares else 'Nenhum vínculo pendente.'
                if erro:
                    st.session_state['fl_erp_msg_vinculo'] = ('erro', erro)
                else:
                    st.session_state['fl_erp_msg_vinculo'] = ('ok', f'{len(pares)} vínculo(s) gravado(s); prévia reprocessada.')
                    st.session_state['fl_erp_pendentes'] = []
                    nova_versao_previa()
                st.rerun(scope='fragment')

    # vínculos já gravados para os códigos deste arquivo
    vinculos = listar_vinculos_erp(linhas)
    if not vinculos.empty:
        st.markdown('**Vínculos usados neste arquivo**')
        rotulos_vinculo = {
            (v.codigo_erp, int(v.id_contrato)): f'{v.codigo_erp} → {v.numero_contrato} — {v.nome_empresa} — {v.banco}'
            for v in vinculos.itertuples()
        }

        with st.container(horizontal=True, vertical_alignment='bottom'):
            remover = st.multiselect('Vínculos', list(rotulos_vinculo), placeholder='Selecione para remover',
                                     format_func=rotulos_vinculo.get, key='fl_erp_vinc_remover')
            if st.button('Remover vínculo(s)'):
                if not remover:
                    st.session_state['fl_erp_msg_vinculo'] = ('erro', 'Selecione o(s) vínculo(s) a remover.')
                else:
                    erro = remover_vinculos_erp(remover)
                    if erro:
                        st.session_state['fl_erp_msg_vinculo'] = ('erro', erro)
                    else:
                        st.session_state['fl_erp_msg_vinculo'] = ('ok', f'{len(remover)} vínculo(s) removido(s); prévia reprocessada.')
                        st.session_state.pop('fl_erp_vinc_remover', None)
                        nova_versao_previa()
                st.rerun(scope='fragment')

@st.dialog('Importar ERP', width='large', dismissible=False)
def modal_liquidacao_importar(ids_contratos, descricao_contratos):
    '''Modal de importação do relatório de pagamentos do ERP e conciliação com a projeção.'''

    st.markdown(f'*Contratos considerados: {len(ids_contratos)} ({descricao_contratos}).*')

    arquivo = st.file_uploader('Relatório de pagamentos do ERP (CSV)', type=['csv'], key='fl_erp_arquivo')

    if arquivo is not None:

        # lê o arquivo uma única vez (guardado no session_state enquanto o modal estiver aberto)
        chave_arquivo = f'{arquivo.name}|{arquivo.size}'
        if st.session_state.get('fl_erp_chave') != chave_arquivo:
            linhas, descartadas, erro = ler_csv_erp(arquivo)
            st.session_state['fl_erp_chave'] = chave_arquivo
            st.session_state['fl_erp_linhas'] = linhas
            st.session_state['fl_erp_descartadas'] = descartadas
            st.session_state['fl_erp_erro'] = erro

        linhas = st.session_state['fl_erp_linhas']
        descartadas = st.session_state['fl_erp_descartadas']
        erro = st.session_state['fl_erp_erro']

        if erro:
            st.error(erro)

        else:
            # prévia (transação desfeita: nada é gravado)
            with st.spinner('Conciliando...'):
                try:
                    df = conciliar_erp(linhas, ids_contratos)
                except Exception as e:
                    df = None
                    st.error(f'Erro ao conciliar. ({getattr(e, "orig", e)})')

            if df is not None:
                resumo = resumir_conciliacao(df)

                df['situacao'] = df['status'].map(SITUACOES_CONCILIACAO)
                df.insert(0, 'sel', df['status'].isin(STATUS_LIQUIDAVEIS))

                df_editado = st.data_editor(
                    df,
                    key=f"fl_erp_editor_{chave_arquivo}_{st.session_state.get('fl_erp_versao', 0)}",  # nova versão a cada vínculo: descarta marcações da prévia anterior
                    hide_index=True,
                    disabled=[coluna for coluna in df.columns if coluna != 'sel'],
                    column_order=['sel', 'situacao', 'contrato', 'codigos_erp', 'vinculo', 'competencia', 'parcela', 'doctos',
                                  'qtd_linhas', 'data_pagamento', 'valor_erp', 'valor_nexus', 'diferenca'],
                    column_config={
                        'sel': st.column_config.CheckboxColumn('', default=False),
                        'situacao': 'Situação',
                        'contrato': 'Contrato',
                        'codigos_erp': 'Códigos ERP',
                        'vinculo': 'Vínculo',
                        'competencia': st.column_config.DateColumn('Competência', format='MM/YYYY'),
                        'parcela': 'Parcela',
                        'doctos': st.column_config.ListColumn('Doctos'),
                        'qtd_linhas': 'Linhas',
                        'data_pagamento': st.column_config.DateColumn('Data pagamento', format='DD/MM/YYYY'),
                        'valor_erp': st.column_config.NumberColumn('Valor ERP', format='localized'),
                        'valor_nexus': st.column_config.NumberColumn('Valor Nexus', format='localized'),
                        'diferenca': st.column_config.NumberColumn('Diferença', format='localized'),
                    }
                )

                if df['datas_diferentes'].fillna(False).any():
                    st.warning('Há parcelas que somaram linhas do ERP com datas de pagamento diferentes; será usada a maior data.')

                # resumo da conciliação
                st.caption(
                    f"**Linhas lidas:** {len(linhas)} (descartadas sem Docto: {descartadas})&nbsp;&nbsp;|&nbsp;&nbsp;"
                    f"**Conciliado:** {resumo['conciliado'][0]} (R\\$ {transformar_float_em_str(resumo['conciliado'][1])})&nbsp;&nbsp;|&nbsp;&nbsp;"
                    f"**Diferença:** {resumo['diferenca'][0]} (R\\$ {transformar_float_em_str(resumo['diferenca'][1])})&nbsp;&nbsp;|&nbsp;&nbsp;"
                    f"**Vínculo conflitante:** {resumo['conflito'][0]}&nbsp;&nbsp;|&nbsp;&nbsp;"
                    f"**Não identificado:** {resumo['nao_identificado'][0]} (R\\$ {transformar_float_em_str(resumo['nao_identificado'][1])})&nbsp;&nbsp;|&nbsp;&nbsp;"
                    f"**Não pago no ERP:** {resumo['nao_pago_erp'][0]} (R\\$ {transformar_float_em_str(resumo['nao_pago_erp'][1])})&nbsp;&nbsp;|&nbsp;&nbsp;"
                    f"**Já liquidada:** {resumo['ja_liquidada'][0]}&nbsp;&nbsp;|&nbsp;&nbsp;"
                    f"**Fora da seleção:** {resumo['fora_selecao'][0]} (R\\$ {transformar_float_em_str(resumo['fora_selecao'][1])})",
                    unsafe_allow_html=True
                )
                st.caption('Somente as linhas *Conciliado* e *Diferença* marcadas são liquidadas; a diferença é gravada como ajuste. '
                           'Em grupos (ex.: A + B), o valor do ERP é dividido entre as parcelas proporcionalmente ao valor projetado.')

                # vínculo manual de códigos não identificados
                secao_vinculos(df, linhas)

                # parcelas das linhas marcadas que podem ser liquidadas (um grupo pode ter mais de uma parcela)
                marcadas = df_editado[(df_editado['sel'] == True) & (df_editado['status'].isin(STATUS_LIQUIDAVEIS))]
                parcelas_marcadas = [int(i) for parcelas in marcadas['parcelas'] for i in parcelas]
                chaves_vinculo_manual = int((marcadas['vinculo'] == 'Manual').sum())

                if st.button('Confirmar', type='primary', use_container_width=True):
                    if not parcelas_marcadas:
                        st.error('Marque ao menos uma linha Conciliado ou Diferença.')
                    else:
                        confirmar_conciliacao(linhas, ids_contratos, parcelas_marcadas, arquivo.name, descartadas, resumo,
                                              chaves_vinculo_manual)
                        limpar_importacao()
                        st.rerun()

    if st.button('Cancelar', use_container_width=True):
        limpar_importacao()
        st.rerun()
