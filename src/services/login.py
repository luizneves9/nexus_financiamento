import base64
import hashlib
import hmac
import secrets
import time
import streamlit as st
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from config.settings import ImportacaoENV
from database.connection import ConexaoBancoSQL
from queries.queries_login import SELECT_USUARIO, CADASTRAR_SENHA
from repositories.login import buscar_usuario, atualizar_usuario

connect = ConexaoBancoSQL()
engine = connect.conexao_banco()

# nome do cookie e tempo de permanência do login (renovado enquanto o usuário usa o sistema)
COOKIE_SESSAO = 'nexus_sessao'
DURACAO_SESSAO = 30 * 60
# intervalo mínimo entre renovações do cookie, para não regravar a cada interação
INTERVALO_RENOVACAO = 5 * 60

CHAVE_SESSAO = ImportacaoENV().processamentoENV().chave_sessao

# parâmetros do hash de senha (scrypt: lento e com uso de memória de propósito, contra força bruta)
SCRYPT_N, SCRYPT_R, SCRYPT_P = 2 ** 14, 8, 1
TAMANHO_MINIMO_SENHA = 8

MENSAGEM_DADOS_INCORRETOS = 'Usuário ou senha incorretos.'

def gerar_hash_senha(senha):
    '''Gera o hash da senha com salt aleatório (formato: scrypt$n$r$p$salt$hash).'''

    salt = secrets.token_bytes(16)
    hash_senha = hashlib.scrypt(senha.encode(), salt=salt, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P)

    return f'scrypt${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}${salt.hex()}${hash_senha.hex()}'

def verificar_senha(senha, senha_hash):
    '''Confere a senha digitada contra o hash gravado no banco.'''

    try:
        algoritmo, n, r, p, salt, hash_gravado = senha_hash.split('$')
        if algoritmo != 'scrypt':
            return False
        hash_senha = hashlib.scrypt(senha.encode(), salt=bytes.fromhex(salt), n=int(n), r=int(r), p=int(p))
        return hmac.compare_digest(hash_senha.hex(), hash_gravado)
    except Exception:
        return False

# hash descartável para manter o mesmo tempo de resposta quando o usuário não existe
_HASH_FICTICIO = gerar_hash_senha(secrets.token_hex(16))

def consultar_usuario(usuario):
    '''Busca o usuário no banco de dados (None se não existir).'''

    with engine.begin() as conn:
        return buscar_usuario(text(SELECT_USUARIO), conn, {'usuario': usuario})

def _assinar(conteudo):
    '''Assinatura HMAC-SHA256 do conteúdo do token.'''

    return hmac.new(CHAVE_SESSAO.encode(), conteudo.encode(), hashlib.sha256).hexdigest()

def gerar_token(usuario):
    '''Gera o token assinado (usuário + expiração) gravado no cookie.'''

    usuario_b64 = base64.urlsafe_b64encode(usuario.encode()).decode()
    conteudo = f'{usuario_b64}.{int(time.time()) + DURACAO_SESSAO}'

    return f'{conteudo}.{_assinar(conteudo)}'

def ler_token(token):
    '''Retorna o usuário do token se a assinatura for válida e não estiver expirado.'''

    if not CHAVE_SESSAO or not token:
        return None

    try:
        usuario_b64, expiracao, assinatura = token.split('.')
        if not hmac.compare_digest(assinatura, _assinar(f'{usuario_b64}.{expiracao}')):
            return None
        if int(expiracao) < time.time():
            return None
        return base64.urlsafe_b64decode(usuario_b64.encode()).decode()
    except Exception:
        return None

def _gravar_cookie(valor, max_age):
    '''Grava o cookie no navegador via JavaScript (o Streamlit só lê cookies nativamente).'''

    st.html(
        f"<script>document.cookie = '{COOKIE_SESSAO}={valor}; max-age={max_age}; path=/; SameSite=Strict';</script>",
        unsafe_allow_javascript=True
    )

def _registrar_login(usuario):
    '''Registra o usuário autenticado na sessão.'''

    st.session_state['auth_usuario'] = usuario
    st.session_state['auth_cookie_em'] = 0
    st.session_state.pop('auth_saiu', None)
    st.session_state.pop('auth_primeiro_acesso', None)

def autenticar(usuario, senha):
    '''Valida as credenciais no banco de dados.

    Retorna True quando o login foi feito. Usuário ativo sem senha cadastrada que
    entra com a senha vazia vai para o cadastro de senha (auth_primeiro_acesso).
    Em qualquer outro erro a mensagem é genérica, para não revelar quais usuários existem.
    '''

    if not usuario:
        st.session_state['mensagem_login'] = MENSAGEM_DADOS_INCORRETOS
        return False

    try:
        registro = consultar_usuario(usuario)
    except OperationalError as e:
        st.session_state['mensagem_login'] = f'Erro ao conectar ao banco de dados. ({e.orig})'
        return False

    if registro is None or not registro['ativo']:
        verificar_senha(senha, _HASH_FICTICIO)
        st.session_state['mensagem_login'] = MENSAGEM_DADOS_INCORRETOS
        return False

    # primeiro acesso: sem senha cadastrada e senha vazia -> cadastrar senha
    if registro['senha_hash'] is None:
        if senha:
            st.session_state['mensagem_login'] = MENSAGEM_DADOS_INCORRETOS
        else:
            st.session_state['auth_primeiro_acesso'] = {'id': registro['id'], 'usuario': registro['usuario']}
        return False

    if not senha or not verificar_senha(senha, registro['senha_hash']):
        st.session_state['mensagem_login'] = MENSAGEM_DADOS_INCORRETOS
        return False

    _registrar_login(registro['usuario'])
    return True

def cadastrar_senha(nova_senha, confirmacao):
    '''Cadastra a senha no primeiro acesso (grava somente o hash) e faz o login.'''

    primeiro_acesso = st.session_state.get('auth_primeiro_acesso')
    if not primeiro_acesso:
        return False

    if len(nova_senha) < TAMANHO_MINIMO_SENHA:
        st.session_state['mensagem_login'] = f'A senha deve ter no mínimo {TAMANHO_MINIMO_SENHA} caracteres.'
        return False

    if nova_senha != confirmacao:
        st.session_state['mensagem_login'] = 'As senhas não conferem.'
        return False

    parametros = {'id': primeiro_acesso['id'], 'senha_hash': gerar_hash_senha(nova_senha)}

    try:
        with engine.begin() as conn:
            linhas = atualizar_usuario(text(CADASTRAR_SENHA), conn, parametros)
    except OperationalError as e:
        st.session_state['mensagem_login'] = f'Erro ao conectar ao banco de dados. ({e.orig})'
        return False

    # a senha já foi cadastrada (ou o usuário foi bloqueado) entre o login e o cadastro
    if linhas != 1:
        st.session_state.pop('auth_primeiro_acesso', None)
        st.session_state['mensagem_login'] = 'Não foi possível cadastrar a senha. Faça o login novamente.'
        return False

    _registrar_login(primeiro_acesso['usuario'])
    st.session_state['mensagem_sucesso'] = 'Senha cadastrada com sucesso!'
    return True

def cancelar_primeiro_acesso():
    '''Volta do cadastro de senha para a tela de login.'''

    st.session_state.pop('auth_primeiro_acesso', None)

def usuario_ativo(usuario):
    '''Confere no banco se o usuário ainda existe, está ativo e com senha cadastrada.'''

    try:
        registro = consultar_usuario(usuario)
    except OperationalError:
        return False

    return registro is not None and registro['ativo'] and registro['senha_hash'] is not None

def usuario_logado():
    '''Retorna o usuário logado, restaurando a sessão pelo cookie quando possível.'''

    if st.session_state.get('auth_usuario'):
        return st.session_state['auth_usuario']

    # após "Sair", o cookie lido na abertura da sessão ainda está em st.context — não reutilizar
    if st.session_state.get('auth_saiu'):
        return None

    usuario = ler_token(st.context.cookies.get(COOKIE_SESSAO))
    if usuario and not usuario_ativo(usuario):
        usuario = None
    if usuario:
        st.session_state['auth_usuario'] = usuario
        st.session_state['auth_cookie_em'] = 0

    return usuario

def renovar_sessao():
    '''Regrava o cookie com nova expiração de 30 minutos (sessão deslizante).

    Na renovação também confere no banco se o usuário continua ativo; se foi
    bloqueado ou teve a senha resetada, encerra a sessão.
    '''

    agora = time.time()
    if agora - st.session_state.get('auth_cookie_em', 0) < INTERVALO_RENOVACAO:
        return

    if not usuario_ativo(st.session_state['auth_usuario']):
        sair()
        st.rerun()

    if CHAVE_SESSAO:
        _gravar_cookie(gerar_token(st.session_state['auth_usuario']), DURACAO_SESSAO)
    st.session_state['auth_cookie_em'] = agora

def sair():
    '''Encerra a sessão do usuário; o cookie é apagado na próxima renderização da tela de login.'''

    st.session_state.pop('auth_usuario', None)
    st.session_state.pop('auth_cookie_em', None)
    st.session_state['auth_saiu'] = True

def apagar_cookie_sessao():
    '''Após "Sair": apaga o cookie de sessão e recarrega a página no navegador.

    O recarregamento abre uma nova sessão do Streamlit, zerando todo o session_state
    (filtros, mensagens etc.). Como o cookie já foi apagado, a nova sessão cai no login.
    '''

    if st.session_state.get('auth_saiu'):
        st.html(
            f"<script>document.cookie = '{COOKIE_SESSAO}=; max-age=0; path=/; SameSite=Strict'; window.location.reload();</script>",
            unsafe_allow_javascript=True
        )
