def registrar_contrato(query, conn, parametro):
    conn.execute(query, parametro)