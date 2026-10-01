import pandas as pd

def registrar_contrato(query, conn, parametro):
    return conn.execute(query, parametro)

def consultar_contratos(query, conn):
    return pd.read_sql(query, conn)
