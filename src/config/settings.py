from dotenv import load_dotenv
import os

class ImportacaoENV():

    def __init__(self):
        load_dotenv()
        self.usuario = None
        self.senha = None
        self.host = None
        self.porta = None
        self.database = None
        self.chave_sessao = None

    def processamentoENV(self):
        self.usuario = os.getenv('DB_USER')
        self.senha = os.getenv('DB_PASS')
        self.host = os.getenv('DB_HOST')
        self.porta = os.getenv('DB_PORT')
        self.database = os.getenv('DB_NAME')
        self.chave_sessao = os.getenv('AUTH_SECRET')

        return self
