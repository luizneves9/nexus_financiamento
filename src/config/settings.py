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

    def processamentoENV(self):
        self.usuario = os.getenv('DB_USER')
        self.senha = os.getenv('DB_PASS')
        self.host = os.getenv('DB_HOST')
        self.porta = os.getenv('DB_PORT')
        self.database = os.getenv('DB_NAME')

        return self
