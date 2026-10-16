import pandas as pd
import streamlit as st
from services.contracts import obter_detalhe_contrato, listar_historico_contrato
from services.anexos import (
    TIPOS_ANEXO,
    listar_anexos,
    obter_conteudo_anexo,
    validar_arquivos,
    incluir_anexos,
    excluir_anexo,
)
from tools.funcoes import transformar_float_em_str
from views.components.visualizador_pdf import visualizar_pdf

# Detalhe do contrato em abas. Para incluir uma funcionalidade nova, criar uma função aba_xxx(...)
# e acrescentá-la na montagem das abas em modal_detalhe_contrato.

SITUACOES_CONTRATO = {'ATIVO': 'Ativo', 'QUITADO': 'Quitado', 'ENCERRADO': 'Encerrado'}

ACOES_HISTORICO = {
    'CONTRATO_INCLUIR': 'Contrato incluído',
    'CONTRATO_EXCLUIR': 'Contrato excluído',
    'ANTECIPACAO_INCLUIR': 'Antecipação lançada',
    'QUITACAO_INCLUIR': 'Quitação lançada',
    'ANTECIPACAO_EXCLUIR': 'Antecipação/quitação excluída',
    'LIQUIDACAO_INCLUIR': 'Parcela liquidada',
    'LIQUIDACAO_ESTORNAR': 'Liquidação estornada',
    'ANEXO_INCLUIR': 'Anexo incluído',
    'ANEXO_EXCLUIR': 'Anexo excluído',
}

def limpar_detalhe():
    '''Remove do session_state as seleções, uploads e confirmações do detalhe do contrato.'''
    for chave in [k for k in st.session_state if k.startswith('fcd_')]:
        del st.session_state[chave]

def formatar_data(valor):
    return valor.strftime('%d/%m/%Y') if valor is not None and not pd.isna(valor) else '—'

def formatar_valor(valor):
    return f'R$ {transformar_float_em_str(float(valor))}' if valor is not None else '—'

def formatar_taxa(valor, casas=2):
    return f'{float(valor):.{casas}f}%'.replace('.', ',') if valor is not None else '—'

def formatar_tamanho(tamanho_bytes):
    if tamanho_bytes >= 1024 * 1024:
        return f'{tamanho_bytes / (1024 * 1024):.1f} MB'.replace('.', ',')
    return f'{max(tamanho_bytes / 1024, 0.1):.1f} KB'.replace('.', ',')

def campo(rotulo, valor):
    st.markdown(f'**{rotulo}:** {valor}')

# ------------------------------------------------------------------ abas

def aba_dados(contrato):
    '''Aba Dados: campos do contrato e situação da projeção.'''

    col1, col2, col3 = st.columns(3)
    with col1:
        campo('Tipo de contrato', contrato['tipo_contrato'])
        campo('Data de emissão', formatar_data(contrato['data_emissao']))
        campo('Data BNDES', formatar_data(contrato['data_bndes']))
        campo('Valor financiado', formatar_valor(contrato['valor_financiado']))
        campo('Selic do contrato', f"{float(contrato['selic']):.6f}".replace('.', ',') if contrato['selic'] is not None else '—')
        campo('Pós-fixado', contrato['pos_fixado'] or '—')
        campo('Débito em conta', 'Sim' if contrato['debito_conta_corrente'] else 'Não')
    with col2:
        campo('Taxa de juros efetiva', formatar_taxa(contrato['taxa_juros_efetiva'], 6))
        campo('Custo BNDES', formatar_taxa(contrato['custo_bndes']))
        campo('Sobretaxa BNDES', formatar_taxa(contrato['sobretaxa_bndes']))
        campo('Percentual do banco', formatar_taxa(contrato['percentual_banco']))
        campo('Registro de cobrança', contrato['registro_cobranca'] or '—')
        campo('Situação', SITUACOES_CONTRATO.get(contrato['status_contrato'], '—'))
        campo('Parcelas liquidadas', f"{contrato['qtd_liquidadas'] or 0} de {contrato['qtd_parcelas'] or 0}")
    with col3:
        campo('Prazo total', f"{contrato['prazo_total']} meses")
        campo('Prazo de carência', f"{contrato['prazo_carencia']} meses")
        campo('Prazo final', f"{contrato['prazo_final']} meses")
        campo('Pagamentos na carência', contrato['carencia_pagamento'] if contrato['carencia_pagamento'] is not None else '—')
        campo('1ª parcela (encargo)', formatar_data(contrato['data_primeira_parcela_encargo']))
        campo('1ª parcela (prestação)', formatar_data(contrato['data_primeira_parcela_prestacao']))
        campo('Última parcela', formatar_data(contrato['data_ultima_parcela']))

def aba_anexos(id_contrato, tipo, df_anexos):
    '''Aba de anexos de um tipo: escolha do arquivo, PDF exibido na tela, baixar/excluir e inclusão de novos.'''

    rotulo = TIPOS_ANEXO[tipo]
    if not df_anexos.empty:
        st.caption(f'{len(df_anexos)} arquivo(s) anexado(s).')

    if df_anexos.empty:
        st.info(f'Nenhum PDF de {rotulo.lower()} anexado.', icon=':material/picture_as_pdf:')
    else:
        rotulos = {
            int(a.id): f"{a.nome_arquivo} · {formatar_tamanho(a.tamanho_bytes)} · {a.data_registro:%d/%m/%Y %H:%M} · {a.usuario or '—'}"
            for a in df_anexos.itertuples()
        }
        id_anexo = st.selectbox('Arquivo', list(rotulos), format_func=rotulos.get, key=f'fcd_arquivo_{tipo}_{id_contrato}')
        nome, conteudo = obter_conteudo_anexo(tipo, id_anexo)

        visualizar_pdf(conteudo)

        with st.container(horizontal=True):
            st.download_button('Baixar', data=conteudo, file_name=nome, mime='application/pdf',
                               key=f'fcd_baixar_{tipo}_{id_anexo}', on_click='ignore')
            if st.button('Excluir', key=f'fcd_excluir_{tipo}_{id_anexo}'):
                st.session_state['fcd_excluir'] = (tipo, id_anexo, nome)
                st.rerun(scope='fragment')

        # confirmação de exclusão do arquivo selecionado
        if st.session_state.get('fcd_excluir', (None,))[0] == tipo:
            _, id_excluir, nome_excluir = st.session_state['fcd_excluir']
            st.warning(f'Excluir o anexo "{nome_excluir}"? Esta ação não pode ser desfeita.')
            with st.container(horizontal=True):
                if st.button('Confirmar exclusão', key=f'fcd_confirmar_exclusao_{tipo}'):
                    erro = excluir_anexo(tipo, id_excluir)
                    st.session_state['fcd_msg'] = ('erro', erro) if erro else ('ok', f'Anexo "{nome_excluir}" excluído.')
                    del st.session_state['fcd_excluir']
                    st.session_state.pop(f'fcd_arquivo_{tipo}_{id_contrato}', None)
                    st.rerun(scope='fragment')
                if st.button('Cancelar exclusão', key=f'fcd_cancelar_exclusao_{tipo}'):
                    del st.session_state['fcd_excluir']
                    st.rerun(scope='fragment')

    # inclusão de novos PDFs (a versão troca a key do upload depois de gravar, limpando a seleção)
    st.divider()
    versao = st.session_state.get(f'fcd_versao_{tipo}', 0)
    arquivos = st.file_uploader(f'Adicionar {rotulo.lower()} (PDF, até 20 MB cada)', type=['pdf'],
                                accept_multiple_files=True, key=f'fcd_upload_{tipo}_{id_contrato}_{versao}')
    if st.button('Anexar', type='primary', key=f'fcd_anexar_{tipo}'):
        mensagem = 'Selecione ao menos um PDF para anexar.' if not arquivos else validar_arquivos(arquivos)
        if not mensagem:
            mensagem = incluir_anexos(id_contrato, {tipo: arquivos})
        if mensagem:
            st.session_state['fcd_msg'] = ('erro', mensagem)
        else:
            st.session_state['fcd_msg'] = ('ok', st.session_state.pop('mensagem_sucesso', 'Anexo(s) incluído(s).'))
            st.session_state[f'fcd_versao_{tipo}'] = versao + 1
            st.session_state.pop(f'fcd_arquivo_{tipo}_{id_contrato}', None)
        st.rerun(scope='fragment')

def resumo_historico(acao, detalhes):
    '''Resumo curto do que a ação registrou (sem expor dados sensíveis).'''

    detalhes = detalhes or {}
    if acao.startswith('ANEXO'):
        return detalhes.get('nome_arquivo', '')
    if acao in ('ANTECIPACAO_INCLUIR', 'QUITACAO_INCLUIR', 'ANTECIPACAO_EXCLUIR'):
        valor = detalhes.get('valor_pago')
        return f"R$ {transformar_float_em_str(float(valor))}" if valor is not None else ''
    if acao.startswith('LIQUIDACAO'):
        valor = detalhes.get('valor_pago')
        texto = f"R$ {transformar_float_em_str(float(valor))}" if valor is not None else ''
        return f"{texto} · {detalhes.get('origem', '')}".strip(' ·')
    if acao == 'CONTRATO_EXCLUIR' and detalhes.get('anexos_excluidos'):
        return f"{len(detalhes['anexos_excluidos'])} anexo(s) excluído(s) junto"
    return ''

def aba_historico(id_contrato):
    '''Aba Histórico: ações registradas no log de auditoria ligadas ao contrato.'''

    df = listar_historico_contrato(id_contrato)
    if df.empty:
        st.info('Nenhuma ação registrada para este contrato.', icon=':material/history:')
        return

    df_visual = pd.DataFrame({
        'data_hora': df['data_hora'],
        'usuario': df['usuario'],
        'acao': df['acao'].map(lambda a: ACOES_HISTORICO.get(a, a)),
        'resultado': df['sucesso'].map(lambda s: 'Sucesso' if s else 'Falha'),
        'detalhe': [resumo_historico(a, d) for a, d in zip(df['acao'], df['detalhes'])],
    })
    st.dataframe(
        df_visual,
        hide_index=True,
        column_config={
            'data_hora': st.column_config.DatetimeColumn('Data/hora', format='DD/MM/YYYY HH:mm'),
            'usuario': 'Usuário',
            'acao': 'Ação',
            'resultado': 'Resultado',
            'detalhe': 'Detalhe',
        }
    )

# ------------------------------------------------------------------ modal

@st.dialog('Detalhe do contrato', width='large', on_dismiss=limpar_detalhe)
def modal_detalhe_contrato(linha):
    '''Detalhe do contrato em abas: Dados, Contrato (PDFs), Ficha Financeira (PDFs) e Histórico.'''

    id_contrato = int(linha['Id'])
    contrato = obter_detalhe_contrato(id_contrato)
    if contrato is None:
        st.error(st.session_state.pop('mensagem_erro', 'Contrato não encontrado.'))
        return

    # cabeçalho: número do contrato e linha de contexto
    st.markdown(f"#### {contrato['numero_contrato']}")
    st.caption(f"{contrato['empresa']} · {contrato['banco']} · {SITUACOES_CONTRATO.get(contrato['status_contrato'], '—')}")

    # mensagem da última ação (sobrevive ao rerun do modal)
    if 'fcd_msg' in st.session_state:
        tipo_msg, texto = st.session_state.pop('fcd_msg')
        if tipo_msg == 'ok':
            st.success(texto)
        else:
            st.error(texto)

    anexos = {tipo: listar_anexos(id_contrato, tipo) for tipo in TIPOS_ANEXO}

    # rótulos fixos: a aba aberta continua a mesma depois de anexar/excluir (a quantidade fica dentro da aba)
    aba_1, aba_2, aba_3, aba_4 = st.tabs(['Dados', 'Contrato', 'Ficha Financeira', 'Histórico'])
    with aba_1:
        aba_dados(contrato)
    with aba_2:
        aba_anexos(id_contrato, 'CONTRATO', anexos['CONTRATO'])
    with aba_3:
        aba_anexos(id_contrato, 'FICHA_FINANCEIRA', anexos['FICHA_FINANCEIRA'])
    with aba_4:
        aba_historico(id_contrato)
