import hashlib
import pandas as pd
import streamlit as st
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from database.connection import ConexaoBancoSQL
from queries.queries_anexos import TABELAS_ANEXO, SELECT_ANEXOS, SELECT_CONTEUDO_ANEXO, INSERIR_ANEXO, EXCLUIR_ANEXO
from repositories.funcoes import ler_query
from repositories.contract import interacao_database
from services.log import registrar_log, registrar_log_falha, ANEXO_INCLUIR, ANEXO_EXCLUIR

connect = ConexaoBancoSQL()
engine = connect.conexao_banco()

# tipos de anexo (rótulo na tela); cada tipo tem a sua tabela (queries_anexos.TABELAS_ANEXO)
TIPOS_ANEXO = {'CONTRATO': 'Contrato', 'FICHA_FINANCEIRA': 'Ficha Financeira'}

TAMANHO_MAXIMO = 20 * 1024 * 1024   # 20 MB por arquivo (também garantido no banco)

def entidade_anexo(tipo):
    '''Nome da tabela do tipo de anexo (entidade no log de auditoria).'''
    return TABELAS_ANEXO[tipo].split('.')[1]

def listar_anexos(id_contrato, tipo):
    '''Lista os anexos do contrato de um tipo (sem o conteúdo do arquivo).'''

    df = pd.DataFrame()
    try:
        with engine.begin() as conn:
            df = ler_query(text(SELECT_ANEXOS[tipo]), conn, {'id_contrato': id_contrato})
    except Exception as e:
        st.session_state['mensagem_erro'] = f'Erro ao consultar os anexos. ({e})'

    return df

def obter_conteudo_anexo(tipo, id_anexo):
    '''Lê o PDF de um anexo; devolve (nome do arquivo, bytes).'''

    with engine.begin() as conn:
        anexo = interacao_database(text(SELECT_CONTEUDO_ANEXO[tipo]), conn, {'id': id_anexo}).mappings().first()

    return anexo['nome_arquivo'], bytes(anexo['conteudo'])

def validar_arquivos(arquivos):
    '''Valida os PDFs enviados de um tipo (extensão, assinatura %PDF, tamanho e o mesmo arquivo repetido
    no envio); devolve a mensagem de erro ou None.'''

    hashes = set()
    for arquivo in arquivos:
        conteudo = arquivo.getvalue()
        if not arquivo.name.lower().endswith('.pdf') or not conteudo.startswith(b'%PDF'):
            return f'O arquivo "{arquivo.name}" não é um PDF.'
        if len(conteudo) > TAMANHO_MAXIMO:
            return f'O arquivo "{arquivo.name}" passa de 20 MB.'
        if not conteudo:
            return f'O arquivo "{arquivo.name}" está vazio.'
        hash_arquivo = hashlib.sha256(conteudo).hexdigest()
        if hash_arquivo in hashes:
            return f'O arquivo "{arquivo.name}" foi selecionado mais de uma vez.'
        hashes.add(hash_arquivo)

    return None

def gravar_anexos(conn, id_contrato, arquivos_por_tipo):
    '''Grava os PDFs ({tipo: [arquivos]}) na transação recebida, com log de cada arquivo; devolve a quantidade.

    Usada pelo Detalhe (incluir_anexos) e pela inclusão do contrato novo (mesma transação do contrato).
    '''

    usuario = st.session_state.get('auth_usuario')
    gravados = 0
    for tipo, arquivos in arquivos_por_tipo.items():
        for arquivo in arquivos:
            conteudo = arquivo.getvalue()
            anexo = interacao_database(text(INSERIR_ANEXO[tipo]), conn, {
                'id_contrato': id_contrato,
                'nome_arquivo': arquivo.name[:255],
                'tamanho_bytes': len(conteudo),
                'hash_sha256': hashlib.sha256(conteudo).hexdigest(),
                'conteudo': conteudo,
                'usuario': usuario
            }).mappings().first()
            registrar_log(ANEXO_INCLUIR, entidade_anexo(tipo), anexo['id'],
                          detalhes={'tipo': tipo, **dict(anexo)}, conn=conn)
            gravados += 1

    return gravados

def incluir_anexos(id_contrato, arquivos_por_tipo):
    '''Grava os PDFs enviados ({tipo: [arquivos]}) numa única transação, com log de cada arquivo.

    Devolve a mensagem de erro ou None.
    '''

    try:
        with engine.begin() as conn:
            gravados = gravar_anexos(conn, id_contrato, arquivos_por_tipo)

        st.session_state['mensagem_sucesso'] = f'{gravados} anexo(s) incluído(s).'
        return None

    except IntegrityError as e:
        erro = getattr(e, 'orig', e)
        registrar_log_falha(ANEXO_INCLUIR, erro, 'anexo', detalhes={'id_contrato': id_contrato})
        if 'arquivo_key' in str(erro):
            return 'Um dos arquivos já está anexado a este contrato. Nenhum arquivo foi gravado.'
        return f'Erro ao incluir anexos. Nenhum arquivo foi gravado. ({erro})'

    except Exception as e:
        erro = getattr(e, 'orig', e)
        registrar_log_falha(ANEXO_INCLUIR, erro, 'anexo', detalhes={'id_contrato': id_contrato})
        return f'Erro ao incluir anexos. Nenhum arquivo foi gravado. ({erro})'

def excluir_anexo(tipo, id_anexo):
    '''Exclui um anexo (com log, sem o conteúdo); devolve a mensagem de erro ou None.'''

    try:
        with engine.begin() as conn:
            anexo = interacao_database(text(EXCLUIR_ANEXO[tipo]), conn, {'id': id_anexo}).mappings().first()
            if anexo is None:
                return 'Anexo não encontrado.'
            registrar_log(ANEXO_EXCLUIR, entidade_anexo(tipo), id_anexo,
                          detalhes={'tipo': tipo, **dict(anexo)}, conn=conn)
        return None

    except Exception as e:
        erro = getattr(e, 'orig', e)
        registrar_log_falha(ANEXO_EXCLUIR, erro, entidade_anexo(tipo), id_anexo)
        return f'Erro ao excluir o anexo. ({erro})'
