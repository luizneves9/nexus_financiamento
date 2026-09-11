CREATE OR REPLACE FUNCTION financiamento.projetar_contrato_selic(
    p_data_emissao date,
    p_data_bndes date,
    p_valor_financiado numeric,
    p_taxa_juros_efetiva numeric,
    p_prazo_carencia integer,
    p_prazo_final integer,
    p_carencia_pagamento integer,
    p_registro_cobranca varchar
)
RETURNS TABLE (
    parcela numeric,
    tipo text,
    dia_util date,
    data_vencimento date,
    data_vcto date,
    dias_uteis integer,
    fator_juros numeric,
    saldo_devedor numeric,
    principal numeric,
    juros numeric,
    total_parcela numeric,
    valor_pagamento numeric
)
LANGUAGE sql
AS $$
WITH parametros AS (
    SELECT
        p_data_emissao AS data_emissao,
        p_data_bndes AS data_bndes,
        p_valor_financiado AS valor_financiado,
        p_taxa_juros_efetiva AS taxa_juros_efetiva,
        p_prazo_carencia AS prazo_carencia,
        p_prazo_final AS prazo_final,
        COALESCE(p_carencia_pagamento, 0) AS carencia_pagamento,
        p_registro_cobranca AS registro_cobranca,
        CASE
            WHEN EXTRACT(DAY FROM p_data_emissao) <= 15
                THEN date_trunc('month', p_data_emissao)::date + INTERVAL '14 days'
            ELSE (date_trunc('month', p_data_emissao)::date + INTERVAL '1 month 14 days')::date
        END AS data_referencia,
        (
            SELECT valor
            FROM financiamento.selic
            WHERE data <= p_data_bndes
            ORDER BY data DESC
            LIMIT 1
        ) AS selic
), parcelas AS (
    SELECT
        p.*,
        serie.numero_seq AS parcela,
        CASE
            WHEN serie.numero_seq <= p.carencia_pagamento THEN 'CARENCIA'
            ELSE 'AMORTIZACAO'
        END AS tipo,
        CASE
            WHEN serie.numero_seq <= p.carencia_pagamento THEN
                (p.data_referencia + INTERVAL '1 month' * serie.numero_seq
                    * (p.prazo_carencia::numeric / NULLIF(p.carencia_pagamento, 0)))::date
            ELSE
                (p.data_referencia + INTERVAL '1 month' * p.prazo_carencia
                    + INTERVAL '1 month' * (serie.numero_seq - p.carencia_pagamento))::date
        END AS data_vencimento
    FROM parametros p
    CROSS JOIN LATERAL generate_series(
        1::numeric,
        (p.prazo_final + p.carencia_pagamento)::numeric
    ) AS serie(numero_seq)
), calendario AS (
    SELECT
        p.*,
        financiamento.proximo_dia_util(p.data_vencimento) AS data_vcto,
        financiamento.proximo_dia_util(
            date_trunc('month', p.data_vencimento)::date
        ) AS dia_util,
        CASE
            WHEN p.parcela = 1 THEN
                financiamento.dias_uteis_entre(p.data_bndes, financiamento.proximo_dia_util(p.data_vencimento))
            WHEN p.tipo = 'CARENCIA' THEN
                financiamento.dias_uteis_entre(
                    financiamento.proximo_dia_util(
                        (p.data_vencimento - INTERVAL '1 month'
                            * (p.prazo_carencia::numeric / NULLIF(p.carencia_pagamento, 0)))::date
                    ),
                    financiamento.proximo_dia_util(p.data_vencimento)
                )
            ELSE
                financiamento.dias_uteis_entre(
                    financiamento.proximo_dia_util((p.data_vencimento - INTERVAL '1 month')::date),
                    financiamento.proximo_dia_util(p.data_vencimento)
                )
        END AS dias_uteis
    FROM parcelas p
), calculo AS (
    SELECT
        c.*,
        ROUND(POWER(c.taxa_juros_efetiva / 100 + 1, c.dias_uteis::numeric / 252), 6) AS fator_juros,
        ROUND(c.valor_financiado / NULLIF(c.selic, 0), 2) AS saldo_inicial,
        CASE
            WHEN c.tipo = 'CARENCIA' THEN 0.00
            ELSE ROUND(c.valor_financiado / NULLIF(c.selic, 0) / c.prazo_final, 2)
        END AS principal_original
    FROM calendario c
), calculo_base AS (
    SELECT
        c.*,
        CASE
            WHEN c.tipo = 'CARENCIA' THEN c.saldo_inicial
            ELSE ROUND(
                c.saldo_inicial
                - c.principal_original * GREATEST(0, c.parcela - c.carencia_pagamento - 1),
                2
            )
        END AS saldo_devedor,
        c.principal_original AS principal,
        ROUND(
            (
                CASE
                    WHEN c.tipo = 'CARENCIA' THEN c.saldo_inicial
                    ELSE ROUND(
                        c.saldo_inicial
                        - c.principal_original * GREATEST(0, c.parcela - c.carencia_pagamento - 1),
                        2
                    )
                END
            ) * (c.fator_juros - 1),
            2
        ) AS juros,
        ROUND(
            c.principal_original
            + (
                CASE
                    WHEN c.tipo = 'CARENCIA' THEN c.saldo_inicial
                    ELSE ROUND(
                        c.saldo_inicial
                        - c.principal_original * GREATEST(0, c.parcela - c.carencia_pagamento - 1),
                        2
                    )
                END
            ) * (c.fator_juros - 1),
            2
        ) AS total_parcela
    FROM calculo c
), valores_selic AS (
    SELECT
        c.*,
        sdu.valor AS selic_dia_util,
        sdv.valor AS selic_vencimento,
        ultima.valor AS selic_ultima,
        CASE
            WHEN c.registro_cobranca = 'PRIMEIRO_DIA_UTIL' THEN
                ROUND(c.total_parcela * sdu.valor, 2)
            ELSE 0.00
        END AS valor_parcela_primeiro_dia_util,
        ROUND(c.total_parcela * sdv.valor, 2) AS valor_parcela_vencimento
    FROM calculo_base c
    LEFT JOIN financiamento.selic sdu ON c.dia_util = sdu.data
    LEFT JOIN financiamento.selic sdv ON c.data_vcto = sdv.data
    LEFT JOIN LATERAL (
        SELECT valor
        FROM financiamento.selic
        ORDER BY data DESC
        LIMIT 1
    ) ultima ON TRUE
), calcular_parcela_h AS (
    SELECT
        c.*,
        CASE
            WHEN c.parcela = 1
                OR c.registro_cobranca <> 'PRIMEIRO_DIA_UTIL'
            THEN 0.00
            ELSE COALESCE(
                LAG(c.valor_parcela_vencimento - c.valor_parcela_primeiro_dia_util, 1, 0.00)
                OVER (ORDER BY c.parcela),
                0.00
            )
        END AS parcela_h
    FROM valores_selic c
)
SELECT
    parcela,
    tipo,
    dia_util,
    data_vencimento,
    data_vcto,
    dias_uteis,
    fator_juros,
    saldo_devedor,
    principal,
    juros,
    total_parcela,
    CASE
        WHEN registro_cobranca = 'PRIMEIRO_DIA_UTIL' THEN
            ROUND(
                COALESCE(
                    valor_parcela_primeiro_dia_util + parcela_h,
                    total_parcela * selic_ultima
                ),
                2
            )
        ELSE valor_parcela_vencimento
    END AS valor_pagamento
FROM calcular_parcela_h
ORDER BY parcela;
$$;

CREATE OR REPLACE FUNCTION financiamento.projetar_contrato_tfc(
    p_data_emissao date,
    p_data_bndes date,
    p_valor_financiado numeric,
    p_taxa_juros_efetiva numeric,
    p_prazo_carencia integer,
    p_prazo_final integer,
    p_carencia_pagamento integer
)
RETURNS TABLE (
    parcela numeric,
    tipo text,
    dia_util date,
    data_vencimento date,
    data_vcto date,
    dias_corridos integer,
    fator_juros numeric,
    saldo_devedor numeric,
    principal numeric,
    juros numeric,
    total_parcela numeric,
    valor_pagamento numeric
)
LANGUAGE sql
AS $$
WITH parametros AS (
    SELECT
        p_data_emissao AS data_emissao,
        p_data_bndes AS data_bndes,
        p_valor_financiado AS valor_financiado,
        p_taxa_juros_efetiva AS taxa_juros_efetiva,
        p_prazo_carencia AS prazo_carencia,
        p_prazo_final AS prazo_final,
        COALESCE(p_carencia_pagamento, 0) AS carencia_pagamento,
        CASE
            WHEN EXTRACT(DAY FROM p_data_emissao) <= 15
                THEN date_trunc('month', p_data_emissao)::date + INTERVAL '14 days'
            ELSE (date_trunc('month', p_data_emissao)::date + INTERVAL '1 month 14 days')::date
        END AS data_referencia
), parcelas AS (
    SELECT
        p.*,
        serie.numero_seq AS parcela,
        CASE
            WHEN serie.numero_seq <= p.carencia_pagamento THEN 'CARENCIA'
            ELSE 'AMORTIZACAO'
        END AS tipo,
        CASE
            WHEN serie.numero_seq <= p.carencia_pagamento THEN
                (p.data_referencia + INTERVAL '1 month' * serie.numero_seq
                    * (p.prazo_carencia::numeric / NULLIF(p.carencia_pagamento, 0)))::date
            ELSE
                (p.data_referencia + INTERVAL '1 month' * p.prazo_carencia
                    + INTERVAL '1 month' * (serie.numero_seq - p.carencia_pagamento))::date
        END AS data_vencimento
    FROM parametros p
    CROSS JOIN LATERAL generate_series(
        1::numeric,
        (p.prazo_final + p.carencia_pagamento)::numeric
    ) AS serie(numero_seq)
), calculo AS (
    SELECT
        p.*,
        financiamento.proximo_dia_util(date_trunc('month', p.data_vencimento)::date) AS dia_util,
        financiamento.proximo_dia_util(p.data_vencimento) AS data_vcto,
        CASE
            WHEN p.parcela = 1 THEN p.data_vencimento - p.data_bndes
            WHEN p.tipo = 'CARENCIA' THEN
                financiamento.proximo_dia_util(p.data_vencimento)
                - financiamento.proximo_dia_util(
                    (p.data_vencimento - INTERVAL '1 month'
                        * (p.prazo_carencia::numeric / NULLIF(p.carencia_pagamento, 0)))::date
                )
            ELSE
                financiamento.proximo_dia_util(p.data_vencimento)
                - financiamento.proximo_dia_util((p.data_vencimento - INTERVAL '1 month')::date)
        END AS dias_corridos,
        ROUND(
            POWER(
                p.taxa_juros_efetiva / 100 + 1,
                (
                    CASE
                        WHEN p.parcela = 1 THEN p.data_vencimento - p.data_bndes
                        WHEN p.tipo = 'CARENCIA' THEN
                            financiamento.proximo_dia_util(p.data_vencimento)
                            - financiamento.proximo_dia_util(
                                (p.data_vencimento - INTERVAL '1 month'
                                    * (p.prazo_carencia::numeric / NULLIF(p.carencia_pagamento, 0)))::date
                            )
                        ELSE
                            financiamento.proximo_dia_util(p.data_vencimento)
                            - financiamento.proximo_dia_util((p.data_vencimento - INTERVAL '1 month')::date)
                    END
                )::numeric / 365
            ),
            6
        ) AS fator_juros,
        ROUND(p.valor_financiado, 2) AS saldo_inicial,
        CASE
            WHEN p.tipo = 'CARENCIA' THEN 0.00
            ELSE ROUND(p.valor_financiado / p.prazo_final, 2)
        END AS principal_original
    FROM parcelas p
), calculo_saldo AS (
    SELECT
        c.*,
        CASE
            WHEN c.tipo = 'CARENCIA' THEN c.saldo_inicial
            ELSE ROUND(
                c.saldo_inicial
                - c.principal_original * GREATEST(0, c.parcela - c.carencia_pagamento - 1),
                2
            )
        END AS saldo_devedor
    FROM calculo c
)
SELECT
    parcela,
    tipo,
    dia_util,
    data_vencimento,
    data_vcto,
    dias_corridos,
    fator_juros,
    saldo_devedor,
    principal_original AS principal,
    ROUND(saldo_devedor * (fator_juros - 1), 2) AS juros,
    ROUND(principal_original + saldo_devedor * (fator_juros - 1), 2) AS total_parcela,
    ROUND(principal_original + saldo_devedor * (fator_juros - 1), 2) AS valor_pagamento
FROM calculo_saldo
ORDER BY parcela;
$$;
