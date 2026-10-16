import urllib.request
import pandas as pd
import streamlit as st
from datetime import datetime
from decimal import Decimal, InvalidOperation
from sqlalchemy import text
from database.connection import ConexaoBancoSQL
from queries.queries_selic import SELECT_SELIC_LISTA, SELECT_DATAS_SELIC, INSERIR_SELIC_LOTE, CONTAR_RECALCULADOS_SELIC
from repositories.funcoes import ler_query
from repositories.contract import interacao_database
from services.log import registrar_log, registrar_log_falha, SELIC_IMPORTAR

connect = ConexaoBancoSQL()
engine = connect.conexao_banco()

# série oficial do BNDES (dias úteis; publicada com alguns dias de antecedência)
URL_SELIC_BNDES = 'https://www.bndes.gov.br/Moedas/um143.txt'

def listar_selic(data_ini=None, data_fim=None):
    '''Lista os valores de SELIC gravados no banco (somente consulta).'''

    df = pd.DataFrame()
    try:
        with engine.begin() as conn:
            df = ler_query(text(SELECT_SELIC_LISTA), conn, {'data_ini': data_ini, 'data_fim': data_fim})
    except Exception as e:
        st.session_state['mensagem_erro'] = f'Erro ao consultar a SELIC. ({e})'

    return df

def baixar_selic_bndes():
    '''Baixa e trata o arquivo da SELIC do BNDES; devolve a lista de (data, valor).'''

    requisicao = urllib.request.Request(URL_SELIC_BNDES, headers={'User-Agent': 'Nexus/1.0'})
    with urllib.request.urlopen(requisicao, timeout=30) as resposta:
        conteudo = resposta.read()

    try:
        texto = conteudo.decode('utf-8-sig')
    except UnicodeDecodeError:
        texto = conteudo.decode('latin-1')

    registros = []
    for numero, linha in enumerate(texto.splitlines(), start=1):
        partes = [parte.strip() for parte in linha.split(';')]
        if len(partes) != 2 or not partes[0] or partes[0].lower() == 'data':
            continue  # cabeçalho ou linha vazia

        try:
            data = datetime.strptime(partes[0], '%d/%m/%Y').date()
            valor = Decimal(partes[1].replace('.', '').replace(',', '.'))
        except (ValueError, InvalidOperation):
            raise ValueError(f'Linha {numero} do arquivo do BNDES em formato inesperado: "{linha.strip()}".')

        registros.append((data, valor))

    if not registros:
        raise ValueError('Arquivo do BNDES sem registros de SELIC.')

    return registros

def importar_selic():
    '''Baixa a SELIC do BNDES e grava só as datas posteriores à última gravada (um único INSERT, com log).'''

    try:
        registros = baixar_selic_bndes()

        with engine.begin() as conn:
            datas_banco = set(ler_query(text(SELECT_DATAS_SELIC), conn)['data'])
            ultima = max(datas_banco) if datas_banco else None

            novos = sorted(r for r in registros if ultima is None or r[0] > ultima)
            lacunas = sum(1 for data, _ in registros if ultima is not None and data <= ultima and data not in datas_banco)

            if not novos:
                mensagem = f'SELIC já está atualizada (última data: {ultima:%d/%m/%Y}).'
                if lacunas:
                    mensagem += f' Há {lacunas} data(s) antiga(s) do BNDES que não estão no banco (não importadas).'
                st.session_state['mensagem_sucesso'] = mensagem
                return

            interacao_database(text(INSERIR_SELIC_LOTE), conn, {
                'datas': [data for data, _ in novos],
                'valores': [valor for _, valor in novos]
            })
            recalculados = conn.execute(text(CONTAR_RECALCULADOS_SELIC)).scalar()

            registrar_log(SELIC_IMPORTAR, 'selic', None, detalhes={
                'fonte': URL_SELIC_BNDES,
                'qtd_datas': len(novos),
                'data_ini': novos[0][0],
                'data_fim': novos[-1][0],
                'ultima_data_anterior': ultima,
                'contratos_recalculados': recalculados,
                'datas_antigas_ausentes': lacunas
            }, conn=conn)

        mensagem = (f'{len(novos)} nova(s) data(s) de SELIC importada(s), de {novos[0][0]:%d/%m/%Y} a {novos[-1][0]:%d/%m/%Y}; '
                    f'{recalculados} contrato(s) recalculado(s).')
        if lacunas:
            mensagem += f' Há {lacunas} data(s) antiga(s) do BNDES que não estão no banco (não importadas).'
        st.session_state['mensagem_sucesso'] = mensagem

    except Exception as e:
        erro = getattr(e, 'orig', e)
        registrar_log_falha(SELIC_IMPORTAR, erro, 'selic', detalhes={'fonte': URL_SELIC_BNDES})
        st.session_state['mensagem_erro'] = f'Erro ao importar a SELIC do BNDES. ({erro})'
