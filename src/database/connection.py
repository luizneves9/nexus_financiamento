import urllib.parse
from sqlalchemy import create_engine
from config.settings import ImportacaoENV

class ConexaoBancoSQL():
    
    def __init__(self):
        self.engine = None
        self.env = ImportacaoENV()
        self.env.processamentoENV()
        
    def conexao_banco(self):
        
        if self.engine is None:
            senha_tratada = urllib.parse.quote_plus(self.env.senha) #type: ignore
            url_conexao = f'postgresql://{self.env.usuario}:{senha_tratada}@{self.env.host}:{self.env.porta}/{self.env.database}'
            
            self.engine = create_engine(url_conexao, echo=False)

        return self.engine
