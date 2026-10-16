import io
import uuid
import pandas as pd
import streamlit as st
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from sqlalchemy import text
from database.connection import ConexaoBancoSQL
from queries.queries_liquidacao import (
    SELECT_PARCELAS_LIQUIDACAO,
    SELECT_PARCELAS_POR_ID,
    INSERIR_LIQUIDACAO_MANUAL,
    ESTORNAR_LIQUIDACAO,
    CRIAR_TMP_CONCILIACAO_ERP,
    INSERIR_TMP_CONCILIACAO_ERP,
    SELECT_CONCILIACAO_ERP,
    INSERIR_LIQUIDACAO_CONCILIACAO,
    SELECT_CONTRATOS_VINCULO,
    INSERIR_VINCULO_ERP,
    EXCLUIR_VINCULO_ERP,
    SELECT_VINCULOS_ERP,
)
from repositories.funcoes import ler_query
from repositories.contract import interacao_database
from tools.funcoes import transformar_float_em_str
from services.log import (
    registrar_log,
    registrar_log_falha,
    LIQUIDACAO_INCLUIR,
    LIQUIDACAO_ESTORNAR,
    CONCILIACAO_ERP,
    VINCULO_ERP_INCLUIR,
    VINCULO_ERP_EXCLUIR,
)

# colunas do relatório de pagamentos do ERP
COLUNAS_OBRIGATORIAS_ERP = ['Docto', 'Vencimento', 'Valor Pago', 'Data Pagamento']

# situações da conciliação que podem ser liquidadas
STATUS_LIQUIDAVEIS = ('CONCILIADO', 'DIFERENCA')

connect = ConexaoBancoSQL()
engine = connect.conexao_banco()

def listar_parcelas_liquidacao(empresa=None, banco=None, contrato=None, data_vcto_ini=None, data_vcto_fim=None, situacao=None):
    '''Função definida para listar as parcelas projetadas e suas liquidações, com filtros opcionais.'''

    df = pd.DataFrame()
    query = text(SELECT_PARCELAS_LIQUIDACAO)
    parametros = {
        'empresa': f"%{empresa}%" if empresa else None,
        'banco': f"%{banco}%" if banco else None,
        'contrato': f"%{contrato}%" if contrato else None,
        'data_vcto_ini': data_vcto_ini,
        'data_vcto_fim': data_vcto_fim,
        'situacao': situacao
    }

    try:
        with engine.begin() as conn:
            df = ler_query(query, conn, parametros)
    except Exception as e:
        st.session_state['mensagem_erro'] = f'Erro ao consultar as parcelas. ({e})'

    return df

def resumir_parcelas_liquidacao(df):
    '''Função definida para resumir as parcelas filtradas (quantidades e totais), antes da formatação.'''

    return {
        'contratos': df['numero_contrato'].nunique(),
        'parcelas': len(df),
        'liquidadas': int((df['situacao'] == 'LIQUIDADA').sum()),
        'valor_projetado': float(df['valor_projetado'].sum()),
        'valor_pago': float(df['valor_pago'].fillna(0).sum()),
        'valor_ajuste': float(df['valor_ajuste'].fillna(0).sum())
    }

def buscar_parcelas(ids_parcela):
    '''Busca no banco os dados atuais das parcelas selecionadas (para a liquidação manual).'''

    df = pd.DataFrame()
    try:
        with engine.begin() as conn:
            df = ler_query(text(SELECT_PARCELAS_POR_ID), conn, {'ids': list(ids_parcela)})
    except Exception as e:
        st.session_state['mensagem_erro'] = f'Erro ao consultar as parcelas. ({e})'

    return df

def montar_itens_liquidacao(df_editado):
    '''Converte a tabela editada no modal em itens de liquidação (id, data e valor pago).'''

    itens = []
    for _, linha in df_editado.iterrows():
        data_pagamento = pd.to_datetime(linha['data_pagamento']).date() if pd.notna(linha['data_pagamento']) else None
        valor_pago = round(float(linha['valor_pago']), 2) if pd.notna(linha['valor_pago']) else None
        itens.append({'id_parcela': int(linha['id_parcela']), 'data_pagamento': data_pagamento, 'valor_pago': valor_pago})

    return itens

def validar_liquidacao_manual(itens):
    '''Valida os itens da liquidação manual; devolve a mensagem de erro ou None.'''

    if not itens:
        return 'Nenhuma parcela para liquidar.'

    for item in itens:
        if item['data_pagamento'] is None:
            return 'Informe a data de pagamento de todas as parcelas.'
        if item['data_pagamento'] > date.today():
            return 'A data de pagamento não pode ser futura.'
        if item['valor_pago'] is None or item['valor_pago'] <= 0:
            return 'O valor pago deve ser maior que zero.'

    return None

def liquidar_parcelas_manual(itens):
    '''Grava as liquidações manuais numa única transação (com log de cada uma); o trigger marca as parcelas como LIQUIDADA.'''

    query = text(INSERIR_LIQUIDACAO_MANUAL)
    usuario = st.session_state.get('auth_usuario')

    try:
        with engine.begin() as conn:
            for item in itens:
                liquidacao = interacao_database(query, conn, {**item, 'usuario': usuario}).mappings().first()
                registrar_log(LIQUIDACAO_INCLUIR, 'liquidacao', liquidacao['id'], detalhes=dict(liquidacao), conn=conn)

        st.session_state['mensagem_sucesso'] = f'{len(itens)} parcela(s) liquidada(s).'

    except Exception as e:
        erro = getattr(e, 'orig', e)
        registrar_log_falha(LIQUIDACAO_INCLUIR, erro, 'liquidacao',
                            detalhes={'parcelas': [item['id_parcela'] for item in itens]})
        st.session_state['mensagem_erro'] = f'Erro ao liquidar parcelas. ({erro})'

def estornar_liquidacoes(ids_liquidacao, motivo):
    '''Estorna as liquidações numa única transação (com log de cada uma); o trigger reabre a parcela e recalcula o contrato.'''

    query = text(ESTORNAR_LIQUIDACAO)
    usuario = st.session_state.get('auth_usuario')

    try:
        with engine.begin() as conn:
            for id_liquidacao in ids_liquidacao:
                estorno = interacao_database(query, conn, {'id': id_liquidacao, 'motivo': motivo, 'usuario': usuario}).mappings().first()
                if estorno is None:
                    raise ValueError(f'Liquidação {id_liquidacao} não encontrada ou já estornada.')
                registrar_log(LIQUIDACAO_ESTORNAR, 'liquidacao', id_liquidacao, detalhes=dict(estorno), conn=conn)

        st.session_state['mensagem_sucesso'] = f'{len(ids_liquidacao)} liquidação(ões) estornada(s).'

    except Exception as e:
        erro = getattr(e, 'orig', e)
        registrar_log_falha(LIQUIDACAO_ESTORNAR, erro, 'liquidacao',
                            detalhes={'liquidacoes': list(ids_liquidacao), 'motivo': motivo})
        st.session_state['mensagem_erro'] = f'Erro ao estornar liquidações. ({erro})'

def _converter_valor(valor):
    '''Converte valor no formato brasileiro (3.972,07 ou 3972,07) em Decimal.'''
    return Decimal(valor.strip().replace('.', '').replace(',', '.'))

def _converter_data(valor):
    '''Converte data dd/mm/aaaa em date.'''
    return datetime.strptime(valor.strip(), '%d/%m/%Y').date()

def ler_csv_erp(arquivo):
    '''Lê e valida o relatório de pagamentos do ERP (CSV ';').

    Devolve (linhas, descartadas, erro): linhas convertidas (lista de dicts), quantidade de linhas
    sem Docto descartadas e a mensagem de erro (None quando o arquivo é válido).
    '''

    conteudo = arquivo.getvalue()
    try:
        texto = conteudo.decode('utf-8-sig')
    except UnicodeDecodeError:
        texto = conteudo.decode('cp1252')

    try:
        df = pd.read_csv(io.StringIO(texto), sep=';', dtype=str, keep_default_na=False)
    except Exception as e:
        return [], 0, f'Não foi possível ler o arquivo. ({e})'

    df.columns = [str(coluna).strip() for coluna in df.columns]
    faltando = [coluna for coluna in COLUNAS_OBRIGATORIAS_ERP if coluna not in df.columns]
    if faltando:
        return [], 0, f'Colunas obrigatórias não encontradas no arquivo: {", ".join(faltando)}.'

    linhas, erros, descartadas = [], [], 0
    for indice, registro in df.iterrows():
        numero_linha = indice + 2  # linha 1 é o cabeçalho
        docto = registro['Docto'].strip()
        if not docto:
            descartadas += 1
            continue

        try:
            linhas.append({
                'linha': numero_linha,
                'filial': registro.get('Filial', '').strip()[:20] or None,
                'data_pagamento': _converter_data(registro['Data Pagamento']),
                'fornecedor': registro.get('Fornecedor', '').strip()[:255] or None,
                'docto': docto[:100],
                'vencimento': _converter_data(registro['Vencimento']),
                'valor_pago': _converter_valor(registro['Valor Pago'])
            })
        except (ValueError, InvalidOperation):
            erros.append(str(numero_linha))

    if erros:
        return [], descartadas, f'Data ou valor inválido nas linhas: {", ".join(erros[:10])}{"..." if len(erros) > 10 else ""}.'

    if not linhas:
        return [], descartadas, 'Nenhuma linha com Docto encontrada no arquivo.'

    return linhas, descartadas, None

def _carregar_temporaria_erp(conn, linhas):
    '''Cria a tabela temporária da conciliação (apagada no fim da transação) e carrega as linhas do ERP.'''
    interacao_database(text(CRIAR_TMP_CONCILIACAO_ERP), conn, {})
    interacao_database(text(INSERIR_TMP_CONCILIACAO_ERP), conn, linhas)

def conciliar_erp(linhas, ids_contratos):
    '''Prévia da conciliação: carrega o ERP na temporária, cruza com a projeção e desfaz a transação (nada é gravado).'''

    with engine.connect() as conn:
        transacao = conn.begin()
        try:
            _carregar_temporaria_erp(conn, linhas)
            return ler_query(text(SELECT_CONCILIACAO_ERP), conn, {'contratos': list(ids_contratos)})
        finally:
            transacao.rollback()

def resumir_conciliacao(df):
    '''Quantidade e valor por situação da conciliação, antes da formatação.'''

    def total(status, coluna):
        return float(df.loc[df['status'] == status, coluna].fillna(0).sum())

    def qtd(status):
        return int((df['status'] == status).sum())

    return {
        'conciliado': (qtd('CONCILIADO'), total('CONCILIADO', 'valor_erp')),
        'diferenca': (qtd('DIFERENCA'), total('DIFERENCA', 'diferenca')),
        'conflito': (qtd('CONFLITO'), total('CONFLITO', 'valor_erp')),
        'nao_identificado': (qtd('NAO_IDENTIFICADO'), total('NAO_IDENTIFICADO', 'valor_erp')),
        'nao_pago_erp': (qtd('NAO_PAGO_ERP'), total('NAO_PAGO_ERP', 'valor_nexus')),
        'ja_liquidada': (qtd('JA_LIQUIDADA'), total('JA_LIQUIDADA', 'valor_erp')),
        'fora_selecao': (qtd('FORA_SELECAO'), total('FORA_SELECAO', 'valor_erp'))
    }

def confirmar_conciliacao(linhas, ids_contratos, parcelas_marcadas, nome_arquivo, descartadas, resumo, chaves_vinculo_manual=0):
    '''Grava as liquidações das chaves marcadas (conciliação refeita na mesma transação) e um log por lote.'''

    lote = str(uuid.uuid4())
    usuario = st.session_state.get('auth_usuario')

    try:
        with engine.begin() as conn:
            _carregar_temporaria_erp(conn, linhas)
            gravadas = interacao_database(text(INSERIR_LIQUIDACAO_CONCILIACAO), conn, {
                'contratos': list(ids_contratos),
                'parcelas_marcadas': list(parcelas_marcadas),
                'lote': lote,
                'nome_arquivo': nome_arquivo,
                'usuario': usuario
            }).mappings().all()

            if not gravadas:
                st.session_state['mensagem_erro'] = 'Nenhuma parcela liquidada: as marcadas não estão mais conciliadas ou com diferença.'
                return

            total_ajuste = float(sum(g['valor_ajuste'] for g in gravadas))
            registrar_log(CONCILIACAO_ERP, 'liquidacao', None, detalhes={
                'lote': lote,
                'nome_arquivo': nome_arquivo,
                'contratos': list(ids_contratos),
                'competencias': sorted({l['vencimento'].strftime('%m/%Y') for l in linhas}),
                'linhas_lidas': len(linhas),
                'linhas_descartadas': descartadas,
                'resumo_previa': {status: {'qtd': q, 'valor': v} for status, (q, v) in resumo.items()},
                'marcadas': len(parcelas_marcadas),
                'chaves_por_vinculo_manual': chaves_vinculo_manual,
                'liquidacoes': [g['id'] for g in gravadas],
                'total_ajuste': total_ajuste
            }, conn=conn)

        mensagem = f'{len(gravadas)} parcela(s) liquidada(s); ajustes R$ {transformar_float_em_str(total_ajuste)}'
        if len(gravadas) < len(parcelas_marcadas):
            mensagem += f'; {len(parcelas_marcadas) - len(gravadas)} descartada(s) por mudança desde a prévia'
        st.session_state['mensagem_sucesso'] = mensagem + '.'

    except Exception as e:
        erro = getattr(e, 'orig', e)
        registrar_log_falha(CONCILIACAO_ERP, erro, 'liquidacao',
                            detalhes={'lote': lote, 'nome_arquivo': nome_arquivo, 'marcadas': len(parcelas_marcadas)})
        st.session_state['mensagem_erro'] = f'Erro ao confirmar a conciliação. ({erro})'

def listar_contratos_vinculo():
    '''Lista os contratos do Nexus para o vínculo manual com o código do ERP.'''

    df = pd.DataFrame()
    try:
        with engine.begin() as conn:
            df = ler_query(text(SELECT_CONTRATOS_VINCULO), conn)
    except Exception as e:
        st.session_state['mensagem_erro'] = f'Erro ao consultar os contratos. ({e})'

    return df

def listar_vinculos_erp(linhas):
    '''Lista os vínculos manuais cadastrados para os códigos do ERP presentes no arquivo.'''

    codigos = sorted({linha['docto'].split('-')[0].strip() for linha in linhas})
    df = pd.DataFrame()
    try:
        with engine.begin() as conn:
            df = ler_query(text(SELECT_VINCULOS_ERP), conn, {'codigos': codigos})
    except Exception as e:
        st.session_state['mensagem_erro'] = f'Erro ao consultar os vínculos. ({e})'

    return df

def vincular_codigos_erp(pares):
    '''Grava os vínculos permanentes (código do ERP, contrato do Nexus) numa única transação, com log de cada um.

    Devolve a mensagem de erro ou None.
    '''

    query = text(INSERIR_VINCULO_ERP)
    usuario = st.session_state.get('auth_usuario')

    try:
        with engine.begin() as conn:
            for codigo_erp, id_contrato in pares:
                vinculo = interacao_database(query, conn, {
                    'codigo_erp': codigo_erp,
                    'id_contrato': id_contrato,
                    'usuario': usuario
                }).mappings().first()
                registrar_log(VINCULO_ERP_INCLUIR, 'contrato_erp_vinculo', vinculo['id'], detalhes=dict(vinculo), conn=conn)
        return None

    except Exception as e:
        erro = getattr(e, 'orig', e)
        registrar_log_falha(VINCULO_ERP_INCLUIR, erro, 'contrato_erp_vinculo',
                            detalhes={'pares': [{'codigo_erp': c, 'id_contrato': i} for c, i in pares]})
        return f'Erro ao vincular. Nenhum vínculo foi gravado. ({erro})'

def remover_vinculos_erp(pares):
    '''Remove os vínculos (código do ERP, contrato do Nexus) numa única transação, com log de cada um.

    Devolve a mensagem de erro ou None.
    '''

    query = text(EXCLUIR_VINCULO_ERP)

    try:
        with engine.begin() as conn:
            for codigo_erp, id_contrato in pares:
                vinculo = interacao_database(query, conn, {'codigo_erp': codigo_erp, 'id_contrato': id_contrato}).mappings().first()
                if vinculo is None:
                    raise ValueError(f'Vínculo do código {codigo_erp} com o contrato {id_contrato} não encontrado.')
                registrar_log(VINCULO_ERP_EXCLUIR, 'contrato_erp_vinculo', vinculo['id'], detalhes=dict(vinculo), conn=conn)
        return None

    except Exception as e:
        erro = getattr(e, 'orig', e)
        registrar_log_falha(VINCULO_ERP_EXCLUIR, erro, 'contrato_erp_vinculo',
                            detalhes={'pares': [{'codigo_erp': c, 'id_contrato': i} for c, i in pares]})
        return f'Erro ao remover. Nenhum vínculo foi removido. ({erro})'
