import json
import streamlit as st
from sqlalchemy import text
from database.connection import ConexaoBancoSQL
from queries.queries_log import INSERIR_LOG
from repositories.log import inserir_log

connect = ConexaoBancoSQL()
engine = connect.conexao_banco()

# catálogo de ações registradas no log de auditoria (database/log_auditoria.sql)
LOGIN = 'LOGIN'
LOGIN_FALHA = 'LOGIN_FALHA'
LOGOUT = 'LOGOUT'
SESSAO_ENCERRADA = 'SESSAO_ENCERRADA'
CADASTRO_SENHA = 'CADASTRO_SENHA'
CONTRATO_INCLUIR = 'CONTRATO_INCLUIR'
CONTRATO_EXCLUIR = 'CONTRATO_EXCLUIR'
ANTECIPACAO_INCLUIR = 'ANTECIPACAO_INCLUIR'
QUITACAO_INCLUIR = 'QUITACAO_INCLUIR'

def _ip():
    '''IP de origem da sessão (None quando o Streamlit não consegue identificar).'''

    try:
        ip = st.context.ip_address
    except Exception:
        return None

    return ip[:45] if isinstance(ip, str) else None

def registrar_log(acao, entidade=None, id_registro=None, sucesso=True, detalhes=None,
                  conn=None, usuario=None, id_usuario=None):
    '''Registra uma ação no log de auditoria.

    - Com `conn`: grava na mesma transação da operação (se o log falhar, a operação é desfeita).
    - Sem `conn`: grava em transação própria (login, logout, falhas de operação).
    Usuário e id são lidos da sessão quando não informados. Nunca passe senha/hash em `detalhes`.
    '''

    parametros = {
        'id_usuario': id_usuario if id_usuario is not None else st.session_state.get('auth_id_usuario'),
        'usuario': (usuario if usuario is not None else st.session_state.get('auth_usuario') or '')[:100] or None,
        'acao': acao,
        'entidade': entidade,
        'id_registro': id_registro,
        'sucesso': sucesso,
        'detalhes': json.dumps(detalhes, default=str, ensure_ascii=False) if detalhes is not None else None,
        'ip': _ip()
    }

    if conn is not None:
        inserir_log(text(INSERIR_LOG), conn, parametros)
        return

    with engine.begin() as conn_log:
        inserir_log(text(INSERIR_LOG), conn_log, parametros)

def registrar_log_falha(acao, erro, entidade=None, id_registro=None, detalhes=None):
    '''Registra a falha de uma operação (transação própria, pois a da operação foi desfeita).

    Não propaga erro do próprio log, para não esconder a mensagem original da operação.
    '''

    try:
        registrar_log(acao, entidade, id_registro, sucesso=False, detalhes={**(detalhes or {}), 'erro': str(erro)[:500]})
    except Exception as e:
        print(f'[log_auditoria] falha ao registrar {acao}: {e}')
