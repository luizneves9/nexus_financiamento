-- =====================================================================
-- Data de contabilização do contrato
-- Define a entrada do contrato no Endividamento e no Painel de Indicadores
-- (antes: data de emissão). Não afeta a projeção de parcelas.
-- =====================================================================
-- Altera a tabela existente financiamento.contratos (aprovado em 09/11/2026).
-- Executar uma única vez, com backup antes:
--   pg_dump -t financiamento.contratos -t financiamento.projecao_controle ...
--
-- Etapa 1 (este bloco): coluna, trigger de recálculo restrito, preenchimento
-- dos contratos existentes com a data de emissão e validação contra a emissão.
-- Etapa 2 (depois que a aplicação gravar a coluna na inclusão): NOT NULL,
-- no fim deste arquivo. Antes disso, o INSERT atual (sem a coluna) falharia.
--
-- Trigger: trg_projecao_contratos passa a recalcular só quando muda um campo
-- usado por calcular_projecao_contrato. Assim, preencher/editar a data de
-- contabilização (ou empresa, banco, número, débito em conta) não recalcula
-- a projeção. data_referencia e selic são preenchidas na inclusão
-- (triggers BEFORE INSERT a partir de data_emissao/data_bndes).
-- =====================================================================

BEGIN;

-- 1. Nova coluna
ALTER TABLE financiamento.contratos ADD COLUMN data_contabilizacao date NULL;
COMMENT ON COLUMN financiamento.contratos.data_contabilizacao IS
	'Data em que o contrato entra no endividamento (Endividamento e Painel). Não afeta a projeção.';

-- 2. Recálculo da projeção só quando muda um campo usado no cálculo
DROP TRIGGER trg_projecao_contratos ON financiamento.contratos;
CREATE TRIGGER trg_projecao_contratos
	AFTER INSERT OR UPDATE OF tipo_contrato, valor_financiado, taxa_juros_efetiva, prazo_carencia,
		prazo_final, carencia_pagamento, registro_cobranca, data_bndes, data_referencia, selic
	ON financiamento.contratos
	FOR EACH ROW EXECUTE FUNCTION financiamento.projecao_trigger_contratos();

-- 3. Contratos existentes: contabilização = emissão (não dispara o recálculo)
UPDATE financiamento.contratos SET data_contabilizacao = data_emissao WHERE data_contabilizacao IS NULL;

-- 4. Contabilização não pode ser anterior à emissão
ALTER TABLE financiamento.contratos ADD CONSTRAINT contratos_data_contabilizacao_ck
	CHECK (data_contabilizacao >= data_emissao);

COMMIT;

-- Conferência (somente leitura):
--   SELECT count(*) total, count(data_contabilizacao) preenchidos,
--          count(*) FILTER (WHERE data_contabilizacao <> data_emissao) diferentes
--   FROM financiamento.contratos;                      -- preenchidos = total; diferentes = 0
--   SELECT max(data_ultimo_calculo) FROM financiamento.projecao_controle;   -- igual ao de antes
--   SELECT pg_get_triggerdef(oid) FROM pg_trigger WHERE tgname = 'trg_projecao_contratos';


-- =====================================================================
-- Etapa 2: executar SÓ depois que a inclusão de contrato gravar a coluna
-- (já executada em 09/11/2026)
-- =====================================================================
-- ALTER TABLE financiamento.contratos ALTER COLUMN data_contabilizacao SET NOT NULL;
