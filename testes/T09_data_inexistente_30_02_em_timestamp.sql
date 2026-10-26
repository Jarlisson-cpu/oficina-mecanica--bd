-- T09 [Tipo] Data inexistente (30/02) em TIMESTAMP
-- Esperado: ERRO 22008
UPDATE ordem_servico SET data_abertura = '2026-02-30 10:00' WHERE id_os = 1;
