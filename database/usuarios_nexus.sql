-- =====================================================================
-- Login do Financiamento pelo cadastro único do Sistema Nexus (nexus.usuarios)
-- =====================================================================
-- A partir desta troca, o login do Financiamento lê os usuários de
-- nexus.usuarios (schema do nexus_portal, database/01_nexus.sql) e só aceita
-- quem tem permissão no módulo em nexus.usuario_modulos (modulo =
-- 'financiamento'). Criar usuário, dar/retirar acesso, resetar senha e
-- bloquear passam a ser feitos no portal (tela Administração).
--
-- O que este script faz:
--   1. copia a senha (hash) de financiamento.usuarios para nexus.usuarios dos
--      usuários com acesso ao Financiamento que ainda não têm senha no nexus
--      (hoje: anna.santos), para entrarem com a mesma senha de hoje;
--   2. troca a FK de financiamento.log_auditoria.id_usuario para
--      nexus.usuarios(id) com NOT VALID: vale para os logs novos e não confere
--      os antigos. Os ids antigos NÃO batem com o nexus (ex.: id 5 era
--      anna.santos no financiamento e é fabiana.pavani no nexus) e o log é
--      somente inserção, então os registros anteriores à troca guardam o id
--      de financiamento.usuarios — para eles, a coluna usuario (nome) é a
--      referência correta.
--
-- financiamento.usuarios NÃO é apagada (fica para a volta atrás e consulta do
-- log antigo); a exclusão fica para depois da validação.
--
-- Ordem na produção: parar o container do Financiamento, executar este
-- script, publicar o código novo (queries_login.py / services/login.py) e
-- subir o container. O código antigo com a FK nova (ou o novo com a FK antiga)
-- grava o log com o id errado ou falha no login.
--
-- Executar uma única vez (usuário fin). Tudo numa transação: em erro, nada fica.
-- =====================================================================

BEGIN;

-- ---------------------------------------------------------------------
-- 1. Senha: copia do financiamento quando o nexus ainda não tem senha
-- ---------------------------------------------------------------------

UPDATE nexus.usuarios n
SET senha_hash = f.senha_hash,
	senha_definida_em = f.senha_definida_em
FROM financiamento.usuarios f
WHERE f.usuario = n.usuario
AND n.senha_hash IS NULL
AND f.senha_hash IS NOT NULL
AND EXISTS (
	SELECT 1 FROM nexus.usuario_modulos um
	WHERE um.id_usuario = n.id AND um.modulo = 'financiamento'
);

-- ---------------------------------------------------------------------
-- 2. FK do log de auditoria: financiamento.usuarios -> nexus.usuarios
-- ---------------------------------------------------------------------

ALTER TABLE financiamento.log_auditoria DROP CONSTRAINT log_auditoria_id_usuario_fkey;

ALTER TABLE financiamento.log_auditoria
	ADD CONSTRAINT log_auditoria_id_usuario_fkey
	FOREIGN KEY (id_usuario) REFERENCES nexus.usuarios(id) NOT VALID;

COMMENT ON COLUMN financiamento.log_auditoria.id_usuario IS 'Usuário autenticado (nexus.usuarios a partir de 11/2026; nos registros anteriores, id de financiamento.usuarios — use a coluna usuario). NULL em falha de login de usuário inexistente.';

-- ---------------------------------------------------------------------
-- Conferência
-- ---------------------------------------------------------------------

-- 1) quem entra no Financiamento: esperado luiz.neves, anna.santos e luiz, todos ativos;
--    senha_cadastrada = true para luiz.neves e anna.santos
SELECT u.id, u.usuario, u.ativo, (u.senha_hash IS NOT NULL) AS senha_cadastrada, um.administrador
FROM nexus.usuarios u
INNER JOIN nexus.usuario_modulos um ON um.id_usuario = u.id AND um.modulo = 'financiamento'
ORDER BY u.id;

-- 2) usuários do financiamento sem acesso pelo nexus (esperado: nenhum)
SELECT f.usuario
FROM financiamento.usuarios f
WHERE NOT EXISTS (
	SELECT 1 FROM nexus.usuarios n
	INNER JOIN nexus.usuario_modulos um ON um.id_usuario = n.id AND um.modulo = 'financiamento'
	WHERE n.usuario = f.usuario
);

-- 3) FK nova (esperado: REFERENCES nexus.usuarios(id) NOT VALID)
SELECT conname, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conrelid = 'financiamento.log_auditoria'::regclass AND contype = 'f';

COMMIT;


-- =====================================================================
-- Operações do desenvolvedor
-- =====================================================================

-- Criar usuário, dar/retirar acesso ao Financiamento, resetar senha e bloquear:
-- tela Administração do portal (ou os SQLs do fim de nexus_portal/database/01_nexus.sql).

-- Depois de validado, apagar a tabela antiga (a FK do log já não depende dela):
-- DROP TABLE financiamento.usuarios;

-- Volta atrás (antes do DROP acima; voltar também o código do login):
-- BEGIN;
-- ALTER TABLE financiamento.log_auditoria DROP CONSTRAINT log_auditoria_id_usuario_fkey;
-- ALTER TABLE financiamento.log_auditoria ADD CONSTRAINT log_auditoria_id_usuario_fkey
-- 	FOREIGN KEY (id_usuario) REFERENCES financiamento.usuarios(id) NOT VALID;
-- COMMIT;
